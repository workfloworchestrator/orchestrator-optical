"""Composition contract tests for the Optical Digital Service modify workflow parts.

These tests are database-free: they verify the composition contract itself (the
page-sequence order and its conditional routing pages, the pure rename/path
helpers and the shipped modify step order), not the workflow execution. The
DB-backed selectors of the modify page sequence are replaced with fakes, so the
page sequences can be driven in-process.
"""

import inspect
from types import SimpleNamespace
from typing import Any, cast

import pytest
from pydantic_forms.validators import Choice, choice_list

from orchestrator.optical.workflows import OPTICAL_MODULE_BLOCK_STATE_KEY
from orchestrator.optical.workflows.optical_digital_service import modify_optical_digital_service as digital_modify
from orchestrator.optical.workflows.optical_digital_service.modify_optical_digital_service import (
    MODIFY_OPTICAL_DIGITAL_SERVICE_BLOCK_STEPS,
    modify_optical_digital_service_form_pages,
)
from orchestrator.optical.workflows.optical_digital_service.shared import (
    flattened_section_port_ids,
    validated_channel_names,
)
from test.support.core_api import step_functions

FREQUENCY_1 = 193_450_000
BANDWIDTH_1 = 100_000


def _fake_single_choice(*args: Any, **kwargs: Any) -> type[Choice]:
    return cast(type[Choice], Choice("FakeChoice", {"opt-a": "opt-a", "opt-b": "opt-b"}))


def _fake_multiple_choice(*args: Any, **kwargs: Any) -> type[list[Choice]]:
    base = Choice("FakeChoice", {"opt-a": "opt-a", "opt-b": "opt-b"})
    return cast(type[list[Choice]], choice_list(base))


def _fake_path_choice(*args: Any, **kwargs: Any) -> type[Choice]:
    return cast(type[Choice], Choice("FakePathChoice", {"p1;p2": ("p1;p2", "nodeA (p1) x nodeB (p2)")}))


def _make_channel(
    name: str = "ch-01",
    owner: str = "sub-1",
    *,
    with_sections: bool = True,
) -> SimpleNamespace:
    """Build a DB-free transport channel with two line ports and optional sections."""
    line_a = SimpleNamespace(subscription_instance_id="line-a")
    line_b = SimpleNamespace(subscription_instance_id="line-b")
    sections = (
        [
            SimpleNamespace(
                subscription_instance_id="sec-1",
                optical_spectrum_section_add_drop_ports=[
                    SimpleNamespace(subscription_instance_id="p1"),
                    SimpleNamespace(subscription_instance_id="p2"),
                ],
                optical_spectrum_section_express_ports=[],
            )
        ]
        if with_sections
        else []
    )
    return SimpleNamespace(
        subscription_instance_id=f"channel-{name}",
        owner_subscription_id=owner,
        optical_transport_channel_name=name,
        optical_transport_central_frequency=FREQUENCY_1,
        optical_transport_mode="opt-a",
        optical_transport_line_ports=[line_a, line_b],
        optical_transport_spectrum=SimpleNamespace(
            optical_spectrum_name=f"{name} spectrum",
            optical_spectrum_passband=(193_400_000, 193_500_000),
            optical_spectrum_sections=sections,
        ),
    )


def _make_digital_subscription(
    service_name: str = "svcA",
    owner: str = "sub-1",
    channel_owner: str = "sub-1",
    *,
    with_sections: bool = True,
) -> SimpleNamespace:
    """Build a DB-free digital service subscription with a single channel."""
    block = SimpleNamespace(
        owner_subscription_id=owner,
        optical_digital_service_name=service_name,
        optical_digital_service_transport_channels=[_make_channel(owner=channel_owner, with_sections=with_sections)],
    )
    return SimpleNamespace(
        product=SimpleNamespace(name="Optical Digital Service"),
        subscription_id="sub-1",
        customer_id="cust-1",
        optical_digital_service=block,
    )


def _monkeypatch_modify_selectors(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch the DB/device-backed modify page selectors with DB-free fakes."""
    monkeypatch.setattr(digital_modify, "optical_transport_mode_selector", _fake_single_choice)
    monkeypatch.setattr(digital_modify, "multiple_optical_node_selector", _fake_multiple_choice)
    monkeypatch.setattr(digital_modify, "multiple_optical_pipe_selector_of_types", _fake_multiple_choice)
    monkeypatch.setattr(digital_modify, "optical_digital_service_path_choice", _fake_path_choice)
    monkeypatch.setattr(digital_modify, "channel_names_taken_by_others", lambda _ids: {})


def test_modify_block_steps_have_the_expected_order() -> None:
    """The shipped digital modify block steps run in the documented order."""
    names = [step.name for step in MODIFY_OPTICAL_DIGITAL_SERVICE_BLOCK_STEPS]
    assert names == [
        "Updating Optical Digital Service block",
        "Replacing the optical path of the transport channels",
        "Configuring the line ports on the transponders",
        "Configuring the client ports on the transponders",
        "Configuring the cross-connects in the transponders",
        "Modifying the optical sections of the transport channels",
        "Updating the available passbands of the OLS ports in the paths",
        "Waiting for the retune to settle",
        "Setting the transmitted optical power to match the line system target",
        "Persist optical module block",
    ]


def test_modify_block_steps_consume_the_block_state_key() -> None:
    """Every shipped digital modify block step takes the block under ``optical_module_block``."""
    for step_func in step_functions(MODIFY_OPTICAL_DIGITAL_SERVICE_BLOCK_STEPS):
        signature = inspect.signature(step_func)
        assert OPTICAL_MODULE_BLOCK_STATE_KEY in signature.parameters, step_func.__name__


def test_modify_form_pages_yield_routing_pages_for_owned_sections(monkeypatch: pytest.MonkeyPatch) -> None:
    """The modify page sequence yields identity, channels, routing and path pages for owned sections."""
    _monkeypatch_modify_selectors(monkeypatch)
    subscription = _make_digital_subscription()
    generator = modify_optical_digital_service_form_pages(
        subscription.optical_digital_service, product_name=subscription.product.name
    )
    page_names: list[str] = []

    page_1 = next(generator)
    page_names.append(page_1.__name__)
    assert set(page_1.model_fields) == {"optical_digital_service_name", "channel_name_1"}

    page_2 = generator.send(
        page_1(optical_digital_service_name="svcB", channel_name_1="ch-02"),
    )
    page_names.append(page_2.__name__)
    assert set(page_2.model_fields) == {"optical_transport_mode", "frequency_1", "bandwidth_1"}

    page_3 = generator.send(
        page_2(optical_transport_mode="opt-a", frequency_1=FREQUENCY_1, bandwidth_1=BANDWIDTH_1),
    )
    page_names.append(page_3.__name__)
    assert set(page_3.model_fields) == {"intermediate_node_instance_ids"}

    page_4 = generator.send(page_3(intermediate_node_instance_ids=["opt-a"]))
    page_names.append(page_4.__name__)
    assert set(page_4.model_fields) == {"exclude_node_instance_ids", "divider1", "exclude_pipe_instance_ids"}

    page_5 = generator.send(
        page_4(exclude_node_instance_ids=["opt-a"], exclude_pipe_instance_ids=["opt-b"], divider1=None),
    )
    page_names.append(page_5.__name__)
    assert set(page_5.model_fields) == {"optical_path"}

    with pytest.raises(StopIteration) as exc_info:
        generator.send(page_5(optical_path="p1;p2"))
    result = exc_info.value.value
    assert result["optical_digital_service_name"] == "svcB"
    assert result["channel_name_1"] == "ch-02"
    assert result["optical_path"] == ["p1", "p2"]

    assert page_names == [
        "ModifyOpticalDigitalServiceIdentityForm",
        "ModifyOpticalDigitalServiceForm",
        "CreateOpticalSpectrumWaypointsForm",
        "CreateOpticalSpectrumConstraintsForm",
        "CreateOpticalDigitalServicePathForm",
    ]


def test_modify_form_pages_skip_routing_pages_for_reused_channels(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reused channels keep their owner's path: the sequence stops after the channels page."""
    _monkeypatch_modify_selectors(monkeypatch)
    subscription = _make_digital_subscription(channel_owner="sub-other")
    generator = modify_optical_digital_service_form_pages(
        subscription.optical_digital_service, product_name=subscription.product.name
    )

    page_1 = next(generator)
    assert page_1.__name__ == "ModifyOpticalDigitalServiceIdentityForm"
    page_2 = generator.send(
        page_1(optical_digital_service_name="svcA", channel_name_1="ch-01"),
    )
    assert page_2.__name__ == "ModifyOpticalDigitalServiceForm"
    with pytest.raises(StopIteration) as exc_info:
        generator.send(
            page_2(optical_transport_mode="opt-a", frequency_1=FREQUENCY_1, bandwidth_1=BANDWIDTH_1),
        )
    assert "optical_path" not in exc_info.value.value


def test_modify_form_pages_skip_routing_pages_without_sections(monkeypatch: pytest.MonkeyPatch) -> None:
    """Directly connected services have no OLS path to change: the sequence stops after the channels page."""
    _monkeypatch_modify_selectors(monkeypatch)
    subscription = _make_digital_subscription(with_sections=False)
    generator = modify_optical_digital_service_form_pages(
        subscription.optical_digital_service, product_name=subscription.product.name
    )

    page_1 = next(generator)
    page_2 = generator.send(
        page_1(optical_digital_service_name="svcA", channel_name_1="ch-01"),
    )
    with pytest.raises(StopIteration) as exc_info:
        generator.send(
            page_2(optical_transport_mode="opt-a", frequency_1=FREQUENCY_1, bandwidth_1=BANDWIDTH_1),
        )
    assert "optical_path" not in exc_info.value.value


def test_modify_identity_form_rejects_reused_channel_rename(monkeypatch: pytest.MonkeyPatch) -> None:
    """The identity page refuses to rename a channel owned by another service."""
    _monkeypatch_modify_selectors(monkeypatch)
    subscription = _make_digital_subscription(channel_owner="sub-other")
    generator = modify_optical_digital_service_form_pages(
        subscription.optical_digital_service, product_name=subscription.product.name
    )
    page_1 = next(generator)
    with pytest.raises(ValueError, match="cannot be renamed"):
        page_1(optical_digital_service_name="svcA", channel_name_1="ch-renamed")


def test_validated_channel_names_keep_current_on_no_request() -> None:
    """No requested name keeps every current name without consulting the taken map."""
    assert validated_channel_names(["ch-01"], [True], None, None, {"ch-02": "sub-x"}) == ["ch-01"]
    assert validated_channel_names(["ch-1", "ch-2"], [True, True], None, None, {}) == ["ch-1", "ch-2"]


def test_validated_channel_names_apply_owned_renames() -> None:
    """Requested names replace the current ones, stripped."""
    assert validated_channel_names(["ch-01"], [True], "  ch-02 ", None, {}) == ["ch-02"]
    assert validated_channel_names(["ch-1", "ch-2"], [True, True], None, "ch-3", {}) == ["ch-1", "ch-3"]


def test_validated_channel_names_reject_reused_rename() -> None:
    """A reused channel keeps the name of its owning subscription."""
    with pytest.raises(ValueError, match="cannot be renamed"):
        validated_channel_names(["ch-01"], [False], "ch-02", None, {})


def test_validated_channel_names_reject_collisions_and_duplicates() -> None:
    """Renaming onto another service's channel or duplicating names is rejected."""
    with pytest.raises(ValueError, match="already used by another service"):
        validated_channel_names(["ch-01"], [True], "ch-02", None, {"ch-02": "sub-x"})
    with pytest.raises(ValueError, match="different names"):
        validated_channel_names(["ch-1", "ch-2"], [True, True], "ch-9", "ch-9", {})


def test_validated_channel_names_reject_blank_and_separators() -> None:
    """Blank names and label separators never reach the devices."""
    with pytest.raises(ValueError, match="cannot be blank"):
        validated_channel_names(["ch-01"], [True], "   ", None, {})
    with pytest.raises(ValueError, match="ambiguous"):
        validated_channel_names(["ch-01"], [True], "ch:02", None, {})


def test_validated_channel_names_reject_second_name_for_single_channel() -> None:
    """A second channel name requires a dual-channel service."""
    with pytest.raises(ValueError, match="dual-channel"):
        validated_channel_names(["ch-01"], [True], None, "ch-02", {})


def _port(port_id: str) -> SimpleNamespace:
    return SimpleNamespace(subscription_instance_id=port_id)


def test_flattened_section_port_ids_collapses_shared_boundaries() -> None:
    """Contiguous sections share their boundary port, reported once."""
    sections = [
        SimpleNamespace(
            optical_spectrum_section_add_drop_ports=[_port("p1"), _port("p2")],
            optical_spectrum_section_express_ports=[_port("x1")],
        ),
        SimpleNamespace(
            optical_spectrum_section_add_drop_ports=[_port("p2"), _port("p3")],
            optical_spectrum_section_express_ports=[],
        ),
    ]
    assert flattened_section_port_ids(sections) == ["p1", "x1", "p2", "p3"]


def test_flattened_section_port_ids_empty() -> None:
    """A section-less (direct) spectrum flattens to no ports."""
    assert flattened_section_port_ids([]) == []
