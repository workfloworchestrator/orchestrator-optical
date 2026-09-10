# RESTCONF client leaks raw transport/JSON exceptions instead of a domain error

- **Status:** open
- **Severity:** high
- **Area:** services (device boundary) / hal adapters
- **Affected:** `src/orchestrator/optical/services/nokia/g30/session_manager.py:99-131` (`RestconfClient._request`), `src/orchestrator/optical/services/nokia/g42/session_manager.py:99-131` (same implementation), adapters `src/orchestrator/optical/hal/adapters/nokia_groove_g30/node.py` and `src/orchestrator/optical/hal/adapters/nokia_gx_g42/node.py`.
- **Discovered by:** `test/contract/test_device_faults.py::test_restconf_malformed_json_leaks_raw_decode_error`, `::test_restconf_connection_timeout_becomes_exception_group`, `::test_restconf_http_500_becomes_requests_http_error`, `::test_g30_adapter_surfaces_restconf_http_error`, `::test_g42_adapter_surfaces_restconf_http_error`.

## Symptom

A single `_request` call can fail in three unrelated ways, each surfacing a different
low-level exception type to the caller:

- Malformed JSON on a 2xx body: `response.json()` at `session_manager.py:113` raises
  `requests.exceptions.JSONDecodeError` directly (not wrapped).
- Every endpoint timing out / refusing connection: the loop accumulates errors and
  raises a builtin `ExceptionGroup` at `session_manager.py:131`.
- HTTP 5xx: re-raised as `requests.HTTPError` at `session_manager.py:127`.

There is no domain error type, so callers (HAL adapters and, above them, workflows)
cannot distinguish "device unreachable" from "device rejected the request" from "device
returned garbage" without catching and introspecting `requests`/`json` internals.

## Root cause

`_request` mixes transport concerns (URL fallback, timeouts) with protocol decoding and
lets the raw exceptions escape. The `except (requests.ConnectionError, requests.Timeout)`
clause only handles the multi-endpoint fallback path; JSON decoding happens inside the
`try` after `raise_for_status()` but is not caught, and `HTTPError` is re-created as
another `requests.HTTPError` rather than a module-owned type.

## Proposed fix

- Introduce a typed RESTCONF error in the service layer, e.g. `RestconfError` exposing
  `.status_code` and `.cause` (mirroring `tnms.exceptions.ApiError`).
- In `_request`, map:
  - `requests.Timeout` / `requests.ConnectionError` → `RestconfError` (after exhausting
    all URLs; keep the list of causes as context instead of a bare `ExceptionGroup`);
  - `requests.HTTPError` → `RestconfError(status_code=..., cause=...)`;
  - `requests.exceptions.JSONDecodeError` (and `ValueError`) → `RestconfError` with no
    status code / a decode marker.
- Have the HAL adapters (`nokia_groove_g30`, `nokia_gx_g42`) propagate that type rather
  than raw `requests` exceptions.
- Share the implementation between G30 and G42 (the two `_request` bodies are identical)
  to avoid fixing the same bug twice.

## Acceptance criteria

- `test/contract/test_device_faults.py` asserts the domain `RestconfError` type for the
  timeout, HTTP 5xx and malformed-JSON cases instead of `ExceptionGroup`,
  `requests.HTTPError` and `JSONDecodeError`.
- The G30/G42 adapter fault tests assert the domain type surfaces through the adapter.
- No raw `requests`/`json` exception escapes `_request`.

## References

- Fault tests: `test/contract/test_device_faults.py:59-122`.
- Current status notes: `todo/testing-architecture.md:40` (finding #1).
- Existing typed-error precedent: `src/orchestrator/optical/services/nokia/tnms/exceptions.py`.
