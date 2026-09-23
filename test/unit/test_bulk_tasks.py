"""Unit tests for the CSV parsing of the bulk creation tasks.

These tests cover the database-free layer only: header handling, per-row
format validation and intra-payload duplicate detection of
``parse_nodes_csv`` and ``parse_pipes_csv``. Database checks (location/node
lookup, uniqueness, span rules, port usage) live in the resolve steps and are
covered by the execution tests.
"""

import pytest

from orchestrator.optical.workflows.tasks.bulk_create_optical_nodes import parse_nodes_csv
from orchestrator.optical.workflows.tasks.bulk_create_optical_pipes import parse_pipes_csv

NODES_HEADER = "location_code,vendor,platform,fqdn,dcn_loopback_ip,dcn_interface_ip,gmpls_id,target_id\n"
PIPES_HEADER = "pipe_type,node_a_fqdn,port_a_name,node_b_fqdn,port_b_name,optical_pipe_name,provider_name\n"

FLEXILS_ROW = "loc-01,Nokia,FlexILS,flexils-01.optical.test,192.0.2.1,192.0.2.2,192.0.2.3,flexils-01\n"
G30_ROW = "loc-01,Nokia,Groove G30,g30-01.optical.test,192.0.2.11,,,\n"
G42_ROW = "loc-02,Nokia,GX G42,g42-01.optical.test,,192.0.2.22,,\n"
SPAN_ROW = "Span,a.optical.test,1-A-1-L1,b.optical.test,1-A-1-L1,span-01,\n"
PATCH_ROW = "Patch,a.optical.test,1-A-1-C1,b.optical.test,1-A-1-C2,patch-01,\n"
LEASED_ROW = "Leased Spectrum,a.optical.test,1-A-2-L1,b.optical.test,1-A-2-L1,ckt-01,Example Provider\n"


def test_parse_nodes_csv_accepts_all_vendors() -> None:
    """One valid row per shipped vendor/platform parses with normalized values."""
    rows = parse_nodes_csv(NODES_HEADER + FLEXILS_ROW + G30_ROW + G42_ROW, ",")

    assert [row["fqdn"] for row in rows] == [
        "flexils-01.optical.test",
        "g30-01.optical.test",
        "g42-01.optical.test",
    ]
    assert [(row["vendor"], row["platform"]) for row in rows] == [
        ("Nokia", "FlexILS"),
        ("Nokia", "Groove G30"),
        ("Nokia", "GX G42"),
    ]
    assert rows[0]["gmpls_id"] == "192.0.2.3"
    assert rows[0]["target_id"] == "flexils-01"
    assert rows[1]["dcn_interface_ip"] is None
    assert rows[2]["dcn_loopback_ip"] is None


def test_parse_nodes_csv_honors_custom_delimiter() -> None:
    """A semicolon payload parses when the delimiter matches, and fails otherwise."""
    payload = (NODES_HEADER + G30_ROW).replace(",", ";")
    rows = parse_nodes_csv(payload, ";")
    assert len(rows) == 1

    with pytest.raises(ValueError, match="Unknown CSV headers"):
        parse_nodes_csv(payload, ",")


def test_parse_nodes_csv_rejects_bad_headers_and_content() -> None:
    """Unknown, missing and duplicated headers, empty payloads and bad delimiters fail."""
    with pytest.raises(ValueError, match="Unknown CSV headers: pop_code"):
        parse_nodes_csv(NODES_HEADER.replace("location_code", "pop_code") + G30_ROW, ",")
    with pytest.raises(ValueError, match="Missing CSV headers: fqdn"):
        parse_nodes_csv(NODES_HEADER.replace("fqdn,", "") + G30_ROW, ",")
    with pytest.raises(ValueError, match="Duplicated CSV headers"):
        parse_nodes_csv(NODES_HEADER.strip() + ",fqdn\n" + G30_ROW, ",")
    with pytest.raises(ValueError, match="CSV content is empty"):
        parse_nodes_csv("   \n", ",")
    with pytest.raises(ValueError, match="CSV contains no data rows"):
        parse_nodes_csv(NODES_HEADER, ",")
    with pytest.raises(ValueError, match="Delimiter must be a single character"):
        parse_nodes_csv(NODES_HEADER + G30_ROW, ",;")


def test_parse_nodes_csv_rejects_bad_vendor_platform_and_fqdn() -> None:
    """Unknown vendors/platforms, unsupported combinations and bad FQDNs fail with the row number."""
    with pytest.raises(ValueError, match="Invalid vendor 'Huawei' at row 2"):
        parse_nodes_csv(NODES_HEADER + G30_ROW.replace("Nokia", "Huawei"), ",")
    with pytest.raises(ValueError, match="Invalid platform 'DreamBox' at row 2"):
        parse_nodes_csv(NODES_HEADER + G30_ROW.replace("Groove G30", "DreamBox"), ",")
    with pytest.raises(ValueError, match="Unsupported vendor/platform combination 'Nokia'/'SR' at row 2"):
        parse_nodes_csv(NODES_HEADER + G30_ROW.replace("Groove G30", "SR"), ",")
    with pytest.raises(ValueError, match="Invalid fqdn 'not a fqdn' at row 2"):
        parse_nodes_csv(NODES_HEADER + G30_ROW.replace("g30-01.optical.test", "not a fqdn"), ",")
    with pytest.raises(ValueError, match="Invalid dcn_loopback_ip '999.1.1.1' at row 2"):
        parse_nodes_csv(NODES_HEADER + G30_ROW.replace("192.0.2.11", "999.1.1.1"), ",")


def test_parse_nodes_csv_enforces_flexils_and_dcn_rules() -> None:
    """GMPLS/TID are FlexILS-only and mandatory there; G30/G42 require a DCN IP."""
    with pytest.raises(ValueError, match="Missing required gmpls_id at row 2"):
        parse_nodes_csv(NODES_HEADER + FLEXILS_ROW.replace("192.0.2.3", ""), ",")
    with pytest.raises(ValueError, match="Missing required target_id at row 2"):
        parse_nodes_csv(NODES_HEADER + FLEXILS_ROW.replace("flexils-01\n", "\n"), ",")
    with pytest.raises(ValueError, match="Invalid target_id 'has spaces here!' at row 2"):
        parse_nodes_csv(NODES_HEADER + FLEXILS_ROW.replace("flexils-01\n", "has spaces here!\n"), ",")
    with pytest.raises(ValueError, match="gmpls_id and target_id are Nokia FlexILS-only at row 2"):
        parse_nodes_csv(NODES_HEADER + G30_ROW.replace(",,,\n", ",,192.0.2.3,node-tid\n"), ",")
    with pytest.raises(ValueError, match="At least one of dcn_loopback_ip or dcn_interface_ip"):
        parse_nodes_csv(NODES_HEADER + G30_ROW.replace("192.0.2.11", ""), ",")
    with pytest.raises(ValueError, match="Missing required location_code at row 2"):
        parse_nodes_csv(NODES_HEADER + G30_ROW.replace("loc-01", ""), ",")


def test_parse_nodes_csv_rejects_intra_payload_duplicates() -> None:
    """FQDN, IP, GMPLS ID and TID reuse within the payload fails with both row numbers."""
    second = FLEXILS_ROW.replace("flexils-01.optical.test", "flexils-02.optical.test")
    with pytest.raises(ValueError, match="IP '192.0.2.1' is duplicated at rows 2 and 3"):
        parse_nodes_csv(NODES_HEADER + FLEXILS_ROW + second, ",")
    with pytest.raises(ValueError, match="FQDN 'flexils-01.optical.test' is duplicated at rows 2 and 3"):
        parse_nodes_csv(NODES_HEADER + FLEXILS_ROW + FLEXILS_ROW, ",")
    other_ip = (
        FLEXILS_ROW.replace("flexils-01.optical.test", "flexils-02.optical.test")
        .replace("192.0.2.1,", "192.0.2.101,")
        .replace(",192.0.2.2,", ",192.0.2.102,")
        .replace(",flexils-01\n", ",flexils-02\n")
    )
    with pytest.raises(ValueError, match="GMPLS ID '192.0.2.3' is duplicated at rows 2 and 3"):
        parse_nodes_csv(NODES_HEADER + FLEXILS_ROW + other_ip, ",")


def test_parse_pipes_csv_accepts_all_pipe_types() -> None:
    """One valid row per pipe type parses with normalized values."""
    rows = parse_pipes_csv(PIPES_HEADER + SPAN_ROW + PATCH_ROW + LEASED_ROW, ",")

    assert [row["pipe_type"] for row in rows] == ["Span", "Patch", "Leased Spectrum"]
    assert rows[0]["optical_pipe_name"] == "span-01"
    assert rows[0]["provider_name"] is None
    assert rows[2]["provider_name"] == "Example Provider"


def test_parse_pipes_csv_rejects_bad_rows() -> None:
    """Unknown pipe types, bad FQDNs, empty ports and provider misuse fail with the row number."""
    with pytest.raises(ValueError, match="Invalid pipe_type 'Fiber' at row 2"):
        parse_pipes_csv(PIPES_HEADER + SPAN_ROW.replace("Span", "Fiber"), ",")
    with pytest.raises(ValueError, match="Invalid node_a_fqdn 'not a fqdn' at row 2"):
        parse_pipes_csv(PIPES_HEADER + SPAN_ROW.replace("a.optical.test", "not a fqdn"), ",")
    with pytest.raises(ValueError, match="Missing required port_b_name at row 2"):
        parse_pipes_csv(PIPES_HEADER + SPAN_ROW.replace(",1-A-1-L1,span-01,", ",,span-01,"), ",")
    with pytest.raises(ValueError, match="Missing required provider_name at row 2"):
        parse_pipes_csv(PIPES_HEADER + LEASED_ROW.replace("Example Provider", ""), ",")
    with pytest.raises(ValueError, match="provider_name is leased-spectrum-only at row 2"):
        parse_pipes_csv(PIPES_HEADER + SPAN_ROW.replace("span-01,\n", "span-01,Someone\n"), ",")
    header = PIPES_HEADER.replace(",provider_name\n", "\n")
    row = SPAN_ROW.replace(",span-01,\n", ",span-01\n")
    with pytest.raises(ValueError, match="Missing CSV headers: provider_name"):
        parse_pipes_csv(header + row, ",")


def test_parse_pipes_csv_enforces_endpoints() -> None:
    """Same-node non-patch pipes and endpoint reuse within the payload fail."""
    same_node_span = SPAN_ROW.replace("b.optical.test", "a.optical.test")
    with pytest.raises(ValueError, match="must be on different nodes at row 2"):
        parse_pipes_csv(PIPES_HEADER + same_node_span, ",")

    same_node_patch = PATCH_ROW.replace("b.optical.test", "a.optical.test")
    rows = parse_pipes_csv(PIPES_HEADER + same_node_patch, ",")
    assert rows[0]["node_a_fqdn"] == rows[0]["node_b_fqdn"]

    with pytest.raises(ValueError, match="is claimed at rows 2 and 3"):
        parse_pipes_csv(PIPES_HEADER + SPAN_ROW + SPAN_ROW.replace("span-01", "span-02"), ",")

    same_node_same_port = PATCH_ROW.replace("b.optical.test", "a.optical.test").replace("1-A-1-C2", "1-A-1-C1")
    with pytest.raises(ValueError, match="is claimed at rows 2 and 2"):
        parse_pipes_csv(PIPES_HEADER + same_node_same_port, ",")


def test_parse_csv_skips_empty_lines() -> None:
    """Blank lines in the payload are ignored and do not shift row numbers."""
    payload = NODES_HEADER + "\n" + G30_ROW + "\n"
    rows = parse_nodes_csv(payload, ",")
    assert len(rows) == 1
    assert rows[0]["line_number"] == 3
