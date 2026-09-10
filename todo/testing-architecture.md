# Target testing architecture

## Status: implemented

The target design below is now in place.

| Area | What landed |
|---|---|
| Lanes | Default `pytest` = DB-free (fast) lane via `addopts = "-m 'not db'"`; `pytest -m db` = integration lane. Markers `db`, `contract`, `unit`. |
| Tree | `test/{unit,contract,composition,execution,migrations}/` plus `test/support/{db,devices,topology,catalog,models,forms,core_api}.py`; `test/conftest.py` reduced to a thin fixture re-export. |
| Models | Duplicated consumer models consolidated into `test/support/models.py`; cross-test-module imports removed. |
| Contract/unit | Added for HAL common helpers, HAL dispatch, custom types, settings, FlexILS TL1, G30/G42 RESTCONF, TNMS, Netbox, and device fault injection. |
| Coverage | Whole-package `source = ["orchestrator.optical"]` with explicit generated/legacy omits; per-family ratchet `scripts/coverage_ratchet.py` + `coverage-floors.toml`; `make coverage`. Patch coverage via `diff-cover` in CI. |
| CI/local | `.github/workflows/ci.yml` (lint, fast matrix 3.12-3.14, integration with pgvector service, nightly core-latest) and a local `Makefile` (`install`, `lint`, `typecheck`, `test-fast`, `test-db`, `test`, `coverage`, `ci`). |
| Drift canary | Self-maintaining: discovers `populate_*`/`update_*`/`build_*` writers and requires them in `WRITERS` or `EXCLUDED_WRITERS`. |
| Registry/migrations | Workflow registry and migrations test derive from `discover_shipped_workflows()`; hardcoded 43-entry dict/count removed; `test/unit/test_translations.py` asserts 1:1 between `en-GB.json` `workflow` keys and shipped workflow names. |
| Warnings/typecheck | `filterwarnings` narrowed to 3 targeted third-party ignores; typecheck (`ty` + `pyrefly`) excludes `test/`, `scripts/`, and the documented `workflows/shared.py` noise. |
| Verified locally | `722` fast tests, `35` db tests, `ruff` clean, `ty`/`pyrefly` 0 errors, ratchet all families above floor, CI YAML valid. |

Coverage (fast-lane baseline):

| family | actual% | floor |
|---|---|---|
| products | 89.53 | 87 |
| settings.py | 100.00 | 98 |
| utils | 78.16 | 76 |
| services | 69.59 | 67 |
| hal | 47.35 | 45 |
| workflows | 45.88 | 43 |
| db.py | 44.44 | 42 |

The full DB lane lifts `workflows` to ~70.7% and `db.py` to ~84.4%, while `hal` stays ~47%.

## Findings / follow-ups

Real issues discovered while writing the contract/fault tests; reported, not fixed.

| # | Area | Issue |
|---|---|---|
| 1 | RESTCONF (`services/nokia/{g30,g42}` `RestconfClient._request`) | Malformed 2xx JSON leaks raw `requests.exceptions.JSONDecodeError`; timeouts collapse into a generic builtin `ExceptionGroup`; HTTP 5xx surfaces as `requests.HTTPError` with no domain error type. |
| 2 | FlexILS TL1 parser (`services/nokia/flexils/commands/base.py` `TL1BaseResponse.from_raw_text`) | A tag present without a status word leaks a raw `AttributeError`; unknown status is a plain `ValueError`. Also `split_preserving_quotes` only toggles quote state on backslash-escaped patterns, so a real OCRS `CKTID="…:OCh…"` is split at the inner colon (corrupts CKTID/OPERSTATE). |
| 3 | TNMS (`services/nokia/tnms/client.py`) | Malformed JSON leaks `JSONDecodeError` (only HTTPError maps to `ApiError`); in `_authenticate` the first `except (HTTPError, RequestException)` catches `ConnectionError`/`Timeout` and then dereferences `e.response.status_code` (None) -> `AttributeError`, making the dedicated `(ConnectionError, Timeout)` clause and the terminal `AuthenticationError` unreachable. |
| 4 | Coverage | `hal` is the lowest family (~47%) and does not improve with DB tests — the device boundary remains the least-covered area. |
| 5 | Patch gate | `diff-cover` is set to 50% (measured patch coverage ~56-67% on this branch); raise it as the branch matures. |
| 6 | Deferred | The HAL "namespace seam" (workflows still import HAL functions by name; `test/support/devices.py` patches import sites) and a `test/support/factories.py`; the `orchestrator-core` minimum was not pinned (track-latest policy + nightly `core-latest` job instead). |

## Goal

Make the test suite a predictable, low-friction safety net that tracks the latest
`orchestrator-core`, is honest about coverage, and isolates the fastest-moving/highest-risk
surfaces (HAL/device boundary and product models).

Today the suite mixes DB-backed and DB-free tests in one collection, hand-maintains workflow
discovery and drift lists, and touches private core APIs from many places. The target below
splits the suite into dependency-defined lanes, moves shared scaffolding into importable
helpers, and makes discovery/drift checks derive from the models themselves.

## Principles

1. **Lanes, not one blob**: separate by dependency/runtime via markers; default run is DB-free
   and fast.
2. **One source of truth**: workflow discovery, catalog shape and drift checks derive from
   models, never hand-maintained lists.
3. **Contract-first at the device boundary**: HAL/services get recorded-fixture contract tests
   plus fault injection.
4. **Patch one seam, not N import sites**: device fakes replace a single HAL boundary.
5. **Coverage is a ratchet, not a number**: per-family floors plus patch coverage (diff-cover).
6. **Zero hidden global state**: no leaking of `core_settings` or the subscription registry
   between lanes.

## Target test tree

```text
test/
  conftest.py                     # pytest hooks + lane wiring only
  support/                        # importable helpers, NOT each other's fixtures
    db.py                         # PG fixture, core migrations, catalog provisioning
    catalog.py                    # seed a consumer catalog
    models.py                     # shared consumer-style chains (is_base=True)
    devices.py                    # FakeDevice per vendor, install_device_stubs, fault injection
    topology.py                   # active_location, active_packet_node, seed_optical_node
    factories.py                  # block/subscription builders
    forms.py                      # finish_form, page-sequence drivers
    core_api.py                   # shim for private core APIs (__wrapped__, _product_block_fields_)
  unit/                           # DB-free, Docker-free, milliseconds
  contract/                       # device boundary, recorded/faked transports
  composition/                    # DB-free workflow-part contracts
  execution/                      # DB-backed end-to-end
  migrations/                     # migration pipeline tests
```

`support/` modules are plain importable helpers: they may be imported by any lane but must not
depend on each other's pytest fixtures. `conftest.py` stays a thin wiring layer (hooks, marker
registration, lane ordering) and holds no business helpers.

## Lanes

| Invocation | Lanes | Docker |
|---|---|---|
| `pytest` (default) | unit + contract + composition | no |
| `pytest -m db` | execution + DB-backed migrations | yes |
| `pytest -m contract` | device boundary only | no |

The default run excludes the DB lane via `addopts = "-m 'not db'"`. Markers: `db`, `contract`,
`unit`. This keeps the inner loop DB-free and fast while still allowing an explicit, opt-in
integration run.

## Database harness

- **CI primary path**: a PostgreSQL service container (`pgvector/pgvector:pg16`) exported as
  `OPTICAL_TEST_PG_URL`; testcontainers is the local fallback. This removes the
  Docker-in-runner dependency.
- Derive the truncated volatile-table list from core metadata instead of the hardcoded list.
- Save/restore `core_settings.app_settings` in fixture teardown so lane/global settings never
  leak between tests.

## Device boundary

- **Pure helpers** (`hal/_common.py`, FlexILS command parsers) -> unit tests.
- **Adapters** (`hal/adapters/*`) -> contract tests with faked transports (FlexILS TL1,
  G30/G42 RESTCONF, TNMS, Netbox via `responses`).
- **Fault injection**: timeouts, HTTP 5xx, malformed JSON, partial success; assert typed errors
  and no half-written blocks.

The fake devices live behind a single HAL seam (`support/devices.py::install_device_stubs`), so
tests patch one boundary rather than many import sites.

## Self-maintaining drift and discovery

- Discover writers by naming convention (`populate_*`, `update_*`, `build_*`, `construct_*`)
  and require each in the drift mapping or an explicit allowlist.
- Derive the workflow registry from `discover_shipped_workflows()`; delete the hand-maintained
  43-entry dict and literal count.
- Add the missing 1:1 check between `translations/en-GB.json` and registered workflow names.

## Coverage and gates

- Per-family explicit coverage floors; add `hal/`, `services/`, `settings.py`, `utils/`.
- Patch coverage (`diff-cover`) on every PR.
- Exclude generated code explicitly (`services/nokia/{g30,g42}/data_models|data_navigators`,
  `optical.old`).
- Narrow `filterwarnings` so core deprecations surface.
- Pin the minimum tested core; run lockfile-pinned plus a scheduled `orchestrator-core @ latest`
  job; centralize private core API use in `support/core_api.py`.

## CI (GitHub Actions)

| Job | What it runs |
|---|---|
| lint | `ruff check`, `ruff format --check`, `ty`, `pyrefly` |
| fast (3.12/3.13/3.14) | `pytest -m "not db"` + coverage + diff-cover |
| integration | pgvector service + `OPTICAL_TEST_PG_URL`, `pytest -m db` |
| core-latest (nightly + label) | `uv pip install -U orchestrator-core`, run fast lane |

Everything is runnable locally via a Makefile/script before pushing.

## Migration phases

| Phase | Deliverable | Risk |
|---|---|---|
| A | Fix uncollectable modules; markers + addopts; CI skeleton. | Low |
| B | Extract `support/`; delete cross-module imports and duplicated consumer models; move files into lanes. | Low |
| C | HAL contract + fault lanes; decide on the `hal` namespace seam. | Medium |
| D | Coverage ratchet + diff-cover; self-maintaining drift; translations check; core-latest job. | Low |

## Known issue resolved in Phase A

Four test modules failed collection with `ValueError: Cannot register a type that has no
__base_type__` because test-local abstract subscription models omitted `is_base=True` (required
by orchestrator-core 5.1.3).
