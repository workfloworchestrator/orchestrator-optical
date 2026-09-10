# Workflows import HAL functions by name, forcing brittle per-import-site stubs

- **Status:** open
- **Severity:** medium
- **Area:** workflows / test support
- **Affected:** workflow modules importing HAL functions by name, e.g. `src/orchestrator/optical/workflows/shared.py:28` (`get_device_ports_by_role`), `workflows/optical_node/shared/retrieve.py:8`, `workflows/optical_digital_service/create_optical_digital_service.py:23-24`, `workflows/optical_spectrum_service/shared.py:39-40`, plus the string-target stub table in `test/support/devices.py:194-280`.
- **Discovered by:** `test/support/devices.py::install_device_stubs` (family stub table) and the workflow composition/execution tests that consume it.

## Symptom

Shipped workflows do `from orchestrator.optical.hal.<area> import <fn>`, which copies the
function into the workflow module's globals. To fake a device, tests must patch every
import site by string target — the `stubs` table in `test/support/devices.py:194-280`
enumerates each module/attribute pair (e.g.
`orchestrator.optical.workflows.optical_spectrum_service.shared.retrieve_ports_spectral_occupations`).
Adding a workflow that imports a HAL function requires editing the table, and a missed
entry silently hits the real device path. The table is brittle and duplicates knowledge of
the HAL surface.

## Root cause

Name-imports create N binding sites for one HAL function. There is no single runtime seam
that all workflow device calls go through, so monkeypatching cannot target one place.

## Proposed fix

- Route workflow device calls through the `hal` package namespace (module attribute
  access), e.g. `from orchestrator.optical import hal` and call
  `hal.get_device_ports_by_role(...)` / `hal.spectrum.deploy_optical_circuit(...)`, so
  tests patch the single `hal` (or sub-module) attribute.
- With that seam in place, collapse `test/support/devices.py` to patch the `hal` namespace
  once and delete the per-module string-target table.
- Note: this is a source change in `workflows/**` and requires maintainer agreement before
  implementation (per AGENTS.md, workflow/HAL layering conventions).

## Acceptance criteria

- `test/support/devices.py` patches one HAL seam instead of a module/attribute table, and
  the string-target `stubs` table is removed.
- Existing composition/execution tests pass unchanged in behaviour.
- New workflow/HAL functions need no test-support edit to be stubbable.

## References

- Stub table: `test/support/devices.py:147-315`.
- Design intent: `todo/testing-architecture.md:66` (principle 4, "Patch one seam, not N
  import sites") and `:125-126`.
- Current status notes: `todo/testing-architecture.md:45` (finding #6).
