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

"""Add optical_spectrum product.

Revision ID: 8c643e73b9a1
Revises: 33f1d689a836
Create Date: 2024-11-28 19:25:44.150149

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
revision = "8c643e73b9a1"
down_revision = "33f1d689a836"
branch_labels = None
depends_on = None

new_products = {
    "products": {
        "optical_spectrum": {
            "product_id": uuid4(),
            "product_type": "OpticalSpectrum",
            "description": "product of an all-optical pipe connecting two add-drop ports on two distant optical devices. Optical signals flow transparently into this pipe without ever being demodulated.",
            "tag": "OPTICAL_SPECTRUM",
            "status": "active",
            "root_product_block": "OpticalSpectrum",
            "fixed_inputs": {},
        },
    },
    "product_blocks": {
        "OpticalSpectrumSection": {
            "product_block_id": uuid4(),
            "description": "a section of an optical spectrum service traversing only optical devices belonging to the same family, e.g. spectra between H1 and H4 nodes have 2 sections (G30, FlexILS)",
            "tag": "OPTIC_SPECTR_SECT",
            "status": "active",
            "resources": {},
            "depends_on_block_relations": [
                "OpticalDevicePort",
            ],
        },
        "OpticalSpectrumPathConstraints": {
            "product_block_id": uuid4(),
            "description": "constraints for the path to be taken by an optical spectrum service",
            "tag": "OPT_SPTR_PATH_CNSTR",
            "status": "active",
            "resources": {},
            "depends_on_block_relations": [
                "OpticalDevice",
                "OpticalFiber",
            ],
        },
        "OpticalSpectrum": {
            "product_block_id": uuid4(),
            "description": "product block of an all-optical pipe connecting two add-drop ports on two distant optical devices. Optical signals flow transparently into this pipe without ever being demodulated.",
            "tag": "OPTICAL_SPECTRUM",
            "status": "active",
            "resources": {
                "spectrum_name": "this optical spectrum name",
                "passband": "the minimum and maximum frequencies in MHz of this optical spectrum",
            },
            "depends_on_block_relations": [
                "OpticalSpectrumPathConstraints",
                "OpticalSpectrumSection",
            ],
        },
    },
    "workflows": {},
}

new_workflows = [
    {
        "name": "create_optical_spectrum",
        "target": Target.CREATE,
        "description": "create optical spectrum service",
        "product_type": "OpticalSpectrum",
    },
    {
        "name": "modify_optical_spectrum",
        "target": Target.MODIFY,
        "description": "modify optical spectrum service",
        "product_type": "OpticalSpectrum",
    },
    {
        "name": "terminate_optical_spectrum",
        "target": Target.TERMINATE,
        "description": "terminate optical spectrum service",
        "product_type": "OpticalSpectrum",
    },
    {
        "name": "validate_optical_spectrum",
        "target": Target.SYSTEM,
        "description": "validate optical spectrum service",
        "product_type": "OpticalSpectrum",
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
