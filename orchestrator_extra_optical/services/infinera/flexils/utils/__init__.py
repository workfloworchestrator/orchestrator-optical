"""
FlexILS support methods.
"""

from services.infinera.flexils.utils.correlation_tag_generator import generate_ctag
from services.infinera.flexils.utils.fixed_params import DEFAULT_CTAG, TL1CompletionStatus

__all__ = ["DEFAULT_CTAG", "TL1CompletionStatus", "generate_ctag"]
