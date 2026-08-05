# AGENTS.md — Workflow Orchestrator (WFO) Optical Module

## What this project is

An addon module for [Workflow Orchestrator](https://workfloworchestrator.org) (built on
[`orchestrator-core`](https://github.com/workfloworchestrator/orchestrator-core) >= 5) that models and provisions
optical transport equipment: Nokia **FlexILS** (TL1 over SSH), **Groove G30** and **GX G42** (RESTCONF), and the
Nokia **TNMS** (TAPI) management system.

It is a **generalized, reusable** module: it was ported away from a GARR-specific implementation. It must stay free of
any organization-specific business logic (see "Hard rules" below). Users install it into their own WFO deployment and
generate their own database migrations.

Stack: Python >= 3.12, pydantic v2, orchestrator-core 5.x, `uv` for tooling. Package: `orchestrator.optical` (src
layout). License: Apache-2.0.

## Structure at a glance

```
src/orchestrator/optical/
├── products/                 # Data models (pydantic + orchestrator-core domain models)
│   ├── product_blocks/       #   Product blocks: one Inactive/Provisioning/Active class chain per block
│   │   ├── optical_node/     #     abstracts.py + one file per vendor (nokia_flexils, nokia_groove_g30, nokia_gx_g42)
│   │   ├── optical_port/     #     abstracts.py + one file per port role (ols_add_drop, ols_line, transponder_client, transponder_line), unions.py
│   │   ├── optical_pipe/     #     abstracts.py + fiber_span / fiber_patch / leased_spectrum + unions.py
│   │   └── …                 #     optical_spectrum.py, optical_spectrum_section.py, optical_transport_channel.py,
│   │                         #     optical_digital_service.py, optical_location.py, optical_packet_node.py,
│   │                         #     optical_coherent_pluggable.py
│   ├── product_types/        #   Subscription models (same Inactive/Provisioning/Active pattern); does NOT 1:1 mirror
│   │                         #   the blocks (no spectrum/section/transport_channel types — consolidated
│   │                         #   optical_spectrum_service.py; no unions.py under optical_pipe/)
│   └── __init__.py           #   ProductName + ProductType enums, SUBSCRIPTION_MODEL_REGISTRY update
├── hal/                      # Hardware Abstraction Layer: device-facing operations
│   ├── optical_node.py       #   Vendor/Vendor_of dispatch, client factories, GNE discovery, spectral occupations
│   ├── optical_port.py       #   port enumeration/admin state/fiber termination configure-reset-check
│   ├── optical_digital_service.py  # transponder line/client/crossconnect config + validation + power alignment
│   └── optical_spectrum.py   #   FlexILS OEL/OSNC/OCRS optical circuit engine
├── services/                 # Device integrations (do not "fix" the auto-generated parts)
│   ├── nokia/                #   flexils (TL1 client + per-command modules), g30, g42 (RESTCONF clients with
│   │                         #   auto-generated data_models/data_navigators), tnms (TAPI client)
│   ├── netbox.py             #   lazy Netbox client (settings-driven)
│   └── asyncsshcli/          #   async SSH terminal helper
├── workflows/                # WFO workflows
│   ├── __init__.py           #   SHIPPED_WORKFLOW_NAMES + register_workflows() (consumers declare 1:1 in their code)
│   ├── shared.py             #   DB query helpers, selectors, summary forms
│   ├── optical_node/         #   per-vendor create/modify/terminate/validate + shared step helpers
│   ├── optical_pipe/         #   fiber_span / fiber_patch / leased_spectrum
│   ├── optical_spectrum_service/   #  path-finding engine (shared.py) + workflows
│   ├── optical_digital_service/    #  4-form create + modify/terminate/validate
│   ├── optical_coherent_pluggable/
│   └── optical_location/     #   (WIP) location selectors/helpers
├── settings.py               # pydantic-settings, env prefix OPTICAL_, lazy get_settings()
├── translations/en-GB.json   # workflow display strings (1:1 with registered workflows)
└── utils/                    # custom_types (dns Pqdn/Fqdn, coordinates, frequencies, ip_address), datadiff,
                              # singledispatch
```

## How users consume it (see README.md)

1. `uv add orchestrator-optical` in their WFO deployment.
2. Generate a DB migration locally (the module ships **no** migrations — consumers create them, e.g. via
   orchestrator-core shell commands).
3. The module is a **work in progress** (ported from a GARR-specific implementation): model files are still being
   finalized and may change between releases. There are currently **no `#FIXME` markers** in the models — consumer-facing
   subclassing guidance will be provided once the port stabilizes.

## Core conventions (follow these in every session)

### Data model pattern
- Every block/subscription has three lifecycle classes: `XInactive` → `XProvisioning` → `X` (ACTIVE), using
  `lifecycle=[SubscriptionLifecycle.X]`; `product_block_name=` is required on classes that are persisted. Abstract
  roots are marked differently per model kind: product blocks use `product_block_name="AbstractX"` on the abstract
  root (`ProductBlockModel` in core 5.x has no `is_base` kwarg); subscription models use `is_base=True` on their
  Inactive classes (including some concrete Inactive classes — whether that is intended is an open question with the
  maintainers).
- Field names are `optical_*`-prefixed and descriptive (`optical_port_name`, `optical_transport_central_frequency`).
  Known exceptions: `pqdn`, `location` (optical_node/packet_node blocks), `longitude`, `latitude`, `fqdn_subdomain`
  (optical_location).

#### Persistence quirk (orchestrator-core 5.1.3)
`ProductBlockModel._find_special_fields` persists **only fields declared directly in a class body** — fields inherited
from an abstract base are silently dropped on save and missing on reload. Therefore: **every concrete block class must
redeclare the fields it inherits from its abstract bases**, or reloads will crash with ValidationError.

This rule is currently **only partially applied**: 8 of 15 concrete block chains comply (the three node vendor chains,
optical_coherent_pluggable, and the four self-contained chains without abstract bases). The remaining 7 chains
(all three `optical_pipe` chains — `optical_pipe_identifier` omitted — and all four `optical_port` role chains —
`optical_port_name`/`optical_port_description`/`optical_passbands` omitted) still need it done; treat those blocks as
suspect until fixed. Any new block must follow the rule.

### Dispatch
- Platform/vendor dispatch is on `vendor_of(block)` (from `hal.optical_node`, values: `Vendor.FLEXILS`,
  `Vendor.GROOVE_G30`, `Vendor.GX_G42`), covering all lifecycle variants. `hal/` dispatches with `match/case`;
  workflows use `if vendor_of(...) == Vendor.X` comparisons. Attribute dispatch was removed — never reintroduce it.

### Hard rules (generalization invariants)
- **No** `.garr.net`, pop codes, `fXXXcYY` naming, `garrxdb_id`/`netbox_id`/`nms_uuid` — anywhere.
- Device-side identifiers (OEL/OSNC/OCRS AIDs, CKTIDSUFFIX, `optical_transport_channel_name`) are
  `subscription_instance_id` **UUID strings**; user-provided free-form names go to the device **label** fields.
- Customer of a subscription is obtained using a choice selection where the function returning the type[Choice] is
defined in the user code-space.

### Configuration
- All env-driven config lives in `settings.py` (`OPTICAL_`-prefixed; e.g. `OPTICAL_FLEXILS_USER`,
  `OPTICAL_TNMS_ENDPOINT`). **No import-time side effects**: importing any module must work with zero env vars.
  Use `get_settings()`; keep clients lazy (`get_netbox_api()`, `get_tnms_client()`).

### Workflows
- One `@create_workflow`/`@modify_workflow`/`@terminate_workflow`/`@validate_workflow` per product (decorators from
  `orchestrator.core.workflows.utils`, chains from `orchestrator.core.workflow`), chains with
  `begin >> …`, `store_process_subscription()`, `set_status(...)`; state returns `subscription` /
  `subscription_id` / `subscription_description`.
- Every workflow is a **factory** (`<name>_workflow` in its module, returning the decorated workflow whose name is
  the shipped name) and is **not registered by this package**: consumers declare one workflow per shipped workflow
  in their own code and register them via `register_workflows()` (see `workflows/__init__.py`). Factories accept
  `pre_steps`/`post_steps` (run before/after the shipped steps, while the subscription is unsynced) and, for
  create/modify workflows, `extra_form_pages`/`extra_summary_fields`, for terminate workflows `extra_form_pages`
  only (no summary form in termination) and for validate workflows only `pre_steps`/`post_steps` (no input forms).
  Keep the display strings in `translations/en-GB.json` (keys are the workflow function names).
- Workflow factory inner functions MUST keep the shipped workflow name (product bindings and translations depend on
  it).
- `from_product_id` is unusable for pipes and digital services (required fields/validators) — those workflows
  assemble the subscription manually (see `optical_pipe/shared.py::new_optical_pipe_subscription`).
- Some terminate/deprovision steps are deliberate stubs returning `{}` (framework signatures keep `customer_id` →
  `# noqa: ARG001`).

## Development commands

```bash
uv run ruff check <path>        # lint (line-length 120, google docstrings); ported code must be 0-findings
uv run ruff format --check <path>
uv run ty check                 # type check (pyrefly)
uv run python -c "import orchestrator.optical.<module>"   # import smoke (no env vars required)
uv build                        # package build
```

### Known pre-existing noise (do NOT "fix" these as a side quest)
- `services/nokia/{g30,g42}/data_models|data_navigators/*` — auto-generated YANG models, tens of thousands of
  ruff/ty findings; never edit manually.
- `workflows/shared.py` — 3 pre-existing ty diagnostics (committed file).
- `ARG001` on terminate-form `customer_id`/`subscription` params in stub steps.
- Dangling config references to the removed `migrations/` dir (pyproject `source-include`/coverage `omit`,
  `.bumpversion.cfg` path) — left as-is; do not "fix" pyproject.toml as a side quest.

### Current status (branch `porting/workflows`)
- 36 workflow factories (workflows are declared and registered in the user code-space, see README); optical_node ×3
  vendors, optical_pipe ×3, optical_spectrum_service, optical_digital_service, optical_coherent_pluggable;
  optical_location workflows are WIP.
- No test suite yet (pyproject has pytest config; `testpaths = ["test"]` but no test dir).
- The legacy `optical.old/` and the GARR admin `tasks/` workflows are there for reference only (`/hal` corresponds to old `products/services`) — do not reintroduce.
- Model files are actively being refined by maintainers: **ask before changing `products/`**; adapt code to their
  changes instead (e.g. field renames must be propagated to `hal/` and `workflows/`).
