"""Tests for ``retryable_form``: unexpected form errors are page validation errors, not HTTP 500s."""

import inspect

import pytest
from pydantic import field_validator
from pydantic_forms.core import FormPage, post_form
from pydantic_forms.exceptions import FormNotCompleteError, FormValidationError
from pydantic_forms.types import FormGenerator, State

from orchestrator.optical.workflows.shared import retryable_form


class _DeviceError(Exception):
    """Stand-in for an error that is neither ``ValueError`` nor ``AssertionError``."""


VALIDATOR_FAILURE = "validator failed"
DEVICE_FAILURE = "device unreachable"


class FirstPage(FormPage):
    name: str

    @field_validator("name")
    @classmethod
    def _check(cls, value: str) -> str:
        if value == "boom":
            raise _DeviceError(VALIDATOR_FAILURE)
        return value


class SecondPage(FormPage):
    port: str


FAIL = {"between_pages": False}


@retryable_form
def _form(product_name: str) -> FormGenerator:
    first = yield FirstPage
    if FAIL["between_pages"]:
        raise _DeviceError(DEVICE_FAILURE)
    second = yield SecondPage
    return {"product_name": product_name, **first.model_dump(), **second.model_dump()}


def _generator(state: State) -> FormGenerator:
    return (yield from _form(state["product_name"]))


@pytest.fixture(autouse=True)
def _reset() -> None:
    FAIL["between_pages"] = False


def test_signature_is_preserved_for_core_argument_injection() -> None:
    assert inspect.isgeneratorfunction(_form)
    assert list(inspect.signature(_form).parameters) == ["product_name"]


def test_happy_path_is_unchanged() -> None:
    with pytest.raises(FormNotCompleteError) as next_page:
        post_form(_generator, {"product_name": "p"}, [{"name": "a"}])
    assert list(next_page.value.form["properties"]) == ["port"]
    result = post_form(_generator, {"product_name": "p"}, [{"name": "a"}, {"port": "1"}])
    assert result == {"product_name": "p", "name": "a", "port": "1"}


def test_error_between_pages_is_reported_on_the_submitted_page_and_is_retryable() -> None:
    FAIL["between_pages"] = True
    with pytest.raises(FormValidationError) as rejected:
        post_form(_generator, {"product_name": "p"}, [{"name": "a"}])
    assert rejected.value.validator_name == "FirstPage"
    (error,) = rejected.value.errors
    assert error["loc"] == ("__root__",)
    assert error["msg"].startswith("_DeviceError: device unreachable")

    FAIL["between_pages"] = False  # cause fixed: the very same submit now goes on
    with pytest.raises(FormNotCompleteError):
        post_form(_generator, {"product_name": "p"}, [{"name": "a"}])


def test_unexpected_validator_error_is_a_validation_error() -> None:
    with pytest.raises(FormValidationError) as rejected:
        post_form(_generator, {"product_name": "p"}, [{"name": "boom"}])
    assert rejected.value.validator_name == "FirstPage"
    assert "_DeviceError: validator failed" in rejected.value.errors[0]["msg"]


def test_regular_validation_errors_are_untouched() -> None:
    with pytest.raises(FormValidationError) as rejected:
        post_form(_generator, {"product_name": "p"}, [{}])
    (error,) = rejected.value.errors
    assert error["loc"] == ("name",)
    assert error["type"] == "missing"
