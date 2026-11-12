"""TL1 test doubles, so the real FlexILS SDK and adapter run without a device.

``scripted_client`` is the adapter's :class:`FlexilsClient` over the SDK's
``FakeTransport``: every byte the adapter sends is recorded (``client.sent``) and the
replies are scripted, so a test pins the exact TL1 wire. ``records_response`` is the
lighter double for fakes that replace a whole client method: a response carrying the
given records, in the shape the SDK materializes them. Import this module only after
``pytest.importorskip("flexils_tl1")``.
"""

from collections.abc import Iterable, Iterator, Mapping
from contextlib import contextmanager
from types import SimpleNamespace
from typing import Any, NoReturn

from flexils_tl1 import FakeTransport, reset_ctag_factory, set_ctag_factory
from flexils_tl1.base import BaseResponse, RecordModel
from flexils_tl1.errors import TL1DeniedError
from flexils_tl1.protocol.parser import parse_reply

from orchestrator.optical.hal.adapters.nokia_flexils._shared import FlexilsClient, _records, _tl1_list

TID = "flex.bo01"
GNE_IP = "10.0.0.1"
CTAG = "ZZTAG1"

_AUTH_VALUE = "not-a-real-secret"


def reply(records: Iterable[str] = (), *, status: str = "COMPLD", error: str = "", ctag: str = CTAG) -> str:
    """Build a TL1 reply: one quoted line per record, or the comment of a denial (``error``)."""
    payload = "".join(f'   "{record}"\n' for record in records)
    comment = f"   /* {error} */\n" if error else ""
    return f"\r\n\n   {TID} 25-10-27 16:45:12\nM  {ctag} {status}\n{payload}{comment};\n"


class ScriptedClient(FlexilsClient):
    """A :class:`FlexilsClient` over a ``FakeTransport``, exposing the commands it sent."""

    transport: FakeTransport

    @property
    def sent(self) -> list[str]:
        """The TL1 commands sent after the session login, in order."""
        return [command for command in self.transport.sent if not command.startswith(("ACT-USER", "INH-MSG-ALL"))]


@contextmanager
def scripted_client(replies: Iterable[tuple[str, str]] = (), *, tid: str = TID) -> Iterator[ScriptedClient]:
    """Yield a client whose node answers ``replies``: ordered ``(command prefix, reply)`` pairs.

    A reply is consumed by the first command it prefixes (the longest prefix wins); a
    command no reply matches is answered with a bare ``COMPLD``. The correlation tag is
    pinned to :data:`CTAG` for the duration.
    """

    class _Transport(FakeTransport):
        def _match(self, command: str) -> str:
            try:
                return super()._match(command)
            except KeyError:
                return reply()

    transport = _Transport(list(replies))
    client = ScriptedClient(tid, GNE_IP, transport=transport, username="user", password=_AUTH_VALUE)
    client.transport = transport
    set_ctag_factory(lambda: CTAG)
    try:
        yield client
    finally:
        reset_ctag_factory()
        client.close()


def records_response(records: Iterable[Mapping[str, Any]]) -> Any:
    """Return a response double carrying ``records`` (wire-keyed dicts) as the SDK would.

    List values are joined the TL1 way (``&`` / ``&-``), since the SDK hands every value
    over as the string the node sent.
    """
    models = [
        RecordModel.model_validate(
            {key: _tl1_list(value) if isinstance(value, list | tuple) else value for key, value in record.items()}
        )
        for record in records
    ]
    return SimpleNamespace(records=models)


def deny(command: str, error: str) -> NoReturn:
    """Raise what the SDK raises when the node denies ``command`` with the comment ``error``."""
    raise TL1DeniedError(command, None, None, reply(status="DENY", error=error))


def parsed_records(response_class: type[BaseResponse], records: Iterable[str]) -> list[dict[str, Any]]:
    """Return what the adapter reads from a node answering ``records`` (record lines) to a retrieve."""
    return _records(response_class.from_reply(parse_reply(reply(records))))
