# FlexILS TL1 parser: raw AttributeError and quote-aware split bug

- **Status:** open
- **Severity:** high
- **Area:** services (FlexILS TL1 parser)
- **Affected:** `src/orchestrator/optical/services/nokia/flexils/commands/base.py:68-141` (`TL1BaseResponse.from_raw_text`), `:74-75` (`match.group(1)`), `:82-101` (`split_preserving_quotes`, quote toggle at `:89-93`).
- **Discovered by:** `test/contract/test_flexils_tl1_commands.py`, `test/contract/test_device_faults.py::test_tl1_parse_missing_status_leaks_attribute_error` (and `::test_tl1_parse_unknown_status_raises_value_error`).

## Symptom

Two defects in the same parser:

1. **Missing status word leaks `AttributeError`.** If the correlation tag is present but
   the status token is missing (`TL1BaseResponse.from_raw_text("WFOTAG", "WFOTAG")`),
   `re.match(r"\s*(\w+)", ...)` at `base.py:74` returns `None` and `match.group(1)` at
   `base.py:75` raises `AttributeError: 'NoneType' object has no attribute 'group'`
   instead of a typed parse error.

2. **`split_preserving_quotes` truncates quoted values containing `:`.** The quote-state
   machine at `base.py:89-93` only toggles `in_quotes` when it sees the backslash-escaped
   patterns `\"` / `:\"` / `\",` / `\":` — i.e. it assumes escaped quotes. A real OCRS
   record such as `CKTID="...:OCh..."` (plain double quotes, inner colon) is therefore
   split at the inner `:`; `CKTID` is truncated and the trailing `OPERSTATE` is corrupted.

## Root cause

- `from_raw_text` assumes the regex always matches and dereferences `match` unconditionally.
- `split_preserving_quotes` tracks quote state on 3-character escaped sequences rather than
  on the actual quote character, so plain `"` never enters/leaves quoted state.

## Proposed fix

- Add a typed `FlexILSResponseError` (in `services/nokia/flexils/exceptions.py`, sibling of
  `TL1CommandDeniedError`) and raise it when the status word cannot be matched, including
  the offending raw text.
- Rewrite the quote-state tracking to toggle on a bare `"` (while still tolerating
  backslash-escaped quotes), so delimiters inside quoted values are preserved.
- Keep the delimiter/`=` handling unchanged otherwise; unknown status may remain a
  `ValueError` from the `TL1CompletionStatus` enum or also be wrapped, but the malformed
  cases must be typed.
- Add a regression test with a colon inside a quoted `CKTID`.

## Acceptance criteria

- A tag without a status raises `FlexILSResponseError` (not `AttributeError`).
- A record containing `CKTID="...:OCh..."` parses with the full `CKTID` and a correct
  `OPERSTATE` (e.g. `test/contract/test_flexils_tl1_commands.py::test_ocrs_response_renames_positional_params`
  extended with a quoted-colon fixture).
- `test/contract/test_device_faults.py::test_tl1_parse_missing_status_leaks_attribute_error`
  is updated to assert the typed error.

## References

- Parser: `src/orchestrator/optical/services/nokia/flexils/commands/base.py`.
- Existing typed error: `TL1CommandDeniedError` in `services/nokia/flexils/exceptions.py`.
- Current status notes: `todo/testing-architecture.md:41` (finding #2).
