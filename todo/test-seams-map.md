# Device-facing test seams map

Scope: the device-facing layers of `orchestrator-optical` (`hal/`, `services/`), the custom
types and `settings.py`. This is a map for writing **unit / contract** tests. It records, with
exact `file:line` references and signatures, where the pure logic is (testable directly) and
where the I/O seam is (testable by faking one transport/client). No test code here.

Conventions used below:

- **PURE** = no network/DB/SSH; deterministic function of its arguments. Test directly.
- **I/O** = reads/writes a device, DB or socket. Test by injecting a fake at the noted seam.
- **Dispatch** = `match/case` on `_vendor_platform(...)`; narrows to a vendor block then calls
  the adapter. Pure except that it raises `UnsupportedPlatformError` in `case _`.
- Import convention: area modules and adapters import the client factory **by name** into their
  module globals (e.g. `hal/adapters/nokia_flexils/port.py:16` imports `get_flex_client`), so
  tests must monkeypatch the **adapter module attribute**, not the `_shared` definition.
- Run lanes: default `pytest` is DB-free (`-m 'not db'`); `pytest -m contract`; `pytest -m db`.
  Markers are registered in `pyproject.toml:213-218` (`noautofixt`, `db`, `contract`, `unit`).

---

## 1. `src/orchestrator/optical/hal/_common.py` — pure helpers

All functions here are PURE except that `_ports_by_role` calls an injected callback. This is the
highest-value unit-test target: no device, no DB.

| Line | Symbol | Signature | Notes |
|---|---|---|---|
| 29 | `ROLE_ORDER` | `tuple[OpticalPortRole, ...]` | Canonical deterministic role order. |
| 38 | `UnsupportedPlatformError` | `class (NotImplementedError)` | Raised by every area dispatcher `case _`. |
| 42 | `UnsupportedPortRoleError` | `class (NotImplementedError)` | Raised by `_ports_by_role` and vendor `port_names_for_role`. |
| 46 | `_ports_by_role` | `(supported_roles: frozenset[OpticalPortRole], port_names_for_role: Callable[[OpticalPortRole], list[str]], roles: list[OpticalPortRole] | None) -> list[str]` | PURE if callback is pure. `None` selects `ROLE_ORDER ∩ supported_roles`; explicit unsupported role -> `UnsupportedPortRoleError`; result de-duplicated via `dict.fromkeys`. |
| 79 | `_vendor_platform` | `(optical_node_block: AnyOpticalNodeBlockProvisioningUnion) -> tuple[Vendor, Platform]` | PURE; reads `management.optical_module_node_vendor/platform`. |
| 87 | `_node_id` | `(optical_node_block) -> str` | PURE; fqdn or `"<no fqdn>"`. |
| 93 | `_same_node` | `(node_a, node_b) -> bool` | PURE; identity or equal non-None fqdn. |
| 105 | `_as_flexils_block` | `(optical_node_block) -> NokiaFlexIlsBlockProvisioning` | PURE narrowing; `TypeError` on mismatch. |
| 113 | `_as_g30_block` | `(optical_node_block) -> NokiaGrooveG30BlockProvisioning` | PURE narrowing; `TypeError`. |
| 121 | `_as_g42_block` | `(optical_node_block) -> NokiaGxG42BlockProvisioning` | PURE narrowing; `TypeError`. |
| 129 | `_port_name` | `(port_block: AnyOpticalPortBlockProvisioning) -> str` | PURE; `ValueError` when name is `None`. |
| 138 | `_extract_remote_port_id` | `(port_name: str) -> str` | PURE; `ValueError` when no digit; replaces non-alphanumerics with `-`. |
| 159 | `_as_decimal` | `(value: Decimal | float | str) -> Decimal` | PURE; `TypeError` otherwise. |

---

## 2. Area dispatchers (`hal/{node,port,spectrum,transport_channel}.py`) and adapters

### 2.1 Area dispatchers — pure dispatch + narrowing; device I/O downstream

Every function below dispatches on `_vendor_platform` and raises `UnsupportedPlatformError` in
`case _`. They are directly testable for the dispatch matrix (wrong vendor/platform -> typed
error) by faking the adapter module function.

**`hal/node.py`** (`__all__` at line 40)

| Line | Signature | Seam / notes |
|---|---|---|
| 55 | `get_optical_node_client(optical_node_block) -> FlexilsClient | G30Client | G42Client` | Calls `get_flex_client` (probes device) or `get_g30_client`/`get_g42_client` (pure construction). |
| 81 | `retrieve_software_version(optical_node_block) -> str` | Adapter `software_version`. |
| 106 | `retrieve_optical_node_role_and_software_version(optical_node_block) -> tuple[OpticalNodeRole, str]` | G30/G42 call two adapter funcs. |
| 135 | `retrieve_omses_terminating_on_device(optical_node_block) -> list[dict[str, Any]]` | G30/G42 return `[]` without I/O. |
| 160 | `retrieve_ports_spectral_occupations(optical_node_block) -> dict[str, list[tuple[int, int]]]` | G30/G42 return `{}` without I/O. |
| 185 | `validate_management_network_config(optical_node_block) -> None` | FlexILS logs a warning; G42 is a no-op; only G30 does I/O. |

**`hal/port.py`** (`__all__` at line 30)

| Line | Signature | Notes |
|---|---|---|
| 42 | `get_device_ports_by_role(optical_node_block, roles: list[OpticalPortRole] | None = None) -> list[str]` | FlexILS/G30/G42 adapter enumeration. |
| 78 | `retrieve_transceiver_modes(optical_node_block, port_name: str) -> list[str]` | FlexILS returns `[]`; G30/G42 do I/O. |
| 104 | `set_port_description(optical_port_block, port_description: str) -> dict[str, Any]` | Host node from `optical_port_block.optical_port_host_node`. |
| 131 | `set_channel_description(optical_node_block, facility_id: str, description: str) -> dict[str, Any]` | FlexILS returns a `{"not-applicable": ...}` dict. |
| 162 | `set_port_admin_state(optical_port_block, admin_state: Literal["up","down","maintenance"]) -> dict[str, Any]` | |
| 192 | `configure_termination_when_attaching_new_fiber(optical_port_block, remote_port_block, pipe_type: OpticalPipeType) -> dict[str, Any]` | G30/G42 ignore `pipe_type`. |
| 228 | `factory_reset_port_configuration(optical_port_block, remote_port_block, pipe_type) -> dict[str, Any]` | G30/G42 ignore `pipe_type`. |
| 261 | `check_fiber_terminating_port(optical_port_block, remote_port_block, pipe_type) -> None` | |

**`hal/spectrum.py`** (`__all__` at line 31) — FlexILS-only engine; G30/G42 are no-ops/`NotImplementedError`.

| Line | Signature | Notes |
|---|---|---|
| 42 | `deploy_optical_circuit(optical_node_block, optical_spectrum_section_block, optical_spectrum_name, passband: Passband, carrier: tuple[Frequency, Bandwidth], label: str | None = None, circuit_identifier: str = "") -> dict[str, Any]` | G30/G42 return `not-applicable` dicts. |
| 92 | `modify_optical_circuit(..., old_passband: Passband | None = None, circuit_identifier: str = "") -> dict[str, Any]` | |
| 149 | `delete_optical_circuit(..., circuit_identifier: str = "") -> dict[str, Any]` | |
| 192 | `validate_optical_circuit(..., label: str, circuit_identifier: str = "") -> None` | G30/G42 return `None`. |
| 235 | `append_optical_circuit_label(source_optical_node_block, ..., label: str, circuit_identifier: str = "") -> dict[str, Any]` | |
| 281 | `create_optical_cross_connection(optical_node_block, from_port, to_port, passband, carrier=None, label=None, circuit_name=None, circuit_identifier="") -> dict[str, Any]` | G30/G42 raise `NotImplementedError`. |
| 335 | `delete_optical_cross_connection(...) -> dict[str, Any] | TL1BaseResponse` | G30/G42 raise `NotImplementedError`. |

**`hal/transport_channel.py`** (`__all__` at line 30) — FlexILS raises `NotImplementedError` for all.

| Line | Signature |
|---|---|
| 46 | `get_signal_bandwidth(optical_node_block, port_name: str) -> int` |
| 74 | `configure_line_transceivers(optical_node_block, port_names: tuple[str, ...], central_frequencies: tuple[Frequency, ...], modes: tuple[str, ...], descriptions: tuple[str, ...]) -> dict[str, Any]` |
| 123 | `configure_transceiver_client(optical_node_block, port_name: str, description: str, speed: OpticalDigitalServiceSpeed) -> dict[str, Any]` |
| 160 | `configure_transponder_crossconnect(optical_node_block, client_port_name: str, line_port_names: list[str], xconn_description: str = "") -> dict[str, Any]` |
| 205 | `delete_transponder_crossconnect(optical_node_block, client_port_name: str) -> dict[str, Any]` |
| 235 | `factory_reset_transponder_client(optical_node_block, port_name: str) -> dict[str, Any]` |
| 264 | `factory_reset_transponder_lines(optical_node_block, line_port_names: list[str]) -> dict[str, Any] | list[Any]` |
| 294 | `validate_trx_line(optical_node_block, port_names, central_frequencies, modes, descriptions) -> None` |
| 340 | `validate_trx_client(optical_node_block, port_name, description, speed) -> None` |
| 372 | `validate_trx_crossconnect(optical_node_block, client_port_name, line_port_names, xconn_description="") -> None` |
| 414 | `delta_rx_power_vs_target(optical_node_block, optical_spectrum_name: str, circuit_identifier: str = "") -> float` |
| 449 | `align_tx_power_to_target(optical_node_block, line_port_name: str, db_from_target: Decimal | float | str) -> dict[str, Any]` |

### 2.2 FlexILS adapters (`hal/adapters/nokia_flexils/`)

Client seam: **`get_flex_client(block) -> FlexilsClient`** (`_shared.py:448`, device-probing) and
its protocol-typed wrapper **`_get_flex_client(block) -> FlexilsClientProtocol`**
(`_shared.py:503`). `FlexilsClientProtocol` (`_shared.py:34`) documents the dynamically-bound TL1
command surface (`rtrv_*`, `ent_*`, `ed_*`, `dlt_*`, `opr_valroute_oel`, `put_maintenance`,
`rst_maintenance`, `rtrv_pm_sch`) plus `tid`, `gne_ip`.

**`_shared.py`**

| Line | Symbol | Purity |
|---|---|---|
| 153 | `class FlexilsGneProvider` | Holds `_tid_ips_xyz_of_gnes` class cache. |
| 165 | `_initialize_cache() -> None` | I/O: DB via `subscription_instances_by_block_type` + `NokiaFlexIlsBlock.from_db`. |
| 215 | `find_closest_gnes(cls, latitude: float, longitude: float) -> list[tuple[str, list[str]]]` | PURE math over the cache, but triggers DB cache init when empty. Reset `_tid_ips_xyz_of_gnes` in tests. |
| 244 | `_record_value(record: dict, key: str) -> str | None` | PURE defensive TL1-record accessor. |
| 256 | `_find_node_entry(flex, tid, optical_flexils_gmpls_id) -> dict[str, Any]` | I/O; `ValueError`. |
| 289 | `_retrieve_node_properties(flex) -> tuple[OpticalNodeRole, str]` | I/O; response parsing is pure; maps `NETYPE` ROADM/OA/OLA, `SWVERSION`; `ValueError`. |
| 321 | `_discover_via_client(flex, target_id, gmpls_id) -> tuple[OpticalNodeRole, str]` | I/O; rebinds client via `FlexilsClient.get_instance`. |
| 351 | `discover_flexils_node(target_id, management_ip=None, loopback_ip=None, gmpls_id=None, location=None) -> tuple[OpticalNodeRole, str]` | I/O; direct IPs first, else GNE lookup; `ValueError`. |
| 410 | `_find_closest_gne_ip(tid, latitude, longitude) -> str` | I/O. |
| 448 | `get_flex_client(block) -> FlexilsClient` | I/O probe; `ValueError`. **Primary monkeypatch target.** |
| 503 | `_get_flex_client(block) -> FlexilsClientProtocol` | Thin cast wrapper. |
| 512 | `_get_remote_node_id(remote_port_block) -> str` | I/O (G30 inventory) or pure fqdn; `ValueError`. |

**`node.py`** — all I/O through `get_flex_client`.

| Line | Signature |
|---|---|
| 16 | `role_and_version(optical_node_block) -> tuple[OpticalNodeRole, str]` |
| 43 | `role(node) -> OpticalNodeRole` |
| 60 | `software_version(node) -> str` |
| 77 | `retrieve_omses(optical_node_block) -> list[dict[str, Any]]` (parses `RTRV-OTELINK`; `ValueError`) |
| 112 | `retrieve_ports_spectral_occupations(optical_node_block) -> dict[str, list[tuple[int, int]]]` |

**`port.py`** — all I/O.

| Line | Signature |
|---|---|
| 29 | `_scg_aids(flex) -> list[str]` (tolerates `TL1CommandDeniedError` "DOES NOT EXIST") |
| 39 | `get_device_ports_by_role(optical_node_block, roles=None) -> list[str]` (supported: `OLS_LINE`, `OLS_ADD_DROP`) |
| 61 | `set_port_description(port_block, port_description) -> dict[str, Any]` |
| 91 | `set_port_admin_state(optical_port_block, admin_state) -> dict[str, Any]` |
| 143 | `_ensure_manualmode2(optical_port_block) -> None` |
| 172 | `configure_termination(optical_port_block, remote_port_block, pipe_type) -> dict[str, Any]` |
| 217 | `factory_reset(optical_port_block, remote_port_block, pipe_type) -> dict[str, Any]` |
| 257 | `check_fiber(optical_port_block, remote_port_block, pipe_type) -> None` |

**`spectrum.py`**

| Line | Symbol | Purity |
|---|---|---|
| 24 | `_node_role(port) -> OpticalNodeRole` | PURE (block fields). |
| 33 | `_divide_path_into_omses(path: list[AnyOpticalPortBlockProvisioning]) -> list[tuple[...]]` | PURE (block fields; `ValueError`). **High-value unit test.** |
| 74 | `_find_or_create_oel(...) -> dict[str, Any]` | I/O. |
| 137 | `_oteintf_from_port_name(device, port_name) -> str` | I/O. |
| 154 | `_find_fbm_port_if_fmm_port(flex, port_name) -> str` | I/O. |
| 174 | `_get_flexils_name_client_tributary(device, port_name) -> tuple[str, FlexilsClientProtocol, str]` | I/O. |
| 185 | `_find_matching_osnc_on_flexils(client, circuit_identifier, src_port_name, dst_port_name, dst_node_name, passband=None, carrier=None, osnc_label=None, oel_aid=None) -> dict | None` | I/O call but the **matching loop is pure given a fake client**; tolerates denied `RTRV-OSNC`. |
| 238 | `_find_or_create_osnc(...) -> dict[str, Any]` | I/O. |
| 305 | `_find_first_free_sch_id(flex, port_name) -> int` | I/O loop 1..128; `ValueError`. |
| 320 | `_open_shutter(device, sch_aid) -> None` | I/O. |
| 328 | `_find_flexils_osnc(optical_spectrum_name, optical_spectrum_section, passband=None, circuit_identifier="") -> tuple[FlexilsClientProtocol, dict]` | I/O; A->Z then Z->A; `ValueError`. |
| 398 | `_remote_flex_for_section(flex, optical_spectrum_section) -> FlexilsClientProtocol` | I/O. |
| 421 | `deploy(...)` | I/O (contains `sleep(5)` at line 466 — patch `time.sleep` / module `sleep`). |
| 480 | `modify(...)` | I/O. |
| 562 | `delete(...)` | I/O. |
| 586 | `validate(...)` | I/O. |
| 642 | `append_label(...)` | I/O. |
| 684 | `create_cross_connection(...)` | I/O. |
| 756 | `delete_cross_connection(...)` | I/O. |

**`transponder.py`**: line 8 `delta_rx_power_vs_target(optical_node_block, optical_spectrum_name, circuit_identifier="") -> float` — I/O.

### 2.3 Groove G30 adapters (`hal/adapters/nokia_groove_g30/`)

Client seam: **`get_g30_client(block) -> G30Client`** (`_shared.py:14`) — pure construction of
`RestconfClient` from the block's management IPs; no network until a navigator call.

| File:line | Symbol | Purity |
|---|---|---|
| `_shared.py:29` | `g30_ids_from_port_name(port_name: str) -> tuple[int, int, int | None, int, int | None]` | **PURE**; parses `port-1/3.1/1.4`; `ValueError` if subport without subslot. |
| `_shared.py:67` | `g30_port_navigator_node_from_port_name(g30_device_block, port_name) -> tuple[PortItemNode | SubportItemNode, int, int, int | None, int, int | None]` | Builds navigator (client construction); no I/O until `.retrieve`. |
| `node.py:17` | `software_version(node) -> str` | I/O; `ValueError`. |
| `node.py:43` | `role(node) -> OpticalNodeRole` | I/O; OCC2 in inventory -> `TRANSPONDER_XOADM` else `TRANSPONDER`. |
| `node.py:61` | `validate_management_network_config(optical_node_block) -> None` | I/O; compares against templates. |
| `node.py:116` | `_get_eth1_details(eth1_ip: str | None) -> tuple[str | None, str | None, bool, int]` | **PURE**; switch nets `10.127/16`,`172.16/16` -> /24, p2p `10.10/16` -> /30; `ValueError` out of range. **High-value unit test.** |
| `port.py:51` | `_g30_aid_id(port_name: str) -> str` | **PURE**. |
| `port.py:56` | `_g30_port_role(*, is_occ2: bool, is_card_port: bool, port_id: int, port_name: str, ots_ids: set[str]) -> OpticalPortRole` | **PURE**. |
| `port.py:72` | `_g30_port_roles(optical_node_block) -> dict[str, OpticalPortRole]` | I/O; covered by existing test (see §4). |
| `port.py:122` | `get_device_ports_by_role(optical_node_block, roles=None) -> list[str]` | I/O via `_g30_port_roles`. |
| `port.py:141` | `retrieve_transceiver_modes(optical_node_block, port_name) -> list[str]` | I/O; pure card-type mapping inside. |
| `port.py:177` | `set_port_description(port_block, port_description) -> dict[str, Any]` | I/O. |
| `port.py:203` | `set_channel_description(optical_node_block, facility_id, description) -> dict[str, Any]` | I/O. |
| `port.py:232` | `set_port_admin_state(port_block, admin_state) -> dict[str, Any]` | I/O; pure `mapping`. |
| `port.py:266` | `_configure_g30_amplifier_port(...) -> dict[str, Any]` | I/O. |
| `port.py:340` | `configure_termination(optical_port_block, remote_port_block) -> dict[str, Any]` | I/O. |
| `port.py:404` | `factory_reset(optical_port_block) -> dict[str, Any]` | I/O. |
| `port.py:425` | `check_fiber(optical_port_block, remote_port_block) -> None` | I/O; pure expected-string logic. |
| `transponder.py:22` | `_client_speed_config(speed) -> tuple[str, str, str]` | **PURE**; `NotImplementedError`. |
| `transponder.py:33` | `_get_modulation_and_rate_from_mode(port_mode: str) -> tuple[str, str]` | **PURE**; large map, default `("not-applicable","not-applicable")`. |
| `transponder.py:89` | `_extract_shelf_slot_port_ids_from_odu_string(odu_string: str) -> tuple[int, int, int]` | **PURE** regex; `ValueError`. |
| `transponder.py:104` | `get_signal_bandwidth(...) -> int` | I/O; pure FEC->MHz map (`SDFEC27ND`=75000, `SDFEC15ND2`=68750, else 37500). |
| `transponder.py:126` | `configure_line_transceivers(...) -> dict[str, Any]` | I/O. |
| `transponder.py:181` | `configure_transceiver_client(...) -> dict[str, Any]` | I/O. |
| `transponder.py:224` | `configure_transponder_crossconnect(...) -> dict[str, Any]` | I/O; catches `HTTPError` 404. |
| `transponder.py:383` | `delete_transponder_crossconnect(...) -> dict[str, Any]` | I/O. |
| `transponder.py:457` | `factory_reset_transponder_client(...) -> dict[str, Any]` | I/O. |
| `transponder.py:481` | `factory_reset_transponder_lines(...) -> list[Any]` | I/O. |
| `transponder.py:508` | `validate_trx_line(...) -> None` | I/O; pure length/single-mode guards first (`ValueError`). |
| `transponder.py:573` | `validate_trx_client(...) -> None` | I/O. |
| `transponder.py:628` | `validate_trx_crossconnect(...) -> None` | I/O. |
| `transponder.py:671` | `align_tx_power_to_target(...) -> dict[str, Any]` | I/O; pure clamp `[-10, 6]`. |

### 2.4 GX G42 adapters (`hal/adapters/nokia_gx_g42/`)

Client seam: **`get_g42_client(block) -> G42Client`** (`_shared.py:7`) — pure construction.

| File:line | Symbol | Purity |
|---|---|---|
| `node.py:12` | `software_version(node) -> str` | I/O; `ValueError`. |
| `node.py:42` | `role(node) -> OpticalNodeRole` | **PURE** — always `TRANSPONDER`. |
| `port.py:28` | `_g42_chm6_cards(optical_node_block) -> list[Any]` | I/O. |
| `port.py:36` | `_g42_client_ports_names(optical_node_block) -> list[str]` | I/O. |
| `port.py:46` | `_g42_line_ports_names(optical_node_block) -> list[str]` | I/O. |
| `port.py:56` | `get_device_ports_by_role(optical_node_block, roles=None) -> list[str]` | I/O; supported `TRANSPONDER_LINE`, `TRANSPONDER_CLIENT`. |
| `port.py:84` | `retrieve_transceiver_modes(optical_node_block, port_name) -> list[str]` | I/O; large C6/C14 mapping. |
| `port.py:164` | `set_port_description(port_block, port_description) -> dict[str, Any]` | I/O. |
| `port.py:189` | `set_channel_description(optical_node_block, facility_id, description) -> dict[str, Any]` | I/O. |
| `port.py:225` | `set_port_admin_state(port_block, admin_state) -> dict[str, Any]` | I/O. |
| `port.py:260` | `configure_termination(optical_port_block, remote_port_block) -> dict[str, Any]` | I/O. |
| `port.py:293` | `factory_reset(optical_port_block) -> dict[str, Any]` | I/O. |
| `port.py:309` | `check_fiber(optical_port_block, remote_port_block) -> None` | I/O. |
| `transponder.py:30` | `_client_speed_config(speed) -> tuple[str, str, str, str]` | **PURE**; `NotImplementedError`. |
| `transponder.py:41` | `_find_xcon(g42, client, line, direction, payload_type) -> XconItem | None` | I/O read; pure match loop; `ValueError` on tributary already connected; catches 404. |
| `transponder.py:91` | `_create_xcon(...) -> None` | I/O; tolerates 412. |
| `transponder.py:132` | `_derive_optical_channel_key(line_port_names: list[str]) -> str` | **PURE**; `ValueError`. |
| `transponder.py:150` | `_retrieve_payload_type(g42, client_port_name) -> Literal["100GBE","400GBE"]` | I/O; `ValueError`. |
| `transponder.py:168` | `_retrieve_time_slots(g42, odu_name, speed) -> str` | I/O; slot parsing is pure (`80`/`320` slots); `ValueError`. |
| `transponder.py:194` | `get_signal_bandwidth(...) -> int` | I/O; pure halving for coupled carriers. |
| `transponder.py:230` | `configure_line_transceivers(...) -> dict[str, Any]` | I/O. |
| `transponder.py:315` | `configure_transceiver_client(...) -> dict[str, Any]` | I/O. |
| `transponder.py:405` | `configure_transponder_crossconnect(...) -> dict[str, Any]` | I/O. |
| `transponder.py:463` | `delete_transponder_crossconnect(...) -> dict[str, Any]` | I/O. |
| `transponder.py:508` | `factory_reset_transponder_client(...) -> dict[str, Any]` | I/O. |
| `transponder.py:563` | `factory_reset_transponder_lines(...) -> dict[str, Any]` | I/O. |
| `transponder.py:611` | `validate_trx_line(...) -> None` | I/O; pure length/single-mode guards. |
| `transponder.py:721` | `validate_trx_client(...) -> None` | I/O. |
| `transponder.py:802` | `validate_trx_crossconnect(...) -> None` | I/O. |
| `transponder.py:861` | `align_tx_power_to_target(...) -> dict[str, Any]` | I/O; pure clamp `[-6, 9]`. |

---

## 3. FlexILS services (`services/nokia/flexils/`)

### 3.1 `client.py` — TL1-over-SSH client

`class FlexilsClient` (line 21), class cache `_cache: dict[tuple[str,str], FlexilsClient]` (22).

| Line | Signature | Seam / notes |
|---|---|---|
| 24 | `get_instance(cls, tid, gne_ip, timeout=30, username=None, password=None) -> FlexilsClient` | Classmethod, caches by `(tid.lower(), gne_ip, username, password)`. Tests: monkeypatch `get_instance` (done by HAL fakes) or `FlexilsClient._cache.clear()`. |
| 39 | `close_all()` | Classmethod; closes+clears cache. |
| 45 | `__init__(self, tid, gne_ip, timeout=30, username=None, password=None)` | Reads `get_settings()` for creds; eagerly calls `_init_command_methods()` (no network). |
| 70 | `_authenticate()` | Sends `ACT-USER` + `INH-MSG-ALL`; calls `execute_raw_command`. |
| 81 | `_connect()` | **paramiko SSH seam** (`SSHClient.connect` + `invoke_subsystem("tl1telnet")`); `RuntimeError` if no creds. |
| 147 | `_close()` | Closes channel/client. |
| 159 | `_send_and_receive_until(command, until_strings) -> str` | **Transport seam**: writes to `self._channel.sendall`, reads `self._channel.recv`, waits for markers + `TL1>>`; `TimeoutError`, `EOFError`. |
| 221 | `execute_raw_command(command, correlation_tag) -> str` | **Primary seam to fake per test**: builds DENY/PRTL/COMPLD markers, re-auths on `LOGIN NOT ACTIVE`, strips command echo and `TL1>>`. |
| 240 | `_execute_command(command_cls: type[T], **kwargs) -> TL1BaseResponse` | Rejects a `tid` kwarg with `ValueError`; calls `command_cls(tid=self.tid, **kwargs).execute(self)`. |
| 260 | `_init_command_methods()` | Dynamically binds `method_name -> command_class` from `TL1CommandRegistry.commands` onto the instance. |
| 275/279/283/287 | `close()`, `__enter__`, `__exit__`, `__del__` | Context-manager / teardown. |

### 3.2 `commands/base.py` — parser, registry, serializer

| Line | Symbol | Notes |
|---|---|---|
| 29 | `class TL1CommandRegistry` | `commands: dict[str, type[TL1BaseCommand]]`; `register(command_class)` builds `f"{verb.lower()}_{modifier.lower().replace('-','_')}"`. |
| 41 | `class TL1CommandMeta(ModelMetaclass)` | Auto-registers **every** `TL1BaseCommand` subclass except the base (line 46). Importing a command module registers its classes as a side effect. |
| 51 | `class TL1BaseResponse(BaseModel)` | Fields `status, raw_data, parsed_data, ctag, sid, tid`. |
| 61 | `rename_positional_params(self, parsed_data) -> list[dict]` | Overridden per command to map `positional_param_i_j` to TL1 mnemonics. |
| 67 | `from_raw_text(cls, message: str, tag: str) -> TL1BaseResponse` | **PURE parser / high-value unit test.** Handles quoted `:`/`,` splitting, `&`/`&-` lists, positional params; raises `ValueError` when the tag is absent. |
| 144 | `class TL1BaseCommand(BaseModel, metaclass=TL1CommandMeta)` | ClassVars `help_text`, `verb`, `modifier`, `response_class`; fields `tid`, `aid`, `ctag`. |
| 155 | `execute(self, client: FlexilsClient) -> TL1BaseResponse` | Calls `client.execute_raw_command(self.to_string(), self.ctag)`; raises `TL1CommandDeniedError` on `DENY` unless `ALREADY`. |
| 165 | `to_string(self) -> str` | **PURE serializer / high-value unit test**: renders the `help_text` template from fields, `&`-joins lists/tuples, `&-`-joins lists of tuples. |

### 3.3 Command modules and registered methods

`commands/__init__.py:36-50` auto-imports every module except `base`/`__init__` and aggregates
`__all__`; importing this package is what populates `TL1CommandRegistry.commands`. Method name
below is the registry key (i.e. the dynamically-bound client method).

| Module | Classes (line) | Registered methods |
|---|---|---|
| `eqpt.py` | `EqptResponse` (19), `RetrieveEqpt` (28) | `rtrv_eqpt` |
| `maintenance_state.py` | `IntoAdminMaintenance` (19, verb PUT, modifier MAINTENANCE), `OutofAdminMaintenance` (271, verb RST, modifier MAINTENANCE) | `put_maintenance`, `rst_maintenance` |
| `ocrs.py` | `OcrsResponse` (6), `RetrieveOcrs` (16), `EnterOcrs` (42), `EditOcrs` (78), `DeleteOcrs` (101) | `rtrv_ocrs`, `ent_ocrs`, `ed_ocrs`, `dlt_ocrs` |
| `oel.py` | `OperateValrouteOel` (19), `OelResponse` (26), `RetrieveOel` (35), `EnterOel` (43), `EditOel` (88) | `opr_valroute_oel`, `rtrv_oel`, `ent_oel`, `ed_oel` |
| `osnc.py` | `EnterOsnc` (19), `OsncResponse` (81), `RetrieveOsnc` (89), `EditOsnc` (101), `DeleteOsnc` (152) | `ent_osnc`, `rtrv_osnc`, `ed_osnc`, `dlt_osnc` |
| `oteintf.py` | `OteintfResponse` (19), `RetrieveOteintf` (28) | `rtrv_oteintf` |
| `otelink.py` | `OtelinkResponse` (19), `RetrieveOtelink` (27) | `rtrv_otelink` |
| `ots.py` | `OtsResponse` (19), `RetrieveOts` (29), `EditOts` (37) | `rtrv_ots`, `ed_ots` |
| `scg.py` | `ScgResponse` (20), `RetrieveScg` (30), `EditScg` (43) | `rtrv_scg`, `ed_scg` |
| `sch.py` | `SchResponse` (19), `RetrieveSch` (29), `EditSch` (37), `EnterSch` (68), `DeleteSch` (87), `MaintenanceSch` (94), `RestoreAdminStateSch` (105), `RetrieveSchPm` (116) | `rtrv_sch`, `ed_sch`, `ent_sch`, `dlt_sch`, `rmv_sch`, `rtrv_pm_sch`. NOTE: `MaintenanceSch` and `RestoreAdminStateSch` share verb/modifier `RMV`/`SCH`, so the second registration **overwrites** the first in the registry. |
| `sys.py` | `SysResponse` (21), `RetrieveSys` (29) | `rtrv_sys` |
| `tidmap.py` | `TidmapResponse` (21), `RetrieveTidmap` (29) | `rtrv_tidmap` |
| `toponode.py` | `ToponodeResponse` (19), `RetrieveToponode` (24) | `rtrv_toponode` |

Pure parsing targets: every `*Response.rename_positional_params` (e.g. `ots.py:20`, `scg.py:21`,
`sch.py:20`, `ocrs.py:7`, `osnc.py:82`, `oel.py:27`, `eqpt.py:20`, `oteintf.py:20`,
`otelink.py:20`) and `TL1BaseResponse.from_raw_text` + `TL1BaseCommand.to_string`.

### 3.4 `utils/`

| Line | Symbol | Notes |
|---|---|---|
| `utils/__init__.py:3-6` | re-exports `generate_ctag`, `DEFAULT_CTAG`, `TL1CompletionStatus` | |
| `utils/correlation_tag_generator.py:18` | `generate_ctag()` | PURE (random 6 chars, first alpha). |
| `utils/fixed_params.py:16,19` | `DEFAULT_CTAG = "WFOTAG"`, `class TL1CompletionStatus(StrEnum)` (`COMPLD`,`DENY`,`ALREADY`) | PURE. |
| `utils/tl1_command_help_to_pydantic_generator.py:41,45,61` | `is_optional`, `parse_param`, `parse_tl1_help` | PURE developer helper (not used at runtime). |

### 3.5 Injecting a fake FlexILS transport/client

- **HAL adapters**: monkeypatch the adapter module's `get_flex_client` (e.g.
  `orchestrator.optical.hal.adapters.nokia_flexils.port.get_flex_client`) or
  `_shared._get_flex_client` for `spectrum`/`transponder`, returning a fake object whose
  `rtrv_*`/`ent_*` methods return `TL1BaseResponse` (or a `SimpleNamespace(parsed_data=[...])`).
- **Client-level tests**: monkeypatch `FlexilsClient.execute_raw_command` (class or instance) to
  return raw TL1 text, then exercise `TL1BaseCommand.execute` / `_execute_command` without SSH.
  Alternatively patch `_send_and_receive_until`.
- Reset `FlexilsClient._cache` (line 22) and `FlexilsGneProvider._tid_ips_xyz_of_gnes` (line 162)
  between tests to avoid cross-test leakage.

---

## 4. G30 / G42 (`services/nokia/g30/`, `services/nokia/g42/`)

### 4.1 Session managers — HTTP seam (both platforms near-identical)

`g30/session_manager.py` and `g42/session_manager.py` both define:

- `class TCPKeepAliveAdapter(HTTPAdapter)` (g30:17 / g42:17) — socket keepalive options.
- `class RestconfClient` (g30:52 / g42:52):
  - `__init__(self, loopback_ip=None, management_ip=None, port=8181, username=None, password=None, verify=False)` (g30:55, g42:55) — builds `self.urls` of `https://<ip>:8181/restconf` (loopback first); creates a `requests.Session`; mounts the keepalive adapter; sets `Content-Type: application/yang-data+json`; creds from `settings.g30_*` / `settings.g42_*`; then `self.data = Data(self, "/data", "")` and `self.operations = Operations(self, "/operations", "")`.
    - G30 warns (does not raise) on missing creds; **G42 raises `UserWarning`** (g42:90-91).
    - `ValueError` when neither IP is given.
  - `_request(self, method, path, **kwargs) -> dict` (g30:99 / g42:99) — loops `self.urls`, calls `self._session.request(method, url, timeout=(10, 2400), **kwargs)`, `raise_for_status()`, returns `response.json()` (or `{}`); on connection errors tries next URL; raises `requests.HTTPError`; after all URLs `ExceptionGroup`.
- Fake seam: replace `RestconfClient._session` with a stub, or monkeypatch `_request`; the
  navigators only ever call `client._request(...)`. Tests can also construct a
  `SimpleNamespace(_request=...)` and assign it to the adapter module's `get_g30_client`/`get_g42_client`.

### 4.2 Data navigators (`data_navigators/`)

`g30/data_navigators/_base.py` and `g42/data_navigators/_base.py` are byte-identical in shape:

- `_get_max_depth(data, current_depth=1) -> int` (11) — PURE.
- `_prune_at_max_depth(data, target_depth, current_depth=1) -> Any` (26) — PURE.
- `class TemplateRegistry` (45) — `register(name)`, `get(name)`.
- `class Node` (61) / `class ItemNode` (140) / `class ListNode` (242) — `_retrieve(*, content, with_defaults, depth, fields)`, `_update(**kwargs)`, `_replace(**kwargs)`, `delete()`, `from_template(**kwargs)`; every method calls `self._client._request(...)`. The response unwrapping/pruning logic is pure given a canned `_request` return.
- `g30/data_navigators/__init__.py` `Data`/`Operations` property facades (`ne_ne` at 14; `coriant_rpc` operations).
- `g42/data_navigators/__init__.py` `Data`/`Operations` (`user_data`, `ne`, `pm`, `alarms`; `create_xcon`, `get_pm`, ...).
- `g30/user_templates/ne.py` registers `InterfaceListNode`/`RoutingProtocolListNode` templates (PURE dict/`model_validate` builders) via `@TemplateRegistry.register` (lines 11, 111); used by `node.validate_management_network_config`.
- Auto-generated large navigators (`ne.py` 19156 lines; `ioa_network_element.py` 21979 lines) — never hand-edit; fake at the `_request` boundary, not inside them.

### 4.3 Data models

`g30/data_models/_base.py` and `g42/data_models/_base.py` define `class YangBaseModel(BaseModel)`
with `model_config(extra="forbid", validate_assignment=True, ...)` and a `model_dump(*,
content="config"|"all"|"nonconfig", **kwargs)` that excludes non-config fields. The generated
`ne.py`/`coriant_rpc.py`/`ioa_*.py` models are huge and excluded from ruff/ty
(`pyproject.toml:103-108, 236-242`). Prefer `SimpleNamespace` fakes over instantiating them.

### 4.4 Existing fake-navigator pattern (`test/unit/test_g30_port_roles.py`)

The test builds nested `types.SimpleNamespace` objects mirroring the navigator tree and patches
the client factory:

- Helpers `_port` (18), `_subport` (22), `_slot` (26), `_card` (30), `_subslot` (38),
  `_fake_g30_client` (42) produce `data.ne_ne.shelf.retrieve` and
  `data.ne_ne.services.optical_interfaces.retrieve`.
- `g30_client` fixture (54-70) does
  `monkeypatch.setattr(g30_port, "get_g30_client", lambda *_: client)`.
- Covered: `g30/port.py::get_device_ports_by_role` / `_g30_port_roles` across all four roles:
  `test_occ2_port_with_matching_ots_is_ols_line` (73), `..._without_matching_ots_is_ols_add_drop`
  (77), `test_non_occ2_line_ports_are_card_ports_1_and_2` (84),
  `test_non_occ2_other_ports_are_transponder_client` (89), `test_each_port_has_exactly_one_role` (94).

**Untested node/transponder adapter functions** (candidates for contract tests with the same
pattern): G30 `node.software_version`, `node.role`, `node.validate_management_network_config`;
G30 `port.retrieve_transceiver_modes`, `set_port_description`, `set_channel_description`,
`set_port_admin_state`, `configure_termination`, `factory_reset`, `check_fiber`; G30
`transponder.*` (all); G42 `node.software_version`, `port.*`, `transponder.*`; G42
`get_device_ports_by_role` (the analogue of the covered G30 test). Pure helpers still untested:
`g30/_shared.g30_ids_from_port_name`, `g30/node._get_eth1_details`,
`g30/port._g30_aid_id`/`_g30_port_role`, `g30/transponder._client_speed_config`/
`_get_modulation_and_rate_from_mode`/`_extract_shelf_slot_port_ids_from_odu_string`,
`g42/transponder._client_speed_config`/`_derive_optical_channel_key`.

---

## 5. TNMS (`services/nokia/tnms/`)

HTTP library: **`requests`** (not httpx). `responses==0.25.7` is available for mocking
(`pyproject.toml:57`).

`client.py`:

| Line | Symbol | Notes |
|---|---|---|
| 33 | `requires_auth(func) -> Callable` | Decorator: catches `requests.HTTPError` 401 -> `_authenticate()` + one retry; otherwise wraps into `ApiError`. |
| 51 | `class TnmsClient` | |
| 52 | `__init__(self, user, password, url, fallback_url=None, verify_tls=False)` | `requests.Session`; `self.data = Data(self)`, `self.operations = Operations(self)`; `_primary_url`/`_fallback_url`/`url`. |
| 72 | `from_settings() -> TnmsClient` (classmethod) | Reads `OPTICAL_TNMS_USER/PASSWORD/ENDPOINT` (+ secondary); `ValidationError` listing missing vars. |
| 110 | `from_env() -> TnmsClient` (classmethod) | Alias of `from_settings`. |
| 119 | `_authenticate() -> None` | `POST {url}/auth` form `{user,password}`, stores `Authorization: {token_type} {access_token}`; `AuthenticationError`. |
| 161 | `_request(self, method, path, log_mask: dict | None = None, **kwargs) -> dict` | `session.request(..., timeout=(10,2400))`, `raise_for_status()`, JSON except `DELETE`. |

`endpoints.py`:

| Line | Symbol | Notes |
|---|---|---|
| 26 | `class Endpoint` | `__init__(client, current_path="", parent_path="")`; `_resolve_path`; `__call__(uuid=None)`; `__getattr__(name)` (plural->singular, `_`->`-`). |
| 57 | `retrieve(self, fields=None, depth=None)` | `GET`; unwraps single-key dict/list. |
| 85 | `class Data(Endpoint)` | `RESOURCES` map (86): equipment/topology/connectivity/notification/job -> TAPI contexts; `__init__` at 94. |
| 106 | `class Operations` | `base_path = "/operations"`. |
| 111 | `get_cli_script_result(job_id, max_retries=10, base_delay=0.1) -> dict` | `POST .../get-cli-script-result/`; exponential backoff; `ApiError` on failure. |
| 172 | `run_cli_script(device_list, command_list, channel="TL1", error_policy="ABORT") -> dict` | `POST .../run-cli-script/`; masks `ACT-USER`/`CANC-USER`; then polls `get_cli_script_result`. |

Exceptions (`exceptions.py`): `TnmsClientError` (17), `AuthenticationError` (21),
`ApiError(status_code, message)` (25), `ValidationError` (34).
Lazy accessor: `services/nokia/__init__.py:38 get_tnms_client()` (`@lru_cache`) ->
`TnmsClient.from_settings()`. Fake seam: monkeypatch `get_tnms_client`, or use `responses` on the
`TnmsClient` session, or patch `TnmsClient._request`.

---

## 6. Netbox (`services/netbox.py`)

HTTP library: **`pynetbox`** (wraps `requests`).

| Line | Symbol | Notes |
|---|---|---|
| 35 | `get_netbox_api() -> Api` (`@lru_cache`) | Builds `pynetbox.api(url, token)`; raises `RuntimeError` when `OPTICAL_NETBOX_URL`/`OPTICAL_NETBOX_TOKEN` are unset. **Lazy** (no import-time call). |
| 54-168 | `NetboxPayload` and dataclass payloads (`SitePayload`, `DeviceRolePayload`, `ManufacturerPayload`, `DeviceTypePayload`, `DevicePayload`, `CableTerminationPayload`, `CablePayload`, `IpPrefixPayload`, `InterfacePayload`, `AvailablePrefixPayload`, `AvailableIpPayload`, `VlanPayload`, `L2vpnPayload`, `L2vpnTerminationPayload`) | PURE `NetboxPayload.dict()` -> `asdict`. |
| 171-256 | `get_sites/get_site/get_device_roles/.../get_ip_address(**kwargs)` | Each calls `get_netbox_api().<endpoint>.filter/get`. |
| 259 | `delete_from_netbox(endpoint, **kwargs) -> None` | `ValueError` when not found. |
| 296 | `skip_network_address(ip_prefix: Prefixes) -> None` | I/O (reserves placeholder IPs). |
| 319 | `reserve_loopback_addresses(device_id: int) -> tuple` | I/O. |
| 350 | `_require_loopback_prefix(prefix: str | None, env_var: str) -> str` | PURE; `RuntimeError`. |
| 369/374 | `create_available_prefix(parent_id, payload)`, `create_available_ip(parent_id, payload)` | I/O. |
| 379 | `create(payload: NetboxPayload, **kwargs) -> int` | `@singledispatch`; `TypeError` via `single_dispatch_base`. |
| 478 | `update(payload: NetboxPayload, **kwargs) -> bool` | `@singledispatch`. |

Faking: monkeypatch `orchestrator.optical.services.netbox.get_netbox_api` (module global used by
all helpers) to return a `SimpleNamespace`/`MagicMock` with the endpoint tree; or set env vars +
`get_netbox_api.cache_clear()`. `_create_object`/`_update_object` (400/499) are the singledispatch
cores and can be tested with a fake endpoint.

---

## 7. `settings.py`

| Line | Symbol | Notes |
|---|---|---|
| 25 | `class OpticalSettings(BaseSettings)` | |
| 54 | `model_config` | `SettingsConfigDict(env_prefix="OPTICAL_", env_file=".env", extra="ignore")`. |
| 56-74 | fields | `netbox_url`, `netbox_token`, `ipv4_loopback_prefix`, `ipv6_loopback_prefix`, `flexils_user`, `flexils_password`, `g30_user`, `g30_password`, `g42_user`, `g42_password`, `tnms_endpoint`, `tnms_secondary_endpoint`, `tnms_user`, `tnms_password`, `customer_choice` — all `str | None = None`. |
| 77 | `get_settings() -> OpticalSettings` | `@lru_cache`; constructs `OpticalSettings()`. |

"No import-time side effects" assertions:

- Import every module under `orchestrator.optical` (at least `settings`, `hal`, `hal.adapters.*`,
  `services.*`, `utils.custom_types.*`) in a subprocess with `OPTICAL_*` removed from the
  environment and assert no exception.
- `get_settings()` must succeed with zero env vars; override env + `get_settings.cache_clear()`
  to assert field mapping (env prefix `OPTICAL_`).
- Confirm the lazy accessors (`get_netbox_api`, `get_tnms_client`, `FlexilsClient`) do not run at
  import: assert `get_netbox_api.cache_info().currsize == 0`, `get_tnms_client.cache_info().currsize == 0`.

---

## 8. Custom types (`utils/custom_types/`)

| Module | Symbols (line) | Tests today |
|---|---|---|
| `flexils.py` | `validate_flexils_target_id(value) -> str` (14); `FlexIlsTargetId` (25) | **HAS** `test/unit/test_flexils_target_id.py` (valid/invalid + `ValidationError` match). |
| `coordinates.py` | `validate_latitude(v: str) -> str` (15), `validate_longitude(v: str) -> str` (29); `LatitudeCoordinate` (43), `LongitudeCoordinate` (52) | **NONE.** Constants `MAX/MIN_LATITUDE` (9-12), `MAX/MIN_LONGITUDE` (9,11). |
| `dns.py` | `validate_domain_syntax(value, *, min_labels=1, allow_numeric_tld=True, allow_wildcard=False, allow_underscore=False) -> str` (32); validators `_fqdn_validator` (142), `_pqdn_validator` (151), `_subdomain_validator` (160), `_subdomain_prefix_validator` (170); types `Fqdn` (146), `Pqdn` (155), `Subdomain` (164), `SubdomainPrefix` (174) | **NONE.** IDNA/punycode, length 253, label regexes (23,26). |
| `frequencies.py` | `Frequency` (22), `Bandwidth` (28), `parse_if_string` (35), `validate_passband_order` (42), `Passband` (50), `disjoint_intervals_overlap_search` (58), `available_to_used_passbands` (94) | **NONE.** `available_to_used_passbands` is used by `flexils/node.py:127`; both helpers are pure and high-value. |
| `ip_address.py` | `validate_ipv4_or_ipv6` (24), `validate_ipv4_or_ipv6_network` (35), `IPv4AddressType`/`IPv4NetworkType`/`IPv6AddressType`/`IPv6NetworkType` (50-53), `IPAddress` (54), `IPNetwork` (55), `IPV4Netmask` (56), `IPV6Netmask` (57), `PortNumber` (58), `AddressSpace` (71) | **NONE.** |

Adjacent pure utilities worth unit tests (used pervasively by adapters): `utils/datadiff.py`
`flatten` (23), `compare_jsons` (67), `anydump` (108), `compare_pydantic_objects` (117),
`compare_dicts` (128); `utils/singledispatch.py` `single_dispatch_base` (21). None have dedicated
tests today.

---

## 9. Existing test infrastructure to reuse

Packages/lanes (all now exist): `test/unit/`, `test/contract/` (only `__init__.py`, empty lane
ready for the device-boundary tests), `test/composition/`, `test/execution/`, `test/migrations/`.
Markers `unit`, `contract`, `db`, `noautofixt`; default run excludes DB (`pyproject.toml:213-218`).

`test/support/` importable helpers (no cross-fixture deps):

- `db.py` — `postgres_database` (session PG container `pgvector/pgvector:pg16` or
  `OPTICAL_TEST_PG_URL`), `run_process`, `product_id_for`, `assert_process_completed`,
  `assert_process_failed`, `subscription_id_of_process`, `set_subscription_status`,
  `clean_database`; catalog provisioned from the generated migration with `verify_no_drift`.
- `devices.py` — `install_device_stubs(monkeypatch, *, families, client_ports, line_ports, modes)`
  plus fixtures `stub_node_device`, `stub_pipe_device`, `stub_spectrum_device`, `stub_ods_device`.
  Patches **workflow-module** attributes (one seam per family). Constants `FAKE_CLIENT_PORTS`,
  `FAKE_LINE_PORTS`, `FAKE_TRANSCEIVER_MODES`, `FAKE_SOFTWARE_VERSION`.
- `models.py` — consumer-style `is_base=True` block/subscription chains for composition tests.
- `topology.py` — `active_location`, `active_packet_node`, `seed_optical_node`,
  `active_coherent_pluggable_host`.
- `catalog.py` — `seed_consumer_catalog(conn, *, product_name, product_type, product_block_name, workflows)`.
- `core_api.py` — `unwrap_step`, `step_functions`, `product_block_fields`, `non_product_block_fields`.
- `forms.py` — `finish_form(generator, page_instance) -> dict`.
- `test/conftest.py` re-exports the fixtures only.

HTTP mocking: `responses==0.25.7` is a dev dependency (`pyproject.toml:57`) — use it for
TNMS/Netbox and for G30/G42 `requests.Session` (or patch `_request`/`_session` directly).
Coverage is currently scoped to the `optical_location` family only (`pyproject.toml:230-234`,
`fail_under = 90`); widening it to `hal/`, `services/`, `settings.py`, `utils/` is a stated goal
in `todo/testing-architecture.md`.

### Suggested placement

- Pure helpers (`hal/_common.py`, port-name parsers, `_get_eth1_details`, `to_string`,
  `from_raw_text`, custom types, `datatypes`) -> `test/unit/`.
- Adapter functions with a faked transport/navigator (G30/G42/FlexILS/TNMS/Netbox) ->
  `test/contract/`.
- No new DB fixtures needed for the above; reuse `test/support/devices.py` patterns for HAL-level
  fakes and `responses` for HTTP-level fakes.
