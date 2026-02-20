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

"""# Modify Optical Digital Service Workflow.

## At a Glance

**What**: Reconfigures optical frequencies, bandwidths, and modulation modes on an active service.

**Traffic Impact**: ⚠️ **up to 5 min service interruption** without failures.

**Use When**: Need to change frequencies, passbands, and/or modulation format.

**Cannot Change**: Physical ports, optical routing, or number of carriers.

**Duration**: 2-3 minutes total (with no failures).

---

## When Traffic Drops

| Step | When | Impact | Duration |
|------|------|--------|----------|
| Step 3 | Transponder line ports reconfigured | ⚠️ **Traffic drops** | 5-30 sec |
| Step 6 | ROADMs reconfigured (if FlexILS in path) | ⚠️ **May drop briefly** | 30-90 sec |

**Action**: Schedule during maintenance window for production services.

---

## What You Can Modify

| Parameter | Modifiable | Notes |
|-----------|------------|-------|
| Central frequencies | ✅ Yes | Must be ITU-T grid (6.25 GHz increments) |
| Spectral bandwidth | ✅ Yes | Must be 12.5 GHz increments |
| Modulation mode | ✅ Yes | All carriers must use same mode |
| Number of carriers | ❌ No | Cannot switch 1↔2 carriers |
| Client ports | ❌ No | Endpoints are fixed |
| Line ports | ❌ No | Cannot change which ports |
| Optical path | ❌ No | Route through network is fixed |

---

## Before Running

### Pre-Flight Checklist
- [ ] Maintenance window scheduled
- [ ] New frequencies don't conflict with other services on same fiber
- [ ] Check telemetry for existing service (power levels, BER)

### Constraints
- All carriers in the service must use the **same modulation mode**
- Cannot switch between single-carrier and dual-carrier configurations
- Path routing cannot be changed (to be implemented in future)

### Rollback
**Manual only** - re-run this workflow with the original frequency/mode values.

---

## After Running

### Validation Checklist
- [ ] Optical power levels normal at all transponders
- [ ] Pre-FEC BER below acceptable threshold
- [ ] No alarms on transponders or ROADMs
- [ ] Traffic flowing end-to-end

### Troubleshooting

**If traffic doesn't come back up**:
1. Check super-channel power levels along the path
2. Check cross-connections/services related alarms on transponders

**If workflow fails mid-execution**:
- Database changes persist even if network config fails
- Partial configurations may remain on devices
- Check error message for which step failed
- May need manual cleanup on affected devices

---

## Workflow Steps

This workflow executes 7 steps in sequence:

### Step 1: Input Form
**Function**: `initial_input_form_generator()`
**What**: User selects new frequencies, bandwidths, and mode
**Traffic Impact**: None (read-only)

Retrieves current service configuration and presents a form with:
- Current frequencies pre-filled (can be modified)
- Current bandwidths pre-filled (can be modified)
- Current mode pre-filled (can be modified)

Validates that frequencies are 6.25 GHz multiples and bandwidths are 12.5 GHz multiples.
Shows before/after comparison for user confirmation.

---

### Step 2: Update Database
**Function**: `update_subscription()`
**What**: Saves new parameters to database
**Traffic Impact**: None (database only)

- Stores old frequencies and passbands (for reference)
- Updates database with new frequencies, bandwidths, and mode
- Calculates new passbands: `[freq - bw/2, freq + bw/2]`
- Does **not** touch any network devices yet

---

### Step 3: Configure Transponder Line Side ⚠️
**Function**: `configure_trx_line_side()`
**What**: Reconfigures optical transmit/receive frequencies
**Traffic Impact**: ⚠️ **Traffic drops here (5-30 seconds)**

**Infinera Groove G30**:
- Modifies och-os (optical channel) on each line port
- Sets new TX/RX frequencies
- Changes port mode (modulation format)
- Enables laser and sets admin status UP

**Infinera GX G42**:
- Reconfigures super-channel with new carrier frequencies
- Updates carrier mode (modulation format)
- Sets optical-carrier resources to new frequencies
- Unlocks all components

**This is when lasers retune and traffic drops.**

---

### Step 4: Configure Transponder Client Side
**Function**: `configure_trx_client_side()`
**What**: Updates client Ethernet port labels and settings
**Traffic Impact**: Minimal (typically hitless)

**Infinera Groove G30**:
- Updates service labels on client ports
- Confirms Ethernet FEC is enabled
- Verifies port mode (100GBE or 400GBE)

**Infinera GX G42**:
- Updates TOM (Transceiver Optical Module) labels
- Updates trib-ptp (tributary) labels
- Confirms Ethernet and FEC settings

**Usually no traffic impact (metadata updates).**

---

### Step 5: Configure Cross-Connects
**Function**: `configure_trx_crossconnects()`
**What**: Updates internal transponder cross-connect labels
**Traffic Impact**: None (metadata only)

**Infinera Groove G30**:
- Finds ODU cross-connects between client and line ports
- Updates service labels

**Infinera GX G42**:
- Finds XCON between Ethernet and ODU
- Updates label and circuit-id-suffix

**No network impact (label updates only).**

---

### Step 6: Reconfigure ROADMs ⚠️
**Function**: `modify_optical_sections()`
**What**: Updates ROADM filters to pass new frequencies
**Traffic Impact**: ⚠️ **May cause brief interruption (30-90 sec)**

**Infinera FlexILS (if ROADMs in path)**:

1. Finds existing OSNC (Optical Supernode Connection) by spectrum name
2. Checks if OEL (path) needs updating
3. Takes OSNC Out-Of-Service
4. Updates OSNC configuration:
   - `passbandlist`: New frequency range
   - `carrierlist`: New center frequency and bandwidth
   - `label`: Service identifier
5. Returns OSNC to In-Service
6. **Opens shutters** on both source and destination ROADMs

**Groove G30 H4 links**:
- No action needed (transparent fiber connection)

**This reconfigures wavelength filters across entire path.**

---

### Step 7: Set Status Active
**Function**: `set_status(SubscriptionLifecycle.ACTIVE)`
**What**: Marks service as active in database
**Traffic Impact**: None (database only)

Final step updates subscription lifecycle to ACTIVE.

---

"""

from time import sleep
from typing import Annotated

from orchestrator.forms import FormPage
from orchestrator.forms.validators import choice_list, unique_conlist
from orchestrator.types import SubscriptionLifecycle
from orchestrator.workflow import StepList, begin, step
from orchestrator.workflows.steps import set_status
from orchestrator.workflows.utils import modify_workflow
from pydantic import Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from structlog import get_logger

from products.product_blocks.optical_digital_service import OpticalDigitalServiceBlock
from products.product_types.optical_digital_service import (
    OpticalDigitalService,
    OpticalDigitalServiceProvisioning,
)
from products.services.optical_digital_service import (
    get_signal_bandwidth,
)
from products.services.optical_spectrum import (
    modify_optical_circuit,
)
from utils.custom_types.frequencies import Bandwidth, Frequency, Passband
from workflows.optical_device.shared import (
    transceiver_mode_selector,
)
from workflows.optical_digital_service.create_optical_digital_service import (
    configure_trx_client_side,
    configure_trx_crossconnects,
    configure_trx_line_side,
    set_trx_transmitted_power,
)
from workflows.shared import (
    summary_form,
)

logger = get_logger(__name__)


def initial_input_form_generator(subscription_id: UUIDstr) -> FormGenerator:
    subscription = OpticalDigitalService.from_subscription(subscription_id)
    ods = subscription.optical_digital_service

    transport_channels = ods.transport_channels
    num_carriers = len(transport_channels)
    old_frequencies = [ch.central_frequency for ch in transport_channels]
    old_passbands = [ch.optical_spectrum.passband for ch in transport_channels]
    old_bandwidths = [end - start for start, end in old_passbands]
    old_mode = transport_channels[0].mode

    source_client_port = ods.client_ports[0]
    source_device = source_client_port.optical_device

    FrequenciesChoice = Annotated[
        unique_conlist(Frequency, min_items=num_carriers, max_items=num_carriers),
        Field(title="Central frequency (MHz) of each optical carrier"),
    ]

    BandwidthsChoice = Annotated[
        choice_list(Bandwidth, min_items=num_carriers, max_items=num_carriers, unique_items=False),
        Field(title="Spectral width (MHz), including guardbands, reserved for each transport channel"),
    ]

    ModeChoice = transceiver_mode_selector(
        optical_device_subscription_id=source_device.owner_subscription_id,
        port_name=source_client_port.port_name,
        prompt="Select the operating mode of all transport channels",
    )

    class ModifyOpticalDigitalServiceForm(FormPage):
        class Config:
            title = "Optical Transport Channels"

        frequencies: FrequenciesChoice = old_frequencies
        bandwidths: BandwidthsChoice = old_bandwidths
        mode: ModeChoice = old_mode

        @model_validator(mode="after")
        def validate_data(self) -> "ModifyOpticalDigitalServiceForm":
            for f in self.frequencies:
                if f % 6_250 != 0:
                    msg = "Frequency must be a multiple of 6_250 MHz"
                    raise ValueError(msg)
            for bw in self.bandwidths:
                if bw % 12_500 != 0:
                    msg = "Bandwidth must be a multiple of 12_500 MHz"
                    raise ValueError(msg)
            return self

    user_input = yield ModifyOpticalDigitalServiceForm
    user_input_dict = user_input.dict()

    summary_fields = ["frequencies", "bandwidths", "mode"]
    before = [str(x) for x in (old_frequencies, old_bandwidths, old_mode)]
    after = [str(user_input_dict[nm]) for nm in summary_fields]
    yield from summary_form(
        subscription.product.name,
        {
            "labels": summary_fields,
            "headers": ["Before", "After"],
            "columns": [before, after],
        },
    )

    return user_input_dict | {"subscription": subscription}


@step("Saving new values in the database")
def update_subscription(
    subscription: OpticalDigitalServiceProvisioning,
    frequencies: list[Frequency],
    bandwidths: list[Passband],
    mode: str,
) -> State:
    ods = subscription.optical_digital_service
    old_frequencies: list[Frequency] = []
    old_passbands: list[Passband] = []
    for channel in ods.transport_channels:
        old_frequencies.append(channel.central_frequency)
        channel.central_frequency = frequencies.pop(0)
        old_passbands.append(channel.optical_spectrum.passband)
        bw = bandwidths.pop(0)
        channel.optical_spectrum.passband = (
            channel.central_frequency - bw // 2,
            channel.central_frequency + bw // 2,
        )
        channel.mode = mode

    return {"subscription": subscription, "old_frequencies": old_frequencies, "old_passbands": old_passbands}


@step("Modifying optical spectrum sections")
def modify_optical_sections(
    subscription: OpticalDigitalServiceProvisioning,
) -> State:
    channels = subscription.optical_digital_service.transport_channels

    label = ""
    ch = channels[0]
    subscription_instances_using_channel = ch.in_use_by
    for si in subscription_instances_using_channel:
        ods = OpticalDigitalServiceBlock.from_db(si.subscription_instance_id)
        flow_id = ods.flow_id
        client_id = ods.client_id
        label += f"f{flow_id:03d}c{client_id:02d}+"
    label = label.strip("+")

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
            results[key] = modify_optical_circuit(
                src_device,
                section,
                spectrum_name,
                passband,
                carrier,
                label=label,
            )

    return {
        "configuration_results": results,
        "subscription": subscription,
    }


additional_steps = begin


@modify_workflow(
    "modify optical digital service",
    initial_input_form=initial_input_form_generator,
    additional_steps=additional_steps,
)
def modify_optical_digital_service() -> StepList:
    return (
        begin
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> update_subscription
        >> configure_trx_line_side
        >> configure_trx_client_side
        >> configure_trx_crossconnects
        >> modify_optical_sections
        >> step("Sleeping for 10 seconds")(lambda: sleep(10))
        >> set_trx_transmitted_power
        >> set_status(SubscriptionLifecycle.ACTIVE)
    )
