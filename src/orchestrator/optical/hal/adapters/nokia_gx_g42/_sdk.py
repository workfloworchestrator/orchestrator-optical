"""The Nokia GX G42 SDK surface used by this adapter: the only module importing ``g42_8_0_2``.

Every SDK name the adapter needs is re-exported here, so that the SDK contract is
explicit and a different SDK (e.g. a newer firmware release) is swapped in one place.
The SDK speaks NETCONF; YANG enumerations defined inline in a leaf are ``Literal``
strings in its models (only typedef'd enumerations are ``Enum`` classes).
"""

from orchestrator.optical.hal._common import VendorSdkNotInstalledError

try:
    from g42_8_0_2 import (
        NetconfClient as G42Client,
    )
    from g42_8_0_2.data_models.ioa_network_element import (
        LldpAdminStatusEnum,
        LldpModeEnum,
        PhyModeEnum,
        PortTypeEnum,
        ServiceTypeEnum,
        SignalTypeEnum,
        XconItem,
    )
    from g42_8_0_2.data_models.ioa_services import (
        CreateXconInput,
        PayloadTypeEnum,
    )
except ModuleNotFoundError as exc:
    raise VendorSdkNotInstalledError(sdk="g42_8_0_2", device="Nokia GX G42") from exc

__all__ = [
    "CreateXconInput",
    "G42Client",
    "LldpAdminStatusEnum",
    "LldpModeEnum",
    "PayloadTypeEnum",
    "PhyModeEnum",
    "PortTypeEnum",
    "ServiceTypeEnum",
    "SignalTypeEnum",
    "XconItem",
]
