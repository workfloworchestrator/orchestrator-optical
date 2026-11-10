"""The Nokia Groove G30 SDK surface used by this adapter: the only module importing ``g30_4_8_0``.

Every SDK name the adapter needs is re-exported here, so that the SDK contract is
explicit and a different SDK (e.g. a newer firmware release) is swapped in one place.
The SDK speaks NETCONF; YANG enumerations defined inline in a leaf are ``Literal``
strings in its models (only typedef'd enumerations are ``Enum`` classes).
"""

from orchestrator.optical.hal._common import VendorSdkNotInstalledError

try:
    from g30_4_8_0 import (
        NetconfClient as G30Client,
    )
    from g30_4_8_0.data_models.ne import (
        CardTypeEnum,
        EquipmentTypeEnum_1,
        GainRangeTypeEnum,
        PortModeEnum,
    )
    from g30_4_8_0.data_navigators.ne import (
        CardPortItemNode,
        CardPortSubportItemNode,
        SubcardPortItemNode,
        SubcardPortSubportItemNode,
    )
except ModuleNotFoundError as exc:
    raise VendorSdkNotInstalledError(sdk="g30_4_8_0", device="Nokia Groove G30") from exc

#: A port navigator node, on a card or on a subcard.
PortItemNode = CardPortItemNode | SubcardPortItemNode

#: A subport navigator node, on a card port or on a subcard port.
SubportItemNode = CardPortSubportItemNode | SubcardPortSubportItemNode

__all__ = [
    "CardTypeEnum",
    "EquipmentTypeEnum_1",
    "G30Client",
    "GainRangeTypeEnum",
    "PortItemNode",
    "PortModeEnum",
    "SubportItemNode",
]
