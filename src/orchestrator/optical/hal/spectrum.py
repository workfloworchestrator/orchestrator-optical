"""Spectrum-area HAL dispatchers.

The FlexILS-centric engine used to provision optical circuits on the spectrum
sections of an Optical Spectrum subscription (OEL, OSNC and OCRS TL1 objects,
shutters and labels), plus optical cross-connections. Each operation is routed
with ``match/case`` on the vendor and platform of the Optical Node; for Groove
G30 and GX G42 nodes the circuit operations are no-ops, as those platforms do
not have internal optical cross-connections. The FlexILS implementation lives in
:mod:`orchestrator.optical.hal.adapters.nokia_flexils.spectrum`.
"""

from __future__ import annotations

from orchestrator.optical.hal._common import (
    UnsupportedPlatformError,
    _as_flexils_block,
    _vendor_platform,
)
from orchestrator.optical.hal.adapters.nokia_flexils import spectrum as flexils
from orchestrator.optical.products.product_blocks.optical_node.unions import AnyOpticalNodeBlockProvisioningUnion
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor
from orchestrator.optical.products.product_blocks.optical_port.unions import AnyOpticalPortBlockProvisioning
from orchestrator.optical.products.product_blocks.optical_spectrum_section import (
    OpticalSpectrumSectionBlockProvisioning,
)
from orchestrator.optical.utils.custom_types.frequencies import Bandwidth, Frequency, Passband
from orchestrator.optical.utils.datadiff import DiffResult, compare_jsons

__all__ = [
    "create_optical_cross_connection",
    "delete_optical_circuit",
    "delete_optical_circuit_oel",
    "delete_optical_cross_connection",
    "ensure_optical_circuit",
    "set_optical_circuit_label",
    "validate_optical_circuit",
]


def ensure_optical_circuit(
    optical_node_block: AnyOpticalNodeBlockProvisioningUnion,
    optical_spectrum_section_block: OpticalSpectrumSectionBlockProvisioning,
    optical_spectrum_name: str,
    passband: Passband,
    carrier: tuple[Frequency, Bandwidth],
    label: str | None = None,
    circuit_identifier: str = "",
) -> DiffResult:
    """Ensure the optical circuit of the given section exists and converges to the desired state.

    This is the single idempotent primitive for every optical-circuit write:
    create, modify and reconcile all flow through it. The circuit is looked up
    by identity (circuit identifier plus endpoints); the label, passband,
    carrier and OEL reference converge in place. A missing OEL or OSNC is
    created, so unlike :func:`set_optical_circuit_label` this never fails on a
    deleted circuit. This is the idempotent primitive for shared (reused) channels.

    Args:
        optical_node_block: The source Optical Node of the section.
        optical_spectrum_section_block: The optical spectrum section configuration.
        optical_spectrum_name: The user-facing name of the optical spectrum.
        passband: Frequency range allowed for transmission.
        carrier: Tuple of (center frequency, bandwidth) for the carrier signal.
        label: Optional label for the circuit.
        circuit_identifier: The subscription instance id of the circuit; used to derive the
            device-side OEL AID and OSNC CKTIDSUFFIX.

    Returns:
        The difference between the circuit configuration before and after the call.
        Platforms without internal cross-connections yield an empty diff.

    Raises:
        ValueError: If the circuit cannot be ensured.
        UnsupportedPlatformError: If the vendor/platform combination is not supported.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.FLEXILS):
            return flexils.ensure(
                _as_flexils_block(optical_node_block),
                optical_spectrum_section_block,
                optical_spectrum_name,
                passband,
                carrier,
                label,
                circuit_identifier,
            )
        case (Vendor.NOKIA, Platform.GROOVE_G30) | (Vendor.NOKIA, Platform.GX_G42):
            return compare_jsons({}, {})
        case _:
            msg = f"ensure_optical_circuit: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)


def delete_optical_circuit(
    optical_node_block: AnyOpticalNodeBlockProvisioningUnion,
    optical_spectrum_section_block: OpticalSpectrumSectionBlockProvisioning,
    optical_spectrum_name: str,
    passband: Passband,
    circuit_identifier: str = "",
) -> DiffResult:
    """Delete an optical circuit for the given optical spectrum section.

    The operation is idempotent: an already absent circuit yields an empty diff
    instead of failing, so a retried or partially applied teardown is safe.

    Args:
        optical_node_block: The source Optical Node of the section.
        optical_spectrum_section_block: The optical spectrum section configuration.
        optical_spectrum_name: The user-facing name of the optical spectrum.
        passband: Frequency range allowed for transmission.
        circuit_identifier: The subscription instance id of the circuit; used as the OSNC CKTIDSUFFIX.

    Returns:
        The difference between the circuit configuration before and after the
        deletion. Platforms without internal cross-connections yield an empty diff.

    Raises:
        UnsupportedPlatformError: If the vendor/platform combination is not supported.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.FLEXILS):
            return flexils.delete(
                _as_flexils_block(optical_node_block),
                optical_spectrum_section_block,
                optical_spectrum_name,
                passband,
                circuit_identifier,
            )
        case (Vendor.NOKIA, Platform.GROOVE_G30) | (Vendor.NOKIA, Platform.GX_G42):
            return compare_jsons({}, {})
        case _:
            msg = f"delete_optical_circuit: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)


def delete_optical_circuit_oel(
    optical_node_block: AnyOpticalNodeBlockProvisioningUnion,
    circuit_identifier: str,
) -> DiffResult:
    """Delete the OEL of the given circuit on the node, when no other OSNC uses it.

    Only FlexILS nodes have OELs; on Groove G30 and GX G42 nodes this is a no-op.
    On FlexILS an OEL may be shared by more than one OSNC: while another OSNC on the
    node still references it, the OEL is left in place.

    Args:
        optical_node_block: The Optical Node hosting the OEL.
        circuit_identifier: The subscription instance id of the circuit; used as the OEL AID.

    Returns:
        The difference between the OEL configuration before and after the deletion.
        Platforms without OELs yield an empty diff.

    Raises:
        UnsupportedPlatformError: If the vendor/platform combination is not supported.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.FLEXILS):
            return flexils.delete_oel(_as_flexils_block(optical_node_block), circuit_identifier)
        case (Vendor.NOKIA, Platform.GROOVE_G30) | (Vendor.NOKIA, Platform.GX_G42):
            return compare_jsons({}, {})
        case _:
            msg = f"delete_optical_circuit_oel: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)


def validate_optical_circuit(
    optical_node_block: AnyOpticalNodeBlockProvisioningUnion,
    optical_spectrum_section_block: OpticalSpectrumSectionBlockProvisioning,
    optical_spectrum_name: str,
    passband: Passband,
    carrier: tuple[Frequency, Bandwidth],
    label: str,
    circuit_identifier: str = "",
) -> None:
    """Validate the optical spectrum section configuration on the given Optical Node.

    Args:
        optical_node_block: The Optical Node to validate.
        optical_spectrum_section_block: The optical spectrum section to validate.
        optical_spectrum_name: Name of the optical spectrum.
        passband: Frequency range allowed for transmission.
        carrier: Tuple of (center frequency, bandwidth) for the carrier signal.
        label: Service label to validate.
        circuit_identifier: The subscription instance id of the circuit; used as the OSNC CKTIDSUFFIX.

    Raises:
        ValueError: If the configuration is invalid.
        UnsupportedPlatformError: If the vendor/platform combination is not supported.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.FLEXILS):
            return flexils.validate(
                _as_flexils_block(optical_node_block),
                optical_spectrum_section_block,
                optical_spectrum_name,
                passband,
                carrier,
                label,
                circuit_identifier,
            )
        case (Vendor.NOKIA, Platform.GROOVE_G30) | (Vendor.NOKIA, Platform.GX_G42):
            # These platforms do not have internal optical crossconnections to validate
            return None
        case _:
            msg = f"validate_optical_circuit: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)


def set_optical_circuit_label(
    source_optical_node_block: AnyOpticalNodeBlockProvisioningUnion,
    optical_spectrum_section_block: OpticalSpectrumSectionBlockProvisioning,
    optical_spectrum_name: str,
    passband: Passband,
    label: str,
    circuit_identifier: str = "",
) -> DiffResult:
    """Overwrite the OSNC label of the given optical spectrum section with the full label.

    The composite digital-service circuit label (``"<channel>: <svcA> + <svcB>"``) is
    always written in full, so reused channels converge and reconcile repairs drift.
    The label is double-quoted on the TL1 wire so the ``":"`` separator survives
    command framing. Label-only writes never touch the admin state; for
    create/modify/reconcile paths (including healing a missing OSNC) use
    :func:`ensure_optical_circuit` instead.

    Args:
        source_optical_node_block: The source Optical Node of the section.
        optical_spectrum_section_block: The optical spectrum section configuration.
        optical_spectrum_name: The user-facing name of the optical spectrum.
        passband: Frequency range allowed for transmission.
        label: The full label to write.
        circuit_identifier: The subscription instance id of the circuit; used as the OSNC CKTIDSUFFIX.

    Returns:
        The difference between the OSNC configuration before and after the update.
        Platforms without internal cross-connections yield an empty diff.

    Raises:
        ValueError: If the OSNC cannot be found.
        UnsupportedPlatformError: If the vendor/platform combination is not supported.
    """
    match _vendor_platform(source_optical_node_block):
        case (Vendor.NOKIA, Platform.FLEXILS):
            return flexils.set_label(
                _as_flexils_block(source_optical_node_block),
                optical_spectrum_section_block,
                optical_spectrum_name,
                passband,
                label,
                circuit_identifier,
            )
        case (Vendor.NOKIA, Platform.GROOVE_G30) | (Vendor.NOKIA, Platform.GX_G42):
            return compare_jsons({}, {})
        case _:
            msg = f"set_optical_circuit_label: {type(source_optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)


def create_optical_cross_connection(
    optical_node_block: AnyOpticalNodeBlockProvisioningUnion,
    from_port: AnyOpticalPortBlockProvisioning,
    to_port: AnyOpticalPortBlockProvisioning,
    passband: Passband,
    carrier: tuple[Frequency, Bandwidth] | None = None,
    label: str | None = None,
    circuit_name: str | None = None,
    circuit_identifier: str = "",
) -> DiffResult:
    """Create an optical cross connection on the given Optical Node.

    Args:
        optical_node_block: The Optical Node to configure.
        from_port: The Optical Port block to connect from.
        to_port: The Optical Port block to connect to.
        passband: Frequency range allowed for transmission.
        carrier: Tuple of (center frequency, bandwidth) for the carrier signal.
        label: Label for the connection.
        circuit_name: Deprecated; kept for backwards compatibility, device-side circuit
            identifiers are derived from `circuit_identifier`.
        circuit_identifier: The subscription instance id of the circuit; used as the OCRS CKTIDSUFFIX.

    Returns:
        The difference between the cross connection configuration before and after
        the creation.

    Raises:
        NotImplementedError: If the node vendor does not support this operation.
        ValueError: If the cross connection cannot be created.
        UnsupportedPlatformError: If the vendor/platform combination is not supported.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.FLEXILS):
            return flexils.create_cross_connection(
                _as_flexils_block(optical_node_block),
                from_port,
                to_port,
                passband,
                carrier,
                label,
                circuit_name,
                circuit_identifier,
            )
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            msg = "create_optical_cross_connection is not implemented for Groove G30 nodes"
            raise NotImplementedError(msg)
        case (Vendor.NOKIA, Platform.GX_G42):
            msg = "create_optical_cross_connection is not implemented for GX G42 nodes"
            raise NotImplementedError(msg)
        case _:
            msg = f"create_optical_cross_connection: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)


def delete_optical_cross_connection(
    optical_node_block: AnyOpticalNodeBlockProvisioningUnion,
    from_port: AnyOpticalPortBlockProvisioning,
    to_port: AnyOpticalPortBlockProvisioning,
    passband: Passband,
    carrier: tuple[Frequency, Bandwidth] | None = None,
    label: str | None = None,
    circuit_name: str | None = None,
    circuit_identifier: str = "",
) -> DiffResult:
    """Delete an optical cross connection on the given Optical Node.

    Args:
        optical_node_block: The Optical Node to configure.
        from_port: The Optical Port block to disconnect from.
        to_port: The Optical Port block to disconnect to.
        passband: Frequency range allowed for transmission.
        carrier: Tuple of (center frequency, bandwidth) for the carrier signal.
        label: Label of the connection.
        circuit_name: Deprecated; kept for backwards compatibility, device-side circuit
            identifiers are derived from `circuit_identifier`.
        circuit_identifier: The subscription instance id of the circuit; used as the OCRS CKTIDSUFFIX.

    Returns:
        The difference between the cross connection configuration before and after
        the deletion.

    Raises:
        NotImplementedError: If the node vendor does not support this operation.
        ValueError: If the cross connection cannot be found.
        UnsupportedPlatformError: If the vendor/platform combination is not supported.
    """
    match _vendor_platform(optical_node_block):
        case (Vendor.NOKIA, Platform.FLEXILS):
            return flexils.delete_cross_connection(
                _as_flexils_block(optical_node_block),
                from_port,
                to_port,
                passband,
                carrier,
                label,
                circuit_name,
                circuit_identifier,
            )
        case (Vendor.NOKIA, Platform.GROOVE_G30):
            msg = "delete_optical_cross_connection is not implemented for Groove G30 nodes"
            raise NotImplementedError(msg)
        case (Vendor.NOKIA, Platform.GX_G42):
            msg = "delete_optical_cross_connection is not implemented for GX G42 nodes"
            raise NotImplementedError(msg)
        case _:
            msg = f"delete_optical_cross_connection: {type(optical_node_block).__name__}"
            raise UnsupportedPlatformError(msg)
