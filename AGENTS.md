# AGENTS.md — Workflow Orchestrator (WFO) Optical Module

## What this project is

An addon module for [Workflow Orchestrator](https://workfloworchestrator.org) (built on
[`orchestrator-core`](https://github.com/workfloworchestrator/orchestrator-core) >= 5.6) that models and provisions
optical transport equipment: Nokia **FlexILS** (TL1 over SSH), **Groove G30** and **GX G42** (NETCONF).

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
│   │   │                         #     + juniper_mx204 (model-only, unregistered) + optical_packet_node (nested use;
│   │   │                         #     standalone packet-node product ships no workflows)
│   │   ├── optical_port/     #     abstracts.py + one file per port role (ols_add_drop, ols_line, transponder_client, transponder_line), unions.py
│   │   ├── optical_pipe/     #     abstracts.py + fiber_span / fiber_patch / leased_spectrum + unions.py
│   │   └── …                 #     optical_spectrum.py, optical_spectrum_section.py, optical_transport_channel.py,
│   │                         #     optical_digital_service.py, optical_location.py, optical_packet_node.py,
│   │                         #     optical_coherent_pluggable.py
│   ├── product_types/        #   Subscription models (same Inactive/Provisioning/Active pattern); does NOT 1:1 mirror
│   │                         #   the blocks (no spectrum/section/transport_channel types — consolidated
│   │                         #   optical_spectrum_service.py; no unions.py under optical_pipe/)
│   └── __init__.py           #   ProductName + ProductType enums, SUBSCRIPTION_MODEL_REGISTRY update
├── hal/                      # Hardware Abstraction Layer: device-facing operations (per-vendor code under adapters/)
│   ├── __init__.py           #   public surface: re-exports the area dispatchers below
│   ├── _common.py            #   vendor/platform dispatch key, block narrowing, shared errors, port-role helpers
│   ├── node.py               #   client/discovery access + node-level retrieve/validate dispatchers
│   ├── port.py               #   port enumeration (incl. get_device_ports_by_role) / admin state / fiber-termination
│   │                         #   configure-reset-check keyed by (local port role, pipe type)
│   ├── spectrum.py           #   FlexILS optical-circuit engine (OEL/OSNC/OCRS); no-ops on G30/G42
│   ├── connectivity.py       #   intra-node routes add/drop port -> reachable degrees (+ occupancy), IntraNodeEdge;
│   │                         #   FlexILS: RTRV-SCG PROVNBRTP + RTRV-EQPT card rules + RTRV-OCRS; G30: fiber-connection
│   ├── transport_channel.py  #   transponder line/client/crossconnect config + validation + power alignment
│   ├── reconcile.py          #   declarative config of the NETCONF devices (G30/G42): Fragment, diff/verify/apply/
│   │                         #   release on the SDK primitives + the applied-config record (golden config per node)
│   └── adapters/             #   per-device implementations: nokia_flexils (TL1) / nokia_groove_g30, nokia_gx_g42 (NETCONF);
│                             #   each imports its vendor SDK only in `_sdk.py` (the SDK contract); SDK-free helpers
│                             #   live in naming.py / gne.py / constants.py; G30/G42 `config.py` = client + release rule
├── workflows/                # WFO workflows of the shipped product types (ready-to-use) + importable parts
│   ├── __init__.py           #   docs the consumption model (register shipped workflows with LazyWorkflowInstance,
│   │                         #   compose your own with the parts)
│   ├── shared.py             #   selectors, summary forms (form-layer; DB queries live in db.py)
│   ├── optical_node/         #   per-vendor create/modify workflows + parts; terminate/validate workflows are
│   │                         #   per-vendor thin wrappers over shared step lists (shared/terminate.py, shared/validate.py)
│   ├── optical_pipe/         #   fiber_span / fiber_patch / leased_spectrum (workflows + parts)
│   ├── optical_spectrum_service/   #  path-finding engine (shared.py) + workflows
│   ├── optical_digital_service/    #  4-form create + modify/terminate/validate + reconcile (identity/client/lines/channels/waypoints/constraints/path/frequencies pages)
│   ├── optical_coherent_pluggable/ #   create/modify/terminate/validate workflows + parts + shared helpers
│   │                         #   (block-based, state key OPTICAL_MODULE_BLOCK_STATE_KEY)
│   └── optical_location/     #   reference family: workflows + parts (selectors/helpers)
├── settings.py               # pydantic-settings, env prefix OPTICAL_, lazy get_settings()
├── db.py                     # neutral DB query helpers + block resolution shared by hal/ and workflows/ (blocks as contracts)
│                             # + the `optical_applied_config` table (model and helpers)
├── translations/en-GB.json   # workflow display strings (1:1 with registered workflows)
└── utils/                    # custom_types (dns Pqdn/Fqdn, coordinates, frequencies, ip_address), datadiff (FlexILS),
                              # singledispatch (legacy helpers only — dispatch uses match/case, never reintroduce it)
```

## How users consume it (see README.md)

1. `uv add orchestrator-optical` in their WFO deployment.
2. Until 1.0, provision the catalog with the orchestrator-core CLI wizards
   (`migrate-domain-models` + `migrate-workflows`); a baseline revision is kept in
   `migrations/versions/schema` for development and drift detection but is not yet a stable
   upgrade path (see README.md "Database migrations").
3. The module is a **work in progress** (ported from a GARR-specific implementation): model files are still being
   finalized and may change between releases.

## Core conventions (follow these in every session)

### Data model pattern

- Every block/subscription has three lifecycle classes: `XInactive` → `XProvisioning` → `X` (ACTIVE), using
  `lifecycle=[SubscriptionLifecycle.X]`; `product_block_name=*`(`is_base=True`) is required on blocks(subscriptions)
  that are persisted. Abstract blocks and subscriptions do not have those args.
- Field names are `optical_*`-prefixed and descriptive (`optical_port_name`, `optical_transport_central_frequency`).

#### Persistence quirk (orchestrator-core 5.1.3–5.6.0, verified unchanged)

`ProductBlockModel._find_special_fields` persists **only fields declared directly in a class body** — any inherited
field (from an abstract base or from a concrete sibling in the same chain) is silently dropped on save and missing on
reload. It fills two class dicts: `_non_product_block_fields_` (scalar values) and `_product_block_fields_` (block
references), both computed from the class's own annotations. Therefore: **every concrete block class must redeclare
every field it inherits**, or reloads will crash with ValidationError. The four base `ProductBlockModel` fields
(`name`, `label`, `subscription_instance_id`, `owner_subscription_id`) are exempt — core passes them explicitly.

This rule is fully applied: all 19 concrete block chains redeclare every inherited field. Any new block must follow the rule.

- Product-block fields must **not** use `Annotated`-wrapped discriminated unions (`Annotated[Union[...],
  Field(discriminator=...)]` or `Discriminator(fn)`): core's (5.1.3–5.6.0) `is_list_type`/`is_union_type`/`is_of_type`
  cannot see through `Annotated`, so such fields are misclassified as scalar strings (silently saved as `repr()`,
  ValidationError on reload). The union aliases in `optical_port/unions.py` and `optical_node/unions.py` are plain
  `Union[...]` on purpose — keep them plain (disambiguation is done by the `enforce_*` model validators).
- A block with a `@computed_field` that loads its owner subscription from the DB
  (`optical_coherent_pluggable_part_number`) requires an explicit `subscription.save()` in the construct step
  **before** the in-step `from_other_lifecycle` transition: the transition serializes the block (`model_dump()`
  evaluates the computed field) and the subscription/instance rows must already be persisted
  (see `construct_optical_coherent_pluggable_subscription`).

### Dispatch

- Vendor/Platform dispatch is achieved in `hal/` with `match/case` wrt the enums in `optical_node_management.py`.
  Dynamic registration using singledispatch was removed — never reintroduce it.

### Declarative device configuration (Groove G30, GX G42)

- The G30/G42 adapters never push configuration imperatively. Each object (line port, client port, cross-connect,
  fiber termination, description, admin state, TX power) has **one** `render_*` function returning
  `hal.reconcile.Fragment`s (`fragment(navigator_node, **leaves)`); configure / validate / factory-reset are that
  rendering handed to `apply_config` / `verify_config` / `release_config`. Never add a second code path that writes
  or compares the same object (no `navigator.update(...)`, no hand-built expected dicts).
- The diff is computed with the SDK primitives only: fragments and the model read from the device are flattened with
  `model_dump_instances()`, classified by `client.diff_instances()`, sent with `client.reconcile()`.
  `model_validate_instances()` is not used: it validates a whole node and the fragments are partial (e.g. the G30
  `och-os` has mandatory leaves), so `fragment()` validates leaf by leaf (`model_construct` + assignment).
- **Never let the SDK infer a removal.** `diff_instances` collapses a removed path to its highest wholly-removed
  ancestor (up to the datastore root when nothing is intended under it). `reconcile.py` restricts the running map
  to the rendered paths (so `removed` is always empty) and builds releases itself from the adapter's
  `release_rule(path)`: `Reset(value)` (factory value of a leaf), `DeleteEntry(path)` (a list entry the module
  created: G30 `CRS`, G42 `xcon` / `super-channel`) or `None` (leave alone).
- Every apply is recorded in the `optical_applied_config` table, one row per **(node, path, owner block)** plus the
  `scope` (rendering unit of the owner: `line`, `client:<port>`, `crossconnect:<port>`, `tx-power:<port>`,
  `termination`, `description`, `admin-state`). Rows mean *applied*, never *desired* (always re-rendered from the
  blocks); they are written only after the device converged. The rows of a node are its golden config
  (`hal.golden_config`). A path may be held by several owners with the same value (released from the device when
  the last one releases it); a different value from another owner is a `ConfigConflictError` before any edit.
- Owners: the Optical Port block for port-level config (`hal/port.py`, signatures unchanged), the Optical Digital
  Service block for transponder config (`owner_instance_id=` keyword of the `hal/transport_channel.py` dispatchers).
- Fragment key leaves are dropped (the SDK edit builder would emit them twice); `stage=` orders the edits for
  objects the device only creates after another one is configured (G30 `och-os`/`eth*` after `port-mode`, G42
  `tom` → `trib-ptp` → `ethernet`, optical carriers after their super-channel).
- Renderers are pure given the SDK data root (`client.data`, or an unconnected `Data(None)` in tests), except the
  cross-connects, whose keys only the device knows (G30 free ODU, G42 RPC-created `xcon`).
- FlexILS (TL1) is not declarative: it keeps its hand-written engine.

### FlexILS TL1 client (generated SDK)

- `flexils_tl1` is the client **generated** by `nokia-flexils-tl1-codegen` (`flexils-tl1 generate`) from the vendor
  command reference: typed per-command methods (`rtrv_scg`, `ed_osnc`, `rmv`/`rst`/`rtrv_pm` with the AID type as
  first argument), every reply value a raw string. Method and parameter names are the reference's, quirks included
  (the admin-state slot is `pst`, but `srcnodename` on `ED-OEL` and `applicable` on `ENT-OEL`).
- `nokia_flexils/_shared.py` is the only place adapting it: `FlexilsClient` (generated surface + SDK runtime, plus
  `tid`/`gne_ip` and the rule that a denial holding `ALREADY` is a success), `_flexils_client` (cached per
  `(tid, gne_ip)`, credentials and host-key policy from the settings through an explicit `SshTransport`),
  `_records(response)` (wire-keyed dicts the engine works on: `""` for an empty value, `_LIST_KEYS` split on
  `&`/`&-`, slots the surface leaves unnamed as `TYPE`/`PST`/`SST`), `_tl1_quoted` / `_tl1_list` for request values.
  Engine policy the old client hid in its models (ENT-OEL / ENT-OSNC defaults) is explicit in `spectrum.py`
  (`_OEL_DEFAULTS`, `_OSNC_DEFAULTS`).
- `test/contract/test_flexils_tl1.py` pins the exact bytes of every command the adapter sends (real SDK over its
  `FakeTransport`, helpers in `test/support/tl1.py`): add the case when adding a command, and run it after
  regenerating the SDK.

### Layering (hal and pages depend on blocks, never on workflows/subscriptions)

- `hal/` implements device-facing logic (aka drivers) and depends only on public **blocks** — these are the shared
  contracts between the module and its consumers — never on subscription models: no module under `hal/` may import from
  `orchestrator.optical.workflows.*` or from `orchestrator.optical.products.product_types.*`. Subscription ids are
  acceptable input parameters, but they are resolved to blocks (never to subscription models), via the neutral DB query
  helpers in `orchestrator/optical/db.py` — the shared home for database queries used by both `hal/` and `workflows/`.
  Queries use SQLAlchemy 2.x `select()` executed on `db.session` (`db.py::_all` / `_one_or_none`); never the legacy
  `Model.query` / `db.session.query()` API (deprecated in core 5.5, removed in v6).
- Shipped `*_form_pages` (the public form surface) follow the same rule: they depend only on shipped **blocks** plus
  scalar ids (`product_name`, `subscription_instance_id` / `exclude_subscription_id`, `customer_id` include). They never
  take `subscription: SubscriptionModel`, `block_field_name`, or `subscription_model`, and never import from
  `product_types`. Full subscription objects appear only in private code: shipped `*_form_generator`, `construct_*`
  steps, and `@*_workflow` functions, which are bound to the shipped subscription models.
- Selectors emit block ids (`subscription_instance_id`), query via the `db.py` block helpers (`pipe_blocks_all`,
  `pipe_blocks_by_types`, `subscription_instances_by_block_type*`), never via product-type strings or
  `SubscriptionTable.subscription_id`. Resolvers are `node_block_from_instance` / `ProductBlockModel.from_db`, never
  `*_block_from_subscription`. Selectors never load blocks: option values come from the instance query and labels
  either from the stored resource values (`subscription_instance_values_by_instance_ids_and_resource_type`, e.g. the
  pipe name — a constant number of queries however many blocks exist) or, when the block has no simple identifying
  field of its own, from the owner subscription's description
  (`subscription_instance.subscription.description`, as `active_instance_selector_by_block_type` does for packet
  nodes, whose identity lives in the management sub-block). Either way, never N+1 `from_db` loads.

### Hard rules (generalization invariants)

- **No** `.garr.net`, pop codes, `fXXXcYY` naming, `garrxdb_id`/`netbox_id`/`nms_uuid` — anywhere.
- Device-side identifiers (OEL/OSNC/OCRS AIDs, CKTIDSUFFIX, `optical_transport_channel_name`) are
  `subscription_instance_id` **UUID strings**; user-provided free-form names go to the device **label** fields.
- Customer (`customer_id`) of a subscription is obtained using a choice selection where the function returning 
  the type[Choice] is defined in the user code-space and passed to this module via the `OpticalSettings`.

### Configuration

- All env-driven config lives in `settings.py` (`OPTICAL_`-prefixed; e.g. `OPTICAL_FLEXILS_USER`,
  `OPTICAL_G30_VERIFY`). **No import-time side effects**: importing any module must work with zero env vars.
  Use `get_settings()`; keep clients lazy (built on demand by the `hal/` client factories).
- **Vendor SDKs are external and confidential**: `flexils_tl1`, `g30_4_8_0`, `g42_8_0_2` (yang2sdk NETCONF, named after the firmware release) live under the
  gitignored `sdks/` (installed editable by `just sync` / `just sdks`) and are never committed or re-added under
  `src/`. They never import `orchestrator.optical.*`: credentials and verify policy are explicit client arguments,
  passed from the settings by the `hal/` factories (`get_g30_client`, `get_g42_client`,
  `nokia_flexils/_shared.py::_flexils_client`; the generated FlexILS SDK could fall back to its own
  `FLEXILS_TL1_*` variables, so that factory refuses to build a client without the settings' credentials).
- Only `hal/adapters/<device>/_sdk.py` imports an SDK (re-exporting the names used; missing SDK →
  `VendorSdkNotInstalledError`). The area dispatchers hold adapters through `_common.LazyAdapter` (real import under
  `TYPE_CHECKING`), so `import orchestrator.optical.*` works with no SDK installed: never import an adapter module
  eagerly from `hal/<area>.py`, `hal/__init__.py` or `workflows/` (SDK-free values go in `naming.py`/`gne.py`/
  `constants.py`, re-exported by the area module). Cross-device adapter calls are local imports.
- Tests needing an SDK (directly or through an adapter) start with `pytest.importorskip("<sdk>")`.

### Workflows

- The module ships the **ready-to-use workflows of the shipped product types**: one module-level
  `@create_workflow`/`@modify_workflow`/`@terminate_workflow`/`@validate_workflow`-decorated function per product
  (plus a `@reconcile_workflow` for each optical pipe family and for the Optical Spectrum and Optical Digital
services), where each is a
  plain function
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
  (e.g. `modify_optical_module_location_form(block, exclude_subscription_id=...)`) are also exported for consumers that
  pick pages individually. The `optical_location` family is the reference implementation of this model; the
  `optical_node`, `optical_pipe`, `optical_coherent_pluggable` and `optical_spectrum_service` families follow it, and
  `optical_digital_service` follows it as well. Consumers
  with their own model compose their own workflows with these parts and their own construct/store steps. Shipped create
  workflows pass the raw form generator (no `partial`): core injects `product_name`/`subscription_id` from the database
  at runtime.
- Public surface of a family is its `*_form_pages` page sequences and its `*_BLOCK_STEPS` lists
  (+ `populate_*_block` helpers). Private (shipped-product only) are the `@*_workflow` functions, `*_form_generator`
  (thin `customer_choice_form_page` + pages + summary compositions, never reused by consumers), `construct_*` steps,
  and `load_*_block` shipped-attribute wiring. Page signatures per family (prefilled from the block at any nesting
  depth — `block = subscription.optical_module_block` or `subscription.router.optical_module`; shipped code never
  traverses the subscription, the consumer extracts with plain Python):
  `create_*_form_pages(product_name)` everywhere;
  `modify_*_form_pages(block, *, exclude_subscription_id=None)` for location and nodes;
  `modify_*_form_pages(block, *, product_name)` for spectrum and digital services;
  `modify_*_form_pages(block)` for pipes and coherent pluggables;
  `terminate_*_form_pages(subscription_id)` everywhere.
  Pages never collect `customer_id` (generators do, via `customer_choice_form_page`). `*_BLOCK_STEPS` bind
  `optical_module_block` (PROVISIONING, terminal `save_optical_module_block`) — except reconcile (`save` then `verify`)
  and validate (read-only).
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
- Every generator handed to `initial_input_form=` is decorated with `workflows/shared.py::retryable_form`: an
  unexpected error raised between two pages or inside a page validator is reported as a validation error of the
  page just submitted (HTTP 400, the user can submit again or go back) instead of an HTTP 500 that loses the form.
  Decorate any new form generator; consumers composing their own generator from the `*_form_pages` decorate theirs.
- Keep the display strings in `translations/en-GB.json` (keys are the shipped workflow function names); they apply
  when consumers keep the shipped workflow names, otherwise they are a reference for consumers' own translations.
- `from_product_id` is unusable for pipes and digital services (required fields/validators) — those workflows
  assemble the subscription manually (see `optical_pipe/shared.py::new_optical_pipe_subscription`).
- Some terminate/deprovision steps are deliberate stubs returning `{}` (framework signatures keep `customer_id` →
  `# noqa: ARG001`).

## Development commands

```bash
just sync                         # install/sync virtual environment (uv sync --all-groups)
just lint                         # ruff check + format check (line-length 120, google docstrings); ported code must be 0-findings
just typecheck                    # ty + pyrefly (pyrefly is the harder gate)
just test-fast                    # DB-free test lane
just test-db                      # DB-backed test lane (needs Postgres)
just coverage                     # DB-free lane + per-family coverage ratchet
just pytest <args>                # passthrough, e.g. just pytest -vx -k foo
uv run python -c "import orchestrator.optical.<module>"   # import smoke (no env vars required)
uv build                        # package build
```

### Development mindset

> [!IMPORTANT]
> Always leave the code of this module more usable, maintainabile, and evolvable than you found it (KISS, YANGI, SOLID).
> If you find minor things that takes less than 5 seconds to fix, just fix them.
> Otherwise, always report for future sessions.

### Open points of the FlexILS generated client (report progress here)

- **Not yet verified on a lab node.** Versus the previous client the wire differs only in: trailing empty blocks no
  longer sent on 18 command shapes (`RTRV-OTS:tid:aid:ctag;` instead of `...:ctag::::;`), and `OELSOURCE=manual`
  (the reference's case) instead of `MANUAL`.
- The SDK copy under `sdks/flexils_tl1` carries **one local kernel patch** (`protocol/serializer.py::_is_quoted`,
  `<` instead of `<=`): unpatched, the empty quoted value `""` (used to clear `LABEL` / `PROVOWREMPTP`) is escaped
  and two literal quote characters are written on the node. To be fixed in the generator's kernel; the contract
  cases `ed-ots-clear-label` / `ed-scg-reset` fail on an unpatched SDK.
- `RTRV-SCG` is sent without the card-type filter in `_find_fbm_port_if_fmm_port` (the previous client silently
  dropped it); `rtrv_scg(ctype="FBM")` would narrow the read but was never sent to a node.

### Known pre-existing noise (do NOT "fix" these as a side quest)

- `ARG001` on terminate-form `customer_id`/`subscription` params in stub steps.

### Open points of the declarative configuration (report progress here)

- **Not yet verified on a lab device** (only against the fake NETCONF manager): that G30/G42 report every rendered
  leaf back unchanged (empty re-diff after apply), that a staged edit per object is accepted, and that the reset
  values of the release rules are accepted. Run reconcile on a lab G30 and G42 before relying on it.
- Subscriptions provisioned before the table existed have no rows: run their reconcile workflow once to record
  them. Releases also cover what the block still renders, and `is_last_client_for_channels` still guards shared
  line ports, so terminating an unrecorded service behaves as before.
- The recorded TX power (`tx-power:<port>` scope) is stored but not yet re-verified by the validate workflows.
- G30 amplifier settings are applied with the termination but excluded from `check_fiber` and from the release
  (they are tuned on the device afterwards).

### Current status (branch `porting/workflows`)

- The legacy `optical.old/` tree and the GARR admin `tasks/` workflows were removed (`/hal` corresponds to old `products/services`) — do not reintroduce.
- Model files are actively being refined by maintainers: **ask before changing `products/`**; adapt code to their
  changes instead (e.g. field renames must be propagated to `hal/` and `workflows/`).
- workflows: done create,modify,validate,terminate for `optical_location`; create,modify,validate,terminate for the 3
  optical nodes (FlexILS, G30, G42); create,modify,validate,terminate + reconcile for the 3 optical pipes
  (`fiber_span`, `fiber_patch`, `leased_spectrum`); create,modify,validate,terminate + reconcile for
  `optical_spectrum_service`
  (the path engine builds a frequency-agnostic graph from fiber spans + patches + leased spectra but only OLS
  `OLS_LINE`/`OLS_ADD_DROP` ports, returns the K shortest loopless paths by hop count (Yen, `OPTICAL_PATH_K`,
  default 5) with ordered waypoints, restricts the source/destination degrees to those the add/drop port reaches
  internally (`hal.retrieve_add_drop_connectivity`, live from the device), splits Groove G30 nodes into one
  vertex per shelf (a port on shelf X only connects to shelf X; FlexILS express nodes are any-to-any), and only
  then computes the free frequencies of the chosen path (line ports + endpoint internal routes) for the frequency
  page; the chosen path is split into single-platform sections at the add/drop ports); create,modify,validate,terminate + reconcile for `optical_digital_service`;
  create,modify,validate,terminate for `optical_coherent_pluggable`. Model-only / no shipped workflows:
  `JuniperMx204` (unregistered) and the standalone packet-node product (compose the packet-node block instead).
