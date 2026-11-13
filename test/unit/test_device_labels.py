"""Naming rules of the device labels and of the subscription descriptions."""

from types import SimpleNamespace
from typing import Any, cast

from orchestrator.optical.utils.labels import (
    conduits_label,
    device_label,
    endpoint,
    label_name,
    node_name,
    via_label,
)
from orchestrator.optical.workflows.optical_digital_service import shared as digital_shared
from orchestrator.optical.workflows.optical_spectrum_service import shared as spectrum_shared


def _node(fqdn: str, target_id: str | None = None) -> SimpleNamespace:
    node = SimpleNamespace(management=SimpleNamespace(optical_module_node_name=fqdn), subscription_instance_id=fqdn)
    if target_id:
        node.optical_flexils_target_id = target_id
    return node


def _port(node: SimpleNamespace, name: str) -> SimpleNamespace:
    return SimpleNamespace(optical_port_host_node=node, optical_port_name=name)


def test_node_name_is_the_flexils_tid_else_the_fqdn() -> None:
    assert node_name(_node("flex.mil01.example.net", "flex.mil01")) == "flex.mil01"
    assert node_name(_node("g30.mil01.example.net")) == "g30.mil01.example.net"
    assert endpoint(_node("g30.a"), "1/1/L1") == "g30.a 1/1/L1"


def test_device_label_puts_the_name_first_and_drops_the_far_end_when_too_long() -> None:
    assert device_label("MIL-BOL-OCH-01", "g42.bol01 1/3/L1") == "MIL-BOL-OCH-01 > g42.bol01 1/3/L1"
    assert device_label("", "flex.bol01 1-4-L1") == "> flex.bol01 1-4-L1"
    assert device_label("ch", None) == "ch"
    assert device_label("ch", "x" * 80) == "ch"
    assert device_label("n" * 80, None) == "n" * 64
    assert label_name("MIL-BOL-OCH-01 > g42.bol01 1/3/L1") == "MIL-BOL-OCH-01"


def test_bundle_and_crossconnect_labels() -> None:
    assert conduits_label(["ch-01", "ch-02", "ch-01"]) == "ch-01 + ch-02"
    assert via_label("svc", ["ch-01", "ch-02"]) == "svc via ch-01 + ch-02"
    assert via_label("svc", []) == "svc"
    assert via_label("svc", ["c" * 70]) == "svc"


def _digital_block() -> Any:
    mil, bol = _node("g30.mil01"), _node("g42.bol01")
    channels = [
        SimpleNamespace(
            optical_transport_channel_name=f"OCH-0{index}",
            optical_transport_central_frequency=193_100_000 + index,
            optical_transport_mode="mode",
            optical_transport_line_ports=[_port(mil, f"1/1/L{index}"), _port(bol, f"1/3/L{index}")],
            optical_transport_spectrum=SimpleNamespace(optical_spectrum_name=f"OCH-0{index}"),
        )
        for index in (1, 2)
    ]
    return SimpleNamespace(
        subscription_instance_id="svc-id",
        optical_digital_service_name="MIL-BOL-100GE-01",
        optical_digital_service_speed=100,
        optical_digital_service_client_ports=[_port(mil, "1/1/C3"), _port(bol, "1/2/C1")],
        optical_digital_service_transport_channels=channels,
    )


def test_digital_service_labels(monkeypatch: Any) -> None:
    """Line labels name the channel and the far line port; clients the service; cross-connects both."""
    monkeypatch.setattr(digital_shared, "is_new_channel", lambda _channel, _block: True)
    line_sides, clients, xconns = digital_shared._channel_endpoints(_digital_block())  # noqa: SLF001

    assert line_sides[0][4] == ("OCH-01 > g42.bol01 1/3/L1", "OCH-02 > g42.bol01 1/3/L2")
    assert line_sides[1][4] == ("OCH-01 > g30.mil01 1/1/L1", "OCH-02 > g30.mil01 1/1/L2")
    assert [client[2] for client in clients] == [
        "MIL-BOL-100GE-01 > g42.bol01 1/2/C1",
        "MIL-BOL-100GE-01 > g30.mil01 1/1/C3",
    ]
    assert {xconn[3] for xconn in xconns} == {"MIL-BOL-100GE-01 via OCH-01 + OCH-02"}


def test_digital_service_subscription_description() -> None:
    subscription = cast(Any, SimpleNamespace(product=SimpleNamespace(name="Optical Digital Service")))
    description = digital_shared.optical_digital_service_subscription_description(subscription, _digital_block())
    assert description == "MIL-BOL-100GE-01 100G g30.mil01 1/1/C3 <-> g42.bol01 1/2/C1 via OCH-01 + OCH-02"


def test_spectrum_subscription_description() -> None:
    src, dst = _port(_node("x", "flex.mil01"), "1-5-3"), _port(_node("y", "flex.rom01"), "1-7-2")
    block = SimpleNamespace(
        optical_spectrum_name="MIL-ROM-SPEC-01",
        optical_spectrum_sections=[SimpleNamespace(optical_spectrum_section_add_drop_ports=[src, dst])],
        optical_spectrum_passband=(193_100_000, 193_175_000),
    )
    subscription = cast(Any, SimpleNamespace(product=SimpleNamespace(name="Optical Spectrum")))

    assert spectrum_shared.optical_spectrum_subscription_description(subscription, cast(Any, block)) == (
        "MIL-ROM-SPEC-01 flex.mil01 1-5-3 <-> flex.rom01 1-7-2 193.1000-193.1750 THz (75 GHz)"
    )
