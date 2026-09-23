"""Shared helpers for exercising the shipped form generators in tests."""

from typing import Any

import pytest
from pydantic_forms.types import FormGenerator

from orchestrator.core.forms import FormPage


def finish_form(generator: FormGenerator, page_instance: FormPage) -> dict[str, Any]:
    """Send the last user input and return the return value of the form generator."""
    with pytest.raises(StopIteration) as exc_info:
        generator.send(page_instance)
    return exc_info.value.value
