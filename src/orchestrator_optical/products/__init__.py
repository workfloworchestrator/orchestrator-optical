"""Product Models for Optical services."""

# Copyright 2025-2026 GARR, GÉANT.
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
from orchestrator.domain import SUBSCRIPTION_MODEL_REGISTRY
from pydantic_forms.types import strEnum

from orchestrator_optical.products.product_types.optical_coherent_pluggable import OpticalCoherentPluggable
from orchestrator_optical.products.product_types.optical_digital_service import OpticalDigitalService
from orchestrator_optical.products.product_types.optical_location import AbstractOpticalLocation
from orchestrator_optical.products.product_types.optical_node.abstracts import AbstractOpticalNode
from orchestrator_optical.products.product_types.optical_node.nokia_flexils import OpticalNodeNokiaFlexIls
from orchestrator_optical.products.product_types.optical_node.nokia_groove_g30 import OpticalNodeNokiaGrooveG30
from orchestrator_optical.products.product_types.optical_node.nokia_gx_g42 import OpticalNodeNokiaGxG42
from orchestrator_optical.products.product_types.optical_packet_node import AbstractOpticalPacketNode
from orchestrator_optical.products.product_types.optical_pipe import (
    AbstractOpticalPipe,
    OpticalFiberPatch,
    OpticalFiberSpan,
    OpticalLeasedSpectrum,
)
from orchestrator_optical.products.product_types.optical_spectrum_service import OpticalSpectrum


class ProductName(strEnum):
    """An enumerator of all product names defined in `orchestrator-optical`."""

    OPTICAL_COHERENT_PLUGGABLE_CISCO_DP04QSDD_HK9 = "Cisco DP04QSDD HK9 Coherent Pluggable"
    OPTICAL_COHERENT_PLUGGABLE_CISCO_QDD_400G_ZRP_S = "Cisco QDD 400G ZR+ Coherent Pluggable"
    OPTICAL_DIGITAL_SERVICE_100G_ETHERNET = "100G Ethernet Optical Digital Service"
    OPTICAL_DIGITAL_SERVICE_400G_ETHERNET = "400G Ethernet Optical Digital Service"
    OPTICAL_DIGITAL_SERVICE_800G_ETHERNET = "800G Ethernet Optical Digital Service"
    OPTICAL_FIBER_PATCH = "Optical Fiber Patch"
    OPTICAL_FIBER_SPAN = "Optical Fiber Span"
    OPTICAL_NODE_NOKIA_FLEXILS = "Nokia FlexILS Optical Node"
    OPTICAL_NODE_NOKIA_GROOVE_G30 = "Nokia Groove G30 Optical Node"
    OPTICAL_NODE_NOKIA_GX_G42 = "Nokia GX G42 Optical Node"
    OPTICAL_LEASED_SPECTRUM = "Optical Leased Spectrum"
    OPTICAL_SPECTRUM = "Optical Spectrum"
    ABSTRACT_OPTICAL_LOCATION = "Abstract Optical Location"
    ABSTRACT_OPTICAL_PACKET_NODE = "Abstract Optical Packet Node"
    ABSTRACT_OPTICAL_NODE = "Abstract Optical Node"
    ABSTRACT_OPTICAL_PIPE = "Abstract Optical Pipe"


class ProductType(strEnum):
    """An enumerator of all available products in `orchestrator-optical`."""

    OPTICAL_COHERENT_PLUGGABLE_CISCO_DP04QSDD_HK9 = OpticalCoherentPluggable.__name__
    OPTICAL_COHERENT_PLUGGABLE_CISCO_QDD_400G_ZRP_S = OpticalCoherentPluggable.__name__
    OPTICAL_DIGITAL_SERVICE_100G_ETHERNET = OpticalDigitalService.__name__
    OPTICAL_DIGITAL_SERVICE_400G_ETHERNET = OpticalDigitalService.__name__
    OPTICAL_DIGITAL_SERVICE_800G_ETHERNET = OpticalDigitalService.__name__
    OPTICAL_FIBER_PATCH = OpticalFiberPatch.__name__
    OPTICAL_FIBER_SPAN = OpticalFiberSpan.__name__
    OPTICAL_NODE_NOKIA_FLEXILS = OpticalNodeNokiaFlexIls.__name__
    OPTICAL_NODE_NOKIA_GROOVE_G30 = OpticalNodeNokiaGrooveG30.__name__
    OPTICAL_NODE_NOKIA_GX_G42 = OpticalNodeNokiaGxG42.__name__
    OPTICAL_LEASED_SPECTRUM = OpticalLeasedSpectrum.__name__
    OPTICAL_SPECTRUM = OpticalSpectrum.__name__
    ABSTRACT_OPTICAL_LOCATION = AbstractOpticalLocation.__name__
    ABSTRACT_OPTICAL_PACKET_NODE = AbstractOpticalPacketNode.__name__
    ABSTRACT_OPTICAL_NODE = AbstractOpticalNode.__name__
    ABSTRACT_OPTICAL_PIPE = AbstractOpticalPipe.__name__


SUBSCRIPTION_MODEL_REGISTRY.update(
    {
        ProductName.OPTICAL_COHERENT_PLUGGABLE_CISCO_DP04QSDD_HK9.value: OpticalCoherentPluggable,
        ProductName.OPTICAL_COHERENT_PLUGGABLE_CISCO_QDD_400G_ZRP_S.value: OpticalCoherentPluggable,
        ProductName.OPTICAL_DIGITAL_SERVICE_100G_ETHERNET.value: OpticalDigitalService,
        ProductName.OPTICAL_DIGITAL_SERVICE_400G_ETHERNET.value: OpticalDigitalService,
        ProductName.OPTICAL_DIGITAL_SERVICE_800G_ETHERNET.value: OpticalDigitalService,
        ProductName.OPTICAL_FIBER_PATCH.value: OpticalFiberPatch,
        ProductName.OPTICAL_FIBER_SPAN.value: OpticalFiberSpan,
        ProductName.OPTICAL_NODE_NOKIA_FLEXILS.value: OpticalNodeNokiaFlexIls,
        ProductName.OPTICAL_NODE_NOKIA_GROOVE_G30.value: OpticalNodeNokiaGrooveG30,
        ProductName.OPTICAL_NODE_NOKIA_GX_G42.value: OpticalNodeNokiaGxG42,
        ProductName.OPTICAL_LEASED_SPECTRUM.value: OpticalLeasedSpectrum,
        ProductName.OPTICAL_SPECTRUM.value: OpticalSpectrum,
        ProductName.ABSTRACT_OPTICAL_LOCATION.value: AbstractOpticalLocation,
        ProductName.ABSTRACT_OPTICAL_PACKET_NODE.value: AbstractOpticalPacketNode,
        ProductName.ABSTRACT_OPTICAL_NODE.value: AbstractOpticalNode,
        ProductName.ABSTRACT_OPTICAL_PIPE.value: AbstractOpticalPipe,
        # FIXME: For some reason this is not enough, check later.
    }
)


__all__ = ["ProductName", "ProductType"]
