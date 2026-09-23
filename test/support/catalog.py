"""Consumer catalog seeding helper for the DB-backed execution tests.

A consumer keeps its own product type and workflows, so the execution tests must seed
them into the catalog after the shipped catalog has been provisioned. This module holds
that seeding as a reusable function: it inserts one product, one product block (which
depends on the shipped ``OpticalModuleLocationBlock``) and one workflow row per
``name -> target`` pair, exactly as the consumer execution test fixture does.
"""

from uuid import uuid4

from sqlalchemy.engine import Connection

from orchestrator.core.migrations.helpers import create as create_catalog
from orchestrator.core.migrations.helpers import create_workflow as create_workflow_row


def seed_consumer_catalog(
    conn: Connection,
    *,
    product_name: str,
    product_type: str,
    product_block_name: str,
    workflows: dict[str, str],
) -> None:
    """Seed a consumer product, its composing product block and its workflow rows.

    Args:
        conn: Database connection (as available inside an ``engine.begin()`` block).
        product_name: Name of the consumer product to create.
        product_type: Product type (subscription model class name) of the product.
        product_block_name: Name of the consumer product block to create; it depends on the
            shipped ``OpticalModuleLocationBlock``.
        workflows: Workflow rows to create, mapping workflow name to target name.
    """
    create_catalog(
        conn,
        {
            "products": {
                product_name: {
                    "product_id": str(uuid4()),
                    "product_type": product_type,
                    "description": product_name,
                    "tag": "consumer-router",
                    "status": "active",
                    "product_blocks": [product_block_name],
                },
            },
            "product_blocks": {
                product_block_name: {
                    "product_block_id": str(uuid4()),
                    "description": "Consumer-style block composing the shipped Optical Module Location block.",
                    "tag": "location-router",
                    "status": "active",
                    "depends_on_block_relations": ["OpticalModuleLocationBlock"],
                },
            },
        },
    )
    for name, target in workflows.items():
        create_workflow_row(
            conn,
            {
                "name": name,
                "target": target,
                "description": name,
                "product_type": product_type,
            },
        )
