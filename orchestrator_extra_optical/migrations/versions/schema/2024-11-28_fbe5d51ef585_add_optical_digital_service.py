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

"""Add optical_digital_service product.

Revision ID: fbe5d51ef585
Revises: 8c643e73b9a1
Create Date: 2024-11-28 19:30:49.209847

"""

from uuid import uuid4

from alembic import op
from orchestrator.migrations.helpers import (
    create,
    create_workflow,
    delete,
    delete_workflow,
    ensure_default_workflows,
)
from orchestrator.targets import Target

# revision identifiers, used by Alembic.
revision = "fbe5d51ef585"
down_revision = "8c643e73b9a1"
branch_labels = None
depends_on = None

new_products = {
    "products": {
        "optical_digital_service": {
            "product_id": uuid4(),
            "product_type": "OpticalDigitalService",
            "description": "A *digital* service offered by the optical network to its clients, e.g. 100GbE and 400GbE services.",
            "tag": "OPT_DIGI_SERVICE",
            "status": "active",
            "root_product_block": "OpticalDigitalService",
            "fixed_inputs": {},
        },
    },
    "product_blocks": {
        "OpticalTransportChannel": {
            "product_block_id": uuid4(),
            "description": "a Transport Channel supporting one, a part of, or more than one Optical Digital Service",
            "tag": "OPT_TRNSP_CH",
            "status": "active",
            "resources": {
                "och_id": "the optical channel ID",
                "central_frequency": "the central frequency in MHz of the optical channel",
                "mode": "the mode indentifying the baudrate, modulation, polarization and fec of the channel",
            },
            "depends_on_block_relations": [
                "OpticalSpectrum",
                "OpticalDevicePort",
            ],
        },
        "OpticalDigitalService": {
            "product_block_id": uuid4(),
            "description": "Main Product Block for an Optical Digital Service",
            "tag": "OPT_DIGI_SERVICE",
            "status": "active",
            "resources": {
                "service_name": "the service name",
                "service_type": "the digital service type offered by this Optical Digital Service",
                "flow_id": "an integer number identifying a set of optical channels with the same endpoints and path",
                "client_id": "integer number that identifies this service inside the Optical Channel(s) that transport it",
                "nms_uuid": "identifier of this service in the Network Management System",
            },
            "depends_on_block_relations": [
                "OpticalTransportChannel",
                "OpticalDevicePort",
            ],
        },
    },
    "workflows": {},
}

new_workflows = [
    {
        "name": "create_optical_digital_service",
        "target": Target.CREATE,
        "description": "Create optical_digital_service",
        "product_type": "OpticalDigitalService",
    },
    {
        "name": "modify_optical_digital_service",
        "target": Target.MODIFY,
        "description": "modify optical digital service",
        "product_type": "OpticalDigitalService",
    },
    {
        "name": "terminate_optical_digital_service",
        "target": Target.TERMINATE,
        "description": "terminate optical digital service",
        "product_type": "OpticalDigitalService",
    },
    {
        "name": "validate_optical_digital_service",
        "target": Target.SYSTEM,
        "description": "validate optical digital service",
        "product_type": "OpticalDigitalService",
    },
]


def upgrade() -> None:
    conn = op.get_bind()
    create(conn, new_products)
    for workflow in new_workflows:
        create_workflow(conn, workflow)
    ensure_default_workflows(conn)


def downgrade() -> None:
    conn = op.get_bind()
    for workflow in new_workflows:
        delete_workflow(conn, workflow["name"])

    delete(conn, new_products)
