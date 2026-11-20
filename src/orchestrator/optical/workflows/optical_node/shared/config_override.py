"""Shared form pages and step overriding the configuration of an Optical Node.

The NOC changes the configuration of a Groove G30 or GX G42 by hand with
``<marker> path: value`` lines: ``+`` sets a value and owns it as an override (also over the
golden configuration of another product block), ``-`` removes a leaf from the device, ``#``
stops overriding (the golden value is written back if there is one, otherwise the device
keeps the value). See :mod:`orchestrator.optical.hal.reconcile`:

* :func:`config_override_form_pages` — the edit page (the running configuration of the
  device next to an empty field for the lines) and the review page (the difference and the
  edit the device will receive);
* :func:`apply_optical_node_config_override` — the step applying the change and recording
  the overrides.
"""

from typing import Any

from pydantic import ConfigDict, Field, model_validator
from pydantic_forms.types import FormGenerator, State
from pydantic_forms.validators import LongText, read_only_field

from orchestrator.core.forms import FormPage
from orchestrator.core.workflow import step
from orchestrator.optical.hal.reconcile import (
    ConfigDiff,
    ConfigOverride,
    apply_config_override,
    diff_config_override,
    format_config_lines,
    format_config_value,
    parse_override_lines,
    running_config,
)
from orchestrator.optical.hal.sessions import device_sessions
from orchestrator.optical.products.product_blocks.optical_node.unions import AnyOpticalNodeBlockProvisioningUnion
from orchestrator.optical.workflows.optical_node.shared.create import optical_node_block_from_state

__all__ = [
    "OPTICAL_NODE_CONFIG_OVERRIDE_STATE_KEY",
    "apply_optical_node_config_override",
    "config_override_form_pages",
]

#: State key of the change collected by :func:`config_override_form_pages` (:meth:`ConfigOverride.as_dict`).
OPTICAL_NODE_CONFIG_OVERRIDE_STATE_KEY = "optical_node_config_override"

_LINES_HELP = (
    "One '<marker> path: value' per line. "
    "'+' sets the value and overrides the path, also over the golden configuration of a subscription; "
    "'-' removes the leaf from the device (the value is the one it runs); "
    "'#' stops overriding (the value is the override): the golden value is written back, if any, "
    "otherwise the device keeps the value."
)


def _difference_lines(diff: ConfigDiff, change: ConfigOverride) -> str:
    """Return the review of the change, one line per path."""
    lines: list[str] = []
    for path in sorted(change.set):
        if path in diff.changed:
            running, desired = diff.changed[path]
            lines.append(f"{path}: {format_config_value(running)} -> {format_config_value(desired)} (overridden)")
        elif path in diff.added:
            lines.append(f"{path}: {format_config_value(diff.added[path])} (added, overridden)")
        else:
            lines.append(f"{path}: {change.set[path]} (unchanged, overridden)")
    for path in sorted(change.restore):
        if path in diff.changed:
            running, golden = diff.changed[path]
            lines.append(f"{path}: {format_config_value(running)} -> {format_config_value(golden)} (golden restored)")
        else:
            lines.append(f"{path}: {change.restore[path]} (no longer overridden, kept on the device)")
    lines += [f"{path} (removed)" for path in sorted(diff.deleted)]
    others = {**diff.added, **diff.changed}.keys() - change.set.keys() - change.restore.keys()
    lines += [f"{path} (override restored on the device)" for path in sorted(others)]
    return "\n".join(lines) or "No lines: nothing changes."


def config_override_form_pages(node: AnyOpticalNodeBlockProvisioningUnion) -> FormGenerator:
    """Yield the edit and review pages of a configuration override of a Groove G30 or GX G42.

    The edit page shows the running configuration of the device as ``path: value`` lines
    and an empty field for the change lines (``+``, ``-``, ``#``); an empty field changes
    nothing. The review page shows the difference and the edit the device will receive;
    the standard Back button returns to the edit page.

    Args:
        node: The Optical Node block of the subscription being modified.

    Returns:
        The change under :data:`OPTICAL_NODE_CONFIG_OVERRIDE_STATE_KEY`, as :meth:`ConfigOverride.as_dict`.
    """
    running = format_config_lines(running_config(node))

    class OpticalNodeConfigOverrideForm(FormPage):
        model_config = ConfigDict(title="Configuration override")

        running_configuration: read_only_field(running, merge_type=LongText)  # type: ignore[valid-type]
        configuration_override: LongText = Field(default="", description=_LINES_HELP)

        @model_validator(mode="after")
        def validate_form(self) -> "OpticalNodeConfigOverrideForm":
            """Raise if a line is malformed or mistyped, or does not match the device or the overrides."""
            diff_config_override(node, parse_override_lines(self.configuration_override))
            return self

    page = yield OpticalNodeConfigOverrideForm
    change = parse_override_lines(page.configuration_override)
    diff, edit = diff_config_override(node, change)
    difference = _difference_lines(diff, change)

    class OpticalNodeConfigOverrideReviewForm(FormPage):
        model_config = ConfigDict(title="Review the configuration override")

        difference_with_the_device: read_only_field(difference, merge_type=LongText)  # type: ignore[valid-type]
        edit_sent_to_the_device: read_only_field(  # type: ignore[valid-type]
            edit or "Nothing to send.", merge_type=LongText
        )

    yield OpticalNodeConfigOverrideReviewForm
    return {OPTICAL_NODE_CONFIG_OVERRIDE_STATE_KEY: change.as_dict()}


@step("Apply configuration override")
@device_sessions()
def apply_optical_node_config_override(
    optical_module_block: AnyOpticalNodeBlockProvisioningUnion | dict[str, Any] | None,
    optical_node_config_override: dict[str, dict[str, str]],
) -> State:
    """Apply the change of the configuration override form to the node and record the overrides.

    The device is read again and the change checked against it again: what the form
    showed is not trusted.

    Raises:
        ValueError: If there is no Optical Node block in the state under
            ``OPTICAL_MODULE_BLOCK_STATE_KEY``, or a line no longer matches the device.
        ConfigConflictError: If a removed leaf is golden configuration of another product block.
        ConfigApplyError: If the device rejects the edit or does not converge.
    """
    node = optical_node_block_from_state(optical_module_block)
    applied = apply_config_override(node, ConfigOverride.from_dict(optical_node_config_override))
    return {"config_override_applied": applied}
