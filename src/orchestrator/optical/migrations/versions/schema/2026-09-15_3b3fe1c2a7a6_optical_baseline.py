"""optical baseline

Revision ID: 3b3fe1c2a7a6
Revises: ca79fd834ba0
Create Date: 2026-09-15

"""

from uuid import uuid4

from alembic import op

from orchestrator.core.migrations.helpers import create, create_task, create_workflow, delete, delete_workflow

# revision identifiers, used by Alembic.
revision = "3b3fe1c2a7a6"
down_revision = "ca79fd834ba0"
branch_labels = None
depends_on = None

new_products = {
    "products": {
        "Cisco DP04QSDD HK9 Coherent Pluggable": {
            "product_id": uuid4(),
            "product_type": "OpticalCoherentPluggableSubscription",
            "description": "Cisco DP04QSDD HK9 Coherent Pluggable",
            "tag": "CISCO_DP04_QSDD_HK9_",
            "status": "active",
            "product_blocks": ["CoherentPluggableBlock"],
            "fixed_inputs": {"optical_coherent_pluggable_part_number": "CISCO QDD-400G-ZRP-S"},
        },
        "Cisco QDD 400G ZR+ Coherent Pluggable": {
            "product_id": uuid4(),
            "product_type": "OpticalCoherentPluggableSubscription",
            "description": "Cisco QDD 400G ZR+ Coherent Pluggable",
            "tag": "CISCO_QDD_400_G_ZR_C",
            "status": "active",
            "product_blocks": ["CoherentPluggableBlock"],
            "fixed_inputs": {"optical_coherent_pluggable_part_number": "CISCO QDD-400G-ZRP-S"},
        },
        "100G Ethernet Optical Digital Service": {
            "product_id": uuid4(),
            "product_type": "OpticalDigitalServiceSubscription",
            "description": "100G Ethernet Optical Digital Service",
            "tag": "100_G_ETHERNET_OPTIC",
            "status": "active",
            "product_blocks": ["OpticalDigitalServiceBlock"],
            "fixed_inputs": {
                "optical_digital_service_speed": "100",
                "optical_digital_service_type": "Ethernet",
            },
        },
        "400G Ethernet Optical Digital Service": {
            "product_id": uuid4(),
            "product_type": "OpticalDigitalServiceSubscription",
            "description": "400G Ethernet Optical Digital Service",
            "tag": "400_G_ETHERNET_OPTIC",
            "status": "active",
            "product_blocks": ["OpticalDigitalServiceBlock"],
            "fixed_inputs": {
                "optical_digital_service_speed": "400",
                "optical_digital_service_type": "Ethernet",
            },
        },
        "800G Ethernet Optical Digital Service": {
            "product_id": uuid4(),
            "product_type": "OpticalDigitalServiceSubscription",
            "description": "800G Ethernet Optical Digital Service",
            "tag": "800_G_ETHERNET_OPTIC",
            "status": "active",
            "product_blocks": ["OpticalDigitalServiceBlock"],
            "fixed_inputs": {
                "optical_digital_service_speed": "800",
                "optical_digital_service_type": "Ethernet",
            },
        },
        "Optical Fiber Patch": {
            "product_id": uuid4(),
            "product_type": "OpticalFiberPatchSubscription",
            "description": "Optical Fiber Patch",
            "tag": "OPTICAL_FIBER_PATCH",
            "status": "active",
            "product_blocks": ["FiberPatchBlock"],
        },
        "Optical Fiber Span": {
            "product_id": uuid4(),
            "product_type": "OpticalFiberSpanSubscription",
            "description": "Optical Fiber Span",
            "tag": "OPTICAL_FIBER_SPAN",
            "status": "active",
            "product_blocks": ["FiberSpanBlock"],
        },
        "Nokia FlexILS Optical Node": {
            "product_id": uuid4(),
            "product_type": "OpticalNodeNokiaFlexIlsSubscription",
            "description": "Nokia FlexILS Optical Node",
            "tag": "NOKIA_FLEX_ILS_OPTIC",
            "status": "active",
            "product_blocks": ["NokiaFlexIlsBlock"],
        },
        "Nokia Groove G30 Optical Node": {
            "product_id": uuid4(),
            "product_type": "OpticalNodeNokiaGrooveG30Subscription",
            "description": "Nokia Groove G30 Optical Node",
            "tag": "NOKIA_GROOVE_G30_OPT",
            "status": "active",
            "product_blocks": ["NokiaGrooveG30Block"],
        },
        "Nokia GX G42 Optical Node": {
            "product_id": uuid4(),
            "product_type": "OpticalNodeNokiaGxG42Subscription",
            "description": "Nokia GX G42 Optical Node",
            "tag": "NOKIA_GX_G42_OPTICAL",
            "status": "active",
            "product_blocks": ["NokiaGxG42Block"],
        },
        "Optical Leased Spectrum": {
            "product_id": uuid4(),
            "product_type": "OpticalLeasedSpectrumSubscription",
            "description": "Optical Leased Spectrum",
            "tag": "OPTICAL_LEASED_SPECT",
            "status": "active",
            "product_blocks": ["LeasedSpectrumBlock"],
        },
        "Optical Spectrum": {
            "product_id": uuid4(),
            "product_type": "OpticalSpectrumServiceSubscription",
            "description": "Optical Spectrum",
            "tag": "OPTICAL_SPECTRUM",
            "status": "active",
            "product_blocks": ["OpticalSpectrumServiceBlock"],
        },
        "Optical Module Location": {
            "product_id": uuid4(),
            "product_type": "OpticalModuleLocationSubscription",
            "description": "Optical Module Location",
            "tag": "OPTICAL_MODULE_LOCAT",
            "status": "active",
            "product_blocks": ["OpticalModuleLocationBlock"],
        },
        "Optical Module Packet Node": {
            "product_id": uuid4(),
            "product_type": "OpticalModulePacketNodeSubscription",
            "description": "Optical Module Packet Node",
            "tag": "OPTICAL_MODULE_PACKE",
            "status": "active",
            "product_blocks": ["OpticalModulePacketNode"],
        },
    },
    "product_blocks": {
        "OpticalModuleLocationBlock": {
            "product_block_id": uuid4(),
            "description": "A Location that hosts optical equipment.",
            "tag": "OPTICAL_MODULE_LOCAT",
            "status": "active",
            "resources": {
                "longitude": "Longitude",
                "latitude": "Latitude",
                "location_code": "Location Code",
                "location_name": "Location Name",
            },
        },
        "OpticalModuleNodeManagementBlock": {
            "product_block_id": uuid4(),
            "description": "Optical Module Node Management block that is active.",
            "tag": "OPTICAL_MODULE_NODE_",
            "status": "active",
            "resources": {
                "optical_module_node_vendor": "Optical Module Node Vendor",
                "optical_module_node_platform": "Optical Module Node Platform",
                "optical_module_node_software_version": "Optical Module Node Software Version",
                "optical_module_node_fqdn": "Optical Module Node Fqdn",
                "optical_module_node_dcn_loopback_ip": "Optical Module Node Dcn Loopback Ip",
                "optical_module_node_dcn_interface_ip": "Optical Module Node Dcn Interface Ip",
            },
        },
        "OpticalModulePacketNode": {
            "product_block_id": uuid4(),
            "description": "A packet layer Node that accepts Optical Coherent Pluggables.",
            "tag": "OPTICAL_MODULE_PACKE",
            "status": "active",
            "resources": {"optical_node_role": "Optical Node Role"},
            "depends_on_block_relations": ["OpticalModuleLocationBlock", "OpticalModuleNodeManagementBlock"],
        },
        "CoherentPluggableBlock": {
            "product_block_id": uuid4(),
            "description": "Base class for active CoherentPluggableBlock product blocks.",
            "tag": "COHERENT_PLUGGABLE_B",
            "status": "active",
            "resources": {
                "optical_port_role": "Optical Port Role",
                "optical_port_name": "Optical Port Name",
                "optical_port_description": "Optical Port Description",
                "optical_coherent_pluggable_firmware_version": "Optical Coherent Pluggable Firmware Version",
                "optical_coherent_pluggable_part_number": "Optical Coherent Pluggable Part Number",
            },
            "depends_on_block_relations": ["OpticalModulePacketNode"],
        },
        "NokiaGrooveG30Block": {
            "product_block_id": uuid4(),
            "description": "Product Block of a Nokia Groove G30 Optical Node that is active.",
            "tag": "NOKIA_GROOVE_G30_BLO",
            "status": "active",
            "resources": {"optical_node_role": "Optical Node Role"},
            "depends_on_block_relations": ["OpticalModuleLocationBlock", "OpticalModuleNodeManagementBlock"],
        },
        "NokiaGxG42Block": {
            "product_block_id": uuid4(),
            "description": "Product Block of a Nokia GX G42 Optical Node that is active.",
            "tag": "NOKIA_GX_G42_BLOCK",
            "status": "active",
            "resources": {"optical_node_role": "Optical Node Role"},
            "depends_on_block_relations": ["OpticalModuleLocationBlock", "OpticalModuleNodeManagementBlock"],
        },
        "OpticalTransponderClientPortBlock": {
            "product_block_id": uuid4(),
            "description": "Optical Transponder Client Port Product Block that is inactive.",
            "tag": "OPTICAL_TRANSPONDER_",
            "status": "active",
            "resources": {
                "optical_port_role": "Optical Port Role",
                "optical_port_name": "Optical Port Name",
                "optical_port_description": "Optical Port Description",
            },
            "depends_on_block_relations": ["NokiaGrooveG30Block", "NokiaGxG42Block"],
        },
        "NokiaFlexIlsBlock": {
            "product_block_id": uuid4(),
            "description": "Product Block of a Nokia FlexILS Optical Node that is active.",
            "tag": "NOKIA_FLEX_ILS_BLOCK",
            "status": "active",
            "resources": {
                "optical_node_role": "Optical Node Role",
                "optical_flexils_gmpls_id": "Optical Flexils Gmpls Id",
                "optical_flexils_target_id": "Optical Flexils Target Id",
            },
            "depends_on_block_relations": ["OpticalModuleLocationBlock", "OpticalModuleNodeManagementBlock"],
        },
        "OlsAddDropPortBlock": {
            "product_block_id": uuid4(),
            "description": "OLS Add Drop Port Product Block that is inactive.",
            "tag": "OLS_ADD_DROP_PORT_BL",
            "status": "active",
            "resources": {
                "optical_port_role": "Optical Port Role",
                "optical_port_name": "Optical Port Name",
                "optical_port_description": "Optical Port Description",
                "optical_passbands": "Optical Passbands",
            },
            "depends_on_block_relations": ["NokiaFlexIlsBlock", "NokiaGrooveG30Block"],
        },
        "OlsLinePortBlock": {
            "product_block_id": uuid4(),
            "description": "OLS Add Drop Port Product Block that is inactive.",
            "tag": "OLS_LINE_PORT_BLOCK",
            "status": "active",
            "resources": {
                "optical_port_role": "Optical Port Role",
                "optical_port_name": "Optical Port Name",
                "optical_port_description": "Optical Port Description",
                "optical_passbands": "Optical Passbands",
            },
            "depends_on_block_relations": ["NokiaFlexIlsBlock", "NokiaGrooveG30Block"],
        },
        "OpticalSpectrumSectionBlock": {
            "product_block_id": uuid4(),
            "description": "Active state of an OpticalSpectrumSectionBlock product block.",
            "tag": "OPTICAL_SPECTRUM_SEC",
            "status": "active",
            "resources": {},
            "depends_on_block_relations": ["OlsAddDropPortBlock", "OlsLinePortBlock"],
        },
        "OpticalSpectrumServiceBlock": {
            "product_block_id": uuid4(),
            "description": "Active state of the Optical Spectrum product block.",
            "tag": "OPTICAL_SPECTRUM_SER",
            "status": "active",
            "resources": {
                "optical_spectrum_name": "Optical Spectrum Name",
                "optical_spectrum_passband": "Optical Spectrum Passband",
            },
            "depends_on_block_relations": ["OpticalSpectrumSectionBlock"],
        },
        "OpticalTransponderLinePortBlock": {
            "product_block_id": uuid4(),
            "description": "Optical Transponder Line Port Product Block that is inactive.",
            "tag": "OPTICAL_TRANSPONDER_",
            "status": "active",
            "resources": {
                "optical_port_role": "Optical Port Role",
                "optical_port_name": "Optical Port Name",
                "optical_port_description": "Optical Port Description",
            },
            "depends_on_block_relations": ["NokiaGrooveG30Block", "NokiaGxG42Block"],
        },
        "OpticalTransportChannelBlock": {
            "product_block_id": uuid4(),
            "description": "Active state of an Optical Transport Channel product block.",
            "tag": "OPTICAL_TRANSPORT_CH",
            "status": "active",
            "resources": {
                "optical_transport_channel_name": "Optical Transport Channel Name",
                "optical_transport_central_frequency": "Optical Transport Central Frequency",
                "optical_transport_mode": "Optical Transport Mode",
                "optical_transport_total_capacity": "Optical Transport Total Capacity",
            },
            "depends_on_block_relations": [
                "CoherentPluggableBlock",
                "OpticalSpectrumServiceBlock",
                "OpticalTransponderLinePortBlock",
            ],
        },
        "OpticalDigitalServiceBlock": {
            "product_block_id": uuid4(),
            "description": "Active state of an Optical Digital Service product block.",
            "tag": "OPTICAL_DIGITAL_SERV",
            "status": "active",
            "resources": {
                "optical_digital_service_name": "Optical Digital Service Name",
                "optical_digital_service_speed": "Optical Digital Service Speed",
                "optical_digital_service_type": "Optical Digital Service Type",
            },
            "depends_on_block_relations": [
                "CoherentPluggableBlock",
                "OpticalTransponderClientPortBlock",
                "OpticalTransportChannelBlock",
            ],
        },
        "FiberPatchBlock": {
            "product_block_id": uuid4(),
            "description": "Active state of a Fiber Patch product block.",
            "tag": "FIBER_PATCH_BLOCK",
            "status": "active",
            "resources": {"optical_pipe_type": "Optical Pipe Type", "optical_pipe_name": "Optical Pipe Name"},
            "depends_on_block_relations": [
                "CoherentPluggableBlock",
                "OlsAddDropPortBlock",
                "OpticalTransponderClientPortBlock",
                "OpticalTransponderLinePortBlock",
            ],
        },
        "FiberSpanBlock": {
            "product_block_id": uuid4(),
            "description": "Active state of a Fiber Span product block.",
            "tag": "FIBER_SPAN_BLOCK",
            "status": "active",
            "resources": {"optical_pipe_type": "Optical Pipe Type", "optical_pipe_name": "Optical Pipe Name"},
            "depends_on_block_relations": [
                "CoherentPluggableBlock",
                "OlsLinePortBlock",
                "OpticalTransponderLinePortBlock",
            ],
        },
        "LeasedSpectrumBlock": {
            "product_block_id": uuid4(),
            "description": "Active state of a Leased Spectrum product block.",
            "tag": "LEASED_SPECTRUM_BLOC",
            "status": "active",
            "resources": {"optical_pipe_type": "Optical Pipe Type", "optical_pipe_name": "Optical Pipe Name"},
            "depends_on_block_relations": [
                "CoherentPluggableBlock",
                "OlsAddDropPortBlock",
                "OlsLinePortBlock",
                "OpticalTransponderLinePortBlock",
            ],
        },
    },
}

new_workflows = [
    {
        "name": "create_optical_coherent_pluggable",
        "target": "CREATE",
        "description": "create optical coherent pluggable",
        "product_type": "OpticalCoherentPluggableSubscription",
    },
    {
        "name": "modify_optical_coherent_pluggable",
        "target": "MODIFY",
        "description": "modify optical coherent pluggable",
        "product_type": "OpticalCoherentPluggableSubscription",
    },
    {
        "name": "terminate_optical_coherent_pluggable",
        "target": "TERMINATE",
        "description": "terminate optical coherent pluggable",
        "product_type": "OpticalCoherentPluggableSubscription",
    },
    {
        "name": "validate_optical_coherent_pluggable",
        "target": "VALIDATE",
        "description": "validate optical coherent pluggable",
        "product_type": "OpticalCoherentPluggableSubscription",
    },
    {
        "name": "create_optical_digital_service",
        "target": "CREATE",
        "description": "create optical digital service",
        "product_type": "OpticalDigitalServiceSubscription",
    },
    {
        "name": "modify_optical_digital_service",
        "target": "MODIFY",
        "description": "modify optical digital service",
        "product_type": "OpticalDigitalServiceSubscription",
    },
    {
        "name": "reconcile_optical_digital_service",
        "target": "RECONCILE",
        "description": "reconcile optical digital service",
        "product_type": "OpticalDigitalServiceSubscription",
    },
    {
        "name": "terminate_optical_digital_service",
        "target": "TERMINATE",
        "description": "terminate optical digital service",
        "product_type": "OpticalDigitalServiceSubscription",
    },
    {
        "name": "validate_optical_digital_service",
        "target": "VALIDATE",
        "description": "validate optical digital service",
        "product_type": "OpticalDigitalServiceSubscription",
    },
    {
        "name": "create_fiber_patch",
        "target": "CREATE",
        "description": "create optical fiber patch",
        "product_type": "OpticalFiberPatchSubscription",
    },
    {
        "name": "modify_fiber_patch",
        "target": "MODIFY",
        "description": "modify optical fiber patch",
        "product_type": "OpticalFiberPatchSubscription",
    },
    {
        "name": "reconcile_fiber_patch",
        "target": "RECONCILE",
        "description": "reconcile optical fiber patch",
        "product_type": "OpticalFiberPatchSubscription",
    },
    {
        "name": "terminate_fiber_patch",
        "target": "TERMINATE",
        "description": "terminate optical fiber patch",
        "product_type": "OpticalFiberPatchSubscription",
    },
    {
        "name": "validate_fiber_patch",
        "target": "VALIDATE",
        "description": "validate optical fiber patch",
        "product_type": "OpticalFiberPatchSubscription",
    },
    {
        "name": "create_fiber_span",
        "target": "CREATE",
        "description": "create optical fiber span",
        "product_type": "OpticalFiberSpanSubscription",
    },
    {
        "name": "modify_fiber_span",
        "target": "MODIFY",
        "description": "modify optical fiber span",
        "product_type": "OpticalFiberSpanSubscription",
    },
    {
        "name": "reconcile_fiber_span",
        "target": "RECONCILE",
        "description": "reconcile optical fiber span",
        "product_type": "OpticalFiberSpanSubscription",
    },
    {
        "name": "terminate_fiber_span",
        "target": "TERMINATE",
        "description": "terminate optical fiber span",
        "product_type": "OpticalFiberSpanSubscription",
    },
    {
        "name": "validate_fiber_span",
        "target": "VALIDATE",
        "description": "validate optical fiber span",
        "product_type": "OpticalFiberSpanSubscription",
    },
    {
        "name": "create_leased_spectrum",
        "target": "CREATE",
        "description": "create optical leased spectrum",
        "product_type": "OpticalLeasedSpectrumSubscription",
    },
    {
        "name": "modify_leased_spectrum",
        "target": "MODIFY",
        "description": "modify optical leased spectrum",
        "product_type": "OpticalLeasedSpectrumSubscription",
    },
    {
        "name": "reconcile_leased_spectrum",
        "target": "RECONCILE",
        "description": "reconcile optical leased spectrum",
        "product_type": "OpticalLeasedSpectrumSubscription",
    },
    {
        "name": "terminate_leased_spectrum",
        "target": "TERMINATE",
        "description": "terminate optical leased spectrum",
        "product_type": "OpticalLeasedSpectrumSubscription",
    },
    {
        "name": "validate_leased_spectrum",
        "target": "VALIDATE",
        "description": "validate optical leased spectrum",
        "product_type": "OpticalLeasedSpectrumSubscription",
    },
    {
        "name": "create_optical_module_location",
        "target": "CREATE",
        "description": "create optical module location",
        "product_type": "OpticalModuleLocationSubscription",
    },
    {
        "name": "modify_optical_module_location",
        "target": "MODIFY",
        "description": "modify optical module location",
        "product_type": "OpticalModuleLocationSubscription",
    },
    {
        "name": "terminate_optical_module_location",
        "target": "TERMINATE",
        "description": "terminate optical module location",
        "product_type": "OpticalModuleLocationSubscription",
    },
    {
        "name": "validate_optical_module_location",
        "target": "VALIDATE",
        "description": "validate optical module location",
        "product_type": "OpticalModuleLocationSubscription",
    },
    {
        "name": "create_optical_node_nokia_flexils",
        "target": "CREATE",
        "description": "create Nokia FlexILS optical node",
        "product_type": "OpticalNodeNokiaFlexIlsSubscription",
    },
    {
        "name": "modify_optical_node_nokia_flexils",
        "target": "MODIFY",
        "description": "modify Nokia FlexILS optical node",
        "product_type": "OpticalNodeNokiaFlexIlsSubscription",
    },
    {
        "name": "terminate_optical_node_nokia_flexils",
        "target": "TERMINATE",
        "description": "terminate Nokia FlexILS optical node",
        "product_type": "OpticalNodeNokiaFlexIlsSubscription",
    },
    {
        "name": "validate_optical_node_nokia_flexils",
        "target": "VALIDATE",
        "description": "validate Nokia FlexILS optical node",
        "product_type": "OpticalNodeNokiaFlexIlsSubscription",
    },
    {
        "name": "create_optical_node_nokia_groove_g30",
        "target": "CREATE",
        "description": "create Nokia Groove G30 optical node",
        "product_type": "OpticalNodeNokiaGrooveG30Subscription",
    },
    {
        "name": "modify_optical_node_nokia_groove_g30",
        "target": "MODIFY",
        "description": "modify Nokia Groove G30 optical node",
        "product_type": "OpticalNodeNokiaGrooveG30Subscription",
    },
    {
        "name": "terminate_optical_node_nokia_groove_g30",
        "target": "TERMINATE",
        "description": "terminate Nokia Groove G30 optical node",
        "product_type": "OpticalNodeNokiaGrooveG30Subscription",
    },
    {
        "name": "validate_optical_node_nokia_groove_g30",
        "target": "VALIDATE",
        "description": "validate Nokia Groove G30 optical node",
        "product_type": "OpticalNodeNokiaGrooveG30Subscription",
    },
    {
        "name": "create_optical_node_nokia_gx_g42",
        "target": "CREATE",
        "description": "create Nokia GX G42 optical node",
        "product_type": "OpticalNodeNokiaGxG42Subscription",
    },
    {
        "name": "modify_optical_node_nokia_gx_g42",
        "target": "MODIFY",
        "description": "modify Nokia GX G42 optical node",
        "product_type": "OpticalNodeNokiaGxG42Subscription",
    },
    {
        "name": "terminate_optical_node_nokia_gx_g42",
        "target": "TERMINATE",
        "description": "terminate Nokia GX G42 optical node",
        "product_type": "OpticalNodeNokiaGxG42Subscription",
    },
    {
        "name": "validate_optical_node_nokia_gx_g42",
        "target": "VALIDATE",
        "description": "validate Nokia GX G42 optical node",
        "product_type": "OpticalNodeNokiaGxG42Subscription",
    },
    {
        "name": "create_optical_spectrum",
        "target": "CREATE",
        "description": "create optical spectrum service",
        "product_type": "OpticalSpectrumServiceSubscription",
    },
    {
        "name": "modify_optical_spectrum",
        "target": "MODIFY",
        "description": "modify optical spectrum service",
        "product_type": "OpticalSpectrumServiceSubscription",
    },
    {
        "name": "reconcile_optical_spectrum",
        "target": "RECONCILE",
        "description": "reconcile optical spectrum service",
        "product_type": "OpticalSpectrumServiceSubscription",
    },
    {
        "name": "terminate_optical_spectrum",
        "target": "TERMINATE",
        "description": "terminate optical spectrum service",
        "product_type": "OpticalSpectrumServiceSubscription",
    },
    {
        "name": "validate_optical_spectrum",
        "target": "VALIDATE",
        "description": "validate optical spectrum service",
        "product_type": "OpticalSpectrumServiceSubscription",
    },
]

new_tasks = [
    {"name": "bulk_create_optical_nodes", "description": "bulk create optical nodes from CSV"},
    {"name": "bulk_create_optical_pipes", "description": "bulk create optical pipes from CSV"},
]


def upgrade() -> None:
    conn = op.get_bind()
    create(conn, new_products)
    for workflow in new_workflows:
        create_workflow(conn, workflow)
    for task in new_tasks:
        create_task(conn, task)


def downgrade() -> None:
    conn = op.get_bind()
    for task in new_tasks:
        delete_workflow(conn, task["name"])
    for workflow in new_workflows:
        delete_workflow(conn, workflow["name"])
    delete(conn, new_products)
