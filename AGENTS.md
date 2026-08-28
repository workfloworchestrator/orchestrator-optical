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
├── workflows/                # WFO workflows of the shipped product types (ready-to-use) + importable parts
│   ├── __init__.py           #   docs the consumption model (register shipped workflows with LazyWorkflowInstance,
│   │                         #   compose your own with the parts)
│   ├── shared.py             #   selectors, summary forms (form-layer; DB queries live in db.py)
│   ├── optical_node/         #   per-vendor create/modify workflows + parts; terminate/validate workflows are
│   │                         #   per-vendor thin wrappers over shared step lists (shared/terminate.py, shared/validate.py)
│   ├── optical_pipe/         #   fiber_span / fiber_patch / leased_spectrum (workflows + parts)
│   ├── optical_spectrum_service/   #  path-finding engine (shared.py) + workflows
│   ├── optical_digital_service/    #  4-form create + modify/terminate/validate
│   ├── optical_coherent_pluggable/ #   create/modify/terminate/validate workflows + parts + shared helpers
│   │                         #   (block-based, state key OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY)
│   └── optical_location/     #   (WIP) location selectors/helpers
├── settings.py               # pydantic-settings, env prefix OPTICAL_, lazy get_settings()
├── db.py                     # neutral DB query helpers + block resolution shared by hal/ and workflows/ (blocks as contracts)
├── translations/en-GB.json   # workflow display strings (1:1 with registered workflows)
└── utils/                    # custom_types (dns Pqdn/Fqdn, coordinates, frequencies, ip_address), datadiff,
                              # singledispatch
```

## How users consume it (see README.md)

1. `uv add orchestrator-optical` in their WFO deployment.
2. DB migrations is still unclear whether will be shipped or not. Consumers could generate DB migrations locally
   (e.g. via orchestrator-core shell commands) but then the module's domain models would not be versionable and
   this is why the module should probably ship migrations.
3. The module is a **work in progress** (ported from a GARR-specific implementation): model files are still being
   finalized and may change between releases.

## Core conventions (follow these in every session)

### Data model pattern

- Every block/subscription has three lifecycle classes: `XInactive` → `XProvisioning` → `X` (ACTIVE), using
  `lifecycle=[SubscriptionLifecycle.X]`; `product_block_name=*`(`is_base=True`) is required on blocks(subscriptions)
  that are persisted. Abstract blocks and subscriptions do not have those args.
- Field names are `optical_*`-prefixed and descriptive (`optical_port_name`, `optical_transport_central_frequency`).

#### Persistence quirk (orchestrator-core 5.1.3)

`ProductBlockModel._find_special_fields` persists **only fields declared directly in a class body** — any inherited
field (from an abstract base or from a concrete sibling in the same chain) is silently dropped on save and missing on
reload. It fills two class dicts: `_non_product_block_fields_` (scalar values) and `_product_block_fields_` (block
references), both computed from the class's own annotations. Therefore: **every concrete block class must redeclare
every field it inherits**, or reloads will crash with ValidationError. The four base `ProductBlockModel` fields
(`name`, `label`, `subscription_instance_id`, `owner_subscription_id`) are exempt — core passes them explicitly.

This rule is fully applied: all 15 concrete block chains redeclare every inherited field. Any new block
must follow the rule.

### Dispatch

- Vendor/Platform dispatch is achieved in `hal/` with `match/case` wrt the enums in `optical_node_management.py`.
  Dynamic registration using singledispatch was removed — never reintroduce it.

### Layering (hal depends on blocks, never on workflows)

- `hal/` implements device-facing logic (aka drivers) and depends only on public **blocks** — these are the shared
  contracts between the module and its consumers — never on subscription models: no module under `hal/` may import from
  `orchestrator.optical.workflows.*`. Subscription ids are acceptable input parameters, but they are resolved to
  blocks (never to subscription models), via the neutral DB query helpers in `orchestrator/optical/db.py` — the
  shared home for database queries used by both `hal/` and `workflows/`. Workflow-layer code may load subscription
  models; `hal/` may not.

### Hard rules (generalization invariants)

- **No** `.garr.net`, pop codes, `fXXXcYY` naming, `garrxdb_id`/`netbox_id`/`nms_uuid` — anywhere.
- Device-side identifiers (OEL/OSNC/OCRS AIDs, CKTIDSUFFIX, `optical_transport_channel_name`) are
  `subscription_instance_id` **UUID strings**; user-provided free-form names go to the device **label** fields.
- Customer (`customer_id`) of a subscription is obtained using a choice selection where the function returning 
  the type[Choice] is defined in the user code-space and passed to this module via the `OpticalSettings`.

### Configuration

- All env-driven config lives in `settings.py` (`OPTICAL_`-prefixed; e.g. `OPTICAL_FLEXILS_USER`,
  `OPTICAL_TNMS_ENDPOINT`). **No import-time side effects**: importing any module must work with zero env vars.
  Use `get_settings()`; keep clients lazy (`get_netbox_api()`, `get_tnms_client()`).

### Workflows

- The module ships the **ready-to-use workflows of the shipped product types**: one module-level
  `@create_workflow`/`@modify_workflow`/`@terminate_workflow`/`@validate_workflow`-decorated function per product
  (decorators from `orchestrator.core.workflows.utils`, chains from `orchestrator.core.workflow`), named exactly as
  the shipped name (the translation keys in `translations/en-GB.json`). No factories, no hooks, no `**kwargs`; the
  workflow function name MUST keep the shipped name. The shipped workflows are bound to the shipped subscription
  models (the `construct_*_subscription` steps build them), so they are only valid for consumers keeping the shipped
  product types.
- The module ships the **parts** alongside the workflows: per product, the **FormPages** of the shipped forms plus
  (PROVISIONING) block-level steps exported as `StepList` constants (e.g. `CREATE_NOKIA_FLEXILS_BLOCK_STEPS`,
  `MODIFY_NOKIA_FLEXILS_BLOCK_STEPS`) and shared step lists (`OPTICAL_NODE_TERMINATE_STEPS`,
  `OPTICAL_NODE_VALIDATE_STEPS`). **No hooks**: shipped form generators do not take `extra_form_pages`/
  `extra_summary_fields` (or similar) parameters — they are thin compositions of the shipped pages and the summary
  form. Each form ships as a page **sequence** (a `FormGenerator` that yields the `FormPage` classes in order and
  returns the collected user input as a flat dict, e.g. `create_optical_module_location_form_pages(product_name)`);
  consumers compose their own form generator by yielding from the shipped page sequence in **one line** and
  optionally interleaving their own pages:
  `user_input_dict = yield from create_optical_module_location_form_pages(product_name)`. Page factories returning 
  the prefilled pages
  (e.g. `modify_optical_module_location_form(subscription, block_field_name)`) are also exported for consumers that
  pick pages individually. The `optical_location` family is the reference implementation of this model; the other
  families still carry the legacy hook-style generators, mid-port. Consumers with their own model compose their own
  workflows with these parts and their own construct/store steps. Shipped create workflows pass the raw form
  generator (no `partial`): core injects `product_name`/`subscription_id` from the database at runtime.
- **Composition, not inheritance**: consumers never subclass the shipped blocks; their model has-a the shipped block
  under an attribute of their choosing. The shipped block steps bind to the common state key
  (`optical_module_block`) and never to a consumer model. Shipped blocks always expect the block to be in the
  PROVISIONING lifecycle status. Shipped blocks are always persisted by the
  consumer's own store/`set_status` steps; the shipped block step lists end with a save step
  (`save_optical_module_block`) because workflow steps reload the subscription
  from the database on every step (in-memory block mutations would be lost otherwise).
- **(TO BE RECONSIDERED) Registration is the consumer's job**: this module never registers workflows itself (no `register_workflows()`,
  no `SHIPPED_WORKFLOW_NAMES`, no `LazyWorkflowInstance` calls at import). Consumers register the shipped workflows
  with the standard orchestrator-core mechanism — one `LazyWorkflowInstance(<module>, <name>)` line per workflow in
  their own workflows package — and persist them with `orchestrator db migrate-workflows`.
- Keep the display strings in `translations/en-GB.json` (keys are the shipped workflow function names); they apply
  when consumers keep the shipped workflow names, otherwise they are a reference for consumers' own translations.
- `from_product_id` is unusable for pipes and digital services (required fields/validators) — those workflows
  assemble the subscription manually (see `optical_pipe/shared.py::new_optical_pipe_subscription`).
- Some terminate/deprovision steps are deliberate stubs returning `{}` (framework signatures keep `customer_id` →
  `# noqa: ARG001`).

## Development commands

```bash
uv run ruff check <path>        # lint (line-length 120, google docstrings); ported code must be 0-findings
uv run ruff format --check <path>
uv run ty check                 # type check (with Astral's ty)
uv run pyrefly check            # type check (with Meta's pyrefly, harder gate than ty)
uv run python -c "import orchestrator.optical.<module>"   # import smoke (no env vars required)
uv build                        # package build
```

### Development mindset

> [!IMPORTANT]
> Always leave the code of this module more usable, maintainabile, and evolvable than you found it.

### Known pre-existing noise (do NOT "fix" these as a side quest)

- `services/nokia/{g30,g42}/data_models|data_navigators/*` — auto-generated YANG models, tens of thousands of
  ruff/ty findings; never edit manually.
- `workflows/shared.py` — pre-existing ty diagnostics in the form/selector helpers (committed file).
- `ARG001` on terminate-form `customer_id`/`subscription` params in stub steps.

### Current status (branch `porting/workflows`)

- The legacy `optical.old/` and the GARR admin `tasks/` workflows are there for reference only (`/hal` corresponds to old `products/services`) — do not reintroduce.
- Model files are actively being refined by maintainers: **ask before changing `products/`**; adapt code to their
  changes instead (e.g. field renames must be propagated to `hal/` and `workflows/`).
- workflows: done create,modify,validate,terminate for `optical_location` and create,modify,validate,terminate for
  the 3 optical nodes (FlexILS, G30, G42). All others are defined but still WIP.
