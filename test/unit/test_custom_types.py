"""Unit tests for the custom pydantic types not covered elsewhere.

Coordinates, frequencies/passbands, DNS names and IP addresses are pure validation
types, so they are exercised directly and through ``pydantic.TypeAdapter``.
"""

import ipaddress
from typing import Any, cast

import pytest
from pydantic import TypeAdapter, ValidationError

from orchestrator.optical.utils.custom_types.coordinates import (
    LatitudeCoordinate,
    LongitudeCoordinate,
    validate_latitude,
    validate_longitude,
)
from orchestrator.optical.utils.custom_types.dns import Fqdn, Pqdn, validate_domain_syntax
from orchestrator.optical.utils.custom_types.frequencies import (
    Bandwidth,
    Frequency,
    Passband,
    available_to_used_passbands,
    disjoint_intervals_overlap_search,
)
from orchestrator.optical.utils.custom_types.ip_address import (
    AddressSpace,
    IPAddress,
    IPNetwork,
    IPv4AddressType,
    IPV4Netmask,
    IPv4NetworkType,
    IPv6AddressType,
    IPV6Netmask,
    IPv6NetworkType,
    PortNumber,
)

_LATITUDE = TypeAdapter(LatitudeCoordinate)
_LONGITUDE = TypeAdapter(LongitudeCoordinate)
_FREQUENCY = TypeAdapter(Frequency)
_BANDWIDTH = TypeAdapter(Bandwidth)
_PASSBAND = TypeAdapter(Passband)
_FQDN = TypeAdapter(Fqdn)
_PQDN = TypeAdapter(Pqdn)
_IP_ADDRESS = TypeAdapter(IPAddress)
_IP_NETWORK = TypeAdapter(IPNetwork)
_IPV4_NETMASK = TypeAdapter(IPV4Netmask)
_IPV6_NETMASK = TypeAdapter(IPV6Netmask)
_PORT_NUMBER = TypeAdapter(PortNumber)


@pytest.mark.parametrize("value", ["40.7128", "-74.0060", "90", "-90", "0", "12.5", "90.0"])
def test_latitude_accepts_valid(value: str) -> None:
    assert _LATITUDE.validate_python(value) == value


@pytest.mark.parametrize("value", ["90.1", "-90.5", "91", "100", "abc", "", "1e2", "40,7"])
def test_latitude_rejects_invalid(value: str) -> None:
    with pytest.raises(ValidationError):
        _LATITUDE.validate_python(value)


@pytest.mark.parametrize("value", ["180", "-180", "0", "40.7128", "-74.0060", "179.999", "180.0"])
def test_longitude_accepts_valid(value: str) -> None:
    assert _LONGITUDE.validate_python(value) == value


@pytest.mark.parametrize("value", ["180.1", "-180.1", "181", "-181", "abc", "", "200"])
def test_longitude_rejects_invalid(value: str) -> None:
    with pytest.raises(ValidationError):
        _LONGITUDE.validate_python(value)


def test_coordinate_validators_return_their_input() -> None:
    assert validate_latitude("45.5") == "45.5"
    assert validate_longitude("-120.0") == "-120.0"
    with pytest.raises(ValueError, match="Invalid latitude coordinate"):
        validate_latitude("91")
    with pytest.raises(ValueError, match="Invalid longitude coordinate"):
        validate_longitude("181")


@pytest.mark.parametrize("value", [191_312_500, 196_137_500, 193_100_000, 191_325_000])
def test_frequency_accepts_valid(value: int) -> None:
    assert _FREQUENCY.validate_python(value) == value


@pytest.mark.parametrize("value", [191_000_000, 197_000_000, 193_100_001])
def test_frequency_rejects_invalid(value: int) -> None:
    with pytest.raises(ValidationError):
        _FREQUENCY.validate_python(value)


@pytest.mark.parametrize("value", [3_125, 6_250, 75_000])
def test_bandwidth_accepts_valid(value: int) -> None:
    assert _BANDWIDTH.validate_python(value) == value


@pytest.mark.parametrize("value", [0, -1, 3_124])
def test_bandwidth_rejects_invalid(value: int) -> None:
    with pytest.raises(ValidationError):
        _BANDWIDTH.validate_python(value)


def test_passband_accepts_valid_tuple() -> None:
    assert _PASSBAND.validate_python((191_325_000, 196_125_000)) == (191_325_000, 196_125_000)


def test_passband_parses_string_literal() -> None:
    assert _PASSBAND.validate_python("[191325000, 196125000]") == (191_325_000, 196_125_000)


@pytest.mark.parametrize("value", [(196_125_000, 191_325_000), (193_100_000, 193_100_000)])
def test_passband_rejects_non_increasing_order(value: tuple[int, int]) -> None:
    with pytest.raises(ValidationError, match="Start frequency must be less than end frequency"):
        _PASSBAND.validate_python(value)


_ENTIRE_BAND = (191_325_000, 196_125_000)


def test_available_to_used_passbands_without_available_returns_entire_band() -> None:
    assert available_to_used_passbands([]) == [_ENTIRE_BAND]


def test_available_to_used_passbands_returns_lower_gap() -> None:
    assert available_to_used_passbands([(193_000_000, 196_125_000)]) == [(191_325_000, 193_000_000)]


def test_available_to_used_passbands_returns_upper_gap() -> None:
    assert available_to_used_passbands([(191_325_000, 193_000_000)]) == [(193_000_000, 196_125_000)]


def test_available_to_used_passbands_returns_inner_gap() -> None:
    available = [(191_325_000, 193_000_000), (194_000_000, 196_125_000)]

    assert available_to_used_passbands(available) == [(193_000_000, 194_000_000)]


def test_available_to_used_passbands_fully_used_returns_empty() -> None:
    assert available_to_used_passbands([_ENTIRE_BAND]) == []


def test_available_to_used_passbands_contiguous_available_returns_empty() -> None:
    available = [(191_325_000, 193_000_000), (193_000_000, 196_125_000)]

    assert available_to_used_passbands(available) == []


def test_available_to_used_passbands_respects_custom_bounds() -> None:
    result = available_to_used_passbands([], absolute_min_freq=191_000_000, absolute_max_freq=196_000_000)

    assert result == [(191_000_000, 196_000_000)]


_INTERVALS = [(0, 10), (20, 30), (40, 50)]


@pytest.mark.parametrize(
    ("target", "expected"),
    [
        ((5, 8), (0, 10)),
        ((15, 25), (20, 30)),
        ((45, 48), (40, 50)),
        ((0, 10), (0, 10)),
        ((-5, 1), (0, 10)),
    ],
)
def test_disjoint_intervals_overlap_search_finds_overlap(target: tuple[int, int], expected: tuple[int, int]) -> None:
    assert disjoint_intervals_overlap_search(_INTERVALS, target) == expected


@pytest.mark.parametrize("target", [(10, 20), (30, 40), (50, 60), (-5, 0), (31, 39)])
def test_disjoint_intervals_overlap_search_returns_none_without_overlap(target: tuple[int, int]) -> None:
    assert disjoint_intervals_overlap_search(_INTERVALS, target) is None


def test_disjoint_intervals_overlap_search_empty_intervals() -> None:
    assert disjoint_intervals_overlap_search([], (0, 10)) is None


@pytest.mark.parametrize("value", ["example.com", "www.example.com", "a.b.c.example", "example.com.", "Example.COM"])
def test_fqdn_accepts_valid(value: str) -> None:
    assert _FQDN.validate_python(value) == value.lower()


@pytest.mark.parametrize(
    "value",
    [
        "localhost",
        "example",
        "example.123",
        "bad_label.com",
        "-bad.com",
        "bad-.com",
        "a..b.com",
        "",
        "a" * 64 + ".com",
    ],
)
def test_fqdn_rejects_invalid(value: str) -> None:
    with pytest.raises(ValidationError):
        _FQDN.validate_python(value)


@pytest.mark.parametrize("value", ["localhost", "my-server-12", "database.local", "123", "Example.COM"])
def test_pqdn_accepts_valid(value: str) -> None:
    assert _PQDN.validate_python(value) == value.lower()


@pytest.mark.parametrize("value", ["", "bad..name", "-bad", "a b", "a" * 64])
def test_pqdn_rejects_invalid(value: str) -> None:
    with pytest.raises(ValidationError):
        _PQDN.validate_python(value)


def test_validate_domain_syntax_normalizes_and_lowercases() -> None:
    assert validate_domain_syntax("Example.COM.") == "example.com."


def test_validate_domain_syntax_enforces_min_labels() -> None:
    with pytest.raises(ValueError, match="at least 2 labels"):
        validate_domain_syntax("example", min_labels=2)


def test_validate_domain_syntax_rejects_non_string() -> None:
    with pytest.raises(TypeError, match="must be a string"):
        validate_domain_syntax(cast(Any, 123))


@pytest.mark.parametrize("value", ["192.0.2.1", "2001:db8::1", "::1"])
def test_ip_address_accepts_valid(value: str) -> None:
    assert _IP_ADDRESS.validate_python(value) == value


@pytest.mark.parametrize("value", ["999.1.1.1", "not-an-ip", "", "192.0.2.1/24"])
def test_ip_address_rejects_invalid(value: str) -> None:
    with pytest.raises(ValidationError):
        _IP_ADDRESS.validate_python(value)


@pytest.mark.parametrize("value", ["192.0.2.0/24", "2001:db8::/32", "10.0.0.0/8"])
def test_ip_network_accepts_valid(value: str) -> None:
    assert _IP_NETWORK.validate_python(value) == value


@pytest.mark.parametrize("value", ["192.0.2.1/24", "192.0.2.0/33", "not-a-network", ""])
def test_ip_network_rejects_invalid(value: str) -> None:
    with pytest.raises(ValidationError):
        _IP_NETWORK.validate_python(value)


def test_typed_ipv4_and_ipv6_addresses_round_trip_to_strings() -> None:
    ipv4 = TypeAdapter(IPv4AddressType)
    ipv6 = TypeAdapter(IPv6AddressType)

    assert ipv4.validate_python("192.0.2.1") == ipaddress.IPv4Address("192.0.2.1")
    assert ipv4.dump_python(ipv4.validate_python("192.0.2.1")) == "192.0.2.1"
    assert ipv6.validate_python("2001:db8::1") == ipaddress.IPv6Address("2001:db8::1")
    assert ipv6.dump_python(ipv6.validate_python("2001:db8::1")) == "2001:db8::1"


def test_typed_ipv4_and_ipv6_networks_round_trip_to_strings() -> None:
    ipv4 = TypeAdapter(IPv4NetworkType)
    ipv6 = TypeAdapter(IPv6NetworkType)

    assert ipv4.validate_python("192.0.2.0/24") == ipaddress.IPv4Network("192.0.2.0/24")
    assert ipv4.dump_python(ipv4.validate_python("192.0.2.0/24")) == "192.0.2.0/24"
    assert ipv6.validate_python("2001:db8::/32") == ipaddress.IPv6Network("2001:db8::/32")
    assert ipv6.dump_python(ipv6.validate_python("2001:db8::/32")) == "2001:db8::/32"


@pytest.mark.parametrize("value", [0, 24, 32])
def test_ipv4_netmask_accepts_valid(value: int) -> None:
    assert _IPV4_NETMASK.validate_python(value) == value


@pytest.mark.parametrize("value", [-1, 33])
def test_ipv4_netmask_rejects_invalid(value: int) -> None:
    with pytest.raises(ValidationError):
        _IPV4_NETMASK.validate_python(value)


@pytest.mark.parametrize("value", [0, 64, 128])
def test_ipv6_netmask_accepts_valid(value: int) -> None:
    assert _IPV6_NETMASK.validate_python(value) == value


@pytest.mark.parametrize("value", [-1, 129])
def test_ipv6_netmask_rejects_invalid(value: int) -> None:
    with pytest.raises(ValidationError):
        _IPV6_NETMASK.validate_python(value)


@pytest.mark.parametrize("value", [1, 80, 49_151])
def test_port_number_accepts_valid(value: int) -> None:
    assert _PORT_NUMBER.validate_python(value) == value


@pytest.mark.parametrize("value", [0, 49_152, 65_535, -1])
def test_port_number_rejects_invalid(value: int) -> None:
    with pytest.raises(ValidationError):
        _PORT_NUMBER.validate_python(value)


def test_address_space_values() -> None:
    assert {space.value for space in AddressSpace} == {"PRIVATE", "PUBLIC"}
