"""Services for Optical Digital Services.

This module provides the device-level operations used by Optical Digital Service
subscriptions: signal bandwidth retrieval, line/client transceiver configuration,
transponder cross-connects, factory resets, validation and transmit power
alignment.

Operations are dispatched on the vendor of the Optical Node product block with
match/case statements, replacing the legacy attribute-based dispatch on the
``platform`` attribute of the old ``OpticalDeviceBlock``.

The device-side identifiers (e.g. the G42 XCON circuit-id-suffix) are derived
from the ``circuit_identifier`` parameter, i.e. the ``subscription_instance_id``
of the digital service subscription, instead of GARR business logic.
"""

from collections.abc import Sequence
from decimal import Decimal
from re import search
from typing import Any, Literal, Protocol, cast

from requests.exceptions import HTTPError

from orchestrator.optical.hal.optical_node import Vendor, get_flex_client, get_g30_client, get_g42_client, vendor_of
from orchestrator.optical.hal.optical_port import (
    g30_ids_from_port_name,
    g30_port_navigator_node_from_port_name,
)
from orchestrator.optical.products.product_blocks.optical_node.abstracts import (
    AbstractOpticalNodeBlock,
    AbstractOpticalNodeBlockInactive,
    AbstractOpticalNodeBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import NokiaFlexIlsBlockInactive
from orchestrator.optical.products.product_types.optical_digital_service import OpticalDigitalServiceSpeed
from orchestrator.optical.services.nokia import G42Client
from orchestrator.optical.services.nokia.flexils.commands.base import TL1BaseResponse
from orchestrator.optical.services.nokia.g42.data_models.ioa_network_element import (
    AdminStateEnum,
    AlarmReportControlEnum,
    EnableSwitchEnum,
    LldpAdminStatusEnum,
    LldpModeEnum,
    LoopbackEnum,
    PhyModeEnum,
    PrbsDirectionEnum,
    ServiceTypeEnum,
    SignalTypeEnum,
    XconItem,
)
from orchestrator.optical.utils.custom_types.frequencies import Frequency
from orchestrator.optical.utils.datadiff import compare_dicts, compare_pydantic_objects

OpticalNodeBlock = (
    AbstractOpticalNodeBlock | AbstractOpticalNodeBlockProvisioning | AbstractOpticalNodeBlockInactive
)


class FlexilsClientProtocol(Protocol):
    """Typing protocol for the dynamically-bound TL1 commands of :class:`FlexilsClient`.

    The FlexILS client binds its command methods (``rtrv_osnc``, ``ent_ocrs``, ...) to
    the instance at runtime, so static type checkers cannot see them on the class.
    This protocol documents the subset of the command surface used by the HAL.
    """

    tid: str
    gne_ip: str

    def rtrv_oteintf(self) -> TL1BaseResponse:
        """Retrieve the OTEINTF entries of the node."""

    def rtrv_eqpt(self, aid: str | None = None) -> TL1BaseResponse:
        """Retrieve the equipment inventory entries of the node."""

    def rtrv_scg(self, aid: str | None = None, type: str | None = None) -> TL1BaseResponse:  # noqa: A002
        """Retrieve the SCG entries of the node, optionally filtered by type."""

    def ent_oel(
        self,
        aid: str,
        label: str,
        srcnodename: str,
        dstnodename: str,
        explicitroute: list[tuple[str, str, str, str]],
        validfrangelist: list[int],
    ) -> TL1BaseResponse:
        """Enter a new Optical Engineered Lightpath (OEL)."""

    def opr_valroute_oel(self, aid: str) -> TL1BaseResponse:
        """Validate the route of the given OEL."""

    def rtrv_oel(self, aid: str | None = None) -> TL1BaseResponse:
        """Retrieve the OEL entries of the node."""

    def rtrv_osnc(self, aid: str | None = None, oelaid: str | None = None) -> TL1BaseResponse:
        """Retrieve the OSNC entries of the node."""

    def ent_osnc(
        self,
        aid: str,
        label: str,
        remnodetid: str,
        remendpoint: str,
        oelaid: str,
        cktidsuffix: str,
        passbandlist: Sequence[str | int],
        carrierlist: Sequence[str | int],
        **kwargs: Any,
    ) -> TL1BaseResponse:
        """Enter a new OSNC between a local and a remote endpoint."""

    def ed_osnc(
        self,
        aid: str,
        label: str | None = None,
        oelaid: str | None = None,
        cktidsuffix: str | None = None,
        passbandlist: Sequence[str | int] | None = None,
        carrierlist: Sequence[str | int] | None = None,
        is_oos: str | None = None,
        **kwargs: Any,
    ) -> TL1BaseResponse:
        """Edit the configuration of the given OSNC."""

    def dlt_osnc(self, aid: str) -> TL1BaseResponse:
        """Delete the given OSNC."""

    def rtrv_sch(self, aid: str | None = None) -> TL1BaseResponse:
        """Retrieve the superchannel entries of the node."""

    def ed_sch(
        self,
        aid: str,
        label: str | None = None,
        shutterstate: str | None = None,
        **kwargs: Any,
    ) -> TL1BaseResponse:
        """Edit the configuration of the given superchannel."""

    def rtrv_ocrs(
        self,
        fromaid: str | None = None,
        toaid: str | None = None,
        sigtype: str | None = None,
    ) -> TL1BaseResponse:
        """Retrieve the optical cross-connection entries of the node."""

    def ent_ocrs(
        self,
        fromaid: str,
        toaid: str,
        label: str | None = None,
        cktidsuffix: str | None = None,
        freqslotplantype: str | None = None,
        schoffset: str | None = None,
        passbandlist: Sequence[str | int] | None = None,
        carrierlist: Sequence[str | int] | None = None,
        autoretunelmsch: str | None = None,
        intracarrspecshaping: str | None = None,
        **kwargs: Any,
    ) -> TL1BaseResponse:
        """Enter a new optical cross-connection (OCRS)."""

    def dlt_ocrs(self, fromaid: str, toaid: str) -> TL1BaseResponse:
        """Delete the given optical cross-connection (OCRS)."""

    def put_maintenance(self, aidtype: str, aid: str) -> TL1BaseResponse:
        """Put the given entity into maintenance state."""

    def rst_maintenance(self, aidtype: str, aid: str) -> TL1BaseResponse:
        """Restore the given entity from maintenance state."""

    def rtrv_pm_sch(self, aid: str, montype: str | None = None) -> TL1BaseResponse:
        """Retrieve the performance monitoring data of the given superchannel."""


def _get_flex_client(optical_node_block: OpticalNodeBlock) -> FlexilsClientProtocol:
    """Return a FlexILS TL1 client for the given Optical Node block.

    Wraps `hal.optical_node.get_flex_client`, returning the dynamically-bound TL1
    command surface as a protocol so that it type checks.
    """
    if not isinstance(optical_node_block, NokiaFlexIlsBlockInactive):
        msg = f"Expected a Nokia FlexILS node block, got {type(optical_node_block).__name__}"
        raise TypeError(msg)
    return cast(FlexilsClientProtocol, get_flex_client(optical_node_block))


def _node_id(optical_node_block: OpticalNodeBlock) -> str:
    """Return the pqdn of the given Optical Node block, for use in identifiers and messages."""
    pqdn = optical_node_block.pqdn
    return pqdn if pqdn is not None else "<no pqdn>"


def _g30_client_speed_config(speed: OpticalDigitalServiceSpeed) -> tuple[str, str, str]:
    """Map a digital service speed to the Groove G30 (port mode, ethernet service, FEC type)."""
    match speed:
        case OpticalDigitalServiceSpeed._100:  # noqa: SLF001
            return "100GBE", "eth100g", "auto"
        case OpticalDigitalServiceSpeed._400:  # noqa: SLF001
            return "400GBE", "eth400g", "enabled"
    msg = f"Unsupported speed {speed} for the Groove G30 client configuration"
    raise NotImplementedError(msg)


def _g42_client_speed_config(speed: OpticalDigitalServiceSpeed) -> tuple[str, str, str, str]:
    """Map a digital service speed to the GX G42 (required type, required subtype, phy mode, service type)."""
    match speed:
        case OpticalDigitalServiceSpeed._100:  # noqa: SLF001
            return "gx:QSFP28", "TOM-100G-Q", "100G", "100GBE"
        case OpticalDigitalServiceSpeed._400:  # noqa: SLF001
            return "gx:QSFPDD", "TOM-400G-Q-DR4", "400GE", "400GBE"
    msg = f"Unsupported speed {speed} for the GX G42 client configuration"
    raise NotImplementedError(msg)


def _g30_get_modulation_and_rate_from_mode(port_mode: str) -> tuple[str, str]:
    """Retrieve the modulation and rate class for a given port mode.

    Returns 'not-applicable' if not found or if the port mode has no coherent properties.
    """
    port_mode_map = {
        # PortMode: (ModulationFormat, RateClass)  # noqa: ERA001
        "QPSK_100G": ("DP-QPSK", "100G"),
        "8QAM_300G": ("DP-8QAM", "150G"),  # Note: Desc says 150G
        "16QAM_200G": ("DP-16QAM", "200G"),
        "OCHOS_OTU2": ("NRZ", "10G"),
        "OCHOS_OTU2e": ("NRZ", "11G"),
        "8QAM_200G": ("DP-8QAM", "200G"),
        "64QAM_600G": ("DP-64QAM", "600G"),
        "SPQPSK_100G": ("DP-SPQPSK", "100G"),
        "SPQPSK_QPSK_100G": ("DP-SPQPSK-QPSK", "100G"),
        "QPSK_200G": ("DP-QPSK", "200G"),
        "SP16QAM_200G": ("DP-SP16QAM", "200G"),
        "32QAM_200G": ("DP-32QAM", "200G"),
        "QPSK_SP16QAM_200G": ("DP-QPSK-SP16QAM", "200G"),
        "16QAM_300G": ("DP-16QAM", "300G"),
        "SP16QAM_300G": ("DP-SP16QAM", "300G"),
        "32QAM_300G": ("DP-32QAM", "300G"),
        "64QAM_300G": ("DP-64QAM", "300G"),
        "SP16QAM_16QAM_300G": ("DP-SP16QAM-16QAM", "300G"),
        "16QAM_400G": ("DP-16QAM", "400G"),
        "32QAM_400G": ("DP-32QAM", "400G"),
        "64QAM_400G": ("DP-64QAM", "400G"),
        "16QAM_32QAM_400G": ("DP-16QAM-32QAM", "400G"),
        "32QAM_500G": ("DP-32QAM", "500G"),
        "64QAM_500G": ("DP-64QAM", "500G"),
        "32QAM_64QAM_500G": ("DP-32QAM-64QAM", "500G"),
        "QPSK_100G_TRANSPARENT": ("DP-QPSK", "100G"),
        "SP16QAM_16QAM_200G": ("DP-SP16QAM-16QAM", "200G"),
        "32QAM_64QAM_600G": ("DP-32QAM-64QAM", "600G"),
        "SP16QAM_300G_C": ("DP-SP16QAM", "150G"),  # 2*150G
        "QPSK_SP16QAM_300G_C": ("DP-QPSK-SP16QAM", "150G"),
        "16QAM_32QAM_500G_C": ("DP-16QAM-32QAM", "250G"),  # 2*250G
        "16QAM_500G_C": ("DP-16QAM", "250G"),
        "SP16QAM_500G_C": ("DP-SP16QAM", "250G"),
        "QPSK_SP16QAM_500G_C": ("DP-QPSK-SP16QAM", "250G"),
        "32QAM_64QAM_700G_C": ("DP-32QAM-64QAM", "350G"),  # 2*350G
        "16QAM_700G_C": ("DP-16QAM", "350G"),
        "SP16QAM_16QAM_700G_C": ("DP-SP16QAM-16QAM", "350G"),
        "32QAM_900G_C": ("DP-32QAM", "450G"),  # 2*450G
        "16QAM_32QAM_900G_C": ("DP-16QAM-32QAM", "450G"),
        "32QAM_64QAM_1100G_C": ("DP-32QAM-64QAM", "550G"),  # 2*550G
        "SPQPSK_QPSK_200G": ("DP-SPQPSK-QPSK", "200G"),
        "QPSK_SP16QAM_300G": ("DP-QPSK-SP16QAM", "300G"),
        "SP16QAM_16QAM_400G": ("DP-SP16QAM-16QAM", "400G"),
        "16QAM_32QAM_500G": ("DP-16QAM-32QAM", "500G"),
    }
    # Use .get() to handle non-coherent modes like '10GBE' or 'not-applicable'
    return port_mode_map.get(port_mode, ("not-applicable", "not-applicable"))


def get_signal_bandwidth(optical_node_block: OpticalNodeBlock, port_name: str) -> int:
    """Return the signal bandwidth, in MHz, of the transport channel carried by the given line port.

    Args:
        optical_node_block: The Optical Node hosting the line port.
        port_name: The line port name, e.g. ``"1-4-L1"``.

    Returns:
        The signal bandwidth in MHz.

    Raises:
        NotImplementedError: If the node vendor does not support this operation.
        ValueError: If the channel of the given port cannot be found.
    """
    match vendor_of(optical_node_block):
        case Vendor.GROOVE_G30:
            g30 = get_g30_client(optical_node_block)
            shelf_id, slot_id, _, port_id, _ = g30_ids_from_port_name(port_name)
            och_os = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card.port(port_id).och_os.retrieve(
                depth=2, content="config"
            )
            if och_os.fec_type == "SDFEC27ND":
                bw = 75_000
            elif och_os.fec_type == "SDFEC15ND2":
                bw = 68_750
            else:
                bw = 37_500
            return bw

        case Vendor.GX_G42:
            g42 = get_g42_client(optical_node_block)
            channel = None
            channels = g42.data.ne.facilities.super_channel.retrieve(depth=2)
            for ch in channels:
                if any(carrier.startswith(port_name) for carrier in ch.carriers):
                    channel = ch
                    break

            if channel is None:
                msg = f"Channel of port {port_name} not found"
                raise ValueError(msg)

            if channel.spectral_bandwidth is None:
                msg = f"Channel of port {port_name} has no spectral bandwidth"
                raise ValueError(msg)

            bw = channel.spectral_bandwidth * 1000
            num_carriers_if_coupled = 2
            if len(channel.carriers) == num_carriers_if_coupled:
                bw = bw // 2
            return round(bw)

        case Vendor.FLEXILS:
            msg = "get_signal_bandwidth is not implemented for Nokia FlexILS nodes"
            raise NotImplementedError(msg)


def configure_line_transceivers(
    optical_node_block: OpticalNodeBlock,
    port_names: tuple[str, ...],
    central_frequencies: tuple[Frequency, ...],
    modes: tuple[str, ...],
    descriptions: tuple[str, ...],
) -> dict[str, Any]:
    """Configure the line transceivers on the given Optical Node.

    Args:
        optical_node_block: The Optical Node to configure.
        port_names: The line port names.
        central_frequencies: The central frequencies of the transport channels.
        modes: The operating modes of the transport channels.
        descriptions: The channel descriptions.

    Returns:
        A dictionary of configuration diffs, keyed by port/facility name.

    Raises:
        NotImplementedError: If the node vendor does not support this operation.
        ValueError: If the configuration is invalid.
    """
    match vendor_of(optical_node_block):
        case Vendor.GROOVE_G30:
            return _configure_line_transceivers_g30(
                optical_node_block,
                port_names,
                central_frequencies,
                modes,
                descriptions,
            )
        case Vendor.GX_G42:
            return _configure_line_transceivers_g42(
                optical_node_block,
                port_names,
                central_frequencies,
                modes,
                descriptions,
            )
        case Vendor.FLEXILS:
            msg = "configure_line_transceivers is not implemented for Nokia FlexILS nodes"
            raise NotImplementedError(msg)


def _configure_line_transceivers_g30(
    optical_node_block: OpticalNodeBlock,
    port_names: tuple[str, ...],
    central_frequencies: tuple[Frequency, ...],
    modes: tuple[str, ...],
    descriptions: tuple[str, ...],
) -> dict[str, Any]:
    g30 = get_g30_client(optical_node_block)
    configurations = {}
    for port_name, central_frequency, mode, description in zip(
        port_names,
        central_frequencies,
        modes,
        descriptions,
        strict=True,
    ):
        shelf_id, slot_id, _, port_id, _ = g30_ids_from_port_name(port_name)
        uri = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card.port(port_id)
        before = uri.retrieve(depth=3, content="config")
        uri.update(
            port_id=port_id,
            port_mode=mode,
            service_label=description,
            admin_status="up",
        )
        modulation, rate = _g30_get_modulation_and_rate_from_mode(mode)
        uri.och_os.update(
            modulation_format=modulation,
            rate_class=rate,
            frequency=central_frequency,
            rx_frequency=central_frequency,
            service_label=description,
            admin_status="up",
            laser_enable="enabled",
            loopback_enable="disabled",
            loopback_type="none",
        )
        after = uri.retrieve(depth=3, content="config")
        diffs = compare_pydantic_objects(before, after)
        configurations[port_name] = diffs

    return configurations


def _configure_line_transceivers_g42(
    optical_node_block: OpticalNodeBlock,
    port_names: tuple[str, ...],
    central_frequencies: tuple[Frequency, ...],
    modes: tuple[str, ...],
    descriptions: tuple[str, ...],
) -> dict[str, Any]:
    if len(set(modes)) != 1:
        msg = f"All modes must be the same for GX_G42 transponder line configuration but got {modes}."
        raise ValueError(msg)

    g42 = get_g42_client(optical_node_block)
    configurations = {}

    # port
    for port_name, description in zip(port_names, descriptions, strict=True):
        shelf_id, slot_id, port_id = port_name.split("-")  # 1-4-L1 -> 1, 4, L1
        navigator = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)
        before = navigator.retrieve(content="config", depth=2)
        conf = before.model_copy(deep=True)
        conf.admin_state = AdminStateEnum.UNLOCK
        conf.label = description
        conf.alarm_report_control = AlarmReportControlEnum.ALLOWED
        navigator.update(conf)
        after = navigator.retrieve(content="config", depth=2)
        diffs = compare_pydantic_objects(before, after)
        configurations[f"port-{port_name}"] = diffs

        # super-channel-group
        navigator = g42.data.ne.facilities.super_channel_group(port_name)
        before = navigator.retrieve(content="config", depth=2)
        navigator.update(name=port_name, admin_state="unlock", label=description, alarm_report_control="allowed")
        after = navigator.retrieve(content="config", depth=2)
        diffs = compare_pydantic_objects(before, after)
        configurations[f"super-channel-group-{port_name}"] = diffs

    # super-channel
    sup_ch_name = "_".join(port_names)
    navigator = g42.data.ne.facilities.super_channel(sup_ch_name)
    before = navigator.retrieve(content="config", depth=2)
    navigator.update(
        name=sup_ch_name,
        admin_state="unlock",
        label="+".join(descriptions),
        alarm_report_control="allowed",
        carrier_mode=modes[0],
        carriers=[f"{port_name}-1" for port_name in port_names],
    )
    after = navigator.retrieve(content="config", depth=2)
    diffs = compare_pydantic_objects(before, after)
    configurations["super-channel"] = diffs

    # optical-carrier
    for port_name, description, frequency in zip(port_names, descriptions, central_frequencies, strict=True):
        navigator = g42.data.ne.facilities.optical_carrier(f"{port_name}-1")
        before = navigator.retrieve(content="config", depth=2)
        navigator.update(
            name=f"{port_name}-1",
            admin_state="unlock",
            label=description,
            alarm_report_control="allowed",
            frequency=frequency,
        )
        after = navigator.retrieve(content="config", depth=2)
        diffs = compare_pydantic_objects(before, after)
        configurations[f"optical-carrier-{port_name}-1"] = diffs

    return configurations


def configure_transceiver_client(
    optical_node_block: OpticalNodeBlock,
    port_name: str,
    description: str,
    speed: OpticalDigitalServiceSpeed,
) -> dict[str, Any]:
    """Configure the client port of a transceiver on the given Optical Node.

    Args:
        optical_node_block: The Optical Node to configure.
        port_name: The client port name.
        description: The description of the client service.
        speed: The speed of the client service in Gbit/s.

    Returns:
        A dictionary of configuration diffs, keyed by facility name.

    Raises:
        NotImplementedError: If the node vendor or the requested speed is not supported.
        ValueError: If the configuration is invalid.
    """
    match vendor_of(optical_node_block):
        case Vendor.GROOVE_G30:
            return _configure_transceiver_client_g30(optical_node_block, port_name, description, speed)
        case Vendor.GX_G42:
            return _configure_transceiver_client_g42(optical_node_block, port_name, description, speed)
        case Vendor.FLEXILS:
            msg = "configure_transceiver_client is not implemented for Nokia FlexILS nodes"
            raise NotImplementedError(msg)


def _configure_transceiver_client_g30(
    optical_node_block: OpticalNodeBlock,
    port_name: str,
    description: str,
    speed: OpticalDigitalServiceSpeed,
) -> dict[str, Any]:
    navigator, _, _, _, port_id, _ = g30_port_navigator_node_from_port_name(optical_node_block, port_name)
    port_mode, eth_name, fec_type = _g30_client_speed_config(speed)
    eth = getattr(navigator, eth_name)

    before = navigator.retrieve(content="config", depth=3)

    navigator.update(
        port_id=port_id,
        admin_status="up",
        service_label=description,
        port_mode=port_mode,
    )

    eth.update(
        admin_status="up",
        service_label=description,
        loopback_enable="disabled",
        test_signal_enable="NONE",
        client_shutdown="no",
        eth_fec_type=fec_type,
    )

    after = navigator.retrieve(content="config", depth=3)

    return compare_pydantic_objects(before, after)


def _configure_transceiver_client_g42(  # noqa: PLR0915
    optical_node_block: OpticalNodeBlock,
    port_name: str,
    description: str,
    speed: OpticalDigitalServiceSpeed,
) -> dict[str, Any]:
    g42 = get_g42_client(optical_node_block)
    shelf_id, slot_id, port_id = port_name.split("-")  # 1-4-L1 -> 1, 4, L1
    required_type, required_subtype, phy_mode, service_type = _g42_client_speed_config(speed)

    configurations = {}

    # port
    navigator = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)
    before = navigator.retrieve(content="config", depth=2)
    conf = before.model_copy(deep=True)
    conf.admin_state = AdminStateEnum.UNLOCK
    conf.label = description
    conf.alarm_report_control = AlarmReportControlEnum.ALLOWED
    navigator.update(conf)
    after = navigator.retrieve(content="config", depth=2)
    diffs = compare_pydantic_objects(before, after)
    configurations["1.port"] = diffs

    # TOM
    navigator = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id).tom
    before = navigator.retrieve(content="config", depth=2)
    conf = before.model_copy(deep=True)
    conf.admin_state = AdminStateEnum.UNLOCK
    conf.label = description
    conf.required_type = required_type
    conf.required_subtype = required_subtype
    conf.phy_mode = PhyModeEnum(phy_mode)
    conf.alarm_report_control = AlarmReportControlEnum.ALLOWED
    navigator.update(conf)
    after = navigator.retrieve(content="config", depth=2)
    diffs = compare_pydantic_objects(before, after)
    configurations["2.tom"] = diffs

    # trib-ptp
    navigator = g42.data.ne.facilities.trib_ptp(port_name)
    before = navigator.retrieve(content="config", depth=2)
    conf = before.model_copy(deep=True)
    conf.admin_state = AdminStateEnum.UNLOCK
    conf.label = description
    conf.alarm_report_control = AlarmReportControlEnum.ALLOWED
    conf.service_type = ServiceTypeEnum(service_type)
    navigator.update(conf)
    after = navigator.retrieve(content="config", depth=2)
    diffs = compare_pydantic_objects(before, after)
    configurations["3.trib-ptp"] = diffs

    # ethernet
    navigator = g42.data.ne.facilities.ethernet(port_name)
    before = navigator.retrieve(content="config", depth=2)
    conf = before.model_copy(deep=True)
    conf.admin_state = AdminStateEnum.UNLOCK
    conf.label = description
    conf.alarm_report_control = AlarmReportControlEnum.ALLOWED
    conf.fec_mode = EnableSwitchEnum.ENABLED
    conf.loopback = LoopbackEnum.NONE
    conf.test_signal_type = SignalTypeEnum.NONE
    conf.test_signal_direction = PrbsDirectionEnum.EGRESS
    conf.test_signal_monitoring = False
    conf.lldp_admin_status = LldpAdminStatusEnum.RX_ONLY
    conf.lldp_ingress_mode = LldpModeEnum.SNOOP
    conf.lldp_egress_mode = LldpModeEnum.SNOOP
    navigator.update(conf)
    after = navigator.retrieve(content="config", depth=2)
    diffs = compare_pydantic_objects(before, after)
    configurations["4.ethernet"] = diffs

    return configurations


def configure_transponder_crossconnect(
    optical_node_block: OpticalNodeBlock,
    client_port_name: str,
    line_port_names: list[str],
    xconn_description: str = "",
) -> dict[str, Any]:
    """Configure a cross-connect between client and line ports on the given Optical Node.

    Args:
        optical_node_block: The Optical Node to configure.
        client_port_name: The client port name (e.g. ``"port-1/2/3"``).
        line_port_names: List of line port names.
        xconn_description: Optional description for the cross-connect.

    Returns:
        The created cross-connect configuration.

    Raises:
        NotImplementedError: If the node vendor does not support this operation.
        ValueError: If the cross-connect cannot be created.
    """
    match vendor_of(optical_node_block):
        case Vendor.GROOVE_G30:
            return _configure_transponder_crossconnect_g30(
                optical_node_block,
                client_port_name,
                line_port_names,
                xconn_description,
            )
        case Vendor.GX_G42:
            return _configure_transponder_crossconnect_g42(
                optical_node_block,
                client_port_name,
                line_port_names,
                xconn_description,
            )
        case Vendor.FLEXILS:
            msg = "configure_transponder_crossconnect is not implemented for Nokia FlexILS nodes"
            raise NotImplementedError(msg)


def _configure_transponder_crossconnect_g30(  # noqa: PLR0912, PLR0915
    optical_node_block: OpticalNodeBlock,
    client_port_name: str,
    line_port_names: list[str],
    xconn_description: str = "",
) -> dict[str, Any]:
    g30 = get_g30_client(optical_node_block)
    shelf_id, slot_id, _, c_port_id, _ = g30_ids_from_port_name(client_port_name)

    before = g30.data.ne_ne.services.CRS.retrieve(depth=2, content="config")

    line_port_ids = []
    for lpn in line_port_names:
        l_shelf_id, l_slot_id, _, line_port_id, _ = g30_ids_from_port_name(lpn)
        if shelf_id != l_shelf_id or slot_id != l_slot_id:
            msg = (
                f"Client and line ports should be on the same shelf and slot. "
                f"Client: {client_port_name}, Line: {lpn}."
            )
            raise ValueError(msg)
        line_port_ids.append(line_port_id)

    client_port = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card.port(c_port_id).retrieve(depth=3, content="config")
    eth_key = next((f for f in ("eth100g", "eth400g") if getattr(client_port, f, None) is not None), None)
    if not eth_key:
        msg = f"No eth service found on {_node_id(optical_node_block)} {client_port_name}"
        raise ValueError(msg)

    odu_a = (
        f"/ne:ne/shelf[shelf-id='{shelf_id}']/slot[slot-id='{slot_id}']/card/port[port-id='{c_port_id}']"
        f"/{eth_key}/odu[odutype-L1='odu4'][oduid-L1='1'][odutype-L2='unused'][oduid-L2='0']"
        f"[odutype-L3='unused'][oduid-L3='0'][odutype-L4='unused'][oduid-L4='0']"
    )

    odu_b = None
    try:
        crs = g30.data.ne_ne.services.CRS.retrieve(depth=2, content="config")
    except HTTPError as e:
        no_xcon_exists_code = 404
        if e.response.status_code == no_xcon_exists_code:
            crs = []
        else:
            raise
    for c in crs:
        if c.src_tp == odu_a:
            odu_b = c.dst_tp
            odu_a, odu_b = (
                odu_b,
                odu_a,
            )  # swap the strings, so that src-tp is odu_b string
            break
        if c.dst_tp == odu_a:
            odu_b = c.src_tp
            break

    if odu_b:
        id1, id2, id3 = _extract_shelf_slot_port_ids_from_odu_string(odu_b)

        if shelf_id != id1 or slot_id != id2 or id3 not in line_port_ids:
            xconn = g30.data.ne_ne.services.CRS(odu_b, odu_a)
            xconn.delete()
            odu_b = None

    if odu_b is None:
        possible_odus: list[tuple[int, str]] = []
        for line_port_id in line_port_ids:
            och_os = (
                g30.data.ne_ne.shelf(shelf_id)
                .slot(slot_id)
                .card.port(line_port_id)
                .och_os.retrieve(depth=4, content="config")
            )
            otu_key = next(
                (
                    f
                    for f in (
                        "otuc2",
                        "otuc3",
                        "otuc4",
                        "otuc5",
                        "otuc6",
                        "otuc7",
                        "otuc9",
                        "otuc11",
                        "otu4",
                        "otu2",
                        "otu2e",
                    )
                    if getattr(och_os, f, None) is not None
                ),
                None,
            )
            if otu_key is None:
                msg = f"No OTU service found for line port {line_port_id} on {_node_id(optical_node_block)}"
                raise ValueError(msg)
            for odu in getattr(och_os, otu_key).odu:
                key_list = [
                    "odutype_L1",
                    "oduid_L1",
                    "odutype_L2",
                    "oduid_L2",
                    "odutype_L3",
                    "oduid_L3",
                    "odutype_L4",
                    "oduid_L4",
                ]

                if any(getattr(odu, key, None) is None for key in key_list):
                    continue

                if all(getattr(odu, key, None) != "odu4" for key in key_list):
                    continue

                odu_string = (
                    f"/ne:ne/shelf[shelf-id='{shelf_id}']/slot[slot-id='{slot_id}']/card/port"
                    f"[port-id='{line_port_id}']/och-os/{otu_key}/odu[odutype-L1='{odu.odutype_L1}']"
                    f"[oduid-L1='{odu.oduid_L1}'][odutype-L2='{odu.odutype_L2}'][oduid-L2='{odu.oduid_L2}']"
                    f"[odutype-L3='{odu.odutype_L3}'][oduid-L3='{odu.oduid_L3}']"
                    f"[odutype-L4='{odu.odutype_L4}'][oduid-L4='{odu.oduid_L4}']"
                )
                odu_index = int(line_port_id) * 10_000 + int(odu.oduid_L1) * 100 + int(odu.oduid_L2)
                possible_odus.append((odu_index, odu_string))

        used_odus = set()
        for c in crs:
            used_odus.add(c.dst_tp)
            used_odus.add(c.src_tp)

        available_odus = [odu for odu in possible_odus if odu[1] not in used_odus]
        if not available_odus:
            msg = f"No available ODU for crossconnect on {_node_id(optical_node_block)}"
            raise ValueError(msg)
        available_odus.sort(key=lambda x: x[0])  # sort by index
        odu_b = available_odus[0][1]  # take the first available ODU string

    xconn = g30.data.ne_ne.services.CRS(odu_b, odu_a)
    xconn.update(
        src_tp=odu_b,
        dst_tp=odu_a,
        service_label=xconn_description,
    )

    after = g30.data.ne_ne.services.CRS.retrieve(depth=2, content="config")
    return compare_pydantic_objects(before, after)


def _configure_transponder_crossconnect_g42(
    optical_node_block: OpticalNodeBlock,
    client_port_name: str,
    line_port_names: list[str],
    xconn_description: str = "",
) -> dict[str, Any]:
    g42 = get_g42_client(optical_node_block)

    client = f"/ioa-ne:ne/facilities/ethernet[name='{client_port_name}']"
    och_key = _derive_optical_channel_key(line_port_names)
    dst_parent_odu = f"{och_key}-ODUCni"
    direction = "two-way"
    label = xconn_description
    payload_type = _retrieve_payload_type(g42, client_port_name)

    xcon = _find_xcon_g42(g42, client, och_key, direction, payload_type)
    if xcon:
        endpoint = g42.data.ne.services.xcon(xcon.name)
        before = endpoint.retrieve(depth=2, content="config")
        xcon = before.model_copy(deep=True)
        xcon.label = label
        xcon.circuit_id_suffix = label
        endpoint.update(xcon)
        after = endpoint.retrieve(depth=2, content="config")
        return compare_pydantic_objects(before, after)

    dst_time_slots = _retrieve_time_slots(g42, dst_parent_odu, payload_type)
    _create_xcon_g42(
        g42=g42,
        client=client,
        dst_parent_odu=dst_parent_odu,
        direction=direction,
        payload_type=payload_type,
        label=label,
        dst_time_slots=dst_time_slots,
    )
    xcon = _find_xcon_g42(g42, client, och_key, direction, payload_type)
    if xcon:
        return xcon.model_dump(exclude_unset=True)

    msg = f"Unable to create XCON for client {client_port_name} on {_node_id(optical_node_block)}. "
    raise ValueError(msg)


def _find_xcon_g42(
    g42: G42Client,
    client: str,
    line: str,
    direction: str,
    payload_type: str,
) -> XconItem | None:
    """Helper function to find an existing cross-connect on the G42 platform.

    Args:
        g42: G42 client instance.
        client: Source client path.
        line: Line ID inside the destination ODU string.
        direction: Direction of the cross-connect.
        payload_type: Payload type for the cross-connect.

    Returns:
        The cross-connect configuration if found, otherwise None.

    Raises:
        ValueError: If a cross-connect with the same source and destination already exists.
    """
    try:
        xcons = g42.data.ne.services.xcon.retrieve(depth=2, content="config")
    except HTTPError as e:
        no_xcon_exists_code = 404
        if e.response.status_code == no_xcon_exists_code:
            return None
        raise

    for xcon in xcons:
        source_destination_match = (xcon.source == client and line in xcon.destination) or (
            xcon.destination == client and line in xcon.source
        )
        payload_type_match = xcon.payload_type == payload_type
        direction_match = xcon.direction == direction
        if source_destination_match and payload_type_match and direction_match:
            return xcon

        if client in (xcon.source, xcon.destination):
            msg = (
                f"Tributary already cross-connected:"
                f" {xcon.destination}  x  {xcon.source} ."
                f"Please check and remove manually if wrong."
            )
            raise ValueError(msg)

    return None


def _create_xcon_g42(
    g42: G42Client,
    client: str,
    dst_parent_odu: str,
    direction: str,
    payload_type: str,
    label: str,
    dst_time_slots: str,
) -> None:
    """Helper function to create a cross-connect on the G42 platform.

    Args:
        g42: G42 client instance.
        client: Source client path.
        dst_parent_odu: Destination parent ODU path.
        direction: Direction of the cross-connect.
        payload_type: Payload type for the cross-connect.
        label: Label for the cross-connect.
        dst_time_slots: Time slots for the cross-connect.

    Raises:
        HTTPError: If the cross-connect creation fails.
    """
    try:
        g42.operations.create_xcon(
            payload_type=payload_type,
            direction=direction,
            label=label,
            circuit_id_suffix=label,
            source=client,
            dst_parent_odu=dst_parent_odu,
            dst_time_slots=dst_time_slots,
        )
    except HTTPError as e:
        xcon_already_exists_code = 412
        if e.response.status_code == xcon_already_exists_code:
            pass
        else:
            raise


def _derive_optical_channel_key(line_port_names: list[str]) -> str:
    """Derive the optical channel key of the given line port names."""
    if len(line_port_names) == 1:
        return f"{line_port_names[0]}-1"

    num_lines_if_coupled_mode = 2
    if len(line_port_names) == num_lines_if_coupled_mode:
        for name in line_port_names:
            if name.endswith("L1"):
                return f"{name}-1"

    msg = (
        f"Invalid line port names: {line_port_names}. "
        "For coupled modes, ensure both ports are on the same card, thus one ends with 'L1'."
    )
    raise ValueError(msg)


def _retrieve_payload_type(g42: G42Client, client_port_name: str) -> Literal["100GBE", "400GBE"]:
    """Retrieve the payload type of the given client port on a G42 device."""
    trib_ptp = g42.data.ne.facilities.trib_ptp(client_port_name).retrieve(depth=2, content="config")
    payload_type = trib_ptp.service_type

    if payload_type is None:
        msg = f"Unable to retrieve payload type for {g42.url} {client_port_name}"
        raise ValueError(msg)

    match payload_type:
        case ServiceTypeEnum("100GBE"):
            return "100GBE"
        case ServiceTypeEnum("400GBE"):
            return "400GBE"
    msg = f"Invalid payload type '{payload_type}' for {g42.url} {client_port_name}. Expected '100GBE' or '400GBE'."
    raise ValueError(msg)


def _retrieve_time_slots(g42: G42Client, odu_name: str, speed: Literal["100GBE", "400GBE"]) -> str:
    """Retrieve the first block of available time slots of the given ODU with enough capacity for the speed."""
    minimum_slots_required = 80 if speed == "100GBE" else 320

    odu = g42.data.ne.facilities.odu(odu_name).retrieve(depth=2)
    available_time_slots = odu.available_time_slots  # e.g. "1..80,161..480"
    if not available_time_slots:
        msg = f"The key 'available-time-slots' is missing or empty in the ODU data.ODU: {odu}"
        raise ValueError(msg)
    available_time_slots = available_time_slots.split(",")  # e.g. ["1..80", "161..480"]
    available_time_slots = [ts.split("..") for ts in available_time_slots]  # e.g. [["1", "80"], ["161", "480"]]
    available_time_slots = [(int(start), int(end)) for start, end in available_time_slots]  # e.g. [(1, 80), (161, 480)]

    # find next time slot that has at least minimum_slots_required
    for start, end in available_time_slots:
        if end - start + 1 >= minimum_slots_required:
            return f"{start}..{start + minimum_slots_required - 1}"

    msg = (
        f"Not enough available time slots for {g42.url} {odu}. "
        f"Minimum required: {minimum_slots_required}, "
        f"Available: {available_time_slots}"
    )
    raise ValueError(msg)


def delete_transponder_crossconnect(
    optical_node_block: OpticalNodeBlock,
    client_port_name: str,
) -> dict[str, Any]:
    """Delete a cross-connect between client and line ports on the given Optical Node.

    Args:
        optical_node_block: The Optical Node (transponder) to configure.
        client_port_name: The client port name (e.g. ``"port-1/2/3"``).

    Returns:
        A dictionary with a ``"message"`` and the list of deleted cross-connects.

    Raises:
        NotImplementedError: If the node vendor does not support this operation.
    """
    match vendor_of(optical_node_block):
        case Vendor.GROOVE_G30:
            return _delete_transponder_crossconnect_g30(optical_node_block, client_port_name)
        case Vendor.GX_G42:
            return _delete_transponder_crossconnect_g42(optical_node_block, client_port_name)
        case Vendor.FLEXILS:
            msg = "delete_transponder_crossconnect is not implemented for Nokia FlexILS nodes"
            raise NotImplementedError(msg)


def _delete_transponder_crossconnect_g30(
    optical_node_block: OpticalNodeBlock,
    client_port_name: str,
) -> dict[str, Any]:
    result = {"message": "", "deleted_xcon": []}

    g30 = get_g30_client(optical_node_block)

    shelf_id, slot_id, _, port_id, _ = g30_ids_from_port_name(client_port_name)

    uri = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card

    card = uri.retrieve(depth=2)
    if card.required_type == "CHM1":
        result["message"] = (
            f"{_node_id(optical_node_block)} {client_port_name}: no need to delete any xcon,"
            " CHM1 crossconnections are not configurable."
        )
        return result

    client_port = uri.port(port_id).retrieve(depth=3, content="config")
    eth_key = next((f for f in ("eth100g", "eth400g") if getattr(client_port, f, None) is not None), None)
    if not eth_key:
        msg = (
            f"{_node_id(optical_node_block)} {client_port_name}:"
            " This port does not have an ethernet service, it must have been deleted manually."
        )
        raise ValueError(msg)

    odu_string = (
        f"/ne:ne/shelf[shelf-id='{shelf_id}']/slot[slot-id='{slot_id}']"
        f"/card/port[port-id='{port_id}']/{eth_key}/odu[odutype-L1='odu4']"
        f"[oduid-L1='1'][odutype-L2='unused'][oduid-L2='0']"
        f"[odutype-L3='unused'][oduid-L3='0'][odutype-L4='unused'][oduid-L4='0']"
    )

    try:
        crs = g30.data.ne_ne.services.CRS.retrieve(depth=2, content="config")
    except HTTPError as e:
        no_xcon_exists_code = 404
        if e.response.status_code == no_xcon_exists_code:
            crs = []
        else:
            raise

    deleted_crs = []
    for c in crs:
        if odu_string in {c.src_tp, c.dst_tp}:
            g30.data.ne_ne.services.CRS(c.src_tp, c.dst_tp).delete()
            deleted_crs.append(c)

    if not deleted_crs:
        result["message"] = (
            f"{_node_id(optical_node_block)} {client_port_name}:"
            " There was no cross-connection associated to this client port in the configuration."
        )
        return result

    result["deleted_xcon"] = deleted_crs
    return result


def _delete_transponder_crossconnect_g42(
    optical_node_block: OpticalNodeBlock,
    client_port_name: str,
) -> dict[str, Any]:
    result = {"message": "", "deleted_xcon": []}

    g42 = get_g42_client(optical_node_block)
    client = f"/ioa-ne:ne/facilities/ethernet[name='{client_port_name}']"

    try:
        xcons = g42.data.ne.services.xcon.retrieve(depth=2, content="config")
    except HTTPError as e:
        no_xcon_exists_code = 404
        if e.response.status_code == no_xcon_exists_code:
            xcons = []
        else:
            raise

    deleted_xcons = []
    for xcon in xcons:
        if client in (xcon.source, xcon.destination):
            uri = g42.data.ne.services.xcon(xcon.name)
            uri.delete()
            deleted_xcons.append(xcon)

    if not deleted_xcons:
        result["message"] = (
            f"{_node_id(optical_node_block)} {client_port_name}:"
            " There was no cross-connection associated to this client port in the configuration."
        )
        return result

    result["deleted_xcon"] = deleted_xcons
    return result


def factory_reset_transponder_client(
    optical_node_block: OpticalNodeBlock,
    port_name: str,
) -> dict[str, Any]:
    """Factory reset the client port configuration of the given Optical Node.

    Args:
        optical_node_block: The Optical Node to reset.
        port_name: The client port name.

    Returns:
        The reset configuration.

    Raises:
        NotImplementedError: If the node vendor does not support this operation.
    """
    match vendor_of(optical_node_block):
        case Vendor.GROOVE_G30:
            return _factory_reset_transponder_client_g30(optical_node_block, port_name)
        case Vendor.GX_G42:
            return _factory_reset_transponder_client_g42(optical_node_block, port_name)
        case Vendor.FLEXILS:
            msg = "factory_reset_transponder_client is not implemented for Nokia FlexILS nodes"
            raise NotImplementedError(msg)


def _factory_reset_transponder_client_g30(
    optical_node_block: OpticalNodeBlock,
    port_name: str,
) -> dict[str, Any]:
    navigator, _, _, _, port_id, _ = g30_port_navigator_node_from_port_name(optical_node_block, port_name)
    before = navigator.retrieve(depth=3, content="config")
    navigator.update(
        port_id=port_id,
        admin_status="down",
        service_label="",
        port_mode="not-applicable",
    )
    after = navigator.retrieve(depth=3, content="config")
    return compare_pydantic_objects(before, after)


def _factory_reset_transponder_client_g42(
    optical_node_block: OpticalNodeBlock,
    port_name: str,
) -> dict[str, Any]:
    g42 = get_g42_client(optical_node_block)
    shelf_id, slot_id, port_id = port_name.split("-")  # 1-4-L1 -> 1, 4, L1

    configurations = {}

    # 1. Ethernet configuration
    navigator = g42.data.ne.facilities.ethernet(port_name)
    conf = navigator.retrieve(content="config", depth=2)
    navigator.update(name=port_name, admin_state="lock", label="")
    diff = compare_pydantic_objects(conf, navigator.retrieve(depth=2, content="config"))
    configurations["1.ethernet"] = diff

    # 2. Tributary point-to-point configuration
    navigator = g42.data.ne.facilities.trib_ptp(port_name)
    conf = navigator.retrieve(content="config", depth=2)
    navigator.update(name=port_name, label="", admin_state="lock")
    diff = compare_pydantic_objects(conf, navigator.retrieve(depth=2, content="config"))
    configurations["2.trib-ptp"] = diff

    # 3. TOM configuration
    navigator = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id).tom
    conf = navigator.retrieve(content="config", depth=2)
    updated_conf = conf.model_copy(deep=True)
    updated_conf.label = ""
    updated_conf.admin_state = AdminStateEnum.LOCK
    navigator.update(updated_conf)
    diff = compare_pydantic_objects(conf, navigator.retrieve(depth=2, content="config"))
    configurations["3.tom"] = diff

    # 4. Port configuration
    navigator = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)
    conf = navigator.retrieve(content="config", depth=2)
    updated_conf = conf.model_copy(deep=True)
    updated_conf.label = ""
    updated_conf.admin_state = AdminStateEnum.LOCK
    navigator.update(updated_conf)
    diff = compare_pydantic_objects(conf, navigator.retrieve(depth=2, content="config"))
    configurations["4.port"] = diff

    return configurations


def factory_reset_transponder_lines(
    optical_node_block: OpticalNodeBlock,
    line_port_names: list[str],
) -> dict[str, Any] | list[Any]:
    """Factory reset the transponder line configuration of the given Optical Node.

    Args:
        optical_node_block: The Optical Node to reset.
        line_port_names: The line port names.

    Returns:
        The reset configuration.

    Raises:
        NotImplementedError: If the node vendor does not support this operation.
    """
    match vendor_of(optical_node_block):
        case Vendor.GROOVE_G30:
            return _factory_reset_transponder_lines_g30(optical_node_block, line_port_names)
        case Vendor.GX_G42:
            return _factory_reset_transponder_lines_g42(optical_node_block, line_port_names)
        case Vendor.FLEXILS:
            msg = "factory_reset_transponder_lines is not implemented for Nokia FlexILS nodes"
            raise NotImplementedError(msg)


def _factory_reset_transponder_lines_g30(
    optical_node_block: OpticalNodeBlock,
    line_port_names: list[str],
) -> list[Any]:
    result = []
    for port_name in line_port_names:
        navigator, _, _, _, port_id, _ = g30_port_navigator_node_from_port_name(optical_node_block, port_name)
        before = navigator.retrieve(depth=3, content="config")
        navigator.update(
            port_id=port_id,
            admin_status="down",
            service_label="",
            port_mode="not-applicable",
        )
        after = navigator.retrieve(depth=3, content="config")
        result.append(compare_pydantic_objects(before, after))
    return result


def _factory_reset_transponder_lines_g42(
    optical_node_block: OpticalNodeBlock,
    line_port_names: list[str],
) -> dict[str, Any]:
    g42 = get_g42_client(optical_node_block)
    configurations = {}

    for port_name in line_port_names:
        # port
        shelf_id, slot_id, port_id = port_name.split("-")  # 1-4-L1 -> 1, 4, L1
        navigator = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)
        before = navigator.retrieve(content="config", depth=2)
        conf = before.model_copy(deep=True)
        conf.admin_state = AdminStateEnum.LOCK
        conf.label = ""
        conf.alarm_report_control = AlarmReportControlEnum.ALLOWED
        navigator.update(conf)
        after = navigator.retrieve(content="config", depth=2)
        diff = compare_pydantic_objects(before, after)
        configurations[f"port-{port_name}"] = diff

        # super-channel-group
        navigator = g42.data.ne.facilities.super_channel_group(port_name)
        before = navigator.retrieve(depth=2, content="config")
        navigator.update(name=port_name, admin_state="lock", label="", alarm_report_control="allowed")
        after = navigator.retrieve(depth=2, content="config")
        diff = compare_pydantic_objects(before, after)
        configurations[f"super-channel-group-{port_name}"] = diff

    # super-channel
    sup_ch_name = "_".join(line_port_names)
    navigator = g42.data.ne.facilities.super_channel(sup_ch_name)
    before = navigator.retrieve(depth=2, content="config")
    navigator.delete()
    configurations[f"super-channel-{sup_ch_name}"] = compare_pydantic_objects(before, None)

    return configurations


def validate_trx_line(
    optical_node_block: OpticalNodeBlock,
    port_names: tuple[str, ...],
    central_frequencies: tuple[Frequency, ...],
    modes: tuple[str, ...],
    descriptions: tuple[str, ...],
) -> None:
    """Validate the transceiver line configuration on the given Optical Node.

    Args:
        optical_node_block: The Optical Node to validate.
        port_names: The line port names.
        central_frequencies: The central frequencies of the transport channels.
        modes: The operating modes of the transport channels.
        descriptions: The channel descriptions.

    Raises:
        NotImplementedError: If the node vendor does not support this operation.
        ValueError: If the configuration is invalid.
    """
    match vendor_of(optical_node_block):
        case Vendor.GROOVE_G30:
            _validate_trx_line_g30(optical_node_block, port_names, central_frequencies, modes, descriptions)
        case Vendor.GX_G42:
            _validate_trx_line_g42(optical_node_block, port_names, central_frequencies, modes, descriptions)
        case Vendor.FLEXILS:
            msg = "validate_trx_line is not implemented for Nokia FlexILS nodes"
            raise NotImplementedError(msg)


def _validate_trx_line_g30(
    optical_node_block: OpticalNodeBlock,
    port_names: tuple[str, ...],
    central_frequencies: tuple[Frequency, ...],
    modes: tuple[str, ...],
    descriptions: tuple[str, ...],
) -> None:
    if not (len(port_names) == len(central_frequencies) == len(modes) == len(descriptions)):
        msg = "All channel attributes must have the same length"
        raise ValueError(msg)

    if len(set(modes)) != 1:
        msg = f"All modes must be the same but got {modes}."
        raise ValueError(msg)

    g30 = get_g30_client(optical_node_block)

    for port_name, central_frequency, mode, description in zip(
        port_names,
        central_frequencies,
        modes,
        descriptions,
        strict=False,
    ):
        shelf_id, slot_id, _, port_id, _ = g30_ids_from_port_name(port_name)
        port_uri = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card.port(port_id)
        actual_config = port_uri.retrieve(depth=3, content="config").model_dump(exclude_unset=True)

        desired_config = {
            "och-os": {
                "frequency": central_frequency,
                "rx-frequency": central_frequency,
                "service-label": description,
                "admin-status": "up",
                "laser-enable": "enabled",
                "loopback-enable": "disabled",
                "loopback-type": "none",
            },
            "port-mode": mode,
            "service-label": description,
            "admin-status": "up",
        }

        diff = compare_dicts(desired_config, actual_config)
        if diff["mismatched_value"] != {} or diff["missing_key"] != {}:
            msg = (
                f"Configuration mismatch for {_node_id(optical_node_block)} {port_name}:\n"
                f"mismatch: {diff['mismatched_value']}\n"
                f"missing: {diff['missing_key']}\n"
            )
            raise ValueError(msg)


def _validate_trx_line_g42(
    optical_node_block: OpticalNodeBlock,
    port_names: tuple[str, ...],
    central_frequencies: tuple[Frequency, ...],
    modes: tuple[str, ...],
    descriptions: tuple[str, ...],
) -> None:
    if not (len(port_names) == len(central_frequencies) == len(modes) == len(descriptions)):
        msg = "All channel attributes must have the same length"
        raise ValueError(msg)

    if len(set(modes)) != 1:
        msg = f"All modes must be the same for GX_G42 validation but got {modes}."
        raise ValueError(msg)

    g42 = get_g42_client(optical_node_block)

    actual_config: dict[str, Any] = {
        "ports": {},
        "super-channel-groups": {},
        "optical-carriers": {},
        "super-channel": {},
    }

    desired_config: dict[str, Any] = {
        "ports": {},
        "super-channel-groups": {},
        "optical-carriers": {},
        "super-channel": {},
    }

    for port_name, central_frequency, description in zip(
        port_names,
        central_frequencies,
        descriptions,
        strict=False,
    ):
        shelf_id, slot_id, port_id = port_name.split("-")  # 1-4-L1 -> 1, 4, L1
        endpoint = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)
        actual_config["ports"][port_name] = endpoint.retrieve(depth=2, content="config").model_dump(exclude_unset=True)

        endpoint = g42.data.ne.facilities.super_channel_group(port_name)
        actual_config["super-channel-groups"][port_name] = endpoint.retrieve(depth=2, content="config").model_dump(
            exclude_unset=True
        )

        endpoint = g42.data.ne.facilities.optical_carrier(f"{port_name}-1")
        actual_config["optical-carriers"][port_name] = endpoint.retrieve(depth=2, content="config").model_dump(
            exclude_unset=True
        )

        desired_config["ports"][port_name] = {
            "name": port_id,
            "label": description,
            "admin-state": "unlock",
            "alarm-report-control": "allowed",
        }
        desired_config["super-channel-groups"][port_name] = {
            "name": f"{shelf_id}-{slot_id}-{port_id}",
            "label": description,
            "admin-state": "unlock",
            "line-system-mode": "openwave",
            "alarm-report-control": "allowed",
        }
        desired_config["optical-carriers"][port_name] = {
            "name": f"{shelf_id}-{slot_id}-{port_id}-1",
            "label": description,
            "tx-cd": "0.00",
            "frequency": str(central_frequency),
            "admin-state": "unlock",
            "frequency-offset": 0,
            "alarm-report-control": "allowed",
        }

    super_channel_name = "_".join(port_names)
    endpoint = g42.data.ne.facilities.super_channel(super_channel_name)
    actual_config["super-channel"] = endpoint.retrieve(depth=2, content="config").model_dump(exclude_unset=True)

    carriers = [f"{port_name}-1" for port_name in port_names]
    desired_config["super-channel"] = {
        "name": super_channel_name,
        "label": "+".join(descriptions),
        "carriers": carriers,
        "admin-state": "unlock",
        "carrier-mode": modes[0],
        "alarm-report-control": "allowed",
    }

    diff = compare_dicts(desired_config, actual_config)
    if diff["mismatched_value"] != {} or diff["missing_key"] != {}:
        msg = (
            f"Configuration mismatch for {_node_id(optical_node_block)} {port_names}:\n"
            f"mismatch: {diff['mismatched_value']}\n"
            f"missing: {diff['missing_key']}\n"
        )
        raise ValueError(msg)


def validate_trx_client(
    optical_node_block: OpticalNodeBlock,
    port_name: str,
    description: str,
    speed: OpticalDigitalServiceSpeed,
) -> None:
    """Validate the transceiver client configuration on the given Optical Node.

    Args:
        optical_node_block: The Optical Node to validate.
        port_name: The client port name.
        description: The description of the client service.
        speed: The speed of the client service in Gbit/s.

    Raises:
        NotImplementedError: If the node vendor or the requested speed is not supported.
        ValueError: If the configuration is invalid.
    """
    match vendor_of(optical_node_block):
        case Vendor.GROOVE_G30:
            _validate_trx_client_g30(optical_node_block, port_name, description, speed)
        case Vendor.GX_G42:
            _validate_trx_client_g42(optical_node_block, port_name, description, speed)
        case Vendor.FLEXILS:
            msg = "validate_trx_client is not implemented for Nokia FlexILS nodes"
            raise NotImplementedError(msg)


def _validate_trx_client_g30(
    optical_node_block: OpticalNodeBlock,
    port_name: str,
    description: str,
    speed: OpticalDigitalServiceSpeed,
) -> None:
    g30 = get_g30_client(optical_node_block)

    shelf_id, slot_id, _, port_id, _ = g30_ids_from_port_name(port_name)

    port_uri = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card.port(port_id)

    port_mode, eth_name, fec_type = _g30_client_speed_config(speed)

    actual_config = port_uri.retrieve(depth=3, content="config").model_dump(exclude_unset=True)

    desired_config = {
        eth_name: {
            "admin-status": "up",
            "service-label": description,
            "loopback-enable": "disabled",
            "test-signal-enable": "NONE",
            "client-shutdown": "no",
            "eth-fec-type": fec_type,
            "mapping-mode": "GMP",
        },
        "pluggable": {
            "admin-status": "up",
        },
        "port-mode": port_mode,
        "admin-status": "up",
        "service-label": description,
    }

    diff = compare_dicts(desired_config, actual_config)
    if diff["mismatched_value"] != {} or diff["missing_key"] != {}:
        msg = (
            f"Configuration mismatch for {_node_id(optical_node_block)} {port_name}:\n"
            f"mismatch: {diff['mismatched_value']}\n"
            f"missing: {diff['missing_key']}\n"
        )
        raise ValueError(msg)


def _validate_trx_client_g42(
    optical_node_block: OpticalNodeBlock,
    port_name: str,
    description: str,
    speed: OpticalDigitalServiceSpeed,
) -> None:
    g42 = get_g42_client(optical_node_block)
    shelf_id, slot_id, port_id = port_name.split("-")  # 1-4-L1 -> 1, 4, L1

    required_type, required_subtype, phy_mode, service_type = _g42_client_speed_config(speed)

    actual_config = {}
    # port
    endpoint = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id)
    actual_config["port"] = endpoint.retrieve(depth=2, content="config").model_dump(exclude_unset=True)
    # TOM
    endpoint = g42.data.ne.equipment.card(f"{shelf_id}-{slot_id}").port(port_id).tom
    actual_config["tom"] = endpoint.retrieve(depth=2, content="config").model_dump(exclude_unset=True)
    # trib-ptp
    endpoint = g42.data.ne.facilities.trib_ptp(port_name)
    actual_config["trib-ptp"] = endpoint.retrieve(depth=2, content="config").model_dump(exclude_unset=True)
    # ethernet
    endpoint = g42.data.ne.facilities.ethernet(port_name)
    actual_config["ethernet"] = endpoint.retrieve(depth=2, content="config").model_dump(exclude_unset=True)

    desired_config = {
        "tom": {
            "label": description,
            "phy-mode": phy_mode,
            "admin-state": "unlock",
            "required-type": required_type,
            "required-subtype": required_subtype,
            "alarm-report-control": "allowed",
        },
        "port": {
            "label": description,
            "admin-state": "unlock",
            "alarm-report-control": "allowed",
        },
        "trib-ptp": {
            "label": description,
            "admin-state": "unlock",
            "service-type": service_type,
            "alarm-report-control": "allowed",
        },
        "ethernet": {
            "label": description,
            "fec-mode": "enabled",
            "loopback": "none",
            "admin-state": "unlock",
            "lldp-egress-mode": "snoop",
            "test-signal-type": "none",
            "lldp-admin-status": "rx-only",
            "lldp-ingress-mode": "snoop",
            "alarm-report-control": "allowed",
            "test-signal-direction": "egress",
            "test-signal-monitoring": False,
        },
    }

    diff = compare_dicts(desired_config, actual_config)
    if diff["mismatched_value"] != {} or diff["missing_key"] != {}:
        msg = (
            f"Configuration mismatch for {_node_id(optical_node_block)} {port_name}:\n"
            f"mismatch: {diff['mismatched_value']}\n"
            f"missing: {diff['missing_key']}\n"
        )
        raise ValueError(msg)


def validate_trx_crossconnect(
    optical_node_block: OpticalNodeBlock,
    client_port_name: str,
    line_port_names: list[str],
    xconn_description: str = "",
) -> None:
    """Validate the transponder cross-connect configuration on the given Optical Node.

    Args:
        optical_node_block: The Optical Node to validate.
        client_port_name: The client port name.
        line_port_names: The line port names.
        xconn_description: The description of the cross-connect.

    Raises:
        NotImplementedError: If the node vendor does not support this operation.
        ValueError: If the configuration is invalid.
    """
    match vendor_of(optical_node_block):
        case Vendor.GROOVE_G30:
            _validate_trx_crossconnect_g30(optical_node_block, client_port_name, line_port_names, xconn_description)
        case Vendor.GX_G42:
            _validate_trx_crossconnect_g42(optical_node_block, client_port_name, line_port_names, xconn_description)
        case Vendor.FLEXILS:
            msg = "validate_trx_crossconnect is not implemented for Nokia FlexILS nodes"
            raise NotImplementedError(msg)


def _validate_trx_crossconnect_g30(
    optical_node_block: OpticalNodeBlock,
    client_port_name: str,
    line_port_names: list[str],
    xconn_description: str = "",
) -> None:
    g30 = get_g30_client(optical_node_block)
    crs_list = g30.data.ne_ne.services.CRS.retrieve(depth=2, content="config")
    for c in crs_list:
        src_shelf_id, src_slot_id, src_port_id = _extract_shelf_slot_port_ids_from_odu_string(c.src_tp)
        dst_shelf_id, dst_slot_id, dst_port_id = _extract_shelf_slot_port_ids_from_odu_string(c.dst_tp)
        src_port_string = f"port-{src_shelf_id}/{src_slot_id}/{src_port_id}"
        dst_port_string = f"port-{dst_shelf_id}/{dst_slot_id}/{dst_port_id}"
        if (src_port_string == client_port_name and dst_port_string in line_port_names) or (
            dst_port_string == client_port_name and src_port_string in line_port_names
        ):
            if c.service_label != xconn_description:
                msg = (
                    f"Cross-connect description mismatch for {_node_id(optical_node_block)} "
                    f"{client_port_name} to {dst_port_string}: "
                    f"Expected: {xconn_description}, Actual: {c.service_label}"
                )
                raise ValueError(msg)
            return

    msg = (
        f"Cross-connect not found for {_node_id(optical_node_block)} {client_port_name} to {line_port_names}. "
        "Please ensure the cross-connect exists and is correctly configured then retry."
    )
    raise ValueError(msg)


def _validate_trx_crossconnect_g42(
    optical_node_block: OpticalNodeBlock,
    client_port_name: str,
    line_port_names: list[str],
    xconn_description: str = "",
) -> None:
    g42 = get_g42_client(optical_node_block)

    client = f"/ioa-ne:ne/facilities/ethernet[name='{client_port_name}']"
    och_key = _derive_optical_channel_key(line_port_names)
    direction = "two-way"
    label = xconn_description
    payload_type = _retrieve_payload_type(g42, client_port_name)

    xcons = g42.data.ne.services.xcon.retrieve(depth=2, content="config")

    actual_config = None
    for xcon in xcons:
        if (xcon.source == client and och_key in xcon.destination) or (
            xcon.destination == client and och_key in xcon.source
        ):
            actual_config = xcon.model_dump(exclude_unset=True)
            break

    if actual_config is None:
        msg = (
            f"Cross-connect not found for {_node_id(optical_node_block)} {client_port_name} to {line_port_names}. "
            "Please ensure the cross-connect exists and is correctly configured then retry."
        )
        raise ValueError(msg)

    desired_config = {
        "label": label,
        "direction": direction,
        "payload-type": payload_type,
        "circuit-id-suffix": label,
    }

    diff = compare_dicts(desired_config, actual_config)
    if diff["mismatched_value"] != {} or diff["missing_key"] != {}:
        msg = (
            f"Configuration mismatch for {_node_id(optical_node_block)} {client_port_name} to {line_port_names}:\n"
            f"mismatch: {diff['mismatched_value']}\n"
            f"missing: {diff['missing_key']}\n"
        )
        raise ValueError(msg)


def diff_btw_current_rx_power_and_target(
    optical_node_block: OpticalNodeBlock,
    optical_spectrum_name: str,
    circuit_identifier: str = "",
) -> float:
    r"""Return the difference :math:`P_{current\_rx} - P_{target\_rx}` in dB for the given optical channel.

    Args:
        optical_node_block: The Optical Node to compute for.
        optical_spectrum_name: The optical spectrum name; used as the CKTIDSUFFIX fallback.
        circuit_identifier: The subscription instance id of the circuit; used as the CKTIDSUFFIX.

    Returns:
        The delta target received power in dB.

    Raises:
        NotImplementedError: If the node vendor does not support this operation.
        ValueError: If the optical channel cannot be found on the device.
    """
    match vendor_of(optical_node_block):
        case Vendor.FLEXILS:
            flex = _get_flex_client(optical_node_block)
            # procedure:
            # >> RTRV-OCRS SIGTYPE=SIGNALED
            # >> find by CKTIDSUFFIX
            # >> save INTERMEDIATESCHCTP if card is not FSM else source AID
            # >> RTRV-SCH AID=INTERMEDIATESCHCTP
            # >> save TARGETOPR
            # >> RTRV-PM-SCH AID=INTERMEDIATESCHCTP
            cktidsuffix = circuit_identifier or optical_spectrum_name.replace(" ", "_")

            ocrs = flex.rtrv_ocrs(sigtype="SIGNALED").parsed_data
            ocr = next(
                (o for o in ocrs if cktidsuffix in o.get("CKTIDSUFFIX", "")),
                None,
            )

            if ocr is None:
                msg = (
                    f"Optical channel with CKTIDSUFFIX={cktidsuffix} not found on {_node_id(optical_node_block)}. "
                    "Please ensure the optical channel exists and is correctly configured then retry."
                )
                raise ValueError(msg)

            tributary_port = ocr.get("FROMAID") if "-T" in ocr.get("FROMAID", "") else ocr.get("TOAID")
            if tributary_port is None:
                msg = f"Optical channel with CKTIDSUFFIX={cktidsuffix} has no tributary endpoint"
                raise ValueError(msg)
            tributary_port = str(tributary_port)
            card_aid = "-".join(tributary_port.split("-")[:-2])
            card = flex.rtrv_eqpt(aid=card_aid).parsed_data[0]
            sch_aid = tributary_port if card["TYPE"] == "FSM" else ocr.get("INTERMEDIATESCHCTP")
            if sch_aid is None:
                msg = f"Optical channel with CKTIDSUFFIX={cktidsuffix} has no superchannel endpoint"
                raise ValueError(msg)
            sch_aid = str(sch_aid)

            sch = flex.rtrv_sch(aid=sch_aid).parsed_data[0]
            target_opr = float(sch["TARGETOPR"])

            pm_sch = flex.rtrv_pm_sch(aid=sch_aid, montype="OPR").parsed_data[0]
            current_rx_power = float(pm_sch["positional_param_1_1"])

            return round(current_rx_power - target_opr, 1)

        case Vendor.GROOVE_G30 | Vendor.GX_G42:
            msg = "diff_btw_current_rx_power_and_target is not implemented for Groove G30 and GX G42 nodes"
            raise NotImplementedError(msg)


def allign_tx_power_to_target(
    optical_node_block: OpticalNodeBlock,
    line_port_name: str,
    db_from_target: Decimal | float | str,
) -> dict[str, Any]:
    r"""Subtract db_from_target decibels (dB) to the transmitted optical power.

    I.e. :math:`P^{new}_{tx} = P^{old}_{tx} - \Delta P`, where :math:`P^{old}_{tx}`
    is the currently configured required transmit power (``required-tx-optical-power``
    on G30, ``tx-power`` on G42), used as the baseline for the adjustment.

    Args:
        optical_node_block: The Optical Node to configure.
        line_port_name: The line port name.
        db_from_target: The difference between current and target transmit power in dB.

    Returns:
        A dictionary indicating the old and new required transmit power.

    Raises:
        NotImplementedError: If the node vendor does not support this operation.
    """
    match vendor_of(optical_node_block):
        case Vendor.GROOVE_G30:
            return _allign_tx_power_to_target_g30(optical_node_block, line_port_name, db_from_target)
        case Vendor.GX_G42:
            return _allign_tx_power_to_target_g42(optical_node_block, line_port_name, db_from_target)
        case Vendor.FLEXILS:
            msg = "allign_tx_power_to_target is not implemented for Nokia FlexILS nodes"
            raise NotImplementedError(msg)


def _as_decimal(db_from_target: Decimal | float | str) -> Decimal:
    """Normalize the power difference to a Decimal."""
    if isinstance(db_from_target, float):
        db_from_target = str(db_from_target)
    if isinstance(db_from_target, str):
        db_from_target = Decimal(db_from_target)
    if not isinstance(db_from_target, Decimal):
        msg = "db_from_target must be of type Decimal at this point."
        raise TypeError(msg)
    return db_from_target


def _allign_tx_power_to_target_g30(
    optical_node_block: OpticalNodeBlock,
    line_port_name: str,
    db_from_target: Decimal | float | str,
) -> dict[str, Any]:
    db_from_target = _as_decimal(db_from_target)

    min_tx_power = Decimal("-10.00")
    max_tx_power = Decimal("6.00")

    g30 = get_g30_client(optical_node_block)
    shelf_id, slot_id, _, port_id, _ = g30_ids_from_port_name(line_port_name)
    och_uri = g30.data.ne_ne.shelf(shelf_id).slot(slot_id).card.port(port_id).och_os
    och_os = och_uri.retrieve(content="config", depth=2)
    current_tx_power = och_os.required_tx_optical_power
    if current_tx_power is None:
        msg = f"No required transmit power configured on {_node_id(optical_node_block)} {line_port_name}"
        raise ValueError(msg)
    new_tx_power = current_tx_power - db_from_target
    new_tx_power = min(max_tx_power, new_tx_power)
    new_tx_power = max(min_tx_power, new_tx_power)
    new_och_os = och_os.model_copy(deep=True)
    new_och_os.required_tx_optical_power = new_tx_power
    och_uri.update(new_och_os)

    return compare_pydantic_objects(och_os, new_och_os)


def _allign_tx_power_to_target_g42(
    optical_node_block: OpticalNodeBlock,
    line_port_name: str,
    db_from_target: Decimal | float | str,
) -> dict[str, Any]:
    db_from_target = _as_decimal(db_from_target)

    min_tx_power = Decimal("-6.00")
    max_tx_power = Decimal("9.00")

    g42 = get_g42_client(optical_node_block)
    uri = g42.data.ne.facilities.optical_carrier(f"{line_port_name}-1")
    conf = uri.retrieve(depth=2, content="config")
    current_tx_power = conf.tx_power
    if current_tx_power is None:
        msg = f"No transmit power configured on {_node_id(optical_node_block)} {line_port_name}"
        raise ValueError(msg)
    new_tx_power = round(current_tx_power - db_from_target, 2)
    new_tx_power = min(max_tx_power, new_tx_power)
    new_tx_power = max(min_tx_power, new_tx_power)
    new_conf = conf.model_copy(deep=True)
    new_conf.tx_power = new_tx_power
    uri.update(new_conf)
    return compare_pydantic_objects(conf, new_conf)


def _extract_shelf_slot_port_ids_from_odu_string(
    odu_string: str,
) -> tuple[int, int, int]:
    """Extract the shelf, slot and port ids from a G30 ODU string."""
    shelf_match = search(r"shelf\[shelf-id='(\d+)'\]", odu_string)
    slot_match = search(r"slot\[slot-id='(\d+)'\]", odu_string)
    port_match = search(r"port\[port-id='(\d+)'\]", odu_string)

    if shelf_match is None or slot_match is None or port_match is None:
        msg = f"Could not extract the shelf, slot and port ids from ODU string: {odu_string}"
        raise ValueError(msg)

    return int(shelf_match.group(1)), int(slot_match.group(1)), int(port_match.group(1))
