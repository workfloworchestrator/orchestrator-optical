from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._base import ItemNode, ListNode, Node

if TYPE_CHECKING:
    from ..data_models import ioa_rpc


class NoOpNode(Node):
    """Navigator for RPC no-op"""

    def __call__(self) -> None:
        resp = self._client._request("POST", self._path)


class DefaultNode(Node):
    """Navigator for RPC default"""

    def __call__(self, input_data: ioa_rpc.DefaultInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import Default, DefaultInput

        if input_data is None:
            input_data = DefaultInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = DefaultInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = DefaultInput.model_validate_json(input_data)

        rpc_data = Default(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)


class VerifyNode(Node):
    """Navigator for RPC verify"""

    def __call__(
        self, input_data: ioa_rpc.VerifyInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.VerifyOutput:
        from ..data_models.ioa_rpc import Verify, VerifyInput, VerifyOutput

        if input_data is None:
            input_data = VerifyInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = VerifyInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = VerifyInput.model_validate_json(input_data)

        rpc_data = Verify(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return VerifyOutput.model_validate(data)


class UpdateNode(Node):
    """Navigator for RPC update"""

    def __call__(self, input_data: ioa_rpc.UpdateInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import Update, UpdateInput

        if input_data is None:
            input_data = UpdateInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = UpdateInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = UpdateInput.model_validate_json(input_data)

        rpc_data = Update(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)


class ClearFileNode(Node):
    """Navigator for RPC clear-file"""

    def __call__(
        self, input_data: ioa_rpc.ClearFileInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.ClearFileOutput:
        from ..data_models.ioa_rpc import ClearFile, ClearFileInput, ClearFileOutput

        if input_data is None:
            input_data = ClearFileInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = ClearFileInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = ClearFileInput.model_validate_json(input_data)

        rpc_data = ClearFile(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return ClearFileOutput.model_validate(data)


class ClearAppNode(Node):
    """Navigator for RPC clear-app"""

    def __call__(self, input_data: ioa_rpc.ClearAppInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import ClearApp, ClearAppInput

        if input_data is None:
            input_data = ClearAppInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = ClearAppInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = ClearAppInput.model_validate_json(input_data)

        rpc_data = ClearApp(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)


class ClearDatabaseNode(Node):
    """Navigator for RPC clear-database"""

    def __call__(self, input_data: ioa_rpc.ClearDatabaseInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import ClearDatabase, ClearDatabaseInput

        if input_data is None:
            input_data = ClearDatabaseInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = ClearDatabaseInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = ClearDatabaseInput.model_validate_json(input_data)

        rpc_data = ClearDatabase(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)


class KillSessionNode(Node):
    """Navigator for RPC kill-session"""

    def __call__(self, input_data: ioa_rpc.KillSessionInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import KillSession, KillSessionInput

        if input_data is None:
            input_data = KillSessionInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = KillSessionInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = KillSessionInput.model_validate_json(input_data)

        rpc_data = KillSession(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)


class ClearCertificateNode(Node):
    """Navigator for RPC clear-certificate"""

    def __call__(
        self, input_data: ioa_rpc.ClearCertificateInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.ClearCertificateOutput:
        from ..data_models.ioa_rpc import ClearCertificate, ClearCertificateInput, ClearCertificateOutput

        if input_data is None:
            input_data = ClearCertificateInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = ClearCertificateInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = ClearCertificateInput.model_validate_json(input_data)

        rpc_data = ClearCertificate(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return ClearCertificateOutput.model_validate(data)


class DisplayCertNode(Node):
    """Navigator for RPC display-cert"""

    def __call__(
        self, input_data: ioa_rpc.DisplayCertInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.DisplayCertOutput:
        from ..data_models.ioa_rpc import DisplayCert, DisplayCertInput, DisplayCertOutput

        if input_data is None:
            input_data = DisplayCertInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = DisplayCertInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = DisplayCertInput.model_validate_json(input_data)

        rpc_data = DisplayCert(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return DisplayCertOutput.model_validate(data)


class ClearCrlNode(Node):
    """Navigator for RPC clear-crl"""

    def __call__(
        self, input_data: ioa_rpc.ClearCrlInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.ClearCrlOutput:
        from ..data_models.ioa_rpc import ClearCrl, ClearCrlInput, ClearCrlOutput

        if input_data is None:
            input_data = ClearCrlInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = ClearCrlInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = ClearCrlInput.model_validate_json(input_data)

        rpc_data = ClearCrl(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return ClearCrlOutput.model_validate(data)


class SshKeygenNode(Node):
    """Navigator for RPC ssh-keygen"""

    def __call__(self, input_data: ioa_rpc.SshKeygenInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import SshKeygen, SshKeygenInput

        if input_data is None:
            input_data = SshKeygenInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = SshKeygenInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = SshKeygenInput.model_validate_json(input_data)

        rpc_data = SshKeygen(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)


class CertGenNode(Node):
    """Navigator for RPC cert-gen"""

    def __call__(
        self, input_data: ioa_rpc.CertGenInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.CertGenOutput:
        from ..data_models.ioa_rpc import CertGen, CertGenInput, CertGenOutput

        if input_data is None:
            input_data = CertGenInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = CertGenInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = CertGenInput.model_validate_json(input_data)

        rpc_data = CertGen(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return CertGenOutput.model_validate(data)


class CsrGenNode(Node):
    """Navigator for RPC csr-gen"""

    def __call__(
        self, input_data: ioa_rpc.CsrGenInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.CsrGenOutput:
        from ..data_models.ioa_rpc import CsrGen, CsrGenInput, CsrGenOutput

        if input_data is None:
            input_data = CsrGenInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = CsrGenInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = CsrGenInput.model_validate_json(input_data)

        rpc_data = CsrGen(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return CsrGenOutput.model_validate(data)


class DiffNode(Node):
    """Navigator for RPC diff"""

    def __call__(self, input_data: ioa_rpc.DiffInput | dict | str | None = None, **kwargs: Any) -> ioa_rpc.DiffOutput:
        from ..data_models.ioa_rpc import Diff, DiffInput, DiffOutput

        if input_data is None:
            input_data = DiffInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = DiffInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = DiffInput.model_validate_json(input_data)

        rpc_data = Diff(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return DiffOutput.model_validate(data)


class CliCommandNode(Node):
    """Navigator for RPC cli-command"""

    def __call__(
        self, input_data: ioa_rpc.CliCommandInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.CliCommandOutput:
        from ..data_models.ioa_rpc import CliCommand, CliCommandInput, CliCommandOutput

        if input_data is None:
            input_data = CliCommandInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = CliCommandInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = CliCommandInput.model_validate_json(input_data)

        rpc_data = CliCommand(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return CliCommandOutput.model_validate(data)


class InstallKrpNode(Node):
    """Navigator for RPC install-krp"""

    def __call__(
        self, input_data: ioa_rpc.InstallKrpInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.InstallKrpOutput:
        from ..data_models.ioa_rpc import InstallKrp, InstallKrpInput, InstallKrpOutput

        if input_data is None:
            input_data = InstallKrpInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = InstallKrpInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = InstallKrpInput.model_validate_json(input_data)

        rpc_data = InstallKrp(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return InstallKrpOutput.model_validate(data)


class DeleteIskNode(Node):
    """Navigator for RPC delete-isk"""

    def __call__(
        self, input_data: ioa_rpc.DeleteIskInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.DeleteIskOutput:
        from ..data_models.ioa_rpc import DeleteIsk, DeleteIskInput, DeleteIskOutput

        if input_data is None:
            input_data = DeleteIskInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = DeleteIskInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = DeleteIskInput.model_validate_json(input_data)

        rpc_data = DeleteIsk(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return DeleteIskOutput.model_validate(data)


class GetLogNode(Node):
    """Navigator for RPC get-log"""

    def __call__(
        self, input_data: ioa_rpc.GetLogInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.GetLogOutput:
        from ..data_models.ioa_rpc import GetLog, GetLogInput, GetLogOutput

        if input_data is None:
            input_data = GetLogInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = GetLogInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = GetLogInput.model_validate_json(input_data)

        rpc_data = GetLog(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return GetLogOutput.model_validate(data)


class ClearLogNode(Node):
    """Navigator for RPC clear-log"""

    def __call__(self, input_data: ioa_rpc.ClearLogInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import ClearLog, ClearLogInput

        if input_data is None:
            input_data = ClearLogInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = ClearLogInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = ClearLogInput.model_validate_json(input_data)

        rpc_data = ClearLog(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)


class ChangeZtpModeNode(Node):
    """Navigator for RPC change-ztp-mode"""

    def __call__(self, input_data: ioa_rpc.ChangeZtpModeInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import ChangeZtpMode, ChangeZtpModeInput

        if input_data is None:
            input_data = ChangeZtpModeInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = ChangeZtpModeInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = ChangeZtpModeInput.model_validate_json(input_data)

        rpc_data = ChangeZtpMode(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)


class EnableLedNode(Node):
    """Navigator for RPC enable-led"""

    def __call__(self, input_data: ioa_rpc.EnableLedInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import EnableLed, EnableLedInput

        if input_data is None:
            input_data = EnableLedInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = EnableLedInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = EnableLedInput.model_validate_json(input_data)

        rpc_data = EnableLed(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)


class DisableLedNode(Node):
    """Navigator for RPC disable-led"""

    def __call__(self, input_data: ioa_rpc.DisableLedInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import DisableLed, DisableLedInput

        if input_data is None:
            input_data = DisableLedInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = DisableLedInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = DisableLedInput.model_validate_json(input_data)

        rpc_data = DisableLed(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)


class ProfileControlNode(Node):
    """Navigator for RPC profile-control"""

    def __call__(
        self, input_data: ioa_rpc.ProfileControlInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.ProfileControlOutput:
        from ..data_models.ioa_rpc import ProfileControl, ProfileControlInput, ProfileControlOutput

        if input_data is None:
            input_data = ProfileControlInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = ProfileControlInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = ProfileControlInput.model_validate_json(input_data)

        rpc_data = ProfileControl(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return ProfileControlOutput.model_validate(data)


class StartOtdrMeasurementNode(Node):
    """Navigator for RPC start-otdr-measurement"""

    def __call__(self, input_data: ioa_rpc.StartOtdrMeasurementInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import StartOtdrMeasurement, StartOtdrMeasurementInput

        if input_data is None:
            input_data = StartOtdrMeasurementInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = StartOtdrMeasurementInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = StartOtdrMeasurementInput.model_validate_json(input_data)

        rpc_data = StartOtdrMeasurement(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)


class StopOtdrMeasurementNode(Node):
    """Navigator for RPC stop-otdr-measurement"""

    def __call__(self, input_data: ioa_rpc.StopOtdrMeasurementInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import StopOtdrMeasurement, StopOtdrMeasurementInput

        if input_data is None:
            input_data = StopOtdrMeasurementInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = StopOtdrMeasurementInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = StopOtdrMeasurementInput.model_validate_json(input_data)

        rpc_data = StopOtdrMeasurement(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)


class StopCableIdNode(Node):
    """Navigator for RPC stop-cable-id"""

    def __call__(self, input_data: ioa_rpc.StopCableIdInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import StopCableId, StopCableIdInput

        if input_data is None:
            input_data = StopCableIdInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = StopCableIdInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = StopCableIdInput.model_validate_json(input_data)

        rpc_data = StopCableId(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)


class CalibrateNode(Node):
    """Navigator for RPC calibrate"""

    def __call__(
        self, input_data: ioa_rpc.CalibrateInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.CalibrateOutput:
        from ..data_models.ioa_rpc import Calibrate, CalibrateInput, CalibrateOutput

        if input_data is None:
            input_data = CalibrateInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = CalibrateInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = CalibrateInput.model_validate_json(input_data)

        rpc_data = Calibrate(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return CalibrateOutput.model_validate(data)


class SimulateNode(Node):
    """Navigator for RPC simulate"""

    def __call__(self, input_data: ioa_rpc.SimulateInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import Simulate, SimulateInput

        if input_data is None:
            input_data = SimulateInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = SimulateInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = SimulateInput.model_validate_json(input_data)

        rpc_data = Simulate(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)


class RestartNode(Node):
    """Navigator for RPC restart"""

    def __call__(self, input_data: ioa_rpc.RestartInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import Restart, RestartInput

        if input_data is None:
            input_data = RestartInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = RestartInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = RestartInput.model_validate_json(input_data)

        rpc_data = Restart(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)


class AppctlNode(Node):
    """Navigator for RPC appctl"""

    def __call__(
        self, input_data: ioa_rpc.AppctlInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.AppctlOutput:
        from ..data_models.ioa_rpc import Appctl, AppctlInput, AppctlOutput

        if input_data is None:
            input_data = AppctlInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = AppctlInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = AppctlInput.model_validate_json(input_data)

        rpc_data = Appctl(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return AppctlOutput.model_validate(data)


class PingNode(Node):
    """Navigator for RPC ping"""

    def __call__(self, input_data: ioa_rpc.PingInput | dict | str | None = None, **kwargs: Any) -> ioa_rpc.PingOutput:
        from ..data_models.ioa_rpc import Ping, PingInput, PingOutput

        if input_data is None:
            input_data = PingInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = PingInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = PingInput.model_validate_json(input_data)

        rpc_data = Ping(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return PingOutput.model_validate(data)


class TracerouteNode(Node):
    """Navigator for RPC traceroute"""

    def __call__(
        self, input_data: ioa_rpc.TracerouteInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.TracerouteOutput:
        from ..data_models.ioa_rpc import Traceroute, TracerouteInput, TracerouteOutput

        if input_data is None:
            input_data = TracerouteInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = TracerouteInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = TracerouteInput.model_validate_json(input_data)

        rpc_data = Traceroute(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return TracerouteOutput.model_validate(data)


class ClearOspfInstanceNode(Node):
    """Navigator for RPC clear-ospf-instance"""

    def __call__(self, input_data: ioa_rpc.ClearOspfInstanceInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import ClearOspfInstance, ClearOspfInstanceInput

        if input_data is None:
            input_data = ClearOspfInstanceInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = ClearOspfInstanceInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = ClearOspfInstanceInput.model_validate_json(input_data)

        rpc_data = ClearOspfInstance(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)


class ClearTopologyNode(Node):
    """Navigator for RPC clear-topology"""

    def __call__(self, input_data: ioa_rpc.ClearTopologyInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import ClearTopology, ClearTopologyInput

        if input_data is None:
            input_data = ClearTopologyInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = ClearTopologyInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = ClearTopologyInput.model_validate_json(input_data)

        rpc_data = ClearTopology(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)


class ClearSystemNode(Node):
    """Navigator for RPC clear-system"""

    def __call__(
        self, input_data: ioa_rpc.ClearSystemInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.ClearSystemOutput:
        from ..data_models.ioa_rpc import ClearSystem, ClearSystemInput, ClearSystemOutput

        if input_data is None:
            input_data = ClearSystemInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = ClearSystemInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = ClearSystemInput.model_validate_json(input_data)

        rpc_data = ClearSystem(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return ClearSystemOutput.model_validate(data)


class DownloadNode(Node):
    """Navigator for RPC download"""

    def __call__(
        self, input_data: ioa_rpc.DownloadInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.DownloadOutput:
        from ..data_models.ioa_rpc import Download, DownloadInput, DownloadOutput

        if input_data is None:
            input_data = DownloadInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = DownloadInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = DownloadInput.model_validate_json(input_data)

        rpc_data = Download(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return DownloadOutput.model_validate(data)


class UploadNode(Node):
    """Navigator for RPC upload"""

    def __call__(
        self, input_data: ioa_rpc.UploadInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.UploadOutput:
        from ..data_models.ioa_rpc import Upload, UploadInput, UploadOutput

        if input_data is None:
            input_data = UploadInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = UploadInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = UploadInput.model_validate_json(input_data)

        rpc_data = Upload(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return UploadOutput.model_validate(data)


class ImportCertificateNode(Node):
    """Navigator for RPC import-certificate"""

    def __call__(
        self, input_data: ioa_rpc.ImportCertificateInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.ImportCertificateOutput:
        from ..data_models.ioa_rpc import ImportCertificate, ImportCertificateInput, ImportCertificateOutput

        if input_data is None:
            input_data = ImportCertificateInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = ImportCertificateInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = ImportCertificateInput.model_validate_json(input_data)

        rpc_data = ImportCertificate(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return ImportCertificateOutput.model_validate(data)


class PrepareUpgradeNode(Node):
    """Navigator for RPC prepare-upgrade"""

    def __call__(
        self, input_data: ioa_rpc.PrepareUpgradeInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.PrepareUpgradeOutput:
        from ..data_models.ioa_rpc import PrepareUpgrade, PrepareUpgradeInput, PrepareUpgradeOutput

        if input_data is None:
            input_data = PrepareUpgradeInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = PrepareUpgradeInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = PrepareUpgradeInput.model_validate_json(input_data)

        rpc_data = PrepareUpgrade(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return PrepareUpgradeOutput.model_validate(data)


class ActivateFileNode(Node):
    """Navigator for RPC activate-file"""

    def __call__(
        self, input_data: ioa_rpc.ActivateFileInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.ActivateFileOutput:
        from ..data_models.ioa_rpc import ActivateFile, ActivateFileInput, ActivateFileOutput

        if input_data is None:
            input_data = ActivateFileInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = ActivateFileInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = ActivateFileInput.model_validate_json(input_data)

        rpc_data = ActivateFile(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return ActivateFileOutput.model_validate(data)


class CancelUpgradeNode(Node):
    """Navigator for RPC cancel-upgrade"""

    def __call__(self) -> ioa_rpc.CancelUpgradeOutput:
        resp = self._client._request("POST", self._path)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return CancelUpgradeOutput.model_validate(data)


class SetTimeNode(Node):
    """Navigator for RPC set-time"""

    def __call__(self, input_data: ioa_rpc.SetTimeInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import SetTime, SetTimeInput

        if input_data is None:
            input_data = SetTimeInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = SetTimeInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = SetTimeInput.model_validate_json(input_data)

        rpc_data = SetTime(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)


class PasswordNode(Node):
    """Navigator for RPC password"""

    def __call__(self, input_data: ioa_rpc.PasswordInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import Password, PasswordInput

        if input_data is None:
            input_data = PasswordInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = PasswordInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = PasswordInput.model_validate_json(input_data)

        rpc_data = Password(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)


class ClearRecoverModeNode(Node):
    """Navigator for RPC clear-recover-mode"""

    def __call__(self) -> None:
        resp = self._client._request("POST", self._path)


class RunTaskNode(Node):
    """Navigator for RPC run-task"""

    def __call__(self, input_data: ioa_rpc.RunTaskInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import RunTask, RunTaskInput

        if input_data is None:
            input_data = RunTaskInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = RunTaskInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = RunTaskInput.model_validate_json(input_data)

        rpc_data = RunTask(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)


class TakeSnapshotNode(Node):
    """Navigator for RPC take-snapshot"""

    def __call__(self, input_data: ioa_rpc.TakeSnapshotInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import TakeSnapshot, TakeSnapshotInput

        if input_data is None:
            input_data = TakeSnapshotInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = TakeSnapshotInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = TakeSnapshotInput.model_validate_json(input_data)

        rpc_data = TakeSnapshot(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)


class ScriptListItemNode(ItemNode):
    """Navigator for list item script-list"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_rpc.ScriptListItem:
        from ..data_models.ioa_rpc import ScriptListItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ScriptListItem.model_validate(resp)

    def update(self, data: ioa_rpc.ScriptListItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import ScriptListItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ScriptListItem.model_validate(data)
        elif isinstance(data, str):
            data = ScriptListItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_rpc.ScriptListItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import ScriptListItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ScriptListItem.model_validate(data)
        elif isinstance(data, str):
            data = ScriptListItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class ScriptListListNode(ListNode[ScriptListItemNode]):
    """Navigator for list script-list"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_rpc.ScriptListItem]:
        from ..data_models.ioa_rpc import ScriptListItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [ScriptListItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_rpc.ScriptListItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_rpc.ScriptListItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class GetScriptNode(Node):
    """Navigator for RPC get-script"""

    def __call__(
        self, input_data: ioa_rpc.GetScriptInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.GetScriptOutput:
        from ..data_models.ioa_rpc import GetScript, GetScriptInput, GetScriptOutput

        if input_data is None:
            input_data = GetScriptInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = GetScriptInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = GetScriptInput.model_validate_json(input_data)

        rpc_data = GetScript(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return GetScriptOutput.model_validate(data)


class RunScriptNode(Node):
    """Navigator for RPC run-script"""

    def __call__(
        self, input_data: ioa_rpc.RunScriptInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.RunScriptOutput:
        from ..data_models.ioa_rpc import RunScript, RunScriptInput, RunScriptOutput

        if input_data is None:
            input_data = RunScriptInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = RunScriptInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = RunScriptInput.model_validate_json(input_data)

        rpc_data = RunScript(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return RunScriptOutput.model_validate(data)


class ManualSwitchoverNode(Node):
    """Navigator for RPC manual-switchover"""

    def __call__(self, input_data: ioa_rpc.ManualSwitchoverInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import ManualSwitchover, ManualSwitchoverInput

        if input_data is None:
            input_data = ManualSwitchoverInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = ManualSwitchoverInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = ManualSwitchoverInput.model_validate_json(input_data)

        rpc_data = ManualSwitchover(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)


class FileOperationNode(Node):
    """Navigator for RPC file-operation"""

    def __call__(
        self, input_data: ioa_rpc.FileOperationInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.FileOperationOutput:
        from ..data_models.ioa_rpc import FileOperation, FileOperationInput, FileOperationOutput

        if input_data is None:
            input_data = FileOperationInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = FileOperationInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = FileOperationInput.model_validate_json(input_data)

        rpc_data = FileOperation(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return FileOperationOutput.model_validate(data)


class CallHomeNode(Node):
    """Navigator for RPC call-home"""

    def __call__(self, input_data: ioa_rpc.CallHomeInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import CallHome, CallHomeInput

        if input_data is None:
            input_data = CallHomeInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = CallHomeInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = CallHomeInput.model_validate_json(input_data)

        rpc_data = CallHome(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)


class ActivateFwNode(Node):
    """Navigator for RPC activate-fw"""

    def __call__(self, input_data: ioa_rpc.ActivateFwInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import ActivateFw, ActivateFwInput

        if input_data is None:
            input_data = ActivateFwInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = ActivateFwInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = ActivateFwInput.model_validate_json(input_data)

        rpc_data = ActivateFw(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)


class ReKeyNode(Node):
    """Navigator for RPC re-key"""

    def __call__(self, input_data: ioa_rpc.ReKeyInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import ReKey, ReKeyInput

        if input_data is None:
            input_data = ReKeyInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = ReKeyInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = ReKeyInput.model_validate_json(input_data)

        rpc_data = ReKey(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)


class ReAuthNode(Node):
    """Navigator for RPC re-auth"""

    def __call__(self, input_data: ioa_rpc.ReAuthInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import ReAuth, ReAuthInput

        if input_data is None:
            input_data = ReAuthInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = ReAuthInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = ReAuthInput.model_validate_json(input_data)

        rpc_data = ReAuth(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)


class ClearDiagnosticsNode(Node):
    """Navigator for RPC clear-diagnostics"""

    def __call__(self, input_data: ioa_rpc.ClearDiagnosticsInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import ClearDiagnostics, ClearDiagnosticsInput

        if input_data is None:
            input_data = ClearDiagnosticsInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = ClearDiagnosticsInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = ClearDiagnosticsInput.model_validate_json(input_data)

        rpc_data = ClearDiagnostics(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)


class DirectoryListItemNode(ItemNode):
    """Navigator for list item directory-list"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_rpc.DirectoryListItem:
        from ..data_models.ioa_rpc import DirectoryListItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return DirectoryListItem.model_validate(resp)

    def update(self, data: ioa_rpc.DirectoryListItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import DirectoryListItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DirectoryListItem.model_validate(data)
        elif isinstance(data, str):
            data = DirectoryListItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_rpc.DirectoryListItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import DirectoryListItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = DirectoryListItem.model_validate(data)
        elif isinstance(data, str):
            data = DirectoryListItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class DirectoryListListNode(ListNode[DirectoryListItemNode]):
    """Navigator for list directory-list"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_rpc.DirectoryListItem]:
        from ..data_models.ioa_rpc import DirectoryListItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [DirectoryListItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_rpc.DirectoryListItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_rpc.DirectoryListItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class GetFileNode(Node):
    """Navigator for RPC get-file"""

    def __call__(
        self, input_data: ioa_rpc.GetFileInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.GetFileOutput:
        from ..data_models.ioa_rpc import GetFile, GetFileInput, GetFileOutput

        if input_data is None:
            input_data = GetFileInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = GetFileInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = GetFileInput.model_validate_json(input_data)

        rpc_data = GetFile(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return GetFileOutput.model_validate(data)


class ApplyTemplateNode(Node):
    """Navigator for RPC apply-template"""

    def __call__(
        self, input_data: ioa_rpc.ApplyTemplateInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.ApplyTemplateOutput:
        from ..data_models.ioa_rpc import ApplyTemplate, ApplyTemplateInput, ApplyTemplateOutput

        if input_data is None:
            input_data = ApplyTemplateInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = ApplyTemplateInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = ApplyTemplateInput.model_validate_json(input_data)

        rpc_data = ApplyTemplate(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return ApplyTemplateOutput.model_validate(data)


class RecordItemNode(ItemNode):
    """Navigator for list item record"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_rpc.RecordItem:
        from ..data_models.ioa_rpc import RecordItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return RecordItem.model_validate(resp)

    def update(self, data: ioa_rpc.RecordItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import RecordItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RecordItem.model_validate(data)
        elif isinstance(data, str):
            data = RecordItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_rpc.RecordItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import RecordItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = RecordItem.model_validate(data)
        elif isinstance(data, str):
            data = RecordItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class RecordListNode(ListNode[RecordItemNode]):
    """Navigator for list record"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_rpc.RecordItem]:
        from ..data_models.ioa_rpc import RecordItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [RecordItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_rpc.RecordItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_rpc.RecordItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class BertNode(Node):
    """Navigator for RPC bert"""

    def __call__(self, input_data: ioa_rpc.BertInput | dict | str | None = None, **kwargs: Any) -> ioa_rpc.BertOutput:
        from ..data_models.ioa_rpc import Bert, BertInput, BertOutput

        if input_data is None:
            input_data = BertInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = BertInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = BertInput.model_validate_json(input_data)

        rpc_data = Bert(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return BertOutput.model_validate(data)


class DbMigrateNode(Node):
    """Navigator for RPC db-migrate"""

    def __call__(self, input_data: ioa_rpc.DbMigrateInput | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import DbMigrate, DbMigrateInput

        if input_data is None:
            input_data = DbMigrateInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = DbMigrateInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = DbMigrateInput.model_validate_json(input_data)

        rpc_data = DbMigrate(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)


class PortSummaryItemNode(ItemNode):
    """Navigator for list item port-summary"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_rpc.PortSummaryItem:
        from ..data_models.ioa_rpc import PortSummaryItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return PortSummaryItem.model_validate(resp)

    def update(self, data: ioa_rpc.PortSummaryItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import PortSummaryItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PortSummaryItem.model_validate(data)
        elif isinstance(data, str):
            data = PortSummaryItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_rpc.PortSummaryItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import PortSummaryItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = PortSummaryItem.model_validate(data)
        elif isinstance(data, str):
            data = PortSummaryItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class PortSummaryListNode(ListNode[PortSummaryItemNode]):
    """Navigator for list port-summary"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_rpc.PortSummaryItem]:
        from ..data_models.ioa_rpc import PortSummaryItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [PortSummaryItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_rpc.PortSummaryItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_rpc.PortSummaryItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class StatusNode(Node):
    """Navigator for RPC status"""

    def __call__(
        self, input_data: ioa_rpc.StatusInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.StatusOutput:
        from ..data_models.ioa_rpc import Status, StatusInput, StatusOutput

        if input_data is None:
            input_data = StatusInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = StatusInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = StatusInput.model_validate_json(input_data)

        rpc_data = Status(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return StatusOutput.model_validate(data)


class ConfigNode(Node):
    """Navigator for RPC config"""

    def __call__(
        self, input_data: ioa_rpc.ConfigInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.ConfigOutput:
        from ..data_models.ioa_rpc import Config, ConfigInput, ConfigOutput

        if input_data is None:
            input_data = ConfigInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = ConfigInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = ConfigInput.model_validate_json(input_data)

        rpc_data = Config(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return ConfigOutput.model_validate(data)


class GetPossibleValuesNode(Node):
    """Navigator for RPC get-possible-values"""

    def __call__(
        self, input_data: ioa_rpc.GetPossibleValuesInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.GetPossibleValuesOutput:
        from ..data_models.ioa_rpc import GetPossibleValues, GetPossibleValuesInput, GetPossibleValuesOutput

        if input_data is None:
            input_data = GetPossibleValuesInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = GetPossibleValuesInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = GetPossibleValuesInput.model_validate_json(input_data)

        rpc_data = GetPossibleValues(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return GetPossibleValuesOutput.model_validate(data)


class GetDefaultNode(Node):
    """Navigator for RPC get-default"""

    def __call__(
        self, input_data: ioa_rpc.GetDefaultInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.GetDefaultOutput:
        from ..data_models.ioa_rpc import GetDefault, GetDefaultInput, GetDefaultOutput

        if input_data is None:
            input_data = GetDefaultInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = GetDefaultInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = GetDefaultInput.model_validate_json(input_data)

        rpc_data = GetDefault(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return GetDefaultOutput.model_validate(data)


class DisplayAccessNode(Node):
    """Navigator for RPC display-access"""

    def __call__(
        self, input_data: ioa_rpc.DisplayAccessInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.DisplayAccessOutput:
        from ..data_models.ioa_rpc import DisplayAccess, DisplayAccessInput, DisplayAccessOutput

        if input_data is None:
            input_data = DisplayAccessInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = DisplayAccessInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = DisplayAccessInput.model_validate_json(input_data)

        rpc_data = DisplayAccess(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return DisplayAccessOutput.model_validate(data)


class CommandItemNode(ItemNode):
    """Navigator for list item command"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_rpc.CommandItem:
        from ..data_models.ioa_rpc import CommandItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return CommandItem.model_validate(resp)

    def update(self, data: ioa_rpc.CommandItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import CommandItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CommandItem.model_validate(data)
        elif isinstance(data, str):
            data = CommandItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_rpc.CommandItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import CommandItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CommandItem.model_validate(data)
        elif isinstance(data, str):
            data = CommandItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class CommandListNode(ListNode[CommandItemNode]):
    """Navigator for list command"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_rpc.CommandItem]:
        from ..data_models.ioa_rpc import CommandItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [CommandItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_rpc.CommandItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_rpc.CommandItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class ReverseCommandItemNode(ItemNode):
    """Navigator for list item reverse-command"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_rpc.ReverseCommandItem:
        from ..data_models.ioa_rpc import ReverseCommandItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return ReverseCommandItem.model_validate(resp)

    def update(self, data: ioa_rpc.ReverseCommandItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import ReverseCommandItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ReverseCommandItem.model_validate(data)
        elif isinstance(data, str):
            data = ReverseCommandItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_rpc.ReverseCommandItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import ReverseCommandItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = ReverseCommandItem.model_validate(data)
        elif isinstance(data, str):
            data = ReverseCommandItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class ReverseCommandListNode(ListNode[ReverseCommandItemNode]):
    """Navigator for list reverse-command"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_rpc.ReverseCommandItem]:
        from ..data_models.ioa_rpc import ReverseCommandItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [ReverseCommandItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_rpc.ReverseCommandItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_rpc.ReverseCommandItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class CommitRecordItemNode(ItemNode):
    """Navigator for list item commit-record"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_rpc.CommitRecordItem:
        from ..data_models.ioa_rpc import CommitRecordItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return CommitRecordItem.model_validate(resp)

    def update(self, data: ioa_rpc.CommitRecordItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import CommitRecordItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CommitRecordItem.model_validate(data)
        elif isinstance(data, str):
            data = CommitRecordItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_rpc.CommitRecordItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import CommitRecordItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = CommitRecordItem.model_validate(data)
        elif isinstance(data, str):
            data = CommitRecordItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)

    @property
    def command(self) -> CommandListNode:
        return CommandListNode(self._client, f"{self._path}/command", "command", CommandItemNode)

    @property
    def reverse_command(self) -> ReverseCommandListNode:
        return ReverseCommandListNode(
            self._client, f"{self._path}/reverse-command", "reverse-command", ReverseCommandItemNode
        )


class CommitRecordListNode(ListNode[CommitRecordItemNode]):
    """Navigator for list commit-record"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_rpc.CommitRecordItem]:
        from ..data_models.ioa_rpc import CommitRecordItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [CommitRecordItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_rpc.CommitRecordItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_rpc.CommitRecordItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class GetCommitNode(Node):
    """Navigator for RPC get-commit"""

    def __call__(
        self, input_data: ioa_rpc.GetCommitInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.GetCommitOutput:
        from ..data_models.ioa_rpc import GetCommit, GetCommitInput, GetCommitOutput

        if input_data is None:
            input_data = GetCommitInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = GetCommitInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = GetCommitInput.model_validate_json(input_data)

        rpc_data = GetCommit(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return GetCommitOutput.model_validate(data)


class RollbackNode(Node):
    """Navigator for RPC rollback"""

    def __call__(
        self, input_data: ioa_rpc.RollbackInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.RollbackOutput:
        from ..data_models.ioa_rpc import Rollback, RollbackInput, RollbackOutput

        if input_data is None:
            input_data = RollbackInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = RollbackInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = RollbackInput.model_validate_json(input_data)

        rpc_data = Rollback(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return RollbackOutput.model_validate(data)


class AutodRecordItemNode(ItemNode):
    """Navigator for list item autod-record"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> ioa_rpc.AutodRecordItem:
        from ..data_models.ioa_rpc import AutodRecordItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return AutodRecordItem.model_validate(resp)

    def update(self, data: ioa_rpc.AutodRecordItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import AutodRecordItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AutodRecordItem.model_validate(data)
        elif isinstance(data, str):
            data = AutodRecordItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for update. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._update(**payload)

    def replace(self, data: ioa_rpc.AutodRecordItem | dict | str | None = None, **kwargs: Any) -> None:
        from ..data_models.ioa_rpc import AutodRecordItem

        if data is None and kwargs:
            data = {k.replace("_", "-"): v for k, v in kwargs.items()}

        if isinstance(data, dict):
            data = AutodRecordItem.model_validate(data)
        elif isinstance(data, str):
            data = AutodRecordItem.model_validate_json(data)

        if data is None:
            raise ValueError("No data provided for replace. Provide a dict, string, or kwargs.")

        payload = data.model_dump(content="config", exclude_unset=True)
        return self._replace(**payload)


class AutodRecordListNode(ListNode[AutodRecordItemNode]):
    """Navigator for list autod-record"""

    def retrieve(
        self,
        *,
        content: str = "all",
        with_defaults: str = "report-all",
        depth: int | str = 2,
        fields: list[str] | None = None,
    ) -> list[ioa_rpc.AutodRecordItem]:
        from ..data_models.ioa_rpc import AutodRecordItem

        resp = self._retrieve(content=content, with_defaults=with_defaults, depth=depth, fields=fields)
        return [AutodRecordItem.model_validate(item) for item in resp]

    def create(self, data: list[ioa_rpc.AutodRecordItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._create(payload)

    def replace(self, data: list[ioa_rpc.AutodRecordItem]) -> None:
        payload = [x.model_dump(content="config", exclude_unset=True) for x in data]
        return self._replace(payload)


class AutoDiscoveryNode(Node):
    """Navigator for RPC auto-discovery"""

    def __call__(
        self, input_data: ioa_rpc.AutoDiscoveryInput | dict | str | None = None, **kwargs: Any
    ) -> ioa_rpc.AutoDiscoveryOutput:
        from ..data_models.ioa_rpc import AutoDiscovery, AutoDiscoveryInput, AutoDiscoveryOutput

        if input_data is None:
            input_data = AutoDiscoveryInput(**kwargs)
        elif isinstance(input_data, dict):
            input_data = AutoDiscoveryInput.model_validate(input_data)
        elif isinstance(input_data, str):
            input_data = AutoDiscoveryInput.model_validate_json(input_data)

        rpc_data = AutoDiscovery(input=input_data)
        payload = rpc_data.model_dump(mode="json", exclude_unset=True, by_alias=True)
        resp = self._client._request("POST", self._path, json=payload)

        if "output" in resp:
            data = resp.get("output")
        elif "ioa-rpc:output" in resp:
            data = resp.get("ioa-rpc:output")
        else:
            data = resp

        return AutoDiscoveryOutput.model_validate(data)
