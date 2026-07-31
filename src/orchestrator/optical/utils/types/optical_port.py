"""Annotated union types for Optical Ports."""

from typing import Annotated

from pydantic import Field

from orchestrator.optical.products.product_blocks.optical_coherent_pluggable import (
    OpticalCoherentPluggableBlock,
    OpticalCoherentPluggableBlockInactive,
    OpticalCoherentPluggableBlockProvisioning,
)
from orchestrator.optical.products.product_blocks.optical_port import (
    OlsAddDropPortBlock,
    OlsAddDropPortBlockInactive,
    OlsAddDropPortBlockProvisioning,
    OlsLinePortBlock,
    OlsLinePortBlockInactive,
    OlsLinePortBlockProvisioning,
    OpticalTransponderClientPortBlock,
    OpticalTransponderClientPortBlockInactive,
    OpticalTransponderClientPortBlockProvisioning,
    OpticalTransponderLinePortBlock,
    OpticalTransponderLinePortBlockInactive,
    OpticalTransponderLinePortBlockProvisioning,
)

OpticalPortBlockInactive = Annotated[
    OlsAddDropPortBlockInactive
    | OlsLinePortBlockInactive
    | OpticalTransponderClientPortBlockInactive
    | OpticalTransponderLinePortBlockInactive
    | OpticalCoherentPluggableBlockInactive,
    Field(discriminator="optical_port_role"),
]
OpticalPortBlockProvisioning = Annotated[
    OlsAddDropPortBlockProvisioning
    | OlsLinePortBlockProvisioning
    | OpticalTransponderClientPortBlockProvisioning
    | OpticalTransponderLinePortBlockProvisioning
    | OpticalCoherentPluggableBlockProvisioning,
    Field(discriminator="optical_port_role"),
]
OpticalPortBlock = Annotated[
    OlsAddDropPortBlock
    | OlsLinePortBlock
    | OpticalTransponderClientPortBlock
    | OpticalTransponderLinePortBlock
    | OpticalCoherentPluggableBlock,
    Field(discriminator="optical_port_role"),
]
