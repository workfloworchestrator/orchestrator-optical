# Copyright 2025 GARR.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Pydantic models for leafs of the G30 YANG data model.
These models are used when creating or modifying resources
via RESTCONF to validate and serialize the data to JSON.
"""

from typing import Literal

from pydantic import BaseModel, Field, validator

_model_registry = {}


def register_model(cls):
    """Decorator to register model classes"""
    _model_registry[cls.__name__.lower()] = cls
    return cls


class NeItem(BaseModel):
    ne_id: str | None = Field(None, alias="ne-id")
    ne_name: str | None = Field(None, alias="ne-name")
    ne_location: str | None = Field(None, alias="ne-location")
    ne_site: str | None = Field(None, alias="ne-site")
    ne_altitude: int | None = Field(None, alias="ne-altitude")


@register_model
class Ne(BaseModel):
    ne: NeItem


class ShelfItem(BaseModel):
    shelf_id: int | None = Field(None, alias="shelf-id")
    admin_status: Literal["up", "down", "up-no-alm"] | None = Field(None, alias="admin-status")
    shelf_location: str | None = Field(None, alias="shelf-location")


@register_model
class Shelf(BaseModel):
    shelf: list[ShelfItem]


class SlotItem(BaseModel):
    slot_id: str | None = Field(None, alias="slot-id")
    admin_status: Literal["up", "down", "up-no-alm"] | None = Field(None, alias="admin-status")


@register_model
class Slot(BaseModel):
    slot: list[SlotItem]


class CardItem(BaseModel):
    admin_status: Literal["up", "down", "up-no-alm"] | None = Field(None, alias="admin-status")
    card_mode: Literal["not-applicable", "normal", "regen", "mix-function", "grey-muxponder"] | None = Field(
        None, alias="card-mode"
    )


@register_model
class Card(BaseModel):
    card: CardItem


class PortItem(BaseModel):
    port_id: str | None = Field(None, alias="port-id")
    port_mode: (
        Literal[
            "100GBE",
            "400GBE",
            "not-applicable",
            "QPSK_100G",
            "16QAM_200G",
            "8QAM_300G",
            "16QAM_300G",
            "16QAM_32QAM_400G",
            "16QAM_32QAM_500G",
            "16QAM_32QAM_500G_C",
            "16QAM_32QAM_900G_C",
            "16QAM_400G",
            "16QAM_500G_C",
            "16QAM_700G_C",
            "32QAM_200G",
            "32QAM_300G",
            "32QAM_400G",
            "32QAM_500G",
            "32QAM_64QAM_1100G_C",
            "32QAM_64QAM_500G",
            "32QAM_64QAM_600G",
            "32QAM_64QAM_700G_C",
            "32QAM_900G_C",
            "64QAM_300G",
            "64QAM_400G",
            "64QAM_500G",
            "64QAM_600G",
            "QPSK_200G",
            "QPSK_SP16QAM_200G",
            "QPSK_SP16QAM_300G",
            "QPSK_SP16QAM_300G_C",
            "QPSK_SP16QAM_500G_C",
            "SP16QAM_16QAM_200G",
            "SP16QAM_16QAM_300G",
            "SP16QAM_16QAM_400G",
            "SP16QAM_16QAM_700G_C",
            "SP16QAM_200G",
            "SP16QAM_300G",
            "SP16QAM_300G_C",
            "SP16QAM_500G_C",
            "SPQPSK_100G",
            "SPQPSK_QPSK_100G",
            "SPQPSK_QPSK_200G",
        ]
        | None
    ) = Field(None, alias="port-mode")
    admin_status: Literal["up", "down", "up-no-alm"] | None = Field(None, alias="admin-status")
    connected_to: str | None = Field(None, alias="connected-to")
    external_connectivity: Literal["yes", "no"] | None = Field(None, alias="external-connectivity")
    service_label: str | None = Field(None, alias="service-label")
    arc_config: Literal["alm", "nalm-qi", "nalm"] | None = Field(None, alias="arc-config")
    arc_timer: int | None = Field(None, alias="arc-timer")


@register_model
class Port(BaseModel):
    port: list[PortItem]


class SubportItem(BaseModel):
    subport_id: str | None = Field(None, alias="subport-id")
    admin_status: Literal["up", "down", "up-no-alm"] | None = Field(None, alias="admin-status")
    connected_to: str | None = Field(None, alias="connected-to")
    external_connectivity: Literal["yes", "no"] | None = Field(None, alias="external-connectivity")
    service_label: str | None = Field(None, alias="service-label")


@register_model
class Subport(BaseModel):
    subport: list[SubportItem]


class OchOsItem(BaseModel):
    admin_status: Literal["up", "down", "up-no-alm"] | None = Field(None, alias="admin-status")
    frequency: str | int | None = None
    rx_frequency: str | int | None = Field(None, alias="rx-frequency")
    laser_enable: str | None = Field(None, alias="laser-enable")
    required_tx_optical_power: str | None = Field(None, alias="required-tx-optical-power")
    fec_type: str | None = Field(None, alias="fec-type")
    rx_attenuation: str | None = Field(None, alias="rx-attenuation")
    tx_filter_roll_off: float | None = Field(None, alias="tx-filter-roll-off")
    preemphasis: str | None = None
    preemphasis_value: float | None = Field(None, alias="preemphasis-value")
    loopback_enable: str | None = Field(None, alias="loopback-enable")
    loopback_type: Literal["none", "terminal", "facility"] | None = Field(None, alias="loopback-type")
    service_label: str | None = Field(None, alias="service-label")
    fast_sop_mode: str | None = Field(None, alias="fast-sop-mode")
    cd_compensation_mode: str | None = Field(None, alias="cd-compensation-mode")
    cd_compensation_value: str | None = Field(None, alias="cd-compensation-value")
    cd_range_high: str | None = Field(None, alias="cd-range-high")
    cd_range_low: str | None = Field(None, alias="cd-range-low")


@register_model
class OchOs(BaseModel):
    och_os: OchOsItem = Field(None, alias="och-os")


class Eth100gItem(BaseModel):
    eth_fec_type: str | None = Field(None, alias="eth-fec-type")
    mapping_mode: (
        Literal["not-applicable", "GMP", "GFP-F", "40GBMP-ODU2E", "PREAMBLE", "BMP-FixedStuff", "BMP", "AMP", "TTT_GMP"]
        | None
    ) = Field(None, alias="mapping-mode")
    admin_status: Literal["up", "down", "up-no-alm"] | None = Field(None, alias="admin-status")
    client_shutdown: str | None = Field(None, alias="client-shutdown")
    client_shutdown_holdoff_timer: int | None = Field(None, alias="client-shutdown-holdoff-timer")
    holdoff_signal: str | None = Field(None, alias="holdoff-signal")
    near_end_als: str | None = Field(None, alias="near-end-als")
    als_degrade_mode: str | None = Field(None, alias="als-degrade-mode")
    loopback_enable: str | None = Field(None, alias="loopback-enable")
    loopback_type: Literal["none", "terminal", "facility"] | None = Field(None, alias="loopback-type")
    test_signal_type: str | None = Field(None, alias="test-signal-type")
    test_signal_enable: str | None = Field(None, alias="test-signal-enable")
    service_label: str | None = Field(None, alias="service-label")
    lldp_status_if: Literal["not-applicable", "rxonly", "txandrx", "disabled"] | None = Field(
        None, alias="lldp-status-if"
    )


@register_model
class Eth100g(BaseModel):
    eth100g: Eth100gItem


class Eth400gItem(BaseModel):
    eth_fec_type: str | None = Field(None, alias="eth-fec-type")
    mapping_mode: (
        Literal["not-applicable", "GMP", "GFP-F", "40GBMP-ODU2E", "PREAMBLE", "BMP-FixedStuff", "BMP", "AMP", "TTT_GMP"]
        | None
    ) = Field(None, alias="mapping-mode")
    admin_status: Literal["up", "down", "up-no-alm"] | None = Field(None, alias="admin-status")
    client_shutdown: str | None = Field(None, alias="client-shutdown")
    client_shutdown_holdoff_timer: int | None = Field(None, alias="client-shutdown-holdoff-timer")
    holdoff_signal: str | None = Field(None, alias="holdoff-signal")
    near_end_als: str | None = Field(None, alias="near-end-als")
    als_degrade_mode: str | None = Field(None, alias="als-degrade-mode")
    loopback_enable: str | None = Field(None, alias="loopback-enable")
    loopback_type: Literal["none", "terminal", "facility"] | None = Field(None, alias="loopback-type")
    test_signal_type: str | None = Field(None, alias="test-signal-type")
    test_signal_enable: str | None = Field(None, alias="test-signal-enable")
    service_label: str | None = Field(None, alias="service-label")
    lldp_status_if: Literal["not-applicable", "rxonly", "txandrx", "disabled"] | None = Field(
        None, alias="lldp-status-if"
    )


@register_model
class Eth400g(BaseModel):
    eth400g: Eth400gItem


class AmplifierItem(BaseModel):
    amplifier_name: Literal["ba", "pa"] = Field(None, alias="amplifier-name")
    admin_status: Literal["up", "down", "up-no-alm"] | None = Field(None, alias="admin-status")
    amplifier_enable: Literal["enabled", "disabled"] | None = Field(None, alias="amplifier-enable")
    input_los_shutdown: Literal["enabled", "disabled"] | None = Field(None, alias="input-los-shutdown")
    control_mode: Literal["manual", "auto"] | None = Field(None, alias="control-mode")
    gain_range_control: Literal["manual", "auto"] | None = Field(None, alias="gain-range-control")
    target_gain_range: Literal["standard", "low", "high", "not-available"] | None = Field(
        None, alias="target-gain-range"
    )
    target_gain: float | None = Field(None, alias="target-gain")
    output_voa: float | None = Field(None, alias="output-voa")
    tilt_control_mode: Literal["manual", "auto"] | None = Field(None, alias="tilt-control-mode")
    gain_tilt: float | None = Field(None, alias="gain-tilt")

    @validator("target_gain", "output_voa", "gain_tilt", pre=True)
    def format_float(cls, v):
        return round(v, 1) if v is not None else None


@register_model
class Amplifier(BaseModel):
    amplifier: list[AmplifierItem]


class CrsItem(BaseModel):
    src_tp: str = Field(None, alias="src-tp")
    dst_tp: str = Field(None, alias="dst-tp")
    service_label: str | None = Field(None, alias="service-label")


@register_model
class Crs(BaseModel):
    CRS: list[CrsItem]


# Add at the bottom of the file
def get_data_model(class_name: str):
    """Get a model class by its name"""
    return _model_registry.get(class_name.lower())
