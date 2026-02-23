# Copyright 2025 GARR.  # noqa: D100
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

from typing import Annotated, TypeAlias

from orchestrator.forms import FormPage
from orchestrator.targets import Target
from orchestrator.workflow import StepList, begin, done, step, workflow
from pydantic import Field, model_validator
from pydantic_forms.types import FormGenerator, State, UUIDstr
from pydantic_forms.validators import Choice
from structlog import get_logger

from products.product_blocks.optical_device import Platform
from products.product_types.optical_device import OpticalDevice
from products.services.optical_device import get_optical_device_client
from workflows.shared import active_subscription_with_instance_value_selector

logger = get_logger(__name__)

achtung = (
    "This workflow is intended for advanced users only.\n"
    "It allows you to execute TL1 commands on a FlexILS node.\n"
    "Please ensure you know what you are doing before proceeding.\n"
    "Write the secret passphrase in this text box to proceed.\n"
)
Achtung = Annotated[
    str,
    Field(
        achtung,
        title="ENTER PASSPHRASE 🗝️🤫",
        json_schema_extra={
            "format": "long",
        },
    ),
]

FlexILSChoice: TypeAlias = Choice  # noqa: UP040
flexils_choice: FlexILSChoice = active_subscription_with_instance_value_selector(
    product_type="OpticalDevice",
    resource_type="platform",
    value=Platform.FlexILS,
    prompt="Select a FlexILS node",
)

CommandsString = Annotated[
    str,
    Field(
        "RMV-SCH:flex.aa00:9-A-1-S20-1:asetag::;\n",
        title="Enter one TL1 command per line.",
        json_schema_extra={
            "format": "long",
        },
    ),
]

ErrorPolicyChoice: TypeAlias = Choice  # noqa: UP040
error_policy_choice: ErrorPolicyChoice = Choice(
    "Error Policy",
    {
        "ABORT": "ABORT",
        "CONTINUE": "CONTINUE",
    },
)


def initial_input_form_generator() -> FormGenerator:
    class Form0(FormPage):
        node_sub_id: flexils_choice
        commands_string: CommandsString
        error_policy: error_policy_choice
        achtung: Achtung

        @model_validator(mode="after")
        def validate_csv(self) -> "Form0":
            self._validate_confirmation()
            self._parse_validate_commands()

        def _validate_confirmation(self) -> None:
            if self.achtung != "gift-parka-snowplow":
                msg = "Wrong passphrase in ⚠️⚠️⚠️ ACHTUNG ⚠️⚠️⚠️ text box!"
                raise ValueError(msg)

        def _parse_validate_commands(self) -> None:
            commands = self.commands_string.strip().splitlines()
            if not commands:
                msg = "Empty TL1 command provided."
                raise ValueError(msg)
            for command in commands:
                if not command[0].isalpha():
                    msg = f"Invalid TL1 command: '{command}'. It must start with a letter."
                    raise ValueError(msg)
                if not command.endswith(";"):
                    msg = f"Invalid TL1 command: '{command}'. It must end with a semicolon."
                    raise ValueError(msg)
                min_colons_in_tl1_command = 5
                max_colons_in_tl1_command = 7
                if not min_colons_in_tl1_command <= command.count(":") <= max_colons_in_tl1_command:
                    msg = (
                        f"Invalid TL1 command: '{command}'. It must contain between "
                        f"{min_colons_in_tl1_command} and {max_colons_in_tl1_command} colons (':')."
                        f" Found {command.count(':')} colons."
                    )
                    raise ValueError(msg)

    user_input = yield Form0
    user_input_dict = user_input.dict()
    return user_input_dict


@step("Saving input data in State")
def save_data(
    node_sub_id: UUIDstr,
    commands_string: str,
    error_policy: str,
) -> State:
    subscription = OpticalDevice.from_subscription(node_sub_id)
    commands = commands_string.strip().splitlines()
    return {
        "subscription": subscription,
        "commands": commands,
        "error_policy": error_policy,
    }


@step("Executing TL1 commands on FlexILS")
def execute_tl1_commands(
    subscription: OpticalDevice,
    commands: list[str],
    error_policy: str,
) -> State:
    flex = get_optical_device_client(subscription.optical_device)
    results = [flex.execute_raw_command(c) for c in commands]
    return {"results": results}


@workflow(
    "Execute a sequence of raw TL1 commands on a FlexILS node",
    target=Target.SYSTEM,
    initial_input_form=initial_input_form_generator,
)
def execute_tl1_commands_on_flexils() -> StepList:
    """Execute TL1 commands on FlexILS device."""
    return begin >> save_data >> execute_tl1_commands >> done
