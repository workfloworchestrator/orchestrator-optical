5 session prompts (one per fix)
Session 1 — Enforce location_code uniqueness
Goal: enforce the documented "Unique code of the location" property of the Optical
Module Location product: `location_code` must be unique across all Optical Module
Location subscriptions, not just well-formed.

Context (read these first):
- `LocationCode` type: src/orchestrator/optical/products/product_blocks/optical_location.py:12-32
  — currently validates format/length only, nothing about uniqueness.
- Form descriptions claim uniqueness: create.py:80-85 and modify.py:95-104
  ("Unique code of the location").
- The create identity FormPage is built in create.py:53-93; the modify page in
  modify.py:61-116. Block population happens in `populate_optical_module_location_block`
  (create.py:177) and `update_optical_module_location_block` (modify.py:188).

Precedent to imitate (read it): optical_coherent_pluggable/create.py:88-122 — a
`model_validator(mode="after")` on the FormPage that queries existing instances with
`subscription_instances_by_block_type_and_resource_value` (workflows/shared.py:355),
using `OpticalModuleLocationBlock.name` as the block name and the INITIAL/PROVISIONING/ACTIVE
states, and raises a ValueError naming the conflicting subscription.

Work to do:
1. Add a uniqueness check so that creating OR modifying a location with a `location_code`
   already in use fails with a clear, user-facing error (mention the conflicting code and
   subscription description/id). Decide and justify placement: recommend BOTH form-level
   validation (good UX) AND a guard in `populate_optical_module_location_block` /
   `update_optical_module_location_block` (the anti-corruption points — consumers calling
   them directly bypass form validation, so the invariant belongs there too).
2. The modify path must exclude the subscription being modified from the conflict check.
3. Document the residual TOCTOU race (form validation vs step execution) in a docstring.
   Do NOT add a DB unique constraint: the module ships no migrations (consumers generate
   them), so app-level enforcement is the scope. Note this as a known limitation.
4. Do not change `products/` (the `LocationCode` validator) unless truly necessary —
   maintainers are actively refining the models; if you must, ask first.

Constraints:
- AGENTS.md hard rules: no org-specific logic, no comments unless needed, keep exported
  `__all__` lists updated, google-style docstrings.
- Tests: add DB-free tests (mock the query helper, mirror how test_optical_module_location_composition.py
  monkeypatches). Keep all existing tests green.
- Verify: `uv run ruff check src/`, `uv run ruff format --check src/`, `uv run ty check`,
  `uv run pytest`.
Session 2 — Remove the hal → workflows layering inversion
Goal: eliminate the inverted dependency where the Hardware Abstraction Layer imports from
the workflow layer. Per project principle: hal logic must depend only on blocks, not on
subscriptions — blocks are the shared contracts.

Context:
- src/orchestrator/optical/hal/optical_node.py:48 imports `location_block_from_subscription`
  from `orchestrator.optical.workflows.optical_location.shared`; it is used at
  hal/optical_node.py:281 in the FlexILS GNE-discovery fallback (no management IPs): it loads
  the location block from a subscription id to read its coordinates.
- The same helper is used by workflows/optical_node/shared/create.py:141 and
  workflows/optical_node/shared/modify.py:48, and `active_location_subscription_selector`
  (also in workflows/optical_location/shared.py) is used by the optical_node create forms.

Work to do:
1. Make hal/optical_node.py's GNE-discovery path block-based: it must not load a
   subscription model. Resolve the location by querying the subscription instance whose
   product block is a location block and load it as the most-derived class via
   `OpticalModuleLocationBlock.from_db(...)` (core resolves the lifecycle variant — see the
   precedent comment at optical_coherent_pluggable/create.py:107-109). The location block
   remains the contract; subscription ids are only an input parameter, not a model dependency.
2. Re-home whatever `hal/` needs so that no module under `hal/` imports from
   `orchestrator.optical.workflows.*`. Choose the placement (e.g. a neutral helper module)
   and justify it; update all importers (including the two optical_node workflow files) to
   the new location, or give the node workflows their own thin subscription-based wrapper.
3. Keep the node workflow behavior identical; keep `active_location_subscription_selector`
   working for the node create forms.
4. Do not touch auto-generated services/ and do not fix unrelated pre-existing noise.

Verify: `uv run ruff check src/`, `uv run ruff format --check src/`, `uv run ty check`,
`uv run pytest`; also confirm `hal/` has no imports of `orchestrator.optical.workflows`
afterwards (grep).
Session 3 — Fail fast in load_optical_module_location_block
Goal: replace the silent-None pattern in the Optical Module Location state loading with
fail-fast behavior and precise error messages.

Context:
- shared.py:180 — `load_optical_module_location_block` uses bare
  `getattr(subscription, "optical_location", None)`, so a consumer model that does NOT
  compose the block under `optical_location` silently yields None, and the failure
  surfaces later with a generic message in a downstream step.
- Same silent fallback pattern exists in validate.py:59-60
  (`location or getattr(subscription, "optical_location", None)`) and shared.py:131
  (description helper).

Work to do:
1. Make `load_optical_module_location_block` fail fast with an explicit, actionable error
   when the subscription has no block under the expected attribute (message should name the
   attribute and state the contract: the subscription model must have-a the
   Optical Module Location block, e.g. under `optical_location`).
2. Decide the same treatment for validate.py and the description helper: fail fast with the
   same clear message instead of deferring (keep the messages consistent across the family).
3. Behavior for the shipped models is unchanged (they always have the attribute) — verify
   the shipped workflows' step order/names stay identical.
4. Add/adjust DB-free tests for the new failure mode (mirror the style of
   test/test_optical_module_location_composition.py).

Verify: `uv run ruff check src/`, `uv run ruff format --check src/`, `uv run ty check`,
`uv run pytest`.
Session 4 — Fix the return-type imprecision of location_block_from_subscription
Goal: correct the declared return type of `location_block_from_subscription` in
src/orchestrator/optical/workflows/optical_location/shared.py:53-70.

Problem: the function is annotated `-> OpticalModuleLocationBlockInactive`, but at runtime
it loads through `subscription_from_subscription` (workflows/shared.py:248), which resolves
the concrete ACTIVE model from SUBSCRIPTION_MODEL_REGISTRY — so it returns the most-derived
`OpticalModuleLocationBlock` (ACTIVE variant), not the Inactive variant. This is a typing
lie that consumers (hal, optical_node workflows) will trip over as models evolve.

Fix:
1. Change the annotation to `OpticalModuleLocationBlock` (the most-derived class, which per
   core semantics can load all lifecycle variants — see the precedent comment at
   optical_coherent_pluggable/create.py:107-109).
2. Update the docstring to state that the most-derived variant is returned and why.
3. Verify all consumers still type-check: hal/optical_node.py:281-282 (uses .latitude/
   .longitude — present on all variants), workflows/optical_node/shared/create.py:141 and
   modify.py:48 (assigned into the node block's `location` field — the Active variant is a
   subclass of Inactive, so assignments remain valid; confirm the node block field
   annotation accepts it).
4. Run `uv run ty check` repo-wide (not just the changed file) to catch downstream effects.

Verify: `uv run ty check`, `uv run ruff check src/`, `uv run pytest`.
Session 5 — Add an execution-level test safety net for the shipped workflows
Goal: add DB-backed, execution-level tests so the shipped workflows' real behavior is
verified, not just their composition. Today every test in test/ is database-free and
contract-only; the paths that will break first as models drift are never executed:
- `construct_optical_module_location_subscription` (create.py:240-262) — `from_product_id`
  on the abstract is_base `OpticalModuleLocationSubscriptionInactive` model
- lifecycle-variant resolution on reload (INITIAL → block Inactive, PROVISIONING, ACTIVE)
- `save_optical_module_location_block` after the JSON state round-trip (shared.py:183)
- description refresh (`set_optical_module_location_subscription_description`, shared.py:140)
- `store_process_subscription`, modify's PROVISIONING/ACTIVE transitions, terminate/validate

Start by reading:
- test/test_optical_module_location_composition.py and test/test_shipped_workflows.py
- pyproject.toml [tool.pytest.ini_options], testpaths, coverage fail_under=90
- AGENTS.md "Development commands" and the model-persistence quirk section

Harness constraints and open decisions (present a plan and get approval BEFORE adding
dependencies or heavy infra):
1. Database: propose how to provision PostgreSQL for tests (e.g. testcontainers-postgres vs
   docker-compose vs a local instance). The repo currently has no DB test infra and no
   testcontainers/devtools dependencies; adding dev-dependencies needs maintainer sign-off.
2. Schema: the module ships no migrations (consumers generate them) — determine how to
   create the schema in tests (orchestrator-core migration machinery vs alembic vs direct
   create_all), and how to register the shipped abstract model chain + product types so
   `from_product_id` and the registry lookups work.
3. Scope: at minimum a full create → modify → terminate → validate cycle for
   `optical_module_location` exercising every step named above; keep existing DB-free tests
   untouched and fast (new tests may be slower; propose a pytest marker and any coverage
   config adjustment, with justification).
4. The no-import-time-side-effects rule still holds: DB settings live in the harness only.

Deliver: the harness + the integration tests, all green, with `uv run ruff check`,
`uv run ruff format --check`, `uv run ty check`, `uv run pytest`.
Notes: all five briefs assume the session reads AGENTS.md first (it's loaded automatically in this repo) and respect its hard rules — no org-specific logic, no #FIXME-style side quests, products/ off-limits without asking (relevant to Sessions 1). Sessions 2 and 5 are the ones where a design decision must be confirmed before heavy work; 1, 3, 4 are bounded edits.