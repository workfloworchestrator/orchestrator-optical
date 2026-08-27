"""Systematic model-workflow drift canary.

The shipped workflows write data into the shipped product blocks through the
anti-corruption populate/update functions. When a block model is restructured
(such as the Optical Node blocks moving their management data into the composed
``management`` sub-block) and the writer is not updated in lockstep, the drift
is silent: the write either raises at workflow time or, worse, is only noticed
for the vendors that happen to have coverage.

This module is the permanent guard: for every shipped populate/update function
it asserts that every block field it writes is declared on the target block
model class. The table below is explicit and discovered by reading each
function body; dotted field paths express nested writes (``a.b`` means the
``b`` field of the product block referenced by field ``a``).

These tests are database-free and fast.
"""

import inspect

import pytest

from orchestrator.optical.products.product_blocks.optical_coherent_pluggable import (
    OpticalCoherentPluggableBlockInactive,
    OpticalCoherentPluggableBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_digital_service import (
    OpticalDigitalServiceBlockInactive,
    OpticalDigitalServiceBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_location import (
    OpticalModuleLocationBlockInactive,
    OpticalModuleLocationBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_node.abstracts import AbstractOpticalNodeBlockInactive
from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import (
    NokiaFlexIlsBlockInactive,
    NokiaFlexIlsBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_node.nokia_groove_g30 import (
    NokiaGrooveG30BlockInactive,
    NokiaGrooveG30BlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_node.nokia_gx_g42 import (
    NokiaGxG42BlockInactive,
    NokiaGxG42BlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_pipe.abstracts import AbstractOpticalPipeBlockProvisioning
from orchestrator.optical.products.product_blocks.optical_pipe.fiber_patch import OpticalFiberPatchBlockInactive
from orchestrator.optical.products.product_blocks.optical_pipe.fiber_span import OpticalFiberSpanBlockInactive
from orchestrator.optical.products.product_blocks.optical_pipe.leased_spectrum import OpticalLeasedSpectrumBlockInactive
from orchestrator.optical.products.product_blocks.optical_port.abstracts import (
    AbstractOpticalOlsPortBlockProvisioning,
    AbstractOpticalPortBlockInactive,
)
from orchestrator.optical.products.product_blocks.optical_port.ols_add_drop import OlsAddDropPortBlockInactive
from orchestrator.optical.products.product_blocks.optical_port.transponder_client import (
    OpticalTransponderClientPortBlockInactive,
)
from orchestrator.optical.products.product_blocks.optical_spectrum import (
    OpticalSpectrumBlockInactive,
    OpticalSpectrumBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_spectrum_section import OpticalSpectrumSectionBlockInactive
from orchestrator.optical.products.product_blocks.optical_transport_channel import (
    OpticalTransportChannelBlockInactive,
    OpticalTransportChannelBlockProvisioning,
)
from orchestrator.optical.workflows.optical_coherent_pluggable.create import (
    populate_optical_coherent_pluggable_block,
)
from orchestrator.optical.workflows.optical_coherent_pluggable.modify import (
    update_optical_coherent_pluggable_block,
)
from orchestrator.optical.workflows.optical_digital_service.create_optical_digital_service import (
    construct_optical_digital_service_model,
)
from orchestrator.optical.workflows.optical_digital_service.modify_optical_digital_service import (
    update_subscription as update_optical_digital_service_subscription,
)
from orchestrator.optical.workflows.optical_location.create import populate_optical_module_location_block
from orchestrator.optical.workflows.optical_location.modify import update_optical_module_location_block
from orchestrator.optical.workflows.optical_node.nokia_flexils.create import (
    populate_optical_node_nokia_flexils_block,
)
from orchestrator.optical.workflows.optical_node.nokia_flexils.modify import (
    update_optical_node_nokia_flexils_block,
)
from orchestrator.optical.workflows.optical_node.nokia_groove_g30.create import (
    populate_optical_node_nokia_groove_g30_block,
)
from orchestrator.optical.workflows.optical_node.nokia_groove_g30.modify import (
    update_optical_node_nokia_groove_g30_block,
)
from orchestrator.optical.workflows.optical_node.nokia_gx_g42.create import (
    populate_optical_node_nokia_gx_g42_block,
)
from orchestrator.optical.workflows.optical_node.nokia_gx_g42.modify import (
    update_optical_node_nokia_gx_g42_block,
)
from orchestrator.optical.workflows.optical_node.shared.create import populate_abstract_optical_node_fields
from orchestrator.optical.workflows.optical_node.shared.modify import update_optical_node_block_fields
from orchestrator.optical.workflows.optical_node.shared.retrieve import (
    retrieve_optical_node_role_and_software_version,
)
from orchestrator.optical.workflows.optical_pipe.fiber_patch.create import build_fiber_patch_block
from orchestrator.optical.workflows.optical_pipe.fiber_span.create import build_fiber_span_block
from orchestrator.optical.workflows.optical_pipe.leased_spectrum.create import build_leased_spectrum_block
from orchestrator.optical.workflows.optical_pipe.shared import new_pipe_port_block, update_optical_pipe_block
from orchestrator.optical.workflows.optical_spectrum_service.create_optical_spectrum import (
    create_optical_spectrum_model,
    divide_path_into_sections,
)
from orchestrator.optical.workflows.optical_spectrum_service.modify_optical_spectrum import (
    update_subscription as update_optical_spectrum_subscription,
)
from orchestrator.optical.workflows.optical_spectrum_service.shared import (
    store_list_of_ports_into_spectrum_sections,
    update_used_passbands,
)


def _entry(writer, block_class, field_paths):
    """Build a ``pytest.param`` for one writer."""
    return pytest.param(writer, block_class, tuple(field_paths), id=writer.__name__)


#: Explicit table of the shipped anti-corruption populate/update functions, the block
#: class each one targets and the block fields it writes. Field paths are dotted for
#: nested writes (``a.b`` = field ``b`` of the block referenced by field ``a``).
WRITERS = [
    # --- Optical Node family ---
    _entry(
        populate_abstract_optical_node_fields,
        AbstractOpticalNodeBlockInactive,
        (
            "location",
            "management.optical_module_node_fqdn",
            "management.optical_module_node_dcn_loopback_ip",
            "management.optical_module_node_dcn_interface_ip",
            "management.optical_module_node_vendor",
            "management.optical_module_node_platform",
        ),
    ),
    # The shared retrieval step writes the node role and the software version
    # onto the block (the shared helper and the populate functions no longer do).
    _entry(
        retrieve_optical_node_role_and_software_version,
        AbstractOpticalNodeBlockInactive,
        (
            "optical_node_role",
            "management.optical_module_node_software_version",
        ),
    ),
    _entry(
        update_optical_node_block_fields,
        AbstractOpticalNodeBlockInactive,
        (
            "management.optical_module_node_fqdn",
            "management.optical_module_node_dcn_loopback_ip",
            "management.optical_module_node_dcn_interface_ip",
        ),
    ),
    _entry(
        populate_optical_node_nokia_flexils_block,
        NokiaFlexIlsBlockInactive,
        (
            "location",
            "management.optical_module_node_fqdn",
            "management.optical_module_node_dcn_loopback_ip",
            "management.optical_module_node_dcn_interface_ip",
            "management.optical_module_node_vendor",
            "management.optical_module_node_platform",
            "optical_flexils_gmpls_id",
            "optical_flexils_target_id",
        ),
    ),
    _entry(
        populate_optical_node_nokia_groove_g30_block,
        NokiaGrooveG30BlockInactive,
        (
            "location",
            "management.optical_module_node_fqdn",
            "management.optical_module_node_dcn_loopback_ip",
            "management.optical_module_node_dcn_interface_ip",
            "management.optical_module_node_vendor",
            "management.optical_module_node_platform",
        ),
    ),
    _entry(
        populate_optical_node_nokia_gx_g42_block,
        NokiaGxG42BlockInactive,
        (
            "location",
            "management.optical_module_node_fqdn",
            "management.optical_module_node_dcn_loopback_ip",
            "management.optical_module_node_dcn_interface_ip",
            "management.optical_module_node_vendor",
            "management.optical_module_node_platform",
        ),
    ),
    _entry(
        update_optical_node_nokia_flexils_block,
        NokiaFlexIlsBlockProvisioning,
        (
            "management.optical_module_node_fqdn",
            "management.optical_module_node_dcn_loopback_ip",
            "management.optical_module_node_dcn_interface_ip",
            "optical_flexils_gmpls_id",
            "optical_flexils_target_id",
        ),
    ),
    _entry(
        update_optical_node_nokia_groove_g30_block,
        NokiaGrooveG30BlockProvisioning,
        (
            "management.optical_module_node_fqdn",
            "management.optical_module_node_dcn_loopback_ip",
            "management.optical_module_node_dcn_interface_ip",
        ),
    ),
    _entry(
        update_optical_node_nokia_gx_g42_block,
        NokiaGxG42BlockProvisioning,
        (
            "management.optical_module_node_fqdn",
            "management.optical_module_node_dcn_loopback_ip",
            "management.optical_module_node_dcn_interface_ip",
        ),
    ),
    # --- Optical Module Location family ---
    _entry(
        populate_optical_module_location_block,
        OpticalModuleLocationBlockInactive,
        ("longitude", "latitude", "location_code", "location_name"),
    ),
    _entry(
        update_optical_module_location_block,
        OpticalModuleLocationBlockProvisioning,
        ("longitude", "latitude", "location_code", "location_name"),
    ),
    # --- Optical Coherent Pluggable family ---
    _entry(
        populate_optical_coherent_pluggable_block,
        OpticalCoherentPluggableBlockInactive,
        (
            "optical_port_host_node",
            "optical_port_name",
            "optical_port_description",
            "optical_coherent_pluggable_firmware_version",
        ),
    ),
    _entry(
        update_optical_coherent_pluggable_block,
        OpticalCoherentPluggableBlockProvisioning,
        ("optical_port_description", "optical_coherent_pluggable_firmware_version"),
    ),
    # --- Optical Pipe family ---
    _entry(build_fiber_span_block, OpticalFiberSpanBlockInactive, ("optical_pipe_name",)),
    _entry(build_fiber_patch_block, OpticalFiberPatchBlockInactive, ("optical_pipe_name",)),
    _entry(build_leased_spectrum_block, OpticalLeasedSpectrumBlockInactive, ("optical_pipe_name",)),
    _entry(update_optical_pipe_block, AbstractOpticalPipeBlockProvisioning, ("optical_pipe_name",)),
    _entry(
        new_pipe_port_block,
        AbstractOpticalPortBlockInactive,
        ("optical_port_name", "optical_port_host_node", "optical_port_description"),
    ),
    # --- Optical Spectrum Service family ---
    _entry(
        create_optical_spectrum_model,
        OpticalSpectrumBlockInactive,
        ("optical_spectrum_name", "optical_spectrum_passband"),
    ),
    _entry(
        divide_path_into_sections,
        OlsAddDropPortBlockInactive,
        ("optical_port_name", "optical_port_host_node", "optical_port_description"),
    ),
    _entry(store_list_of_ports_into_spectrum_sections, OpticalSpectrumBlockInactive, ("optical_spectrum_sections",)),
    _entry(
        store_list_of_ports_into_spectrum_sections,
        OpticalSpectrumSectionBlockInactive,
        ("optical_spectrum_section_add_drop_ports", "optical_spectrum_section_express_ports"),
    ),
    _entry(update_used_passbands, AbstractOpticalOlsPortBlockProvisioning, ("optical_passbands",)),
    _entry(
        update_optical_spectrum_subscription,
        OpticalSpectrumBlockProvisioning,
        ("optical_spectrum_name", "optical_spectrum_passband"),
    ),
    # --- Optical Digital Service family ---
    _entry(
        construct_optical_digital_service_model,
        OpticalTransponderClientPortBlockInactive,
        ("optical_port_name", "optical_port_host_node", "optical_port_description"),
    ),
    _entry(
        construct_optical_digital_service_model,
        OpticalSpectrumBlockInactive,
        ("optical_spectrum_name", "optical_spectrum_passband"),
    ),
    _entry(
        construct_optical_digital_service_model,
        OpticalTransportChannelBlockInactive,
        (
            "optical_transport_central_frequency",
            "optical_transport_mode",
            "optical_transport_line_ports",
            "optical_transport_spectrum",
            "optical_transport_channel_name",
        ),
    ),
    _entry(
        construct_optical_digital_service_model,
        OpticalDigitalServiceBlockInactive,
        (
            "optical_digital_service_name",
            "optical_digital_service_client_ports",
            "optical_digital_service_transport_channels",
        ),
    ),
    _entry(
        update_optical_digital_service_subscription,
        OpticalDigitalServiceBlockProvisioning,
        ("optical_digital_service_name",),
    ),
    _entry(
        update_optical_digital_service_subscription,
        OpticalTransportChannelBlockProvisioning,
        (
            "optical_transport_central_frequency",
            "optical_transport_mode",
            "optical_transport_spectrum.optical_spectrum_passband",
        ),
    ),
]


def _assert_field_declared(writer, block_class, field_path: str) -> None:
    """Assert that ``field_path`` is declared on ``block_class`` (or a nested product block of it)."""
    segments = field_path.split(".")
    current_class = block_class
    for segment in segments[:-1]:
        nested_class = current_class._product_block_fields_.get(segment)
        assert nested_class is not None, (
            f"{writer.__name__} writes {field_path!r}, but {segment!r} is not a product-block field on "
            f"{current_class.__name__}"
        )
        current_class = nested_class
    leaf = segments[-1]
    assert leaf in current_class.model_fields, (
        f"{writer.__name__} writes {field_path!r}, but {leaf!r} is not declared on {current_class.__name__}"
    )


@pytest.mark.parametrize(("writer", "block_class", "field_paths"), WRITERS)
def test_written_block_fields_are_declared(writer, block_class, field_paths) -> None:
    """Assert every block field written by the shipped populate/update function is declared on its target model."""
    for field_path in field_paths:
        _assert_field_declared(writer, block_class, field_path)


#: Flat ``optical_*``/FQDN fields the shipped node create forms declare, per vendor.
NODE_FORM_OPTICAL_FIELDS: dict[str, set[str]] = {
    "flexils": {
        "optical_module_node_fqdn",
        "optical_flexils_target_id",
        "optical_module_node_dcn_loopback_ip",
        "optical_module_node_dcn_interface_ip",
        "optical_flexils_gmpls_id",
    },
    "groove_g30": {
        "optical_module_node_fqdn",
        "optical_module_node_dcn_loopback_ip",
        "optical_module_node_dcn_interface_ip",
    },
    "gx_g42": {
        "optical_module_node_fqdn",
        "optical_module_node_dcn_loopback_ip",
        "optical_module_node_dcn_interface_ip",
    },
}

#: Block-level create steps consuming the flat create-form keys, per vendor: the
#: shared retrieval step (block-only, consumes no flat keys) and the populate
#: step (the rest).
NODE_BLOCK_STEP_CONSUMERS = {
    "flexils": (retrieve_optical_node_role_and_software_version, populate_optical_node_nokia_flexils_block),
    "groove_g30": (retrieve_optical_node_role_and_software_version, populate_optical_node_nokia_groove_g30_block),
    "gx_g42": (retrieve_optical_node_role_and_software_version, populate_optical_node_nokia_gx_g42_block),
}

#: Form fields shown for display only (not stored on the node block by a block step).
NODE_FORM_DISPLAY_ONLY_FIELDS: dict[str, set[str]] = {
    "flexils": set(),
    "groove_g30": set(),
    "gx_g42": set(),
}


@pytest.mark.parametrize("vendor", ["flexils", "groove_g30", "gx_g42"])
def test_node_form_optical_fields_are_consumed_by_a_block_step(vendor: str) -> None:
    """Assert every flat ``optical_*``/``pqdn`` node create-form field is consumed or display-only."""
    discover_fn, populate_fn = NODE_BLOCK_STEP_CONSUMERS[vendor]
    consumed = (
        set(inspect.signature(discover_fn).parameters)
        | set(inspect.signature(populate_fn).parameters)
        | NODE_FORM_DISPLAY_ONLY_FIELDS[vendor]
    )
    unconsumed = NODE_FORM_OPTICAL_FIELDS[vendor] - consumed
    assert not unconsumed, (
        f"node form fields not consumed by {discover_fn.__name__}/{populate_fn.__name__}: {sorted(unconsumed)}"
    )
