"""Unit tests for the intra-node connectivity of the OLS nodes (device-free).

FlexILS: the internal topology is rebuilt from parsed ``RTRV-SCG`` (with the
``PROVNBRTP`` internal patches), ``RTRV-EQPT`` (card types), ``RTRV-OTS`` and
``RTRV-OCRS`` records, using real TL1 response lines run through the shipped parser.
Groove G30: the reachability is rebuilt from the fiber-connection XPaths and the
installed modules.
"""

import pytest

pytest.importorskip("flexils_tl1")
pytest.importorskip("g30_4_8_0")

from flexils_tl1.generated.responses import RtrvOcrsResponse, RtrvScgResponse
from g30_4_8_0.data_models.ne import CardTypeEnum

from orchestrator.optical.hal.adapters.nokia_flexils.connectivity import add_drop_connectivity_from_records
from orchestrator.optical.hal.adapters.nokia_groove_g30 import connectivity as g30_connectivity
from orchestrator.optical.hal.adapters.nokia_groove_g30._shared import G30Function, G30Module
from orchestrator.optical.hal.connectivity import IntraNodeEdge
from orchestrator.optical.utils.custom_types.frequencies import (
    OLS_BAND,
    free_intervals,
    merge_intervals,
    passband_within_any,
)
from test.support.tl1 import parsed_records

#: RTRV-SCG lines as returned by a FlexILS node (the first three verbatim from a device).
SCG_LINES = [
    "2-A-3-1-L1:SCG:LABEL=,PROVNBRTP=7-A-1-S9,HISTSTATS=ENABLED,DISCNBRTP=7-A-1-S9,MPO=2-A-3-1-1,"
    "PROVFPMPO=FSP-S-4D-8MPO-3-5,AUTODISCSTATE=Associated,PATHLOSCHEKSTAT=Idle,PATHLOSS=0.237936,"
    "AVAILSLICELIST=100&384:OOS-AU,FAF",
    "2-A-3-L1:SCG:LABEL=,PROVNBRTP=1-A-1-S9,HISTSTATS=ENABLED,DISCNBRTP=1-A-1-S9,MPO=2-A-3-1,"
    "PROVFPMPO=FSP-S-4D-8MPO-2-5,AUTODISCSTATE=Associated,PATHLOSS=0.669803,AVAILSLICELIST=100&384:OOS-AU,FAF",
    "1-E1-1-L1:SCG:LABEL=,PROVNBRTP=1-A-1-S4,HISTSTATS=ENABLED,DISCNBRTP=1-A-1-S4,MPO=1-E1-1-1,PROVFPMPO=,"
    "PATHLOSS=NA,LINEOPMODE=ACTIVE,INSERTIONLOSS=3.578,AUTODISCNBR=ENABLE:OOS-AU,FAF",
    "2-A-3-T1:SCG:LABEL=:IS-NR",
    "2-A-3-T2:SCG:LABEL=:IS-NR",
    "1-E1-1-T2A:SCG:LABEL=:IS-NR",
    "1-E1-1-T2B:SCG:LABEL=:IS-NR",
    "1-E1-1-T3A:SCG:LABEL=,PROVNBRTP=3-A-5-L1:IS-NR",
    "1-E1-1-T3B:SCG:LABEL=:IS-NR",
    "3-A-5-L1:SCG:LABEL=:IS-NR",
    "3-A-5-T1:SCG:LABEL=:IS-NR",
    "3-A-5-T2:SCG:LABEL=:IS-NR",
    "1-A-1-S4:SCG:LABEL=:IS-NR",
    "1-A-1-S9:SCG:LABEL=:IS-NR",
    "1-A-1-S12:SCG:LABEL=,PROVNBRTP=7-A-1-S12:IS-NR",
    "7-A-1-S9:SCG:LABEL=:IS-NR",
    "7-A-1-S12:SCG:LABEL=:IS-NR",
]
EQPT = [
    {"AID": "1", "TYPE": "CHASSIS"},
    {"AID": "1-A-1", "TYPE": "FRM"},
    {"AID": "7-A-1", "TYPE": "FRM"},
    {"AID": "2-A-3", "TYPE": "FSM"},
    {"AID": "1-E1-1", "TYPE": "FBM"},
    {"AID": "3-A-5", "TYPE": "FMMC12"},
]
OTS = ["1-A-1-L1", "7-A-1-L1"]


def _scg() -> list[dict]:
    return parsed_records(RtrvScgResponse, SCG_LINES)


def _ocrs(lines: list[str]) -> list[dict]:
    return parsed_records(RtrvOcrsResponse, lines)


def _connectivity(port: str, ocrs_lines: list[str] | None = None) -> list[IntraNodeEdge]:
    return add_drop_connectivity_from_records(port, _scg(), EQPT, OTS, _ocrs(ocrs_lines or []))


def test_scg_parser_exposes_provnbrtp() -> None:
    """The named PROVNBRTP key of RTRV-SCG reaches the connectivity code unchanged."""
    records = {record["AID"]: record for record in _scg()}
    assert records["2-A-3-1-L1"]["PROVNBRTP"] == "7-A-1-S9"
    assert records["1-E1-1-L1"]["PROVNBRTP"] == "1-A-1-S4"


def test_fsm_tributary_reaches_every_degree_of_its_l_ports() -> None:
    """An FSM is a multicast switch: a free T port reaches every L port and hence every degree."""
    assert _connectivity("2-A-3-T1") == [
        IntraNodeEdge("2-A-3-T1", "1-A-1-L1"),
        IntraNodeEdge("2-A-3-T1", "7-A-1-L1"),
    ]


def test_fsm_tributary_bound_by_a_cross_connection_reaches_only_its_l_port() -> None:
    """An FSM T port is bound to a single L for the whole spectrum once a cross-connection uses it."""
    edges = _connectivity(
        "2-A-3-T1",
        ["2-A-3-T1-1,7-A-1-L1-1:2WAY:LABEL=x,PASSBANDLIST=191400000&191450000:IS-NR"],
    )
    assert edges == [IntraNodeEdge("2-A-3-T1", "7-A-1-L1", ((191_400_000, 191_450_000),))]


def test_fsm_l_port_is_shared_by_its_tributaries() -> None:
    """The spectrum used by another T port on the same FSM L port is used on the shared L."""
    edges = _connectivity(
        "2-A-3-T2",
        ["2-A-3-T1-1,1-A-1-L1-1:2WAY:LABEL=x,PASSBANDLIST=191400000&191450000:IS-NR"],
    )
    assert edges == [
        IntraNodeEdge("2-A-3-T2", "1-A-1-L1", ((191_400_000, 191_450_000),)),
        IntraNodeEdge("2-A-3-T2", "7-A-1-L1"),
    ]


def test_fbm_coupled_tributaries_share_the_spectrum() -> None:
    """A frequency used on FBM T2B cannot be reused on T2A."""
    edges = _connectivity(
        "1-E1-1-T2A",
        ["1-E1-1-T2B-1,1-A-1-L1-1:2WAY:LABEL=x,PASSBANDLIST=193450000&193550000:IS-NR"],
    )
    assert edges == [IntraNodeEdge("1-E1-1-T2A", "1-A-1-L1", ((193_450_000, 193_550_000),))]


def test_fmm_tributary_reaches_the_degree_through_the_fbm() -> None:
    """An FMM T port reaches the degree via FMM L -> FBM T -> FBM L -> FRM S -> OTS; FMM L is shared."""
    edges = _connectivity(
        "3-A-5-T1",
        [
            "3-A-5-T2-1,1-A-1-L1-1:2WAY:LABEL=x,PASSBANDLIST=192000000&192050000:IS-NR",
            "1-E1-1-T3B-1,1-A-1-L1-2:2WAY:LABEL=y,PASSBANDLIST=194000000&194050000:IS-NR",
        ],
    )
    # The FMM L (shared by T1/T2) and the coupled FBM T3A/T3B pair are both on the route.
    assert edges == [
        IntraNodeEdge("3-A-5-T1", "1-A-1-L1", ((192_000_000, 192_050_000), (194_000_000, 194_050_000))),
    ]


@pytest.mark.parametrize(
    ("serial", "expected"),
    [
        pytest.param("MA4621081160", ["1-A-1-L1", "1-A-2-L1"], id="chassis-serial-is-internal"),
        pytest.param("MA9999999999", [], id="serial-of-another-node-is-external"),
    ],
)
def test_fmm_l_patched_to_fbm_t_through_provowremptp(serial: str, expected: list[str]) -> None:
    """The FMM L -> FBM T patch is only on the FBM T: ``PROVOWREMPTP=<chassis SERNO>/<FMM>-L1`` (seen on a node).

    The FMM L has no ``PROVNBRTP``; a ``PROVOWREMPTP`` to a transponder (``CQ.../1-1-1``) is ignored.
    """
    lines = [
        "1-E1-1-L1:SCG:LABEL=,PROVNBRTP=1-A-1-S4,HISTSTATS=ENABLED,DISCNBRTP=1-A-1-S4,MPO=1-E1-1-1:OOS-AU,FAF",
        "1-E1-1-L5:SCG:LABEL=,PROVNBRTP=1-A-2-S4,HISTSTATS=ENABLED,DISCNBRTP=1-A-2-S4,MPO=1-E1-1-2:OOS-AU,FAF",
        "1-E1-1-T1A:SCG:LABEL=,PROVNBRTP=,INTFTYP=MANUALMODE-2,HISTSTATS=ENABLED,"
        f"PROVOWREMPTP={serial}/1-A-3-L1,DISCNBRTP=:OOS-AU,FAF",
        "1-A-3-L1:SCG:LABEL=,HISTSTATS=ENABLED,DISCNBRTP=,LINEOPMODE=PASSIVE:OOS-AU,FAF",
        "1-A-3-T12:SCG:LABEL=,PROVNBRTP=,INTFTYP=MANUALMODE-2,HISTSTATS=ENABLED,"
        "PROVOWREMPTP=CQ2842491/1-1-1:OOS-AU,FAF",
        "1-A-1-S4:SCG:LABEL=,PROVNBRTP=,INTFTYP=INFWAVE:OOS-AU,FAF",
        "1-A-2-S4:SCG:LABEL=,PROVNBRTP=,INTFTYP=INFWAVE:OOS-AU,FAF",
    ]
    eqpt = [
        {"AID": "1", "TYPE": "CHASSIS", "SERNO": "MA4621081160"},
        {"AID": "1-A-1", "TYPE": "FRM"},
        {"AID": "1-A-2", "TYPE": "FRM"},
        {"AID": "1-E1-1", "TYPE": "FBM"},
        {"AID": "1-A-3", "TYPE": "FMMC12"},
    ]
    scg = parsed_records(RtrvScgResponse, lines)
    edges = add_drop_connectivity_from_records("1-A-3-T12", scg, eqpt, ["1-A-1-L1", "1-A-2-L1"], [])
    assert [edge.line_port for edge in edges] == expected


def test_express_patches_between_degrees_are_not_traversed() -> None:
    """A degree is terminal: an express S-S patch never leads an add/drop port to another degree."""
    assert [edge.line_port for edge in _connectivity("1-E1-1-T2A")] == ["1-A-1-L1"]


def test_add_drop_port_on_unknown_card_is_rejected() -> None:
    """An add/drop port on a card without known internal rules raises a clear error."""
    with pytest.raises(ValueError, match="known internal connectivity"):
        _connectivity("9-Z-9-T1")


def _module(card_type: CardTypeEnum, functions: set[G30Function], shelf: int, slot: int, subslot: int | None):
    return G30Module(
        card_type=card_type,
        functions=frozenset(functions),
        is_occ2=subslot is not None,
        slot_id=slot,
        subslot_id=subslot,
        ots_ids=frozenset({"1/3.3/1", "2/3.3/1", "1/4/1"}),
        shelf_id=shelf,
    )


def test_g30_port_name_from_xpath() -> None:
    """The fiber-connection XPaths map to the G30 port names."""
    xpath = (
        "/ne:ne/ne:shelf[ne:shelf-id='2']/ne:slot[ne:slot-id='3']/ne:card/ne:subslot[ne:subslot-id='3']"
        "/ne:subcard/ne:port[ne:port-id='3']"
    )
    assert g30_connectivity.g30_port_name_from_xpath(xpath) == "port-2/3.3/3"
    assert (
        g30_connectivity.g30_port_name_from_xpath(
            "/ne:ne/ne:shelf[ne:shelf-id='1']/ne:slot[ne:slot-id='4']/ne:card/ne:port[ne:port-id='7']"
        )
        == "port-1/4/7"
    )
    with pytest.raises(ValueError, match="Unparsable"):
        g30_connectivity.g30_port_name_from_xpath("/ne:ne/ne:shelf[ne:shelf-id='1']")


def test_g30_add_drop_reaches_line_ports_through_fibers_on_the_same_shelf_only() -> None:
    """The add/drop module follows the fibers to the modules owning OTS ports, never leaving its shelf."""
    modules = [
        _module(CardTypeEnum.OCC2, {G30Function.ADD_DROP}, 1, 3, 1),  # CAD, no OTS
        _module(CardTypeEnum.OCC2, {G30Function.WAVELENGTH_SELECTOR}, 1, 3, 3),  # WSS, OTS 1/3.3/1
        _module(CardTypeEnum.OCC2, {G30Function.WAVELENGTH_SELECTOR}, 2, 3, 3),  # WSS on shelf 2
        _module(CardTypeEnum.OCC2, {G30Function.TRANSPONDER}, 1, 5, None),
    ]
    fibers = [
        ("port-1/3.1/1", "port-1/5/1"),  # the add/drop port itself to a transponder: ignored
        ("port-1/3.1/9", "port-1/3.3/5"),  # CAD -> WSS on shelf 1
        ("port-1/3.1/10", "port-2/3.3/5"),  # CAD -> WSS on shelf 2: never crossed
    ]

    edges = g30_connectivity.add_drop_connectivity_from_records("port-1/3.1/1", modules, fibers)

    assert edges == [IntraNodeEdge("port-1/3.1/1", "port-1/3.3/1")]


def test_g30_module_owning_line_ports_reaches_them_directly() -> None:
    """An add/drop port on a module owning OTS ports (e.g. a fixed mux) reaches its own line port."""
    modules = [_module(CardTypeEnum.OCC2, {G30Function.ADD_DROP}, 1, 4, None)]
    assert g30_connectivity.add_drop_connectivity_from_records("port-1/4/3", modules, []) == [
        IntraNodeEdge("port-1/4/3", "port-1/4/1")
    ]


def test_interval_helpers() -> None:
    """merge/free/within helpers on half-open intervals."""
    assert merge_intervals([(5, 7), (1, 3), (2, 4), (7, 8), (9, 9)]) == [(1, 4), (5, 8)]
    assert free_intervals([(2, 4), (3, 5)], (0, 10)) == [(0, 2), (5, 10)]
    assert free_intervals([]) == [OLS_BAND]
    assert passband_within_any((0, 2), [(0, 2), (5, 10)])
    assert not passband_within_any((1, 6), [(0, 2), (5, 10)])
