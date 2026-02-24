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

"""# Create Optical Digital Service Workflow.

## At a Glance

**What**: Provisions a new end-to-end optical transport service between two sites.

**Traffic Impact**: ⚠️ **New service** - traffic begins flowing after successful completion.

**Use When**: Need to establish a new point-to-point optical connection for 100GBE or 400GBE Ethernet.

**Duration**: 3-5 minutes for new channels, 1-2 minutes when reusing existing channels.

**How**: Guided input forms, automatic path calculation, device configuration via TL1/NETCONF/RESTCONF APIs.

---

## Service Types Supported

| Service Type | Description | Carriers |
|--------------|-------------|----------|
| 100GBE | 100 Gigabit Ethernet | 1 or 2 carriers |
| 400GBE | 400 Gigabit Ethernet | 1 or 2 carriers |

**Dual-carrier services** provide higher bandwidth or longer reach by bonding two optical carriers together.

---

## Two Provisioning Modes

This workflow supports **two distinct scenarios**:

### Mode 1: New Optical Channels (Full Provisioning)
- Creates new optical transport channels from scratch
- Configures transponders and ROADMs along entire path
- User selects frequencies, bandwidth, modulation mode
- User defines optical routing path
- **Duration**: 3-5 minutes

### Mode 2: Reuse Existing Channels (Client-Only Provisioning)
- Attaches to optical channels already provisioned by another service
- Only configures client ports and updates labels
- No line-side or ROADM configuration needed
- **Duration**: 1-2 minutes

**The workflow automatically detects which mode to use** based on whether the specified OCh IDs already exist.

---

## Before Running

### Prerequisites
- [ ] Two transponders/transceivers are available at source and destination sites
- [ ] Client ports are available and unused on both devices
- [ ] Line ports are fiber-patched to Optical Line Systems or directly connected
- [ ] For new channels: Optical path exists between sites (fiber spans and ROADMs)
- [ ] Flow ID and Client ID combination is unique
- [ ] OCh IDs are available or correctly reference existing channels

### Constraints
- Cannot connect a device to itself (must be two different nodes)
- Flow ID (fX) and Client ID (cY) must be positive integers
- The combination fXcY must be unique across all services
- OCh IDs must be positive integers
- For dual-carrier: both OCh IDs must belong to same service or both be new
- Frequencies must be ITU-T grid aligned (6.25 GHz increments)
- Bandwidths must be 12.5 GHz increments

### Rollback
**Manual only** - use "Terminate optical_digital_service" workflow to remove the service
or manually clean up partial configuration if needed.

---

## After Running

### Validation Checklist
- [ ] Subscription status is ACTIVE
- [ ] Client ports are UP on both transponders
- [ ] Line ports show correct frequencies and modes
- [ ] Optical power levels are within acceptable range
- [ ] Pre-FEC BER is below threshold
- [ ] No alarms on transponders or ROADMs
- [ ] End-to-end Ethernet connectivity verified

### Troubleshooting

**If workflow fails during provisioning**:
1. Check which step failed in the workflow page
2. Review error message for specific device or configuration issue
3. Verify all prerequisites were met
4. Check device reachability and API access
5. May need to manually clean up partial configuration

**Common Issues**:
- **No optical path found**: Fiber spans may be missing or frequency unavailable (run validate workflow for
optical fibers attached to ROADMs along the path)
- **Device unreachable**: TL1/NETCONF/RESTCONF API not accessible
- **Too fast retry**: Device still processing previous command, wait a few seconds and retry

---

## Workflow Steps

This workflow executes up to 13 steps (some are conditional):

### Input Forms (Steps 1-4)

#### Form 1: Service Definition
**What**: Define basic service parameters
**User Input**:
- Partner/customer subscription
- Service type (100GBE or 400GBE)
- Source and destination nodes (Node A and Node B)
- Flow ID (fX) and Client ID (cY)
- OCh IDs (1 or 2 for single/dual-carrier)

**Validation**:
- Node A ≠ Node B
- Flow ID and Client ID must be positive
- fXcY combination must be unique
- For dual-carrier: OCh IDs must not be from different services

---

#### Form 2: Client Port Selection
**What**: Select Ethernet client ports
**User Input**:
- Client port on Node A (from available unused ports)
- Client port on Node B (from available unused ports)

**Auto-detection**: Workflow checks if OCh IDs already exist to determine provisioning mode.

---

#### Form 3: Optical Transport Channels (New Channels Only)
**What**: Configure optical layer parameters
**User Input**:
- Line port for each carrier on Node A
- Line port for each carrier on Node B
- Central frequency for each carrier (MHz, ITU-T grid)
- Spectral bandwidth for each carrier (MHz, with guardbands)
- Modulation mode (e.g., DP-16QAM, DP-QPSK)
- Exclude devices list (routing constraint)
- Exclude fibers list (routing constraint)

**Validation**:
- Frequencies must be multiples of 6,250 MHz
- Bandwidths must be multiples of 12,500 MHz

**Skipped if**: Reusing existing channels.

---

#### Form 4: Optical Path Selection (New Channels Only)
**What**: Choose routing through network
**User Input**:
- Select from available optical paths between nodes

**Path Calculation**:
- Workflow automatically finds paths that:
  - Connect specified line ports
  - Have sufficient spectrum for the passband
  - Avoid excluded devices and fibers
  - Stay within device platform compatibility

**Skipped if**: Reusing existing channels or direct fiber connection.

---

### Step 5: Save Input Data
**Function**: `construct_optical_digital_service_model()`
**What**: Creates database subscription model
**Traffic Impact**: None (database only)

Creates the OpticalDigitalService subscription with:
- Service name: `f{fX:03d}c{cY:02d} OCh{id:03d} {siteA}-{siteB}`
- Client port mappings with cross-site descriptions
- Transport channel(s) with frequencies and modes
- Optical spectrum definitions with passbands
- Routing constraints (excluded devices/fibers)

For existing channels: Links to existing OpticalTransportChannelBlock instances.

---

### Step 6: Store Subscription
**Function**: `store_process_subscription()`
**What**: Persists subscription to database
**Traffic Impact**: None (database only)

Standard orchestrator step to save the subscription.

---

### Step 7: Divide Path Into Sections (New Channels Only)
**Function**: `divide_path_into_sections()`
**What**: Segments optical path by device platform
**Traffic Impact**: None (database only)

**Why needed**: Different device platforms (FlexILS, Groove G30 H4) require different configuration approaches.

Splits the optical path into sections where:
- Each section contains ports from same device platform
- Section boundaries are add/drop points
- Each section gets its own OpticalSpectrumSection block

**Example**:
```
Path: G30 -> FlexILS -> FlexILS -> G30
Sections: [G30], [FlexILS, FlexILS], [G30]
```

**Skipped if**: Direct connection (no managed line system) or reusing existing channels.

---

### Step 8: Set Status to Provisioning
**Function**: `set_status(SubscriptionLifecycle.PROVISIONING)`
**What**: Updates subscription lifecycle state
**Traffic Impact**: None (database only)

Marks the subscription as actively being provisioned.

---

### Step 9: Update Subscription Description
**Function**: `update_subscription_description()`
**What**: Generates human-readable description
**Traffic Impact**: None (database only)

Creates description: `f001c01 OCh042 rom-mi (100GBE)`.

---

### Step 10: Configure Transponder Line Side ⚠️ (New Channels Only)
**Function**: `configure_trx_line_side()`
**What**: Configures optical transmit/receive on line ports
**Traffic Impact**: ⚠️ **Enables lasers** (no traffic yet, cross-connects not established)

**Infinera Groove G30**:
- Creates och-os (optical channel) on each line port
- Sets TX/RX frequencies
- Configures port mode (modulation format)
- Enables laser with admin status UP

**Infinera GX G42**:
- Creates super-channel with carrier frequencies
- Sets carrier mode (modulation format)
- Configures optical-carrier resources
- Unlocks all components

**This step turns on the lasers** but traffic doesn't flow until cross-connects are established.

**Skipped if**: Reusing existing channels (lasers already configured).

---

### Step 11: Configure Transponder Client Side
**Function**: `configure_trx_client_side()`
**What**: Configures Ethernet client ports
**Traffic Impact**: Minimal (port configuration)

**Infinera Groove G30**:
- Updates service labels on client ports
- Enables Ethernet FEC
- Verifies port mode (100GBE or 400GBE)

**Infinera GX G42**:
- Updates TOM (Transceiver Optical Module) labels
- Updates trib-ptp (tributary) labels
- Enables Ethernet and FEC

**Runs in both modes** (new channels and reusing existing).

---

### Step 12: Configure Cross-Connects ✅
**Function**: `configure_trx_crossconnects()`
**What**: Maps client ports to line ports inside transponder
**Traffic Impact**: ✅ **Traffic starts flowing**

**Infinera Groove G30**:
- Creates ODU cross-connects from client to line ports
- Sets service name as label
- For dual-carrier: creates 2 cross-connects

**Infinera GX G42**:
- Creates XCON between Ethernet and ODU
- Sets label and circuit-id-suffix

**This is when the service becomes operational** - client Ethernet traffic is now mapped to optical carriers.

**Runs in both modes** (new channels and reusing existing).

---

### Step 13: Provision ROADM Sections (New Channels Only)
**Function**: `provision_optical_sections()`
**What**: Configures wavelength filters on ROADMs
**Traffic Impact**: ✅ **Opens filters** to pass optical signal

**Infinera FlexILS**:
1. Creates OSNC (Optical Supernode Connection) for each section
2. Configures:
   - `passbandlist`: Frequency range to pass
   - `carrierlist`: Center frequency and bandwidth
   - `label`: Service identifier (f001c01)
3. Sets OSNC to In-Service
4. **Opens shutters** on source and destination ROADMs

**Groove G30 H4 links**:
- No action needed (transparent fiber, no active filtering)

**This configures the wavelength-selective switches** along the path to pass the optical signal.

**Skipped if**: Reusing existing channels (ROADMs already configured).

---

### Step 14: Update Used Passbands (New Channels Only)
**Function**: `update_used_passbands()`
**What**: Refreshes spectrum occupancy data for ports in path
**Traffic Impact**: None (database update)

Queries each ROADM/OADM along the path to retrieve current spectral occupancy and updates the `used_passbands` field on each port. This keeps database in sync with actual device state for future path calculations.

**Skipped if**: Reusing existing channels.

---

### Step 15: Update Labels (Existing Channels Only)
**Function**: `update_optical_spectrum_sections_label()`
**What**: Appends service ID to OSNC labels
**Traffic Impact**: None (cosmetic label update)

When reusing existing channels, updates the OSNC labels to include the new service's fXcY identifier. Multiple services sharing channels have labels like: "f001c01+f002c03".

**Skipped if**: New channels (labels already set in Step 13).

---

## Provisioning Flow Comparison

### New Channels (Full Workflow)
```
1. Input forms (define everything)
2. Save to database
3. Divide path into sections
4. Set status PROVISIONING
5. Update description
6. Configure transponder line side ← Lasers on
7. Configure transponder client side
8. Configure cross-connects ← Traffic starts
9. Provision ROADM sections ← Filters open
10. Update used passbands
```

### Reuse Existing Channels (Short Workflow)
```
1. Input forms (minimal: nodes, ports, OCh IDs)
2. Save to database (link to existing channels)
3. [SKIP sections - already exist]
4. Set status PROVISIONING
5. Update description
6. [SKIP transponder line - already configured]
7. Configure transponder client side
8. Configure cross-connects ← Traffic starts
9. [SKIP ROADM provisioning]
10. [SKIP update passbands]
11. Update OSNC labels ← Add service ID
```

---

## Service Naming Convention

**Service Name Format**: `f{fX:03d}c{cY:02d} OCh{id:03d}[+OCh{id:03d}] {siteA}-{siteB}`

**Examples**:
- Single carrier: `f001c01 OCh042 rom-mi`
- Dual carrier: `f002c05 OCh033+OCh034 rom-fi`

**Components**:
- `fX`: Flow ID (3 digits, zero-padded)
- `cY`: Client ID (2 digits, zero-padded)
- `OCh`: Optical Channel ID(s)
- Site codes: POP location codes (lowercase)

**Label on ROADMs**: `f001c01+f002c03` (when multiple services share spectrum)

---

<details>
<summary>Technical Reference</summary>

## Database Schema Created

The workflow creates an `OpticalDigitalServiceBlock` with:
- **service_name**: Human-readable identifier
- **service_type**: 100GBE or 400GBE
- **flow_id**, **client_id**: Unique service identifiers
- **client_ports[2]**: Source and destination Ethernet ports
- **transport_channels[1-2]**: Optical carrier(s)
  - **och_id**: Optical channel identifier
  - **central_frequency**: Carrier frequency in MHz
  - **mode**: Modulation format
  - **line_ports[2]**: Transmit and receive ports
  - **optical_spectrum**: Spectrum allocation
    - **spectrum_name**: OCh identifier
    - **passband**: (start_freq, end_freq) in MHz
    - **optical_spectrum_sections[]**: ROADM segments
      - **add_drop_ports[2]**: Section endpoints
      - **optical_path[]**: Intermediate ports
    - **optical_spectrum_path_constraints**: Routing exclusions

## Conditional Logic

The workflow uses `conditional()` steps to handle two scenarios:

**Condition**: `are_channels_yet_to_be_provisioned()`
- **True**: `subscription_id == owner_subscription_id` (new channels)
- **False**: Existing OpticalTransportChannelBlock has different owner (reusing channels)

**Steps executed when True** (new channels):
- divide_path_into_sections
- configure_trx_line_side
- provision_optical_sections
- update_used_passbands

**Steps executed when False** (reusing):
- update_optical_spectrum_sections_label

## Service Functions Called

- `configure_line_transceivers()`: Line port configuration
- `configure_transceiver_client()`: Client port configuration
- `configure_transponder_crossconnect()`: Internal cross-connects
- `deploy_optical_circuit()`: ROADM OSNC provisioning
- `append_optical_circuit_label()`: OSNC label updates
- `retrieve_ports_spectral_occupations()`: Spectrum occupancy query
- `subscription_description()`: Description generator

## Optical Path Calculation

Path finding algorithm:
1. Starts at source line port
2. Traverses fiber spans and device internal connections
3. Filters paths that:
   - Avoid excluded devices and fibers
   - Have sufficient unallocated spectrum for passband
   - Maintain platform compatibility for sections
4. Returns list of port UUIDs representing full path

## ITU-T Grid Alignment

**Frequency Grid**: 193,100,000 MHz (193.1 THz) ± n × 6,250 MHz
- Valid: 193,100,000; 193,106,250; 193,112,500; etc.
- Invalid: 193,105,000; 193,110,000; etc.

**Bandwidth Grid**: n × 12,500 MHz
- Valid: 50,000; 62,500; 75,000; etc.
- Invalid: 60,000; 70,000; etc.

## Related Workflows

- **Modify Optical Digital Service**: Change frequencies/modes on existing service
- **Validate Optical Digital Service**: Verify configuration consistency
- **Terminate Optical Digital Service**: Decommission service

## Device Platform Support

- **Infinera Groove G30**: Transponder/transceiver
- **Infinera GX G42**: Transponder/transceiver
- **Infinera FlexILS**: ROADM with wavelength-selective switching
- **Groove G30 H4**: Optical amplifier (transparent pass-through)

</details>
"""

from time import sleep
from typing import Annotated

from orchestrator.domain import SubscriptionModel
from orchestrator.forms import FormPage
from orchestrator.forms.validators import Choice, Divider, Label, choice_list, unique_conlist
from orchestrator.types import SubscriptionLifecycle
from orchestrator.workflow import (
    StepList,
    begin,
    conditional,
    step,
)
from orchestrator.workflows.steps import set_status, store_process_subscription
from orchestrator.workflows.utils import create_workflow
from pydantic import Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from structlog import get_logger

from products.product_blocks.optical_device import DeviceType, Platform
from products.product_blocks.optical_device_port import OpticalDevicePortBlock
from products.product_blocks.optical_digital_service import ClientSpeednType
from products.product_blocks.transport_channel import (
    OpticalTransportChannelBlock,
    OpticalTransportChannelBlockInactive,
)
from products.product_types.optical_device import OpticalDevice
from products.product_types.optical_digital_service import (
    OpticalDigitalService,
    OpticalDigitalServiceInactive,
    OpticalDigitalServiceProvisioning,
)
from products.product_types.optical_fiber import OpticalFiber
from products.services.optical_device import retrieve_ports_spectral_occupations
from products.services.optical_digital_service import (
    allign_tx_power_to_target,
    configure_line_transceivers,
    configure_transceiver_client,
    configure_transponder_crossconnect,
    diff_btw_current_rx_power_and_target,
    get_signal_bandwidth,
)
from products.services.optical_spectrum import (
    append_optical_circuit_label,
    deploy_optical_circuit,
)
from utils.custom_types.frequencies import Frequency
from workflows.optical_device.shared import (
    multiple_optical_device_selector,
    optical_device_selector_of_types,
    transceiver_mode_selector,
    unused_optical_client_port_selector,
)
from workflows.optical_digital_service.shared import (
    trx_line_port_patched_but_not_used_multiple_selector,
)
from workflows.optical_fiber.shared import multiple_optical_fiber_selector
from workflows.optical_spectrum.shared import (
    NoOpticalPathFoundError,
    find_add_drop_ports,
    store_list_of_ports_into_spectrum_sections,
    transport_channel_path_selector,
    update_used_passbands,
)
from workflows.shared import (
    active_subscription_selector,
    subscription_instances_by_block_type_and_resource_value,
    subscriptions_by_product_type_and_instance_value,
)

logger = get_logger(__name__)

FlexBandwidth = Annotated[int, Field(ge=37_500, multiple_of=12_500)]


def subscription_description(subscription: SubscriptionModel) -> str:
    """Generate subscription description.

    The suggested pattern is to implement a subscription service that generates a subscription specific
    description, in case that is not present the description will just be set to the product name.
    """
    ods = subscription.optical_digital_service
    return f"{ods.service_name} ({ods.service_type})"


def initial_input_form_generator(product_name: str) -> FormGenerator:
    PartnerChoice = NotImplementedError("Not implemented")  # FIXME

    transceivers_types = [
        DeviceType.Transceiver,
        DeviceType.Transponder,
        DeviceType.TransponderAndOADM,
    ]
    NodeAChoice = optical_device_selector_of_types(
        device_types=transceivers_types,
        prompt="This service connects this node: ",
    )

    NodeBChoice = optical_device_selector_of_types(
        device_types=transceivers_types,
        prompt="...to this other node: ",
    )

    ServiceTypeChoice = Choice("What service do you want?", [(speed, speed.value) for speed in ClientSpeednType])

    och_id_annotated_type = Annotated[int, Field(ge=1, le=999)]

    class OdsForm0(FormPage):
        class Config:
            title = "Optical Digital Service"

        user_id: PartnerChoice
        service_type: ServiceTypeChoice = ClientSpeednType.Ethernet100Gbps
        id_node_a: NodeAChoice
        id_node_b: NodeBChoice
        fx_flow_id: Annotated[
            int, Field(title="This type of service is identified with ID fXcY. Enter number X", ge=1, le=999)
        ] = 1
        cy_client_id: Annotated[int, Field(title="Enter number Y", ge=1, le=16)] = 1
        och_ids: Annotated[
            unique_conlist(och_id_annotated_type, min_items=1, max_items=2), Field(title="Optical Channel ID(s)")
        ] = [1]

        @model_validator(mode="after")
        def validate_data(self) -> "OdsForm0":
            if self.id_node_a == self.id_node_b:
                msg = "Only different devices can be connected"
                raise ValueError(msg)

            subs = subscriptions_by_product_type_and_instance_value(
                product_type="OpticalDigitalService",
                resource_type="flow_id",
                value=str(self.fx_flow_id),
                status=[
                    SubscriptionLifecycle.INITIAL,
                    SubscriptionLifecycle.PROVISIONING,
                    SubscriptionLifecycle.ACTIVE,
                ],
            )
            for sub in subs:
                ods = OpticalDigitalService.from_subscription(sub.subscription_id).optical_digital_service
                if ods.client_id == self.cy_client_id:
                    msg = f"f{self.fx_flow_id}c{self.cy_client_id} already in use by subscription {sub.subscription_id}"
                    raise ValueError(msg)

            owner_ids = set()
            for och_id in self.och_ids:
                existing_channel = subscription_instances_by_block_type_and_resource_value(
                    product_block_type="OpticalTransportChannel",
                    resource_type="och_id",
                    resource_value=str(och_id),
                )

                if existing_channel == []:
                    current_owner_id = None

                else:
                    current_owner_id = existing_channel[0].subscription_id
                    block = OpticalTransportChannelBlock.from_db(existing_channel[0].subscription_instance_id)
                    existing_id_node_a = str(block.line_ports[0].optical_device.owner_subscription_id)
                    existing_id_node_b = str(block.line_ports[1].optical_device.owner_subscription_id)
                    if existing_id_node_a == self.id_node_b and existing_id_node_b == self.id_node_a:
                        self.id_node_a, self.id_node_b = self.id_node_b, self.id_node_a
                    elif existing_id_node_a != self.id_node_a and existing_id_node_b != self.id_node_b:
                        msg = (
                            f"Terminations mismatch for OCh ID {och_id}. Source and destination nodes "
                            f"must be {block.line_ports[0].optical_device.fqdn} and "
                            f"{block.line_ports[1].optical_device.fqdn} respectively."
                        )
                        raise ValueError(msg)

                owner_ids.add(current_owner_id)

            if len(owner_ids) > 1:
                msg = (
                    "It seems like the provided OCh IDs are already in use by two different services. "
                    "A digital service can only be transported over one channel or two coupled channels."
                    "Please correct this inconsistency before proceeding."
                )
                raise ValueError(msg)

            return self

    user_input = yield OdsForm0
    user_input_dict = user_input.dict()

    sub_node_a = OpticalDevice.from_subscription(user_input_dict["id_node_a"])
    optical_device_a = sub_node_a.optical_device
    sub_node_b = OpticalDevice.from_subscription(user_input_dict["id_node_b"])
    optical_device_b = sub_node_b.optical_device

    ClientAChoice = unused_optical_client_port_selector(
        user_input_dict["id_node_a"],
        prompt=f"Select the client port on {optical_device_a.fqdn}",
    )

    ClientBChoice = unused_optical_client_port_selector(
        user_input_dict["id_node_b"],
        prompt=f"Select the client port on {optical_device_b.fqdn}",
    )

    class OdsForm1(FormPage):
        class Config:
            title = "Client Ports"

        name_client_port_a: ClientAChoice
        name_client_port_b: ClientBChoice

    user_input = yield OdsForm1
    user_input_dict.update(user_input.dict())

    are_channel_already_provisioned = True
    first_och_id = user_input_dict["och_ids"][0]
    existing_channels = subscription_instances_by_block_type_and_resource_value(
        product_block_type="OpticalTransportChannel",
        resource_type="och_id",
        resource_value=str(first_och_id),
    )

    if not existing_channels:
        are_channel_already_provisioned = False

    if are_channel_already_provisioned:
        user_input_dict.update(
            {
                "line_ports_a": [],
                "line_ports_b": [],
                "frequencies": [],
                "bandwidths": [],
                "mode": [],
                "exclude_devices_list": [],
                "exclude_fibers_list": [],
                "optical_path": [],
            }
        )

    else:
        num_carriers = len(user_input_dict["och_ids"])

        LinesAChoice = trx_line_port_patched_but_not_used_multiple_selector(
            optical_device_subscription_id=user_input_dict["id_node_a"],
            client_port_name=user_input_dict["name_client_port_a"],
            prompt=f"Select the line port for each carrier on {optical_device_a.fqdn}",
            min_items=num_carriers,
            max_items=num_carriers,
            unique_items=True,
        )

        LinesBChoice = trx_line_port_patched_but_not_used_multiple_selector(
            optical_device_subscription_id=user_input_dict["id_node_b"],
            client_port_name=user_input_dict["name_client_port_b"],
            prompt=f"Select the line port for each carrier on {optical_device_b.fqdn}",
            min_items=num_carriers,
            max_items=num_carriers,
            unique_items=True,
        )

        ModeChoice = transceiver_mode_selector(
            optical_device_subscription_id=user_input_dict["id_node_a"],
            port_name=user_input_dict["name_client_port_a"],
            prompt="Select the operating mode of the transport channels",
        )

        FrequenciesChoice = Annotated[
            unique_conlist(Frequency, min_items=num_carriers, max_items=num_carriers),
            Field(title="Central frequency (MHz) of each optical carrier"),
        ]

        BandwidthsChoice = Annotated[
            choice_list(FlexBandwidth, min_items=num_carriers, max_items=num_carriers, unique_items=False),
            Field(title="Spectral width (MHz), including guardbands, reserved for each transport channel"),
        ]

        line_system_types = [
            DeviceType.ROADM,
            DeviceType.TransponderAndOADM,
            DeviceType.Amplifier,
        ]

        ExcludeOpticalDeviceChoiceList = multiple_optical_device_selector(
            device_types=line_system_types,
            prompt="Do *not* pass through these Optical Devices",
        )

        ExcludeSpanChoiceList = multiple_optical_fiber_selector(
            prompt="Do *not* pass through these Optical Fibers",
        )

        class OdsForm2(FormPage):
            class Config:
                title = "Optical Transport Channels"

            line_ports_a: LinesAChoice
            line_ports_b: LinesBChoice
            frequencies: FrequenciesChoice
            bandwidths: BandwidthsChoice
            mode: ModeChoice

            routing_constraints: Label
            divider_002: Divider
            exclude_devices_list: ExcludeOpticalDeviceChoiceList | None = []
            exclude_fibers_list: ExcludeSpanChoiceList | None = []

        user_input = yield OdsForm2
        user_input_dict.update(user_input.dict())

        passband = (
            user_input_dict["frequencies"][0] - user_input_dict["bandwidths"][0] // 2,
            user_input_dict["frequencies"][0] + user_input_dict["bandwidths"][0] // 2,
        )

        no_path_found_msg = (
            "No optical path found, please adjust the routing constraints"
            " in the previous step or validate fibers in the path."
        )
        try:
            PathChoice = transport_channel_path_selector(
                user_input_dict["line_ports_a"][0],
                user_input_dict["line_ports_b"][0],
                passband,
                user_input_dict["exclude_devices_list"],
                user_input_dict["exclude_fibers_list"],
                prompt=(
                    "Select the optical path, if you don't see the desired path,"
                    " adjust constraints in previous step or validate fibers along the path."
                ),
            )
        except NoOpticalPathFoundError:
            logger.exception(
                "No optical path found",
                line_ports_a=user_input_dict["line_ports_a"],
                line_ports_b=user_input_dict["line_ports_b"],
                passband=passband,
                exclude_devices_list=user_input_dict["exclude_devices_list"],
                exclude_fibers_list=user_input_dict["exclude_fibers_list"],
            )

            PathChoice = Choice(
                no_path_found_msg,
                [
                    (no_path_found_msg, no_path_found_msg),
                ],
            )

        class OdsForm3(FormPage):
            class Config:
                title = "Optical Path"

            optical_path: PathChoice

            @model_validator(mode="after")
            def validate_data(self) -> "OdsForm3":
                if self.optical_path == no_path_found_msg:
                    msg = (
                        "No optical path found, please adjust the routing constraints "
                        "in the previous step or update fibers in the path."
                    )
                    raise ValueError(msg)
                return self

        user_input = yield OdsForm3
        user_input_dict.update(user_input.dict())

        user_input_dict["optical_path"] = user_input_dict["optical_path"].split(";")

    return user_input_dict


@step("Saving input data into the optical digital service model")
def construct_optical_digital_service_model(
    product: UUIDstr,
    user_id: UUIDstr,
    id_node_a: UUIDstr,
    id_node_b: UUIDstr,
    fx_flow_id: int,
    cy_client_id: int,
    service_type: ClientSpeednType,
    name_client_port_a: str,
    name_client_port_b: str,
    och_ids: list[int],
    frequencies: list[Frequency],
    bandwidths: list[FlexBandwidth],
    mode: str,
    line_ports_a: list[UUIDstr],
    line_ports_b: list[UUIDstr],
    exclude_devices_list: list[UUIDstr],
    exclude_fibers_list: list[UUIDstr],
) -> State:
    subscription = OpticalDigitalServiceInactive.from_product_id(
        product_id=product,
        customer_id=user_id,
        status=SubscriptionLifecycle.INITIAL,
    )
    ods = subscription.optical_digital_service

    sub_device_a = OpticalDevice.from_subscription(id_node_a)
    sub_device_b = OpticalDevice.from_subscription(id_node_b)
    device_a = sub_device_a.optical_device
    device_b = sub_device_b.optical_device
    code_pop_a = device_a.pop.code.lower()
    code_pop_b = device_b.pop.code.lower()
    ods.service_name = f"f{fx_flow_id:03d}c{cy_client_id:02d} "
    ods.service_name += "+".join([f"OCh{och_id:03d}" for och_id in och_ids])
    ods.service_name += f" {code_pop_a}-{code_pop_b}"

    ods.service_type = service_type

    ods.flow_id = fx_flow_id
    ods.client_id = cy_client_id

    ods.client_ports[0].port_name = name_client_port_a
    ods.client_ports[0].port_description = f"{ods.service_name} remote:{device_b.fqdn} {name_client_port_b}"
    ods.client_ports[0].optical_device = sub_device_a.optical_device

    ods.client_ports[1].port_name = name_client_port_b
    ods.client_ports[1].port_description = f"{ods.service_name} remote:{device_a.fqdn} {name_client_port_a}"
    ods.client_ports[1].optical_device = sub_device_b.optical_device

    for i in range(len(och_ids)):
        existing_channels = subscription_instances_by_block_type_and_resource_value(
            product_block_type="OpticalTransportChannel",
            resource_type="och_id",
            resource_value=str(och_ids[i]),
        )
        if len(existing_channels) > 1:
            msg = f"Found multiple active transport channels with OCh ID {och_ids[i]}"
            raise ValueError(msg)
        if len(existing_channels) == 1:
            block = OpticalTransportChannelBlock.from_db(existing_channels[0].subscription_instance_id)
            if i == 0:
                ods.transport_channels[i] = block
            else:
                ods.transport_channels.append(block)
            continue

        if len(ods.transport_channels) < i + 1:
            ods.transport_channels.append(
                OpticalTransportChannelBlockInactive.new(subscription_id=subscription.subscription_id)
            )
        channel = ods.transport_channels[i]
        channel.och_id = och_ids[i]
        channel.central_frequency = frequencies[i]
        channel.mode = mode
        channel.line_ports[0] = OpticalDevicePortBlock.from_db(line_ports_a[i])
        channel.line_ports[1] = OpticalDevicePortBlock.from_db(line_ports_b[i])

        optical_spectrum = channel.optical_spectrum
        optical_spectrum.spectrum_name = f"OCh{och_ids[i]:03d} {code_pop_a}-{code_pop_b}"
        optical_spectrum.passband = (
            frequencies[i] - bandwidths[i] // 2,
            frequencies[i] + bandwidths[i] // 2,
        )
        constraints = optical_spectrum.optical_spectrum_path_constraints
        for sub_id in exclude_devices_list:
            sub = OpticalDevice.from_subscription(sub_id)
            constraints.exclude_nodes.append(sub.optical_device)
        for sub_id in exclude_fibers_list:
            sub = OpticalFiber.from_subscription(sub_id)
            constraints.exclude_spans.append(sub.optical_fiber)

    owner_ids = [ch.owner_subscription_id for ch in ods.transport_channels]
    if len(set(owner_ids)) != 1:
        msg = (
            "The provided OCh IDs correspond to *uncoupled* optical transport channels. "
            "A digital service can only be transported over one channel or two coupled channels."
        )
        raise ValueError(msg)

    return {
        "subscription": subscription,
        "subscription_id": subscription.subscription_id,  # necessary to be able to use older generic step functions
    }


@step("Dividing the optical path into single-device-family sections")
def divide_path_into_sections(
    subscription: OpticalDigitalServiceInactive,
    optical_path: list[UUIDstr],
    line_ports_a: list[UUIDstr],
    line_ports_b: list[UUIDstr],
) -> State:
    if optical_path == ["direct_connection"]:
        # direct connection between transceivers without any managed line system in the middle
        return {
            "subscription": subscription,
        }

    ods = subscription.optical_digital_service
    channels = ods.transport_channels
    optical_spectrum = channels[0].optical_spectrum
    store_list_of_ports_into_spectrum_sections(optical_path, optical_spectrum)

    if len(channels) == 2:
        optical_spectrum = channels[1].optical_spectrum
        first_add_drop_port, last_add_drop_port = find_add_drop_ports(
            line_ports_a[-1],
            line_ports_b[-1],
        )
        optical_path[0] = first_add_drop_port
        optical_path[-1] = last_add_drop_port
        store_list_of_ports_into_spectrum_sections(optical_path, optical_spectrum)

    return {
        "subscription": subscription,
    }


@step("Updating the subscription description")
def update_subscription_description(
    subscription: OpticalDigitalServiceProvisioning,
) -> State:
    subscription.description = subscription_description(subscription)
    return {
        "subscription_description": subscription.description,
        "subscription": subscription,
    }


@step("Configuring the line ports on the transponders/transceivers")
def configure_trx_line_side(subscription: OpticalDigitalServiceProvisioning) -> State:
    ods = subscription.optical_digital_service
    channels = ods.transport_channels

    descriptions = tuple(ch.optical_spectrum.spectrum_name for ch in channels)
    central_freqs = tuple(ch.central_frequency for ch in channels)
    modes = tuple(ch.mode for ch in channels)
    devices = tuple(port.optical_device for port in channels[0].line_ports)
    port_names = (
        tuple(ch.line_ports[0].port_name for ch in channels),
        tuple(ch.line_ports[1].port_name for ch in channels),
    )

    results = {}
    for i, device in enumerate(devices):
        results[device.fqdn] = configure_line_transceivers(device, port_names[i], central_freqs, modes, descriptions)

    return {
        "configuration_results": results,
    }


@step("Configuring the client ports on the transponders/transceivers")
def configure_trx_client_side(subscription: OpticalDigitalServiceProvisioning) -> State:
    ods = subscription.optical_digital_service
    results = {}
    for port in ods.client_ports:
        result_key = f"{port.optical_device.fqdn}"
        results[result_key] = configure_transceiver_client(
            port.optical_device, port.port_name, port.port_description, ods.service_type
        )

    return {
        "configuration_results": results,
    }


@step("Configuring the cross-connections in the transponders")
def configure_trx_crossconnects(
    subscription: OpticalDigitalServiceProvisioning,
) -> State:
    ods = subscription.optical_digital_service
    client_a, client_b = ods.client_ports
    channels = ods.transport_channels

    lines_a, lines_b = [], []
    for channel in channels:
        lines_a.append(channel.line_ports[0])
        lines_b.append(channel.line_ports[1])

    results = {}
    for pair in [(client_a, lines_a), (client_b, lines_b)]:
        client, lines = pair
        device = client.optical_device
        client = client.port_name
        for i in range(len(lines)):
            lines[i] = lines[i].port_name

        result_key = f"{device.fqdn}"
        results[result_key] = configure_transponder_crossconnect(
            device, client, lines, xconn_description=ods.service_name
        )

    return {
        "configuration_results": results,
        "subscription": subscription,
    }


@step("Provisioning optical spectrum sections")
def provision_optical_sections(
    subscription: OpticalDigitalServiceProvisioning,
) -> State:
    flow_id = subscription.optical_digital_service.flow_id
    client_id = subscription.optical_digital_service.client_id
    channels = subscription.optical_digital_service.transport_channels
    results = {}
    for channel in channels:
        passband = channel.optical_spectrum.passband
        spectrum_name = channel.optical_spectrum.spectrum_name
        port = channel.line_ports[0]
        carrier_width = get_signal_bandwidth(port.optical_device, port.port_name)
        carrier = (channel.central_frequency, carrier_width)
        for section in channel.optical_spectrum.optical_spectrum_sections:
            src_device = section.add_drop_ports[0].optical_device
            key = f"OCh{channel.och_id:03d} {src_device.platform}"
            results[key] = deploy_optical_circuit(
                src_device,
                section,
                spectrum_name,
                passband,
                carrier,
                label=f"f{flow_id:03d}c{client_id:02d}",
            )

    return {
        "configuration_results": results,
    }


@step("Appending service ID to label/description/tag of the optical spectrum sections")
def update_optical_spectrum_sections_label(
    subscription: OpticalDigitalServiceProvisioning,
) -> State:
    flow_id = subscription.optical_digital_service.flow_id
    client_id = subscription.optical_digital_service.client_id
    channels = subscription.optical_digital_service.transport_channels
    results = {}
    for channel in channels:
        passband = channel.optical_spectrum.passband
        spectrum_name = channel.optical_spectrum.spectrum_name
        for section in channel.optical_spectrum.optical_spectrum_sections:
            src_device = section.add_drop_ports[0].optical_device
            key = f"OCh{channel.och_id:03d} {src_device.platform}"
            results[key] = append_optical_circuit_label(
                src_device,
                section,
                spectrum_name,
                passband,
                label=f"f{flow_id:03d}c{client_id:02d}",
            )

    return {
        "configuration_results": results,
    }


@step("Updating the available passbands of any Open Line System port in the path")
def update_used_passbands_step(subscription: OpticalDigitalServiceProvisioning) -> State:
    spectrum = subscription.optical_digital_service.transport_channels[0].optical_spectrum
    update_used_passbands(spectrum)

    return {"subscription": subscription}


@step("Setting the transmitted optical power to match the line system target")
def set_trx_transmitted_power(
    subscription: OpticalDigitalServiceProvisioning,
) -> State:
    ods = subscription.optical_digital_service
    results = {}

    for channel in ods.transport_channels:
        line_ports = channel.line_ports
        optical_spectrum = channel.optical_spectrum
        spectrum_name = optical_spectrum.spectrum_name

        add_drop_ports: list[OpticalDevicePortBlock] = []
        for section in optical_spectrum.optical_spectrum_sections:
            section_platform = section.add_drop_ports[0].optical_device.platform
            if section_platform == Platform.FlexILS:
                add_drop_ports = section.add_drop_ports
                break

        if add_drop_ports == []:
            continue

        for i, trib_port in enumerate(add_drop_ports):
            db_from_target = diff_btw_current_rx_power_and_target(trib_port.optical_device, spectrum_name)

            min_acceptable_diff = 0.0
            max_acceptable_diff = 1.5
            if min_acceptable_diff <= db_from_target <= max_acceptable_diff:
                result_key = f"{trib_port.optical_device.fqdn} {trib_port.port_name}"
                results[result_key] = (
                    f"Received optical power is {db_from_target} dB from target. "
                    "Within margins. No need to adjust transmitted power."
                )
                continue

            trx_line_port = line_ports[i]
            trx = trx_line_port.optical_device
            trx_port_name = trx_line_port.port_name
            result_key = f"{trx.fqdn} {trx_port_name}"
            results[result_key] = allign_tx_power_to_target(trx, trx_port_name, db_from_target)

    return {
        "configuration_results": results,
    }


additional_steps = begin


@create_workflow(
    "Create optical_digital_service",
    initial_input_form=initial_input_form_generator,
    additional_steps=additional_steps,
)
def create_optical_digital_service() -> StepList:
    def are_channels_yet_to_be_provisioned(state: State) -> bool:
        subscription = state["subscription"]
        ods = subscription["optical_digital_service"]
        owner_id = ods["transport_channels"][0]["owner_subscription_id"]
        return subscription["subscription_id"] == owner_id

    return (
        begin
        >> construct_optical_digital_service_model
        >> store_process_subscription()
        >> conditional(are_channels_yet_to_be_provisioned)(divide_path_into_sections)
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> update_subscription_description
        >> conditional(are_channels_yet_to_be_provisioned)(configure_trx_line_side)
        >> configure_trx_client_side
        >> configure_trx_crossconnects
        >> conditional(are_channels_yet_to_be_provisioned)(provision_optical_sections)
        >> conditional(are_channels_yet_to_be_provisioned)(update_used_passbands_step)
        >> conditional(lambda state: not are_channels_yet_to_be_provisioned(state))(
            update_optical_spectrum_sections_label
        )
        >> conditional(are_channels_yet_to_be_provisioned)(step("Sleeping for 30 seconds")(lambda: sleep(30)))
        >> conditional(are_channels_yet_to_be_provisioned)(set_trx_transmitted_power)
    )
