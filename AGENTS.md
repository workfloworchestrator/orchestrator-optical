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
│   ├── shared.py             #   DB query helpers, selectors, summary forms
│   ├── optical_node/         #   per-vendor create/modify workflows + parts; terminate/validate workflows are
│   │                         #   per-vendor thin wrappers over shared step lists (shared/terminate.py, shared/validate.py)
│   ├── optical_pipe/         #   fiber_span / fiber_patch / leased_spectrum (workflows + parts)
│   ├── optical_spectrum_service/   #  path-finding engine (shared.py) + workflows
│   ├── optical_digital_service/    #  4-form create + modify/terminate/validate
│   ├── optical_coherent_pluggable/ #   create/modify/terminate/validate workflows + parts + shared helpers
│   │                         #   (block-based, state key OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY)
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
  Inactive classes.
- Field names are `optical_*`-prefixed and descriptive (`optical_port_name`, `optical_transport_central_frequency`).
  Known exceptions: `pqdn`, `location` (optical_node/packet_node blocks), `longitude`, `latitude`, `fqdn_subdomain`
  (optical_location).

#### Persistence quirk (orchestrator-core 5.1.3)
`ProductBlockModel._find_special_fields` persists **only fields declared directly in a class body** — any inherited
field (from an abstract base or from a concrete sibling in the same chain) is silently dropped on save and missing on
reload. It fills two class dicts: `_non_product_block_fields_` (scalar values) and `_product_block_fields_` (block
references), both computed from the class's own annotations. Therefore: **every concrete block class must redeclare
every field it inherits**, or reloads will crash with ValidationError. The four base `ProductBlockModel` fields
(`name`, `label`, `subscription_instance_id`, `owner_subscription_id`) are exempt — core passes them explicitly.

Check compliance at runtime by verifying that every `model_fields` entry of a concrete class appears in its own class
annotations (and hence in one of the two dicts).

This rule is fully applied: all 15 concrete block chains redeclare every inherited field (the three node vendor chains,
`optical_coherent_pluggable`, the four self-contained chains without abstract bases, the three `optical_pipe` chains and
the four `optical_port` role chains — including `optical_port_role` in the Provisioning/Active variants). Any new block
must follow the rule.

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
- The module ships the **ready-to-use workflows of the shipped product types**: one module-level
  `@create_workflow`/`@modify_workflow`/`@terminate_workflow`/`@validate_workflow`-decorated function per product
  (decorators from `orchestrator.core.workflows.utils`, chains from `orchestrator.core.workflow`), named exactly as
  the shipped name (the translation keys in `translations/en-GB.json`). No factories, no hooks, no `**kwargs`; the
  workflow function name MUST keep the shipped name. The shipped workflows are bound to the shipped subscription
  models (the `construct_*_subscription` steps build them), so they are only valid for consumers keeping the shipped
  product types. State returns `subscription` / `subscription_id` / `subscription_description`.
- The module ships the **parts** alongside the workflows: per product, the **FormPages** of the shipped forms plus
  block-level steps exported as `StepList` constants (e.g. `CREATE_NOKIA_FLEXILS_BLOCK_STEPS`,
  `MODIFY_NOKIA_FLEXILS_BLOCK_STEPS`) and shared step lists (`OPTICAL_NODE_TERMINATE_STEPS`,
  `OPTICAL_NODE_VALIDATE_STEPS`). **No hooks**: shipped form generators do not take `extra_form_pages`/
  `extra_summary_fields` (or similar) parameters — they are thin compositions of the shipped pages and the summary
  form. Each form ships as a page **sequence** (a `FormGenerator` that yields the `FormPage` classes in order and
  returns the collected user input as a flat dict, e.g. `create_optical_module_location_form_pages(product_name)`);
  consumers compose their own form generator by yielding from the shipped page sequence in **one line** and
  optionally interleaving their own pages:
  `user_input_dict = yield from create_optical_module_location_form_pages(product_name)`, then `yield from
  create_summary_form(user_input_dict, product_name, summary_fields)`. Page factories returning the prefilled pages
  (e.g. `modify_optical_module_location_form(subscription, block_field_name)`) are also exported for consumers that
  pick pages individually. The `optical_location` family is the reference implementation of this model; the other
  families still carry the legacy hook-style generators, mid-port. Consumers with their own model compose their own
  workflows with these parts and their own construct/store steps. Shipped create workflows pass the raw form
  generator (no `partial`): core injects `product_name`/`subscription_id` from the database at runtime.
- **Composition, not inheritance**: consumers never subclass the shipped blocks; their model has-a the shipped block
  under an attribute of their choosing. The shipped block steps bind to a per-family state key
  (`OPTICAL_NODE_BLOCK_STATE_KEY`/`optical_node_block`, `OPTICAL_COHERENT_PLUGGABLE_BLOCK_STATE_KEY`/
  `optical_coherent_pluggable_block`) and never to a consumer model. Shipped blocks are always persisted by the
  consumer's own store/`set_status` steps; the shipped block step lists end with a save step
  (`save_optical_node_block`, `save_optical_coherent_pluggable_block`) because workflow steps reload the subscription
  from the database on every step (in-memory block mutations would be lost otherwise).
- Shipped **create** steps: block-free steps (e.g. `discover_optical_node_nokia_flexils`) plus
  `populate_optical_node_<vendor>_block` (plain function = the anti-corruption point consumers call from their own
  construct step) plus a thin `@step` wrapper and a shipped `construct_optical_node_<vendor>_subscription` step that
  builds the shipped product type. Shipped **modify** form generators take `subscription_model` (defaulting to the
  shipped model class) and `block_field_name` (default `"optical_node"` or `"optical_coherent_pluggable"`).
- **Registration is the consumer's job**: this module never registers workflows itself (no `register_workflows()`,
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
- Every product family (`optical_node` ×3 vendors, `optical_coherent_pluggable`, `optical_pipe` ×3,
  `optical_spectrum_service`, `optical_digital_service`, `optical_module_location`) ships the ready-to-use workflows
  of its shipped product types (module-level decorated functions, 40 in total, listed in the README) plus the
  importable parts. There are no workflow factories or hooks anymore; `register_workflows()`/`SHIPPED_WORKFLOW_NAMES`
  are gone. Consumers register the shipped workflows with `LazyWorkflowInstance` lines in their own workflows
  package (see README); `optical_location` workflows were ported and the family ships its workflows. The
  `optical_location` family is the reference implementation of the FormPage consumption model (shipped page sequences
  + one-line `yield from` composition, no `extra_form_pages`/`extra_summary_fields` hooks); the other families still
  carry the legacy hook-style form generators, mid-port.
- Test suite: composition tests + shipped-workflow contract tests (`test/test_workflow_composition.py`,
  `test/test_optical_node_composition.py`, `test/test_optical_coherent_pluggable_composition.py`,
  `test/test_optical_module_location_composition.py`, `test/test_shipped_workflows.py`), database-free.
- The legacy `optical.old/` and the GARR admin `tasks/` workflows are there for reference only (`/hal` corresponds to old `products/services`) — do not reintroduce.
- Model files are actively being refined by maintainers: **ask before changing `products/`**; adapt code to their
  changes instead (e.g. field renames must be propagated to `hal/` and `workflows/`).
