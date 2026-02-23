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
Pydantic models for leafs of the G42 YANG data model.
These models are used when creating or modifying resources
via RESTCONF to validate and serialize the data to JSON.
"""

from typing import Literal

from pydantic import BaseModel, Field

_model_registry = {}


def register_model(cls):
    """Decorator to register model classes"""
    _model_registry[cls.__name__.lower()] = cls
    return cls

class NeItem(BaseModel):
    ne_name: str | None = Field(None, alias="ne-name")
    label: str | None = None
    node_type: str | None = Field(None, alias="node-type")
    ne_site: str | None = Field(None, alias="ne-site")
    ne_location: str | None = Field(None, alias="ne-location")
    ne_sub_location: str | None = Field(None, alias="ne-sub-location")
    clli: str | None = None
    node_controller_chassis_name: str | None = Field(None, alias="node-controller-chassis-name")
    altitude: int | None = None
    latitude: str | None = None
    longitude: str | None = None
    contact: str | None = None
    alarm_report_control: str | None = Field(None, alias="alarm-report-control")


@register_model
class Ne(BaseModel):
    ne: NeItem

class EthernetItem(BaseModel):
    name: str = Field(..., alias="name")
    label: str | None = None
    admin_state: Literal["lock", "unlock"] | None = Field(None, alias="admin-state")
    alarm_report_control: Literal["allowed", "inhibited"] | None = Field(
        None, alias="alarm-report-control"
    )
    fec_mode: Literal["enabled", "disabled"] | None = Field(None, alias="fec-mode")
    loopback: Literal["none", "terminal", "facility"] | None = None
    test_signal_type: Literal["none", "prbs", "square-wave"] | None = Field(
        None, alias="test-signal-type"
    )
    test_signal_direction: Literal["ingress", "egress"] | None = Field(
        None, alias="test-signal-direction"
    )
    test_signal_monitoring: bool | None = Field(None, alias="test-signal-monitoring")
    lldp_admin_status: Literal["disabled", "rx-only", "tx-and-rx"] | None = Field(
        None, alias="lldp-admin-status"
    )
    lldp_ingress_mode: Literal["snoop", "forward"] | None = Field(
        None, alias="lldp-ingress-mode"
    )
    lldp_egress_mode: Literal["snoop", "forward"] | None = Field(
        None, alias="lldp-egress-mode"
    )


@register_model
class Ethernet(BaseModel):
    ethernet: list[EthernetItem]


class TribPtpItem(BaseModel):
    name: str = Field(..., alias="name")
    label: str | None = None
    admin_state: Literal["maintenance", "unlock", "lock"] | None = Field(
        None, alias="admin-state"
    )
    auto_in_service_enabled: bool | None = Field(None, alias="auto-in-service-enabled")
    valid_signal_time: int | None = Field(None, alias="valid-signal-time")
    alarm_report_control: Literal["allowed", "inhibited"] | None = Field(
        None, alias="alarm-report-control"
    )
    service_type: str | None = Field(None, alias="service-type")
    tributary_disable_action: Literal["laser-shut-off", "none"] | None = Field(
        None, alias="tributary-disable-action"
    )
    tributary_disable_holdoff_timer: int | None = Field(
        None, alias="tributary-disable-holdoff-timer"
    )
    forward_defect_trigger: bool | None = Field(None, alias="forward-defect-trigger")
    power_threshold_low_offset: str | None = Field(None, alias="power-threshold-low-offset")
    power_threshold_high_offset: str | None = Field(None, alias="power-threshold-high-offset")


@register_model
class TribPtp(BaseModel):
    trib_ptp: list[TribPtpItem] = Field(..., alias="trib-ptp")


class SuperChannelGroupItem(BaseModel):
    name: str = Field(..., alias="name")
    label: str | None = None
    admin_state: Literal["maintenance", "unlock", "lock"] | None = Field(
        None, alias="admin-state"
    )
    auto_in_service_enabled: bool | None = Field(None, alias="auto-in-service-enabled")
    valid_signal_time: int | None = Field(None, alias="valid-signal-time")
    alarm_report_control: Literal["allowed", "inhibited"] | None = Field(
        None, alias="alarm-report-control"
    )
    line_system_mode: str | None = Field(None, alias="line-system-mode")
    openwave_contention_check: bool | None = Field(None, alias="openwave-contention-check")


@register_model
class SuperChannelGroup(BaseModel):
    super_channel_group: list[SuperChannelGroupItem] = Field(
        ..., alias="super-channel-group"
    )

class ChassisItem(BaseModel):
    name: str = Field(..., alias="name")
    expected_serial_number: str | None = Field(None, alias="expected-serial-number")
    alias_name: str | None = Field(None, alias="alias-name")
    admin_state: Literal["lock", "unlock"] | None = Field(None, alias="admin-state")
    alarm_report_control: Literal["allowed", "inhibited"] | None = Field(
        None, alias="alarm-report-control"
    )
    label: str | None = None
    required_type: str | None = Field(None, alias="required-type")
    chassis_location: str | None = Field(None, alias="chassis-location")
    rack_name: str | None = Field(None, alias="rack-name")
    position_in_rack: int | None = Field(None, alias="position-in-rack")
    expected_pem_type: str | None = Field(None, alias="expected-pem-type")
    expected_fan_type: str | None = Field(None, alias="expected-fan-type")
    pem_under_voltage_threshold: str | None = Field(None, alias="pem-under-voltage-threshold")
    pem_over_voltage_threshold: str | None = Field(None, alias="pem-over-voltage-threshold")
    configured_max_power_draw: str | None = Field(None, alias="configured-max-power-draw")
    configured_ambient_temperature: int | None = Field(None, alias="configured-ambient-temperature")
    power_redundancy: str | None = Field(None, alias="power-redundancy")
    no_switchover: str | None = Field(None, alias="no-switchover")


@register_model
class Chassis(BaseModel):
    chassis: list[ChassisItem]


class NtpServerItem(BaseModel):
    ip_address: str = Field(..., alias="ip-address")
    origin: str | None = None
    auth_key_id: str | None = Field(None, alias="auth-key-id")
    label: str | None = None
    admin_state: Literal["lock", "unlock"] | None = Field(None, alias="admin-state")
    alarm_report_control: Literal["allowed", "inhibited"] | None = Field(
        None, alias="alarm-report-control"
    )


class NtpItem(BaseModel):
    ntp_enabled: bool = Field(..., alias="ntp-enabled")
    ntp_auth_enabled: bool = Field(..., alias="ntp-auth-enabled")
    assignment_method: str | None = Field(None, alias="assignment-method")
    ntp_server: list[NtpServerItem] = Field(..., alias="ntp-server")


@register_model
class Ntp(BaseModel):
    ntp: NtpItem

class PortItem(BaseModel):
    name: str = Field(..., alias="name")
    alias_name: str | None = Field(None, alias="alias-name")
    admin_state: Literal["lock", "unlock"] | None = Field(None, alias="admin-state")
    alarm_report_control: Literal["allowed", "inhibited"] | None = Field(
        None, alias="alarm-report-control"
    )
    label: str | None = None
    connected_to: str | None = Field(None, alias="connected-to")
    external_connectivity: str | None = Field(None, alias="external-connectivity")


@register_model
class Port(BaseModel):
    port: list[PortItem]


class SuperChannelItem(BaseModel):
    name: str = Field(..., alias="name")
    label: str | None = None
    admin_state: Literal["lock", "unlock"] | None = Field(None, alias="admin-state")
    alarm_report_control: Literal["allowed", "inhibited"] | None = Field(
        None, alias="alarm-report-control"
    )
    carriers: list[str] = Field(None, alias="carriers")
    carrier_mode: str | None = Field(None, alias="carrier-mode")


@register_model
class SuperChannel(BaseModel):
    super_channel: list[SuperChannelItem] = Field(..., alias="super-channel")


class OpticalCarrierItem(BaseModel):
    name: str = Field(..., alias="name")
    label: str | None = None
    admin_state: Literal["lock", "unlock"] | None = Field(None, alias="admin-state")
    alarm_report_control: Literal["allowed", "inhibited"] | None = Field(
        None, alias="alarm-report-control"
    )
    frequency: int | None = None
    frequency_offset: int | None = Field(None, alias="frequency-offset")
    tx_power: float | None = Field(None, alias="tx-power")
    pre_fec_q_sig_deg_threshold: str | None = Field(None, alias="pre-fec-q-sig-deg-threshold")
    pre_fec_q_sig_deg_hysteresis: str | None = Field(None, alias="pre-fec-q-sig-deg-hysteresis")
    tx_cd: str | None = Field(None, alias="tx-cd")
    dgd_high_threshold: int | None = Field(None, alias="dgd-high-threshold")
    post_fec_q_sig_deg_threshold: str | None = Field(None, alias="post-fec-q-sig-deg-threshold")
    post_fec_q_sig_deg_hysteresis: str | None = Field(None, alias="post-fec-q-sig-deg-hysteresis")
    enable_advanced_parameters: bool | None = Field(None, alias="enable-advanced-parameters")
    sop_data_collection: str | None = Field(None, alias="sop-data-collection")


@register_model
class OpticalCarrier(BaseModel):
    optical_carrier: list[OpticalCarrierItem] = Field(..., alias="optical-carrier")


class TomItem(BaseModel):
    required_type: str | None = Field(None, alias="required-type")
    required_subtype: str | None = Field(None, alias="required-subtype")
    phy_mode: str | None = Field(None, alias="phy-mode")
    power_class_override: str | None = Field(None, alias="power-class-override")
    alias_name: str | None = Field(None, alias="alias-name")
    admin_state: Literal["lock", "unlock", "maintenance"] | None = Field(None, alias="admin-state")
    alarm_report_control: Literal["allowed", "inhibited"] | None = Field(
        None, alias="alarm-report-control"
    )
    label: str | None = None
    enable_serdes: bool | None = Field(None, alias="enable-serdes")

@register_model
class Tom(BaseModel):
    tom: TomItem = Field(..., alias="tom")


class XconItem(BaseModel):
    name: str = Field(..., alias="name")
    source: str | None = None
    destination: str | None = None
    payload_type: str | None = Field(None, alias="payload-type")
    direction: Literal["one-way", "two-way"] | None = None
    label: str | None = None
    circuit_id_suffix: str | None = Field(None, alias="circuit-id-suffix")

@register_model
class Xcon(BaseModel):
    xcon: list[XconItem] = Field(..., alias="xcon")

# This function MUST be at the bottom of the file
def get_data_model(class_name: str):
    """Get a model class by its name"""
    return _model_registry.get(class_name.lower())
