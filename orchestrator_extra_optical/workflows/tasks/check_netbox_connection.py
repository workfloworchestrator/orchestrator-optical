# Copyright 2025 GARR.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from orchestrator import workflow
from orchestrator.targets import Target
from orchestrator.workflow import StepList, done, init, step
from pydantic_forms.types import State
from structlog import get_logger

from services import netbox

logger = get_logger(__name__)


@step("Checking the connection to Netbox by login via API token and retrieving regions")
def check_netbox_conn() -> State:
    regions = netbox.api.dcim.regions.all()
    region_list = [region.name for region in regions]
    return {"netbox_api_version": netbox.api.version, "netbox_regions": region_list}


@workflow("Check Netbox connection", target=Target.SYSTEM)
def task_check_netbox_connection() -> StepList:
    return init >> check_netbox_conn >> done
