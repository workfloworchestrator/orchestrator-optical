# SPEC — Optical Digital Service workflows

Spec-driven contract for the shipped Optical Digital Service family
(`orchestrator.optical.workflows.optical_digital_service`).
Code MUST satisfy every normative statement below; the drift canary
(`test/unit/test_model_workflow_drift.py`) and the gates in §12 enforce it.

## 1. Purpose and scope

- The family ships ready-to-use workflows for the shipped
  `OpticalDigitalService` product type (100G / 400G / 800G Ethernet):
  `create_optical_digital_service`, `modify_optical_digital_service`,
  `terminate_optical_digital_service`, `validate_optical_digital_service`,
  `reconcile_optical_digital_service`.
- It ALSO ships importable parts (page sequences, builders, block-level
  `StepList`s) for consumers whose own model has-a the shipped block.
- Out of scope: product-block/subscription model changes (maintainer-owned,
  ask first), HAL adapter implementations, DB migrations.

## 2. Product model

Defined in `products/`.

## 3. Architecture invariants (MUST)

1. `hal/` depends only on blocks, never on workflows or subscription models.
   Device access ONLY via HAL dispatchers (`hal.transport_channel`,
   `hal.spectrum`); never adapters directly.
2. Reuse, don't duplicate: path engine, OLS selectors, port-availability
   guard, section teardown, spectrum form pages and shared constants come
   from `optical_spectrum_service` (`shared`, `create_optical_spectrum`,
   `modify_optical_spectrum`). Digital-only logic lives here.
3. All shipped block steps bind to `OPTICAL_MODULE_BLOCK_STATE_KEY` and
   assume the PROVISIONING variant with mandatory fields set (provided by the
   caller's construct step). Steps re-hydrate via
   `optical_digital_service_block_from_state`; persistence ONLY via the
   terminal `save_optical_module_block`.
4. No hooks/factories/`**kwargs`; workflow function names MUST equal the
   translation keys. No workflow registration in-module. No
   `.garr.net`/pop-codes/`fXXXcYY`/`nms_uuid`. Device identifiers are
   `subscription_instance_id` UUIDs; free-form names go to label fields only.
5. `from_product_id` is NOT used for construction: the digital block is built
   first (port blocks require their host node plus live availability checks),
   then the subscription is assembled around it under the same id via
   `new_optical_digital_service_subscription`. Speed/type are fixed inputs
   (1:1 on the product row, spread by core into the model) — never asked in a
   form; read them via `optical_digital_service_speed_and_type[_for_product]`.
6. Coherent device push raises `NotImplementedError` (explicit, temporary).

## 4. Shared module (`shared.py`) — normative parts

- `optical_digital_service_block_from_state`, `load_optical_digital_service_block`
  (reads `optical_digital_service` attr), description pair
  (`…_subscription_description` pure + `set_…_description` step).
- `DIGITAL_ENDPOINT_ROLES = [TRANSPONDER, TRANSPONDER_XOADM, IPODWDM]`;
  `optical_digital_endpoint_selector` merges transponder-role nodes and
  packet-node subscriptions (values = host subscription ids).
- `line_port_selector(host_id, client)`: the line-port Choice of an endpoint
  host's card, computed from the client selected on the client page. On a
  packet node it holds a single option: the client pluggable itself. On a
  transponder host the candidates are the patched
  `OpticalTransponderLinePortBlock`s on the same card (shelf/slot, parsed
  from the device-native client port name per platform: `port-1/2/3` on
  Groove G30, `1-4-L1` on GX G42) that are not already in use by another
  digital service, restricted to line-role suffixes (G30 ports 1-2, G42
  L1/L2). Values are instance ids. Convergence point for the future pipe
  termination of pluggables: the filter will apply here once, to both types.
- `resolve_channels_by_names(names, speed, src_host_id, dst_host_id)`:
  THE name-driven fork, used by the identity validator and re-run by the
  sequence and construct. `"new"` iff no channel carries any of the names;
  else the named channels must be all ACTIVE, share exactly one owner, cover
  the owner's whole ACTIVE group (whole groups linked, never split),
  terminate on the `{src, dst}` host pair (order-insensitive — reversed
  endpoints are accepted, channels are bidirectional), have known totals,
  and group spare ≥ speed → `"reuse"`. Every other shape raises
  `ValueError` naming the cause (duplicate names, mixed new/existing,
  in-flight use, cross-owner, partial group, termination mismatch, unknown
  capacity, overbooked).
- `unused_coherent_pluggable_selector(host_id)`: existing
  `CoherentPluggableBlock`s on the packet node minus §4-used set. The
  digital service NEVER creates a pluggable (no part_number/firmware anywhere).
  No fiber-attachment filter: pipes cannot terminate on pluggables yet, so the
  relation is inexpressible; hosted + ACTIVE is the gate until the
  pluggable-as-line convergence lands.
- `get_transceiver_capacity_from_mode(hosts, mode)`: per host through the
  HAL dispatcher (`hal.port`, match/case on vendor/platform — G30 effective
  rate map, G42 leading `<N>E.` digits, FlexILS/packet-node/unknown → None);
  hosts that resolve nothing are skipped best-effort, distinct known values
  raise `ValueError`.
- `channel_spare_capacity(channel)`: total minus non-terminated user speeds;
  None when total unknown. `reusable_channel_groups(src, dst, speed)`: ACTIVE
  channels whose line-port hosts set-match `{src, dst}`, known totals, summed
  spare ≥ speed; sorted by spare.
- `channel_name_in_use(name)`: uniqueness over INITIAL/PROVISIONING/ACTIVE.
- `ChannelReuseGroup` (ids, names, mode, total, spare): one channel or the
  coupled channels of one owning subscription; group spare is the summed total
  minus the distinct using-service speeds (a service coupled over both members
  counts once). `reusable_channel_groups` stays as the query part for
  consumers composing their own forms; the shipped form resolves names via
  `resolve_channels_by_names` instead of offering groups.
- `port_ids_used_by_digital_services()`: instance ids of ALL client+line
  ports referenced by INITIAL/PROVISIONING/ACTIVE digital services (covers
  composed types via shipped block name).
- `is_packet_node_host(host_id)`, `has_new_channels_with_sections(block)`,
  `has_flexils_sections(block)`, `is_last_client_for_channels(channels)`
  (non-terminated `in_use_by` count == 1 per channel).
- `populate_optical_digital_service_block` (anti-corruption: name/speed/type).
- `build_optical_digital_service_block(...)`: creates fresh transponder
  client blocks (re-checking availability via the spectrum guard); LINKS
  coherent client pluggables by id (re-checking the §4-used set); links
  line ports by id; links the `reuse_channel_ids` as-is (one, or a coupled
  pair) OR builds one channel per `channel_names` entry (user-typed names;
  `optical_transport_total_capacity` parsed from the mode; spectrum +
  vendor-grouped sections via
  `store_list_of_ports_into_spectrum_sections`; channel ≥2 with a packet-node
  side shares channel-1's path, otherwise derives endpoints via
  `find_add_drop_ports`). MUST raise `ValueError` if a packet-node side
  carries line ports other than the client pluggable (client==line coupling).
- `optical_digital_service_speed_and_type[_for_product]`: speed/type are fixed
  inputs — read them from the product row (by id in steps, by name in forms),
  never ask the user. `ValueError` on missing/invalid, `KeyError` on unknown
  product.
- `new_optical_digital_service_subscription(...)`: manual INITIAL assembly
  (ProductTable row + fixed inputs + explicit speed/type/block, explicit wins).
- Block steps: `configure_…_line_ports` (new channels only),
  `configure_…_client_ports`, `configure_…_crossconnects`,
  `provision_optical_digital_sections` (new only, idempotent deploy),
  `refresh_optical_digital_used_passbands` (new only; foreign ports saved
  under owners), `append_reused_channel_labels` (reused only),
  `align_optical_digital_tx_power` (FlexILS sections; adjusts outside
  [0, 1.5] dB), `modify_optical_digital_sections`,
  verify ×4, `factory_reset_…` ×3 (lines gated by last-client),
  `delete_optical_digital_sections` (gated; delegates per-channel to
  `delete_optical_spectrum_sections`), `refresh_…_after_teardown` (gated).
- `PROVISION_…_BLOCK_STEPS` (line→client→xconn→sections),
  `VERIFY_…_BLOCK_STEPS` (line→client→xconn→sections, read-only).

## 5. Create (`create.py`)

Pages (`create_optical_digital_service_form_pages`), in order:
1. Identity: `optical_digital_service_name`, `src/dst_node_block_instance_id`
   (endpoint selectors, validated different), `channel_name_1` (required,
   non-blank) + `channel_name_2` (optional — titled/described as the reverse-
   multiplexing second channel, leave empty for single-carrier). The names ARE
   the fork: the validator runs `resolve_channels_by_names` (speed from the
   product's fixed inputs); coupling = "`channel_name_2` filled in". No
   reverse-multiplexing bool anywhere. Speed/type NOT asked, NOT in state.
2. Clients: `unused_src_client`/`unused_dst_client` (REUSED generic
   `optical_port_selector(host, [TRANSPONDER_CLIENT])` on transponder sides —
   live device enumeration minus used names, fail loudly when unreachable;
   pluggable Choice on packet-node sides; freshness re-checked).
   Reuse resolves here at the latest: named-existing channels skip every
   later page straight to summary.
3. Lines (new channels only): `src_lines`/`dst_lines` (`choice_list`,
   min=max=1|2 per name count, `unique_items=True`, values = instance ids),
   always both fields — each side's Choice comes from
   `line_port_selector(host, client)`, so a packet-node side offers its
   pluggable as the single option (no auto-injection, no special cases).
   Validator only re-checks availability.
4. New channels only (`_yield_new_channel_spec_pages` helper generator):
   channels page (shared `mode` best-effort live check,
   `frequency_N`/`bandwidth_N` `% 12500 == 0` — names already known from page
   1), REUSED waypoints page (`intermediate_node_ids`, `LINE_SYSTEM_ROLES`),
   REUSED constraints page, path page via `optical_digital_service_path_choice`
   (trx ends → add/drop resolve → direct-connection special case →
   `all_shortest_paths_through_waypoints` on the add/drop hosts → wrap as
   `[line, *ols, line]` (engine-identical shape, `build` untouched) →
   `human_readable_transport_channel_path_selector`; any failure →
   rejecting placeholder).
- Generator = customer page + page sequence + summary (dynamic fields:
  always customer/name/nodes/channel names/clients; plus `reuse_channel_ids`
  when reused, else lines + spec keys; speed/type never shown — the product
  implies them).
- `construct_optical_digital_service_subscription`: `uuid4` →
  speed/type from product fixed inputs → names from state (count = coupling)
  → authoritative `resolve_channels_by_names` → `build_…` (links group or
  builds named channels; lines/freqs optional, required only when new) →
  manual subscription → `from_other_lifecycle(PROVISIONING)` →
  `{subscription, subscription_id, KEY: block}`.
- Settle step sleeps 30s only with new channels holding sections.
- `CREATE_…_BLOCK_STEPS` = configure×3 → provision → refresh → append-labels
  → settle → align → save.
- Workflow = construct → PROVISIONING → BLOCK_STEPS → description → store.

## 6. Modify (`modify.py`)

- Scope is FROZEN: frequencies, bandwidths, mode only. Ports, path and
  carrier count MUST NOT change (`update_…` raises on count mismatch).
- Prefilled single/dual form (bandwidth `% 12500` re-checked);
  generator adds customer + before/after summary.
- `update_optical_digital_service_block` rewrites freq/passband
  (`freq ± bw/2`)/mode, re-derives `optical_transport_total_capacity` from the
  new mode on service-owned channels only (reused keep the owner's
  accounting), returns `old_passbands` for circuit modify.
- Settle step sleeps 10s only with FlexILS sections (shared predicate).
- `MODIFY_…_BLOCK_STEPS` = update → configure×3 → modify-sections →
  refresh → settle → align → save.
- Workflow = PROVISIONING → load → BLOCK_STEPS → description → ACTIVE.

## 7. Terminate (`terminate.py`)

- Confirmation-only form (`DisplaySubscription`; `customer_id  # noqa: ARG001`).
- `TERMINATE_…_BLOCK_STEPS` = load → reset xconn → reset clients →
  reset lines (last-client gate) → delete sections (gate) →
  refresh-after-teardown (gate) → save.

## 8. Validate (`validate.py`) and reconcile (`reconcile.py`)

- Validate: load → `VERIFY_…_BLOCK_STEPS` → description. Read-only (no save).
- Reconcile: load → PROVISION + refresh + save + VERIFY → description.
  No input, no status change.

## 9. Coherent coupling rule (normative)

A coherent pluggable is simultaneously client and line. Therefore on a
packet-node side the lines page offers the client pluggable as its single
option (no separate selection exists), and the build enforces the coupling
with `ValueError`. Transponder sides select client names and same-card line
blocks independently.

## 10. Reuse and sharing rules (normative)

- No fork page, no group picker, no bool: the channel names typed on page 1
  ARE the fork (`resolve_channels_by_names`, §4). All-new → build; all named
  covering exactly one owner group with fitting spare → link the whole group
  (never split: name 1|2 channels, get 1|2 linked); anything else errors.
  Reversed endpoints are accepted (order-insensitive match).
- New channels: full device push. Reused channels: NO line/section/passband
  push, ONLY label append.
- Teardown of lines/sections/passbands runs ONLY for the last
  non-terminated client (`is_last_client_for_channels`); xconn/client reset
  ALWAYS runs.

## 11. Translations (`translations/en-GB.json`)

Keys MUST equal workflow names: `create/modify/terminate/validate/reconcile_optical_digital_service`.

## 12. Tests and gates (MUST stay green)

- `test/unit/test_model_workflow_drift.py`: `populate_…`,
  `build_optical_digital_service_block`, `update_optical_digital_service_block`
  MUST have WRITERS entries with exact field paths; any new
  `populate_/update_/build_` function MUST be added (or excluded with reason).
- `test/support/devices.py` `ods` family: stub targets MUST exist as module
  attributes (device calls imported by name into `shared`/`create`/`modify`).
- Gates: `ruff check` + `ruff format --check`, `ty check`, `pyrefly check`,
  import smoke (`python -c "import …"` with zero env vars), `pytest test/unit`.
