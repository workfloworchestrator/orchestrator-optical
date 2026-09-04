"""optical baseline

Revision ID: 263aedd1b28d
Revises: ca79fd834ba0
Create Date: 2026-09-04

"""
from alembic import op

from orchestrator.core.migrations.helpers import create, create_workflow, delete, delete_workflow

# revision identifiers, used by Alembic.
revision = '263aedd1b28d'
down_revision = 'ca79fd834ba0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    create(conn, {
        "products": {
            "Cisco DP04QSDD HK9 Coherent Pluggable": {
                "product_id": "32183c75-8eb4-513d-b476-b2732d98cb8c",
                "product_type": "OpticalCoherentPluggable",
                "description": "Cisco DP04QSDD HK9 Coherent Pluggable",
                "tag": "CISCO_DP04_QSDD_HK9_",
                "status": "active",
                "product_blocks": [
                    "CoherentPluggableBlock"
                ],
                "fixed_inputs": {
                    "optical_coherent_pluggable_part_number": "CISCO QDD-400G-ZRP-S"
                }
            },
            "Cisco QDD 400G ZR+ Coherent Pluggable": {
                "product_id": "f171d241-e35c-55bc-b10c-7cce850598eb",
                "product_type": "OpticalCoherentPluggable",
                "description": "Cisco QDD 400G ZR+ Coherent Pluggable",
                "tag": "CISCO_QDD_400_G_ZR_C",
                "status": "active",
                "product_blocks": [
                    "CoherentPluggableBlock"
                ],
                "fixed_inputs": {
                    "optical_coherent_pluggable_part_number": "CISCO QDD-400G-ZRP-S"
                }
            },
            "100G Ethernet Optical Digital Service": {
                "product_id": "6e891792-2bf8-59ce-9744-3efd8bfe7d05",
                "product_type": "OpticalDigitalService",
                "description": "100G Ethernet Optical Digital Service",
                "tag": "100_G_ETHERNET_OPTIC",
                "status": "active",
                "product_blocks": [
                    "OpticalDigitalServiceBlock"
                ],
                "fixed_inputs": {
                    "optical_digital_service_speed": "100",
                    "optical_digital_service_type": "Ethernet"
                }
            },
            "400G Ethernet Optical Digital Service": {
                "product_id": "b3a92f9d-57e3-5273-ae34-28e52579aafa",
                "product_type": "OpticalDigitalService",
                "description": "400G Ethernet Optical Digital Service",
                "tag": "400_G_ETHERNET_OPTIC",
                "status": "active",
                "product_blocks": [
                    "OpticalDigitalServiceBlock"
                ],
                "fixed_inputs": {
                    "optical_digital_service_speed": "100",
                    "optical_digital_service_type": "Ethernet"
                }
            },
            "800G Ethernet Optical Digital Service": {
                "product_id": "de0e0e28-6078-58ee-9c49-1c63df688c87",
                "product_type": "OpticalDigitalService",
                "description": "800G Ethernet Optical Digital Service",
                "tag": "800_G_ETHERNET_OPTIC",
                "status": "active",
                "product_blocks": [
                    "OpticalDigitalServiceBlock"
                ],
                "fixed_inputs": {
                    "optical_digital_service_speed": "100",
                    "optical_digital_service_type": "Ethernet"
                }
            },
            "Optical Fiber Patch": {
                "product_id": "58c713f7-cdf2-50ef-82ae-d45790c0a79e",
                "product_type": "OpticalFiberPatchSubscription",
                "description": "Optical Fiber Patch",
                "tag": "OPTICAL_FIBER_PATCH",
                "status": "active",
                "product_blocks": [
                    "FiberPatchBlock"
                ]
            },
            "Optical Fiber Span": {
                "product_id": "f71b8ebc-20e7-5857-9e59-1dcbb557a434",
                "product_type": "OpticalFiberSpanSubscription",
                "description": "Optical Fiber Span",
                "tag": "OPTICAL_FIBER_SPAN",
                "status": "active",
                "product_blocks": [
                    "FiberSpanBlock"
                ]
            },
            "Nokia FlexILS Optical Node": {
                "product_id": "e0c15bd6-578f-5c29-98f8-0c0866001326",
                "product_type": "OpticalNodeNokiaFlexIls",
                "description": "Nokia FlexILS Optical Node",
                "tag": "NOKIA_FLEX_ILS_OPTIC",
                "status": "active",
                "product_blocks": [
                    "NokiaFlexIlsBlock"
                ]
            },
            "Nokia Groove G30 Optical Node": {
                "product_id": "52667c13-3ab0-5272-8a5a-e3ffe2f634a8",
                "product_type": "OpticalNodeNokiaGrooveG30",
                "description": "Nokia Groove G30 Optical Node",
                "tag": "NOKIA_GROOVE_G30_OPT",
                "status": "active",
                "product_blocks": [
                    "NokiaGrooveG30Block"
                ]
            },
            "Nokia GX G42 Optical Node": {
                "product_id": "5245a251-5893-577b-b294-8fd31fc236ac",
                "product_type": "OpticalNodeNokiaGxG42",
                "description": "Nokia GX G42 Optical Node",
                "tag": "NOKIA_GX_G42_OPTICAL",
                "status": "active",
                "product_blocks": [
                    "NokiaGxG42Block"
                ]
            },
            "Optical Leased Spectrum": {
                "product_id": "9c0f4750-5b1b-5f3d-b4c5-5054b192860d",
                "product_type": "OpticalLeasedSpectrumSubscription",
                "description": "Optical Leased Spectrum",
                "tag": "OPTICAL_LEASED_SPECT",
                "status": "active",
                "product_blocks": [
                    "LeasedSpectrumBlock"
                ]
            },
            "Optical Spectrum": {
                "product_id": "d94b809c-bbe2-55cc-9fa7-efb210f07e74",
                "product_type": "OpticalSpectrum",
                "description": "Optical Spectrum",
                "tag": "OPTICAL_SPECTRUM",
                "status": "active",
                "product_blocks": [
                    "OpticalSpectrumBlock"
                ]
            },
            "Optical Module Location": {
                "product_id": "6da3eea2-abbb-5971-ac96-6049ee55e393",
                "product_type": "OpticalModuleLocationSubscription",
                "description": "Optical Module Location",
                "tag": "OPTICAL_MODULE_LOCAT",
                "status": "active",
                "product_blocks": [
                    "OpticalModuleLocationBlock"
                ]
            },
            "Optical Module Packet Node": {
                "product_id": "38e0a8e2-96ec-506f-a2a4-95fa0e11a91e",
                "product_type": "OpticalModulePacketNodeSubscription",
                "description": "Optical Module Packet Node",
                "tag": "OPTICAL_MODULE_PACKE",
                "status": "active",
                "product_blocks": [
                    "OpticalModulePacketNode"
                ]
            }
        },
        "product_blocks": {
            "OpticalModuleLocationBlock": {
                "product_block_id": "e90ba4df-5c8f-5b22-a142-6a5df10a11a7",
                "description": "A Location that hosts optical equipment.",
                "tag": "OPTICAL_MODULE_LOCAT",
                "status": "active",
                "resources": {
                    "longitude": "Longitude",
                    "latitude": "Latitude",
                    "location_code": "Location Code",
                    "location_name": "Location Name"
                }
            },
            "OpticalModuleNodeManagementBlock": {
                "product_block_id": "a7c14fac-ad34-56e8-a57d-c4623e28a4cd",
                "description": "Optical Module Node Management block that is active.",
                "tag": "OPTICAL_MODULE_NODE_",
                "status": "active",
                "resources": {
                    "optical_module_node_vendor": "Optical Module Node Vendor",
                    "optical_module_node_platform": "Optical Module Node Platform",
                    "optical_module_node_software_version": "Optical Module Node Software Version",
                    "optical_module_node_fqdn": "Optical Module Node Fqdn",
                    "optical_module_node_dcn_loopback_ip": "Optical Module Node Dcn Loopback Ip",
                    "optical_module_node_dcn_interface_ip": "Optical Module Node Dcn Interface Ip"
                }
            },
            "OpticalModulePacketNode": {
                "product_block_id": "1b2b1c01-c02a-5045-b288-7889f0053c4b",
                "description": "A packet layer Node that accepts Optical Coherent Pluggables.",
                "tag": "OPTICAL_MODULE_PACKE",
                "status": "active",
                "resources": {
                    "optical_node_role": "Optical Node Role"
                },
                "depends_on_block_relations": [
                    "OpticalModuleLocationBlock",
                    "OpticalModuleNodeManagementBlock"
                ]
            },
            "CoherentPluggableBlock": {
                "product_block_id": "d068889c-9d53-5f5a-949e-0418a816d7b7",
                "description": "Base class for active CoherentPluggableBlock product blocks.",
                "tag": "COHERENT_PLUGGABLE_B",
                "status": "active",
                "resources": {
                    "optical_port_role": "Optical Port Role",
                    "optical_port_name": "Optical Port Name",
                    "optical_port_description": "Optical Port Description",
                    "optical_coherent_pluggable_firmware_version": "Optical Coherent Pluggable Firmware Version",
                    "optical_coherent_pluggable_part_number": "Optical Coherent Pluggable Part Number"
                },
                "depends_on_block_relations": [
                    "OpticalModulePacketNode"
                ]
            },
            "NokiaGrooveG30Block": {
                "product_block_id": "4c15c3d5-ef18-5f56-8896-3d5be5a2885b",
                "description": "Product Block of a Nokia Groove G30 Optical Node that is active.",
                "tag": "NOKIA_GROOVE_G30_BLO",
                "status": "active",
                "resources": {
                    "optical_node_role": "Optical Node Role"
                },
                "depends_on_block_relations": [
                    "OpticalModuleLocationBlock",
                    "OpticalModuleNodeManagementBlock"
                ]
            },
            "NokiaGxG42Block": {
                "product_block_id": "dcc70084-42a2-52d8-9d35-a27311aec728",
                "description": "Product Block of a Nokia GX G42 Optical Node that is active.",
                "tag": "NOKIA_GX_G42_BLOCK",
                "status": "active",
                "resources": {
                    "optical_node_role": "Optical Node Role"
                },
                "depends_on_block_relations": [
                    "OpticalModuleLocationBlock",
                    "OpticalModuleNodeManagementBlock"
                ]
            },
            "OpticalTransponderClientPortBlock": {
                "product_block_id": "ece0ae5e-9f5c-5a04-8890-869e6b867fc5",
                "description": "Optical Transponder Client Port Product Block that is inactive.",
                "tag": "OPTICAL_TRANSPONDER_",
                "status": "active",
                "resources": {
                    "optical_port_role": "Optical Port Role",
                    "optical_port_name": "Optical Port Name",
                    "optical_port_description": "Optical Port Description"
                },
                "depends_on_block_relations": [
                    "NokiaGrooveG30Block",
                    "NokiaGxG42Block"
                ]
            },
            "NokiaFlexIlsBlock": {
                "product_block_id": "a8e2e178-ae48-5769-9d18-7224a88ea207",
                "description": "Product Block of a Nokia FlexILS Optical Node that is active.",
                "tag": "NOKIA_FLEX_ILS_BLOCK",
                "status": "active",
                "resources": {
                    "optical_node_role": "Optical Node Role",
                    "optical_flexils_gmpls_id": "Optical Flexils Gmpls Id",
                    "optical_flexils_target_id": "Optical Flexils Target Id"
                },
                "depends_on_block_relations": [
                    "OpticalModuleLocationBlock",
                    "OpticalModuleNodeManagementBlock"
                ]
            },
            "OlsAddDropPortBlock": {
                "product_block_id": "f51f4a05-45ec-5515-af98-6352ce6fb537",
                "description": "OLS Add Drop Port Product Block that is inactive.",
                "tag": "OLS_ADD_DROP_PORT_BL",
                "status": "active",
                "resources": {
                    "optical_port_role": "Optical Port Role",
                    "optical_port_name": "Optical Port Name",
                    "optical_port_description": "Optical Port Description",
                    "optical_passbands": "Optical Passbands"
                },
                "depends_on_block_relations": [
                    "NokiaFlexIlsBlock",
                    "NokiaGrooveG30Block"
                ]
            },
            "OlsLinePortBlock": {
                "product_block_id": "44410078-b5ed-5336-b317-6c10abc083bd",
                "description": "OLS Add Drop Port Product Block that is inactive.",
                "tag": "OLS_LINE_PORT_BLOCK",
                "status": "active",
                "resources": {
                    "optical_port_role": "Optical Port Role",
                    "optical_port_name": "Optical Port Name",
                    "optical_port_description": "Optical Port Description",
                    "optical_passbands": "Optical Passbands"
                },
                "depends_on_block_relations": [
                    "NokiaFlexIlsBlock",
                    "NokiaGrooveG30Block"
                ]
            },
            "OpticalSpectrumSectionBlock": {
                "product_block_id": "4582b1fd-d5f3-53ee-bc2a-ec428a8a723b",
                "description": "Active state of an OpticalSpectrumSectionBlock product block.",
                "tag": "OPTICAL_SPECTRUM_SEC",
                "status": "active",
                "resources": {},
                "depends_on_block_relations": [
                    "OlsAddDropPortBlock",
                    "OlsLinePortBlock"
                ]
            },
            "OpticalSpectrumBlock": {
                "product_block_id": "163e7fed-c2e0-5102-906d-1cad2d967fac",
                "description": "Active state of the Optical Spectrum product block.",
                "tag": "OPTICAL_SPECTRUM_BLO",
                "status": "active",
                "resources": {
                    "optical_spectrum_name": "Optical Spectrum Name",
                    "optical_spectrum_passband": "Optical Spectrum Passband"
                },
                "depends_on_block_relations": [
                    "OpticalSpectrumSectionBlock"
                ]
            },
            "OpticalTransponderLinePortBlock": {
                "product_block_id": "e67f7e15-6aa2-5995-ae9d-e8d591ef1849",
                "description": "Optical Transponder Line Port Product Block that is inactive.",
                "tag": "OPTICAL_TRANSPONDER_",
                "status": "active",
                "resources": {
                    "optical_port_role": "Optical Port Role",
                    "optical_port_name": "Optical Port Name",
                    "optical_port_description": "Optical Port Description"
                },
                "depends_on_block_relations": [
                    "NokiaGrooveG30Block",
                    "NokiaGxG42Block"
                ]
            },
            "OpticalTransportChannelBlock": {
                "product_block_id": "24180b56-29fb-5670-bd42-93eeab994ad6",
                "description": "Active state of an Optical Transport Channel product block.",
                "tag": "OPTICAL_TRANSPORT_CH",
                "status": "active",
                "resources": {
                    "optical_transport_channel_name": "Optical Transport Channel Name",
                    "optical_transport_central_frequency": "Optical Transport Central Frequency",
                    "optical_transport_mode": "Optical Transport Mode"
                },
                "depends_on_block_relations": [
                    "CoherentPluggableBlock",
                    "OpticalSpectrumBlock",
                    "OpticalTransponderLinePortBlock"
                ]
            },
            "OpticalDigitalServiceBlock": {
                "product_block_id": "c384557b-c47d-5cc2-b685-74d72e748159",
                "description": "Active state of an Optical Digital Service product block.",
                "tag": "OPTICAL_DIGITAL_SERV",
                "status": "active",
                "resources": {
                    "optical_digital_service_name": "Optical Digital Service Name"
                },
                "depends_on_block_relations": [
                    "CoherentPluggableBlock",
                    "OpticalTransponderClientPortBlock",
                    "OpticalTransportChannelBlock"
                ]
            },
            "FiberPatchBlock": {
                "product_block_id": "71d2119f-9c18-5e1c-aa92-d4f8b20602b8",
                "description": "Active state of a Fiber Patch product block.",
                "tag": "FIBER_PATCH_BLOCK",
                "status": "active",
                "resources": {
                    "optical_pipe_type": "Optical Pipe Type",
                    "optical_pipe_name": "Optical Pipe Name"
                },
                "depends_on_block_relations": [
                    "CoherentPluggableBlock",
                    "OlsAddDropPortBlock",
                    "OpticalTransponderClientPortBlock",
                    "OpticalTransponderLinePortBlock"
                ]
            },
            "FiberSpanBlock": {
                "product_block_id": "217240e4-d756-53a0-a0fe-5b9bfacc6c6f",
                "description": "Active state of a Fiber Span product block.",
                "tag": "FIBER_SPAN_BLOCK",
                "status": "active",
                "resources": {
                    "optical_pipe_type": "Optical Pipe Type",
                    "optical_pipe_name": "Optical Pipe Name"
                },
                "depends_on_block_relations": [
                    "CoherentPluggableBlock",
                    "OlsLinePortBlock",
                    "OpticalTransponderLinePortBlock"
                ]
            },
            "LeasedSpectrumBlock": {
                "product_block_id": "05485d77-d27c-5ffe-a88c-ef146450d6a5",
                "description": "Active state of a Leased Spectrum product block.",
                "tag": "LEASED_SPECTRUM_BLOC",
                "status": "active",
                "resources": {
                    "optical_pipe_type": "Optical Pipe Type",
                    "optical_pipe_name": "Optical Pipe Name"
                },
                "depends_on_block_relations": [
                    "CoherentPluggableBlock",
                    "OlsAddDropPortBlock",
                    "OlsLinePortBlock",
                    "OpticalTransponderLinePortBlock"
                ]
            }
        }
    })
    create_workflow(conn, {
        "name": "create_optical_coherent_pluggable",
        "target": "CREATE",
        "description": "create optical coherent pluggable",
        "product_type": "OpticalCoherentPluggable"
    })
    create_workflow(conn, {
        "name": "modify_optical_coherent_pluggable",
        "target": "MODIFY",
        "description": "modify optical coherent pluggable",
        "product_type": "OpticalCoherentPluggable"
    })
    create_workflow(conn, {
        "name": "terminate_optical_coherent_pluggable",
        "target": "TERMINATE",
        "description": "terminate optical coherent pluggable",
        "product_type": "OpticalCoherentPluggable"
    })
    create_workflow(conn, {
        "name": "validate_optical_coherent_pluggable",
        "target": "VALIDATE",
        "description": "validate optical coherent pluggable",
        "product_type": "OpticalCoherentPluggable"
    })
    create_workflow(conn, {
        "name": "create_optical_digital_service",
        "target": "CREATE",
        "description": "create optical digital service",
        "product_type": "OpticalDigitalService"
    })
    create_workflow(conn, {
        "name": "modify_optical_digital_service",
        "target": "MODIFY",
        "description": "modify optical digital service",
        "product_type": "OpticalDigitalService"
    })
    create_workflow(conn, {
        "name": "terminate_optical_digital_service",
        "target": "TERMINATE",
        "description": "terminate optical digital service",
        "product_type": "OpticalDigitalService"
    })
    create_workflow(conn, {
        "name": "validate_optical_digital_service",
        "target": "VALIDATE",
        "description": "validate optical digital service",
        "product_type": "OpticalDigitalService"
    })
    create_workflow(conn, {
        "name": "create_fiber_patch",
        "target": "CREATE",
        "description": "create optical fiber patch",
        "product_type": "OpticalFiberPatchSubscription"
    })
    create_workflow(conn, {
        "name": "modify_fiber_patch",
        "target": "MODIFY",
        "description": "modify optical fiber patch",
        "product_type": "OpticalFiberPatchSubscription"
    })
    create_workflow(conn, {
        "name": "reconcile_fiber_patch",
        "target": "RECONCILE",
        "description": "reconcile optical fiber patch",
        "product_type": "OpticalFiberPatchSubscription"
    })
    create_workflow(conn, {
        "name": "terminate_fiber_patch",
        "target": "TERMINATE",
        "description": "terminate optical fiber patch",
        "product_type": "OpticalFiberPatchSubscription"
    })
    create_workflow(conn, {
        "name": "validate_fiber_patch",
        "target": "VALIDATE",
        "description": "validate optical fiber patch",
        "product_type": "OpticalFiberPatchSubscription"
    })
    create_workflow(conn, {
        "name": "create_fiber_span",
        "target": "CREATE",
        "description": "create optical fiber span",
        "product_type": "OpticalFiberSpanSubscription"
    })
    create_workflow(conn, {
        "name": "modify_fiber_span",
        "target": "MODIFY",
        "description": "modify optical fiber span",
        "product_type": "OpticalFiberSpanSubscription"
    })
    create_workflow(conn, {
        "name": "reconcile_fiber_span",
        "target": "RECONCILE",
        "description": "reconcile optical fiber span",
        "product_type": "OpticalFiberSpanSubscription"
    })
    create_workflow(conn, {
        "name": "terminate_fiber_span",
        "target": "TERMINATE",
        "description": "terminate optical fiber span",
        "product_type": "OpticalFiberSpanSubscription"
    })
    create_workflow(conn, {
        "name": "validate_fiber_span",
        "target": "VALIDATE",
        "description": "validate optical fiber span",
        "product_type": "OpticalFiberSpanSubscription"
    })
    create_workflow(conn, {
        "name": "create_leased_spectrum",
        "target": "CREATE",
        "description": "create optical leased spectrum",
        "product_type": "OpticalLeasedSpectrumSubscription"
    })
    create_workflow(conn, {
        "name": "modify_leased_spectrum",
        "target": "MODIFY",
        "description": "modify optical leased spectrum",
        "product_type": "OpticalLeasedSpectrumSubscription"
    })
    create_workflow(conn, {
        "name": "reconcile_leased_spectrum",
        "target": "RECONCILE",
        "description": "reconcile optical leased spectrum",
        "product_type": "OpticalLeasedSpectrumSubscription"
    })
    create_workflow(conn, {
        "name": "terminate_leased_spectrum",
        "target": "TERMINATE",
        "description": "terminate optical leased spectrum",
        "product_type": "OpticalLeasedSpectrumSubscription"
    })
    create_workflow(conn, {
        "name": "validate_leased_spectrum",
        "target": "VALIDATE",
        "description": "validate optical leased spectrum",
        "product_type": "OpticalLeasedSpectrumSubscription"
    })
    create_workflow(conn, {
        "name": "create_optical_module_location",
        "target": "CREATE",
        "description": "create optical module location",
        "product_type": "OpticalModuleLocationSubscription"
    })
    create_workflow(conn, {
        "name": "modify_optical_module_location",
        "target": "MODIFY",
        "description": "modify optical module location",
        "product_type": "OpticalModuleLocationSubscription"
    })
    create_workflow(conn, {
        "name": "terminate_optical_module_location",
        "target": "TERMINATE",
        "description": "terminate optical module location",
        "product_type": "OpticalModuleLocationSubscription"
    })
    create_workflow(conn, {
        "name": "validate_optical_module_location",
        "target": "VALIDATE",
        "description": "validate optical module location",
        "product_type": "OpticalModuleLocationSubscription"
    })
    create_workflow(conn, {
        "name": "create_optical_node_nokia_flexils",
        "target": "CREATE",
        "description": "create Nokia FlexILS optical node",
        "product_type": "OpticalNodeNokiaFlexIls"
    })
    create_workflow(conn, {
        "name": "modify_optical_node_nokia_flexils",
        "target": "MODIFY",
        "description": "modify Nokia FlexILS optical node",
        "product_type": "OpticalNodeNokiaFlexIls"
    })
    create_workflow(conn, {
        "name": "terminate_optical_node_nokia_flexils",
        "target": "TERMINATE",
        "description": "terminate Nokia FlexILS optical node",
        "product_type": "OpticalNodeNokiaFlexIls"
    })
    create_workflow(conn, {
        "name": "validate_optical_node_nokia_flexils",
        "target": "VALIDATE",
        "description": "validate Nokia FlexILS optical node",
        "product_type": "OpticalNodeNokiaFlexIls"
    })
    create_workflow(conn, {
        "name": "create_optical_node_nokia_groove_g30",
        "target": "CREATE",
        "description": "create Nokia Groove G30 optical node",
        "product_type": "OpticalNodeNokiaGrooveG30"
    })
    create_workflow(conn, {
        "name": "modify_optical_node_nokia_groove_g30",
        "target": "MODIFY",
        "description": "modify Nokia Groove G30 optical node",
        "product_type": "OpticalNodeNokiaGrooveG30"
    })
    create_workflow(conn, {
        "name": "terminate_optical_node_nokia_groove_g30",
        "target": "TERMINATE",
        "description": "terminate Nokia Groove G30 optical node",
        "product_type": "OpticalNodeNokiaGrooveG30"
    })
    create_workflow(conn, {
        "name": "validate_optical_node_nokia_groove_g30",
        "target": "VALIDATE",
        "description": "validate Nokia Groove G30 optical node",
        "product_type": "OpticalNodeNokiaGrooveG30"
    })
    create_workflow(conn, {
        "name": "create_optical_node_nokia_gx_g42",
        "target": "CREATE",
        "description": "create Nokia GX G42 optical node",
        "product_type": "OpticalNodeNokiaGxG42"
    })
    create_workflow(conn, {
        "name": "modify_optical_node_nokia_gx_g42",
        "target": "MODIFY",
        "description": "modify Nokia GX G42 optical node",
        "product_type": "OpticalNodeNokiaGxG42"
    })
    create_workflow(conn, {
        "name": "terminate_optical_node_nokia_gx_g42",
        "target": "TERMINATE",
        "description": "terminate Nokia GX G42 optical node",
        "product_type": "OpticalNodeNokiaGxG42"
    })
    create_workflow(conn, {
        "name": "validate_optical_node_nokia_gx_g42",
        "target": "VALIDATE",
        "description": "validate Nokia GX G42 optical node",
        "product_type": "OpticalNodeNokiaGxG42"
    })
    create_workflow(conn, {
        "name": "create_optical_spectrum",
        "target": "CREATE",
        "description": "create optical spectrum service",
        "product_type": "OpticalSpectrum"
    })
    create_workflow(conn, {
        "name": "modify_optical_spectrum",
        "target": "MODIFY",
        "description": "modify optical spectrum service",
        "product_type": "OpticalSpectrum"
    })
    create_workflow(conn, {
        "name": "terminate_optical_spectrum",
        "target": "TERMINATE",
        "description": "terminate optical spectrum service",
        "product_type": "OpticalSpectrum"
    })
    create_workflow(conn, {
        "name": "validate_optical_spectrum",
        "target": "VALIDATE",
        "description": "validate optical spectrum service",
        "product_type": "OpticalSpectrum"
    })


def downgrade() -> None:
    conn = op.get_bind()
    delete_workflow(conn, 'validate_optical_spectrum')
    delete_workflow(conn, 'terminate_optical_spectrum')
    delete_workflow(conn, 'modify_optical_spectrum')
    delete_workflow(conn, 'create_optical_spectrum')
    delete_workflow(conn, 'validate_optical_node_nokia_gx_g42')
    delete_workflow(conn, 'terminate_optical_node_nokia_gx_g42')
    delete_workflow(conn, 'modify_optical_node_nokia_gx_g42')
    delete_workflow(conn, 'create_optical_node_nokia_gx_g42')
    delete_workflow(conn, 'validate_optical_node_nokia_groove_g30')
    delete_workflow(conn, 'terminate_optical_node_nokia_groove_g30')
    delete_workflow(conn, 'modify_optical_node_nokia_groove_g30')
    delete_workflow(conn, 'create_optical_node_nokia_groove_g30')
    delete_workflow(conn, 'validate_optical_node_nokia_flexils')
    delete_workflow(conn, 'terminate_optical_node_nokia_flexils')
    delete_workflow(conn, 'modify_optical_node_nokia_flexils')
    delete_workflow(conn, 'create_optical_node_nokia_flexils')
    delete_workflow(conn, 'validate_optical_module_location')
    delete_workflow(conn, 'terminate_optical_module_location')
    delete_workflow(conn, 'modify_optical_module_location')
    delete_workflow(conn, 'create_optical_module_location')
    delete_workflow(conn, 'validate_leased_spectrum')
    delete_workflow(conn, 'terminate_leased_spectrum')
    delete_workflow(conn, 'reconcile_leased_spectrum')
    delete_workflow(conn, 'modify_leased_spectrum')
    delete_workflow(conn, 'create_leased_spectrum')
    delete_workflow(conn, 'validate_fiber_span')
    delete_workflow(conn, 'terminate_fiber_span')
    delete_workflow(conn, 'reconcile_fiber_span')
    delete_workflow(conn, 'modify_fiber_span')
    delete_workflow(conn, 'create_fiber_span')
    delete_workflow(conn, 'validate_fiber_patch')
    delete_workflow(conn, 'terminate_fiber_patch')
    delete_workflow(conn, 'reconcile_fiber_patch')
    delete_workflow(conn, 'modify_fiber_patch')
    delete_workflow(conn, 'create_fiber_patch')
    delete_workflow(conn, 'validate_optical_digital_service')
    delete_workflow(conn, 'terminate_optical_digital_service')
    delete_workflow(conn, 'modify_optical_digital_service')
    delete_workflow(conn, 'create_optical_digital_service')
    delete_workflow(conn, 'validate_optical_coherent_pluggable')
    delete_workflow(conn, 'terminate_optical_coherent_pluggable')
    delete_workflow(conn, 'modify_optical_coherent_pluggable')
    delete_workflow(conn, 'create_optical_coherent_pluggable')
    delete(conn, {
        "products": [
            "Cisco DP04QSDD HK9 Coherent Pluggable",
            "Cisco QDD 400G ZR+ Coherent Pluggable",
            "100G Ethernet Optical Digital Service",
            "400G Ethernet Optical Digital Service",
            "800G Ethernet Optical Digital Service",
            "Optical Fiber Patch",
            "Optical Fiber Span",
            "Nokia FlexILS Optical Node",
            "Nokia Groove G30 Optical Node",
            "Nokia GX G42 Optical Node",
            "Optical Leased Spectrum",
            "Optical Spectrum",
            "Optical Module Location",
            "Optical Module Packet Node"
        ],
        "product_blocks": [
            "OpticalModuleLocationBlock",
            "OpticalModuleNodeManagementBlock",
            "OpticalModulePacketNode",
            "CoherentPluggableBlock",
            "NokiaGrooveG30Block",
            "NokiaGxG42Block",
            "OpticalTransponderClientPortBlock",
            "NokiaFlexIlsBlock",
            "OlsAddDropPortBlock",
            "OlsLinePortBlock",
            "OpticalSpectrumSectionBlock",
            "OpticalSpectrumBlock",
            "OpticalTransponderLinePortBlock",
            "OpticalTransportChannelBlock",
            "OpticalDigitalServiceBlock",
            "FiberPatchBlock",
            "FiberSpanBlock",
            "LeasedSpectrumBlock"
        ]
    })
