# HAL coverage is the lowest family and does not improve with DB-backed tests

- **Status:** open
- **Severity:** medium
- **Area:** hal (device boundary)
- **Affected:** `src/orchestrator/optical/hal/**`, e.g. `hal/node.py:185` (`validate_management_network_config`), `hal/adapters/nokia_groove_g30/node.py:61` (same), `hal/adapters/nokia_gx_g42/transponder.py:41-168` (`_find_xcon`, `_create_xcon`, `_retrieve_time_slots`), `hal/adapters/nokia_groove_g30/transponder.py:89` (`_extract_shelf_slot_port_ids_from_odu_string`), `services/nokia/flexils/client.py:25` (`get_instance`) and `:81` (`_connect`).
- **Discovered by:** `make coverage` / `scripts/coverage_ratchet.py` (fast lane: `hal` = 47.35%, floor 45 in `coverage-floors.toml:13`).

## Symptom

`hal` is the least-covered family of the package (~47.35% on the default DB-free lane) and
its coverage does not rise when the DB-backed execution lane is added, because the
uncovered code is device-transport logic rather than persistence logic. The device
boundary — the highest-risk surface for silent breakage — is therefore the weakest part of
the safety net.

## Root cause

The large vendor adapters (ODU/XCON tree walks, transceiver configuration, network
validation, FlexILS connect/GNE discovery) are exercised only end-to-end behind DB tests,
which stub at the workflow boundary and never reach most adapter branches. There is no
contract test driving the adapter functions with a faked transport, and some logic is
embedded in functions that are hard to test without network/SSH.

## Proposed fix

- Add `test/contract/` tests for the remaining HAL paths, driving adapter functions with
  faked transports/navigators:
  - large ODU/XCON tree functions in `hal/adapters/nokia_gx_g42/transponder.py` and
    `hal/adapters/nokia_groove_g30/transponder.py`;
  - `validate_management_network_config` (`hal/node.py:185`,
    `hal/adapters/nokia_groove_g30/node.py:61`);
  - FlexILS `_connect`/GNE discovery via a faked SSH transport
    (`services/nokia/flexils/client.py:81`, `get_instance` at `:25`).
- Where a function mixes I/O with parsing, extract the pure core into a helper and unit-test
  it directly (KISS/YANGI).
- Raise the `hal` floor in `coverage-floors.toml` once the new tests land.

## Acceptance criteria

- `hal` coverage increases measurably and the `"hal"` floor in `coverage-floors.toml` is
  raised accordingly (never lowered).
- New contract tests cover the ODU/XCON tree functions, `validate_management_network_config`,
  and FlexILS connect/discovery paths.

## References

- Floors: `coverage-floors.toml:13`; ratchet: `scripts/coverage_ratchet.py`.
- Coverage table: `todo/testing-architecture.md:28` (`hal 47.35 | 45`).
- Gap list / suggested placement: `todo/test-seams-map.md:106-266`, `:534-541`.
