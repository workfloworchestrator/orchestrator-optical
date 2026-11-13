"""Create form page sequences of the Optical Nodes: the node is read from the device while the form is filled in.

The page sequences are driven page by page with the device discovery and the database
lookups replaced, so no device and no database are needed.
"""

from types import SimpleNamespace
from typing import Any

import pytest
from pydantic import ValidationError

from orchestrator.core.forms import FormPage
from orchestrator.optical.hal.node import OpticalNodeDiscovery
from orchestrator.optical.products.product_blocks.optical_node.abstracts import OpticalNodeRole
from orchestrator.optical.products.product_blocks.optical_node_management import Platform, Vendor
from orchestrator.optical.workflows.optical_node.nokia_flexils import create_nokia_flexils
from orchestrator.optical.workflows.optical_node.nokia_groove_g30 import create_nokia_groove_g30
from orchestrator.optical.workflows.optical_node.nokia_gx_g42 import create_nokia_gx_g42
from orchestrator.optical.workflows.optical_node.shared import forms
from test.support.forms import finish_form

LOCATION_INSTANCE_ID = "0a9f2f5e-6f0f-4d0f-9d6b-0f6a3f1d2c11"


class _LocationPage(FormPage):
    location_instance_id: str


@pytest.fixture
def discoveries(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    """Replace the database lookups of the pages; return the list the test fills with discovery calls."""
    for module in (create_nokia_flexils, create_nokia_groove_g30, create_nokia_gx_g42):
        monkeypatch.setattr(module, "create_optical_node_location_form", lambda _product_name: _LocationPage)
    monkeypatch.setattr(forms, "validate_management_ips_uniqueness", lambda *_, **__: None)
    monkeypatch.setattr(forms, "validate_optical_node_name_uniqueness", lambda *_, **__: None)
    monkeypatch.setattr(forms, "location_block_from_instance", lambda instance_id: f"location {instance_id}")
    monkeypatch.setattr(create_nokia_flexils, "validate_optical_flexils_target_id_uniqueness", lambda *_, **__: None)
    monkeypatch.setattr(create_nokia_flexils, "validate_gmpls_id_uniqueness", lambda *_, **__: None)
    return []


def _discover_as(monkeypatch: pytest.MonkeyPatch, calls: list[dict[str, Any]], discovery: OpticalNodeDiscovery) -> None:
    def _discover(vendor: Vendor, platform: Platform, **kwargs: Any) -> OpticalNodeDiscovery:
        calls.append({"vendor": vendor, "platform": platform, **kwargs})
        return discovery

    monkeypatch.setattr(forms, "discover_optical_node", _discover)


@pytest.mark.parametrize(
    ("module", "pages", "platform"),
    [
        (create_nokia_groove_g30, "create_optical_node_nokia_groove_g30_form_pages", Platform.GROOVE_G30),
        (create_nokia_gx_g42, "create_optical_node_nokia_gx_g42_form_pages", Platform.GX_G42),
    ],
    ids=["g30", "g42"],
)
def test_netconf_node_form_asks_an_ip_and_prefills_the_name_read_from_the_device(
    module: Any, pages: str, platform: Platform, discoveries: list[dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    _discover_as(
        monkeypatch,
        discoveries,
        OpticalNodeDiscovery(name="lab-node-01", role=OpticalNodeRole.TRANSPONDER, software_version="22.1"),
    )
    generator = getattr(module, pages)("Product")

    location_page = next(generator)
    management_page = generator.send(location_page(location_instance_id=LOCATION_INSTANCE_ID))
    assert set(management_page.model_fields) == {
        "optical_module_node_management_loopback_ip",
        "optical_module_node_management_ip",
    }
    identity_page = generator.send(management_page(optical_module_node_management_ip="192.0.2.2"))

    assert discoveries == [
        {
            "vendor": Vendor.NOKIA,
            "platform": platform,
            "dcn_loopback_ip": None,
            "dcn_interface_ip": "192.0.2.2",
            "flexils_target_id": None,
            "location": None,
        }
    ]
    assert "role Transponder, software version 22.1" in identity_page.model_fields["discovered"].default
    # Submitted untouched, the page keeps the name read from the device.
    assert finish_form(generator, identity_page()) == {
        "location_instance_id": LOCATION_INSTANCE_ID,
        "optical_module_node_management_loopback_ip": None,
        "optical_module_node_management_ip": "192.0.2.2",
        "optical_module_node_name": "lab-node-01",
    }


def test_the_name_read_from_the_device_can_be_changed(
    discoveries: list[dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    _discover_as(
        monkeypatch,
        discoveries,
        OpticalNodeDiscovery(name="lab-node-01", role=OpticalNodeRole.TRANSPONDER, software_version="22.1"),
    )
    generator = create_nokia_groove_g30.create_optical_node_nokia_groove_g30_form_pages("Product")
    management_page = generator.send(next(generator)(location_instance_id=LOCATION_INSTANCE_ID))
    identity_page = generator.send(management_page(optical_module_node_management_loopback_ip="192.0.2.1"))

    user_input = finish_form(generator, identity_page(optical_module_node_name=" Lab Node 01.example.net "))

    # Free-form and case-preserving: only the surrounding whitespace is dropped.
    assert user_input["optical_module_node_name"] == "Lab Node 01.example.net"


def test_a_device_without_a_name_requires_one_from_the_user() -> None:
    page = forms.create_optical_node_identity_form(
        "Product", OpticalNodeDiscovery(name=None, role=OpticalNodeRole.ROADM, software_version="22.1")
    )

    assert "It has no name configured" in page.model_fields["discovered"].default
    with pytest.raises(ValidationError, match="optical_module_node_name"):
        page()


def test_netconf_node_form_requires_a_management_ip(discoveries: list[dict[str, Any]]) -> None:
    generator = create_nokia_groove_g30.create_optical_node_nokia_groove_g30_form_pages("Product")
    management_page = generator.send(next(generator)(location_instance_id=LOCATION_INSTANCE_ID))

    with pytest.raises(ValidationError, match="At least one of the management loopback IP or the management IP"):
        management_page()
    assert discoveries == []


def test_flexils_form_asks_the_target_id_and_reads_the_gmpls_id_from_the_device(
    discoveries: list[dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    _discover_as(
        monkeypatch,
        discoveries,
        OpticalNodeDiscovery(
            name="flex.ba01", role=OpticalNodeRole.ROADM, software_version="R21.0", flexils_gmpls_id="10.0.0.3"
        ),
    )
    generator = create_nokia_flexils.create_optical_node_nokia_flexils_form_pages("Product")

    vendor_page = generator.send(next(generator)(location_instance_id=LOCATION_INSTANCE_ID))
    assert set(vendor_page.model_fields) == {"optical_flexils_target_id"}
    management_page = generator.send(vendor_page(optical_flexils_target_id="flex.ba01"))
    # A subtended node has no DCN IP: it is reached through the GNE closest to its location.
    identity_page = generator.send(management_page())

    assert discoveries == [
        {
            "vendor": Vendor.NOKIA,
            "platform": Platform.FLEXILS,
            "dcn_loopback_ip": None,
            "dcn_interface_ip": None,
            "flexils_target_id": "flex.ba01",
            "location": f"location {LOCATION_INSTANCE_ID}",
        }
    ]
    assert "GMPLS ID 10.0.0.3" in identity_page.model_fields["discovered"].default
    assert finish_form(generator, identity_page()) == {
        "location_instance_id": LOCATION_INSTANCE_ID,
        "optical_flexils_target_id": "flex.ba01",
        "optical_module_node_management_loopback_ip": None,
        "optical_module_node_management_ip": None,
        "optical_flexils_gmpls_id": "10.0.0.3",
        "optical_module_node_name": "flex.ba01",
    }


def test_flexils_form_rejects_a_gmpls_id_already_in_use(
    discoveries: list[dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    _discover_as(
        monkeypatch,
        discoveries,
        OpticalNodeDiscovery(
            name="flex.ba01", role=OpticalNodeRole.ROADM, software_version="R21.0", flexils_gmpls_id="10.0.0.3"
        ),
    )

    def _in_use(gmpls_id: str, **_: Any) -> None:
        msg = f"GMPLS ID '{gmpls_id}' is already in use"
        raise ValueError(msg)

    monkeypatch.setattr(create_nokia_flexils, "validate_gmpls_id_uniqueness", _in_use)
    generator = create_nokia_flexils.create_optical_node_nokia_flexils_form_pages("Product")
    vendor_page = generator.send(next(generator)(location_instance_id=LOCATION_INSTANCE_ID))
    management_page = generator.send(vendor_page(optical_flexils_target_id="flex.ba01"))

    with pytest.raises(ValueError, match="GMPLS ID '10.0.0.3' is already in use"):
        generator.send(management_page())


def test_flexils_form_fails_when_the_node_reports_no_gmpls_id(
    discoveries: list[dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    _discover_as(
        monkeypatch,
        discoveries,
        OpticalNodeDiscovery(name="flex.ba01", role=OpticalNodeRole.ROADM, software_version="R21.0"),
    )
    generator = create_nokia_flexils.create_optical_node_nokia_flexils_form_pages("Product")
    vendor_page = generator.send(next(generator)(location_instance_id=LOCATION_INSTANCE_ID))
    management_page = generator.send(vendor_page(optical_flexils_target_id="flex.ba01"))

    with pytest.raises(ValueError, match="reports no GMPLS ID"):
        generator.send(management_page())


def _stored_node(name: str = "old-name.example.net") -> Any:
    """Return a stand-in for the node block being modified."""
    return SimpleNamespace(
        owner_subscription_id="5d1c2a50-3f55-4d6c-8a43-1b2c3d4e5f60",
        management=SimpleNamespace(
            optical_module_node_name=name,
            optical_module_node_management_loopback_ip="192.0.2.1",
            optical_module_node_management_ip=None,
        ),
    )


def test_modify_form_reads_the_node_again_and_prefills_the_device_name(
    discoveries: list[dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    from orchestrator.optical.workflows.optical_node.nokia_groove_g30 import modify_nokia_groove_g30

    _discover_as(
        monkeypatch,
        discoveries,
        OpticalNodeDiscovery(name="lab-node-01", role=OpticalNodeRole.TRANSPONDER, software_version="22.1"),
    )
    generator = modify_nokia_groove_g30.modify_optical_node_nokia_groove_g30_form_pages(_stored_node())

    management_page = next(generator)
    assert "optical_module_node_name" not in management_page.model_fields
    identity_page = generator.send(management_page())

    assert discoveries[0]["platform"] is Platform.GROOVE_G30
    assert "The current name is old-name.example.net." in identity_page.model_fields["discovered"].default
    assert finish_form(generator, identity_page())["optical_module_node_name"] == "lab-node-01"


def test_modify_identity_page_keeps_the_stored_name_when_the_device_has_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(forms, "validate_optical_node_name_uniqueness", lambda *_, **__: None)
    page = forms.modify_optical_node_identity_form(
        _stored_node(), OpticalNodeDiscovery(name=None, role=OpticalNodeRole.ROADM, software_version="22.1")
    )

    assert page().optical_module_node_name == "old-name.example.net"
