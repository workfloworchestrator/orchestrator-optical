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

"""# Validate Optical Digital Service Workflow.

## At a Glance

**What**: Verifies that network device configurations match database records for an optical service.

**Traffic Impact**: ✅ **None** (read-only validation).

**Use When**: Need to verify service consistency after maintenance, troubleshooting, or as periodic audit.

**Duration**: 1-2 minutes total.

---

## What Gets Validated

| Component | What's Checked | Impact |
|-----------|----------------|--------|
| Transponder Line Ports | Frequencies, modes, laser status | ✅ None |
| Transponder Client Ports | Labels, FEC, port mode | ✅ None |
| Cross-Connects | Internal mappings, labels | ✅ None |
| ROADM Sections | Passbands, carriers, labels | ✅ None |

**All operations are read-only** - no configuration changes are made.

---

## Before Running

### Prerequisites
- [ ] Service exists and is in ACTIVE state
- [ ] Network devices are reachable
- [ ] No ongoing maintenance on devices

### What It Does NOT Do
- Does not fix misconfigurations (read-only)
- Does not modify any network devices
- Does not change database records
- Does not affect traffic in any way

---

## After Running

### Success Criteria
- All steps complete without errors
- Subscription description updated
- Configuration matches database expectations

### If Validation Fails

**Common Issues**:
- **Frequency mismatch**: Device frequency ≠ database → Manual reconciliation needed
- **Missing cross-connect**: Device XC not found → May need to re-run create workflow
- **ROADM filter mismatch**: OSNC passband incorrect → May need to re-run modify workflow
- **Label mismatch**: Descriptive labels don't match → Cosmetic only, low priority

**Next Steps**:
1. Review error message to identify which component failed
2. Manually fix the configuration on the device or in the database as needed
3. Re-run this validation workflow to confirm resolution

---

## Workflow Steps

This workflow executes 6 steps in sequence:

### Step 1: Load Initial State
**Function**: `load_initial_state_optical_digital_service()`
**What**: Retrieves subscription from database
**Traffic Impact**: None (database read)

Loads the OpticalDigitalService subscription and prepares it for validation.

---

### Step 2: Update Subscription Description
**Function**: `update_subscription_description()`
**What**: Refreshes human-readable service description
**Traffic Impact**: None (database write)

Generates and saves description in format: "Site A <-> Site B (frequency info)".
This keeps the description field in sync with current configuration.

---

### Step 3: Verify Transponder Line Ports ✅
**Function**: `verify_trx_line_ports()`
**What**: Checks optical transmit/receive configuration
**Traffic Impact**: None (device read)

**Infinera Groove G30**:
- Queries OCh-OS (optical channel) configuration on each line port
- Validates TX/RX frequencies match database
- Verifies port mode (modulation format) is correct
- Checks laser is enabled and operational

**Infinera GX G42**:
- Queries super-channel configuration
- Validates carrier frequencies match database
- Verifies carrier mode (modulation format)
- Checks optical-carrier resources are properly configured

**Compares**: Device frequencies and modes against `transport_channels[].central_frequency` and `transport_channels[].mode`.

---

### Step 4: Verify Transponder Client Ports ✅
**Function**: `verify_trx_client_ports()`
**What**: Checks Ethernet client port configuration
**Traffic Impact**: None (device read)

**Infinera Groove G30**:
- Queries Ethernet port configuration
- Validates service labels match port description
- Verifies Ethernet FEC is enabled
- Checks port mode (100GBE or 400GBE)

**Infinera GX G42**:
- Queries TOM (Transceiver Optical Module) configuration
- Validates trib-ptp (tributary) labels
- Verifies Ethernet and FEC settings

**Compares**: Device labels against `client_ports[].port_description` and validates service type.

---

### Step 5: Verify Transponder Cross-Connects ✅
**Function**: `verify_transponder_crossconnects()`
**What**: Validates internal mappings between client and line ports
**Traffic Impact**: None (device read)

**Infinera Groove G30**:
- Queries ODU cross-connects
- Validates mapping from client ports to line ports
- Checks service labels on cross-connects

**Infinera GX G42**:
- Queries XCON (cross-connection) between Ethernet and ODU
- Validates circuit-id-suffix and label fields

**Compares**: Device cross-connect configuration against expected client-to-line mappings with service name labels.

---

### Step 6: Verify Optical Spectrum Sections ✅
**Function**: `verify_optical_transport_channels()`
**What**: Validates ROADM configurations along optical path
**Traffic Impact**: None (device read)

**Infinera FlexILS**:
- Queries OSNC (Optical Supernode Connection) for each section
- Validates `passbandlist` matches expected frequency range
- Validates `carrierlist` includes correct center frequency and bandwidth
- Checks service label follows format: "f001c01+f002c02" (flow and client IDs)

**Groove G30 H4 links**:
- No validation needed (transparent fiber, no active devices)

**Compares**: Device OSNC configuration against `optical_spectrum.passband`, carrier frequency, and bandwidth from database.

---

## Validation Logic

Each validation step:
1. **Queries** device via NETCONF/RESTCONF API
2. **Extracts** relevant configuration data
3. **Compares** against database subscription model
4. **Raises exception** if mismatch found (fails workflow)
5. **Continues** to next step if match confirmed

**No automatic remediation** - workflow fails on first mismatch to alert operators.

---

<details>
<summary>Technical Reference</summary>

## Database Schema Validated

The workflow validates consistency between:
- `OpticalDigitalServiceBlock` (product block)
  - `transport_channels[]` (frequencies, modes, line ports)
  - `client_ports[]` (port names, descriptions)
  - `optical_spectrum.optical_spectrum_sections[]` (ROADM paths)

And device configurations across:
- Transponders (Infinera Groove G30, Infinera GX G42)
- ROADMs (Infinera FlexILS)

## Service Functions Called

- `validate_trx_line()`: Validates transponder line side configuration
- `validate_trx_client()`: Validates transponder client side configuration
- `validate_trx_crossconnect()`: Validates transponder internal cross-connects
- `validate_optical_circuit()`: Validates ROADM optical circuit configuration
- `get_signal_bandwidth()`: Retrieves carrier bandwidth from device
- `subscription_description()`: Generates human-readable description

## Label Format

OSNC labels follow the pattern: `f{flow_id:03d}c{client_id:02d}+f{flow_id:03d}c{client_id:02d}`

Example: `f001c01+f002c02` indicates two services sharing the spectrum.
Labels are sorted alphabetically and joined with `+`.

## Related Workflows

- **Create Optical Digital Service**: Initial service provisioning
- **Modify Optical Digital Service**: Change frequencies/modes (may require re-validation)
- **Terminate Optical Digital Service**: Service decommissioning

</details>
"""

from orchestrator.workflow import StepList, begin, step
from orchestrator.workflows.utils import validate_workflow
from pydantic_forms.types import State
from structlog import get_logger

from products.product_blocks.optical_digital_service import OpticalDigitalServiceBlock
from products.product_types.optical_digital_service import OpticalDigitalService
from products.services.optical_digital_service import (
    get_signal_bandwidth,
    validate_trx_client,
    validate_trx_crossconnect,
    validate_trx_line,
)
from products.services.optical_spectrum import validate_optical_circuit
from workflows.optical_digital_service.create_optical_digital_service import (
    subscription_description,
)

logger = get_logger(__name__)


@step("Loading initial state")
def load_initial_state_optical_digital_service(
    subscription: OpticalDigitalService,
) -> State:
    return {
        "subscription": subscription,
    }


@step("Updating the subscription description")
def update_subscription_description(
    subscription: OpticalDigitalService,
) -> State:
    subscription.description = subscription_description(subscription)
    return {
        "subscription_description": subscription.description,
    }


@step("Verifying transceiver/transponder line ports")
def verify_trx_line_ports(subscription: OpticalDigitalService) -> State:
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

    for i, device in enumerate(devices):
        validate_trx_line(device, port_names[i], central_freqs, modes, descriptions)

    return


@step("Verifying transceiver/transponder client ports")
def verify_trx_client_ports(subscription: OpticalDigitalService) -> State:
    ods = subscription.optical_digital_service

    for port in ods.client_ports:
        validate_trx_client(port.optical_device, port.port_name, port.port_description, ods.service_type)

    return


@step("Verifying transponder crossconnects")
def verify_transponder_crossconnects(subscription: OpticalDigitalService) -> State:
    ods = subscription.optical_digital_service
    client_a, client_b = ods.client_ports
    channels = ods.transport_channels

    lines_a, lines_b = [], []
    for channel in channels:
        lines_a.append(channel.line_ports[0])
        lines_b.append(channel.line_ports[1])

    for pair in [(client_a, lines_a), (client_b, lines_b)]:
        client, lines = pair
        device = client.optical_device
        client = client.port_name
        for i in range(len(lines)):
            lines[i] = lines[i].port_name

        validate_trx_crossconnect(device, client, lines, xconn_description=ods.service_name)

    return


@step("Verifying optical spectrum sections")
def verify_optical_transport_channels(subscription: OpticalDigitalService) -> State:
    channels = subscription.optical_digital_service.transport_channels

    label = []
    ch = channels[0]
    subscription_instances_using_channel = ch.in_use_by
    for si in subscription_instances_using_channel:
        ods = OpticalDigitalServiceBlock.from_db(si.subscription_instance_id)
        flow_id = ods.flow_id
        client_id = ods.client_id
        label.append(f"f{flow_id:03d}c{client_id:02d}")
    label = sorted(label)
    label = "+".join(label)

    for channel in channels:
        spectrum_name = channel.optical_spectrum.spectrum_name
        passband = channel.optical_spectrum.passband
        port = channel.line_ports[0]
        carrier_bandwidth = get_signal_bandwidth(port.optical_device, port.port_name)
        carrier_frequency = channel.central_frequency
        carrier = (carrier_frequency, carrier_bandwidth)

        for section in channel.optical_spectrum.optical_spectrum_sections:
            src_device = section.add_drop_ports[0].optical_device
            validate_optical_circuit(
                src_device,
                section,
                spectrum_name,
                passband,
                carrier,
                label,
            )

    return


@validate_workflow("validate optical digital service")
def validate_optical_digital_service() -> StepList:
    return (
        begin
        >> load_initial_state_optical_digital_service
        >> update_subscription_description
        >> verify_trx_line_ports
        >> verify_trx_client_ports
        >> verify_transponder_crossconnects
        >> verify_optical_transport_channels
    )
