# TNMS client: JSON decode leaks and unreachable error clauses in `_authenticate`

- **Status:** open
- **Severity:** high
- **Area:** services (TNMS TAPI client)
- **Affected:** `src/orchestrator/optical/services/nokia/tnms/client.py:119-159` (`_authenticate`), specifically `:138-141` (broad `except` + `e.response.status_code`), `:143-145` (unreachable `ConnectionError`/`Timeout` clause), `:159` (unreachable `AuthenticationError`); `:162-182` (`_request`), specifically `response.json()` at `:182`.
- **Discovered by:** `test/contract/test_tnms_client.py`, `test/contract/test_device_faults.py::test_tnms_malformed_body_leaks_raw_decode_error` (and `::test_tnms_http_500_is_mapped_to_api_error`).

## Symptom

- **Malformed JSON leaks `JSONDecodeError`.** In `_request`, `response.json()` at
  `client.py:182` is not guarded; only `requests.HTTPError` is mapped to `ApiError` (via
  the `requires_auth` decorator, `client.py:40-46`), so a 2xx non-JSON body surfaces a raw
  `requests.exceptions.JSONDecodeError`.
- **`_authenticate` timeout raises `AttributeError`.** The first handler
  `except (requests.HTTPError, requests.RequestException)` at `client.py:138` is broader
  than the later `except (requests.ConnectionError, requests.Timeout)` at `client.py:143`.
  Since `ConnectionError`/`Timeout` are subclasses of `RequestException`, they are caught
  by the first clause, which then evaluates `e.response.status_code` at `client.py:139` —
  `e.response` is `None` for transport errors, raising `AttributeError`. Consequently the
  dedicated `(ConnectionError, Timeout)` clause and the terminal
  `raise AuthenticationError(...)` at `client.py:159` are unreachable.

## Root cause

Exception-clause ordering plus a missing guard for `e.response`. `RequestException` is the
base class of the specific transport exceptions, so the specific handler can never run.
Separately, JSON decoding is outside any typed mapping.

## Proposed fix

- In `_authenticate`, handle `requests.ConnectionError` / `requests.Timeout` **before** the
  broad `(HTTPError, RequestException)` clause (or narrow the broad clause to
  `requests.HTTPError` only and guard `if e.response is not None`), so transport failures
  fall through to `last_error` and eventually raise `AuthenticationError`.
- Map non-HTTP transport errors and JSON decode failures to typed TNMS exceptions
  (`TnmsClientError` subclasses) rather than leaking `requests`/`json` types.
- In `_request`, wrap `response.json()` so a malformed body raises a typed TNMS error
  (e.g. `ApiError`/`TnmsClientError`) instead of `JSONDecodeError`.

## Acceptance criteria

- A simulated timeout/connection failure in `_authenticate` produces a typed TNMS error
  (`AuthenticationError` or a `TnmsClientError` subclass), never `AttributeError`.
- A malformed 2xx body produces a typed TNMS error, not `JSONDecodeError`
  (`test/contract/test_device_faults.py::test_tnms_malformed_body_leaks_raw_decode_error`
  updated accordingly).
- The dedicated `(ConnectionError, Timeout)` path and terminal `AuthenticationError` are
  reachable (asserted by a test).

## References

- Client: `src/orchestrator/optical/services/nokia/tnms/client.py`.
- Typed errors: `src/orchestrator/optical/services/nokia/tnms/exceptions.py`
  (`ApiError`, `AuthenticationError`, `TnmsClientError`).
- Current status notes: `todo/testing-architecture.md:42` (finding #3).
