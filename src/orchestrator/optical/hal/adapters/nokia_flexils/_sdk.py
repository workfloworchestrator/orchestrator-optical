"""The Nokia FlexILS SDK surface used by this adapter: the only module importing ``flexils_tl1``.

Every SDK name the adapter needs is re-exported here, so that the SDK contract is
explicit and a different SDK (e.g. a newer firmware release) is swapped in one place.
"""

from orchestrator.optical.hal._common import VendorSdkNotInstalledError

try:
    from flexils_tl1.client import (
        FlexilsClient,
    )
    from flexils_tl1.commands.base import (
        TL1BaseResponse,
    )
    from flexils_tl1.exceptions import (
        TL1CommandDeniedError,
    )
except ModuleNotFoundError as exc:
    raise VendorSdkNotInstalledError(sdk="flexils_tl1", device="Nokia FlexILS") from exc

__all__ = [
    "FlexilsClient",
    "TL1BaseResponse",
    "TL1CommandDeniedError",
]
