"""Union types for Optical Port Product Blocks."""

from typing import Annotated

from pydantic import Field

from orchestrator.optical.products.product_blocks.optical_coherent_pluggable import (
    OpticalCoherentPluggableBlock,
    OpticalCoherentPluggableBlockInactive,
    OpticalCoherentPluggableBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_port.ols_add_drop import (
    OlsAddDropPortBlock,
    OlsAddDropPortBlockInactive,
    OlsAddDropPortBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_port.ols_line import (
    OlsLinePortBlock,
    OlsLinePortBlockInactive,
    OlsLinePortBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_port.transponder_client import (
    OpticalTransponderClientPortBlock,
    OpticalTransponderClientPortBlockInactive,
    OpticalTransponderClientPortBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_port.transponder_line import (
    OpticalTransponderLinePortBlock,
    OpticalTransponderLinePortBlockInactive,
    OpticalTransponderLinePortBlockProvisioning,
)

PatchPortBlockInactive = Annotated[
    OpticalTransponderClientPortBlockInactive
    | OpticalTransponderLinePortBlockInactive
    | OlsAddDropPortBlockInactive
    | OpticalCoherentPluggableBlockInactive,
    Field(discriminator="optical_port_role"),
]
PatchPortBlockProvisioning = Annotated[
    OpticalTransponderClientPortBlockProvisioning
    | OpticalTransponderLinePortBlockProvisioning
    | OlsAddDropPortBlockProvisioning
    | OpticalCoherentPluggableBlockProvisioning,
    Field(discriminator="optical_port_role"),
]
PatchPortBlock = Annotated[
    OpticalTransponderClientPortBlock
    | OpticalTransponderLinePortBlock
    | OlsAddDropPortBlock
    | OpticalCoherentPluggableBlock,
    Field(discriminator="optical_port_role"),
]

SpanPortBlockInactive = Annotated[
    OlsLinePortBlockInactive
    | OpticalTransponderLinePortBlockInactive
    | OpticalCoherentPluggableBlockInactive,
    Field(discriminator="optical_port_role"),
]
SpanPortBlockProvisioning = Annotated[
    OlsLinePortBlockProvisioning
    | OpticalTransponderLinePortBlockProvisioning
    | OpticalCoherentPluggableBlockProvisioning,
    Field(discriminator="optical_port_role"),
]
SpanPortBlock = Annotated[
    OlsLinePortBlock | OpticalTransponderLinePortBlock | OpticalCoherentPluggableBlock,
    Field(discriminator="optical_port_role"),
]

LeasedSpectrumPortBlockInactive = Annotated[
    OpticalTransponderLinePortBlockInactive
    | OlsAddDropPortBlockInactive
    | OlsLinePortBlockInactive
    | OpticalCoherentPluggableBlockInactive,
    Field(discriminator="optical_port_role"),
]

LeasedSpectrumPortBlockProvisioning = Annotated[
    OpticalTransponderLinePortBlockProvisioning
    | OlsAddDropPortBlockProvisioning
    | OlsLinePortBlockProvisioning
    | OpticalCoherentPluggableBlockProvisioning,
    Field(discriminator="optical_port_role"),
]

LeasedSpectrumPortBlock = Annotated[
    OpticalTransponderLinePortBlock | OlsAddDropPortBlock | OlsLinePortBlock | OpticalCoherentPluggableBlock,
    Field(discriminator="optical_port_role"),
]

OpticalTransportLineChannelBlockInactive = Annotated[
    OpticalTransponderLinePortBlockInactive | OpticalCoherentPluggableBlockInactive,
    Field(discriminator="optical_port_role"),
]

OpticalTransportLineChannelBlockProvisioning = Annotated[
    OpticalTransponderLinePortBlockProvisioning | OpticalCoherentPluggableBlockProvisioning,
    Field(discriminator="optical_port_role"),
]

OpticalTransportLineChannelBlock = Annotated[
    OpticalTransponderLinePortBlock | OpticalCoherentPluggableBlock,
    Field(discriminator="optical_port_role"),
]

OpticalDigitalServiceClientPortBlockInactive = Annotated[
    OpticalTransponderClientPortBlockInactive | OpticalCoherentPluggableBlockInactive,
    Field(discriminator="optical_port_role"),
]

OpticalDigitalServiceClientPortBlockProvisioning = Annotated[
    OpticalTransponderClientPortBlockProvisioning | OpticalCoherentPluggableBlockProvisioning,
    Field(discriminator="optical_port_role"),
]

OpticalDigitalServiceClientPortBlock = Annotated[
    OpticalTransponderClientPortBlock | OpticalCoherentPluggableBlock, Field(discriminator="optical_port_role")
]
