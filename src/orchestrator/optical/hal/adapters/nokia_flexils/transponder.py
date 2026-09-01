"""Nokia FlexILS transponder operations (received optical power)."""

from orchestrator.optical.hal._common import _node_id
from orchestrator.optical.hal.adapters.nokia_flexils._shared import _get_flex_client
from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import NokiaFlexIlsBlockProvisioning


def delta_rx_power_vs_target(
    optical_node_block: NokiaFlexIlsBlockProvisioning,
    optical_spectrum_name: str,
    circuit_identifier: str = "",
) -> float:
    r"""Return the difference :math:`P_{current\_rx} - P_{target\_rx}` in dB for the given optical channel.

    Args:
        optical_node_block: The FlexILS Optical Node to compute for.
        optical_spectrum_name: The optical spectrum name; used as the CKTIDSUFFIX fallback.
        circuit_identifier: The subscription instance id of the circuit; used as the CKTIDSUFFIX.

    Returns:
        The delta target received power in dB.

    Raises:
        ValueError: If the optical channel cannot be found on the device.
    """
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
