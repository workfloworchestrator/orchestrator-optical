from __future__ import annotations

from typing import TYPE_CHECKING

from ._base import Node

if TYPE_CHECKING:
    from . import ioa_alarm, ioa_network_element, ioa_pm, ioa_protection, ioa_rpc, ioa_services, ioa_user_data


class Data(Node):
    """Navigator for data nodes."""

    @property
    def user_data(self) -> ioa_user_data.UserDataNode:
        from .ioa_user_data import UserDataNode
        return UserDataNode(self._client, f"{self._path}/ioa-user-data:user-data", "ioa-user-data:user-data")

    @property
    def ne(self) -> ioa_network_element.NeNode:
        from .ioa_network_element import NeNode
        return NeNode(self._client, f"{self._path}/ioa-network-element:ne", "ioa-network-element:ne")

    @property
    def pm(self) -> ioa_pm.PmNode:
        from .ioa_pm import PmNode
        return PmNode(self._client, f"{self._path}/ioa-pm:pm", "ioa-pm:pm")

    @property
    def alarms(self) -> ioa_alarm.AlarmsNode:
        from .ioa_alarm import AlarmsNode
        return AlarmsNode(self._client, f"{self._path}/ioa-alarm:alarms", "ioa-alarm:alarms")


class Operations(Node):
    """Navigator for RPC operations."""

    @property
    def no_op(self) -> ioa_rpc.NoOpNode:
        from .ioa_rpc import NoOpNode
        return NoOpNode(self._client, f"{self._path}/ioa-rpc:no-op", "ioa-rpc:no-op")

    @property
    def default(self) -> ioa_rpc.DefaultNode:
        from .ioa_rpc import DefaultNode
        return DefaultNode(self._client, f"{self._path}/ioa-rpc:default", "ioa-rpc:default")

    @property
    def verify(self) -> ioa_rpc.VerifyNode:
        from .ioa_rpc import VerifyNode
        return VerifyNode(self._client, f"{self._path}/ioa-rpc:verify", "ioa-rpc:verify")

    @property
    def update(self) -> ioa_rpc.UpdateNode:
        from .ioa_rpc import UpdateNode
        return UpdateNode(self._client, f"{self._path}/ioa-rpc:update", "ioa-rpc:update")

    @property
    def clear_file(self) -> ioa_rpc.ClearFileNode:
        from .ioa_rpc import ClearFileNode
        return ClearFileNode(self._client, f"{self._path}/ioa-rpc:clear-file", "ioa-rpc:clear-file")

    @property
    def clear_app(self) -> ioa_rpc.ClearAppNode:
        from .ioa_rpc import ClearAppNode
        return ClearAppNode(self._client, f"{self._path}/ioa-rpc:clear-app", "ioa-rpc:clear-app")

    @property
    def clear_database(self) -> ioa_rpc.ClearDatabaseNode:
        from .ioa_rpc import ClearDatabaseNode
        return ClearDatabaseNode(self._client, f"{self._path}/ioa-rpc:clear-database", "ioa-rpc:clear-database")

    @property
    def kill_session(self) -> ioa_rpc.KillSessionNode:
        from .ioa_rpc import KillSessionNode
        return KillSessionNode(self._client, f"{self._path}/ioa-rpc:kill-session", "ioa-rpc:kill-session")

    @property
    def clear_certificate(self) -> ioa_rpc.ClearCertificateNode:
        from .ioa_rpc import ClearCertificateNode
        return ClearCertificateNode(self._client, f"{self._path}/ioa-rpc:clear-certificate", "ioa-rpc:clear-certificate")

    @property
    def display_cert(self) -> ioa_rpc.DisplayCertNode:
        from .ioa_rpc import DisplayCertNode
        return DisplayCertNode(self._client, f"{self._path}/ioa-rpc:display-cert", "ioa-rpc:display-cert")

    @property
    def clear_crl(self) -> ioa_rpc.ClearCrlNode:
        from .ioa_rpc import ClearCrlNode
        return ClearCrlNode(self._client, f"{self._path}/ioa-rpc:clear-crl", "ioa-rpc:clear-crl")

    @property
    def ssh_keygen(self) -> ioa_rpc.SshKeygenNode:
        from .ioa_rpc import SshKeygenNode
        return SshKeygenNode(self._client, f"{self._path}/ioa-rpc:ssh-keygen", "ioa-rpc:ssh-keygen")

    @property
    def cert_gen(self) -> ioa_rpc.CertGenNode:
        from .ioa_rpc import CertGenNode
        return CertGenNode(self._client, f"{self._path}/ioa-rpc:cert-gen", "ioa-rpc:cert-gen")

    @property
    def csr_gen(self) -> ioa_rpc.CsrGenNode:
        from .ioa_rpc import CsrGenNode
        return CsrGenNode(self._client, f"{self._path}/ioa-rpc:csr-gen", "ioa-rpc:csr-gen")

    @property
    def diff(self) -> ioa_rpc.DiffNode:
        from .ioa_rpc import DiffNode
        return DiffNode(self._client, f"{self._path}/ioa-rpc:diff", "ioa-rpc:diff")

    @property
    def cli_command(self) -> ioa_rpc.CliCommandNode:
        from .ioa_rpc import CliCommandNode
        return CliCommandNode(self._client, f"{self._path}/ioa-rpc:cli-command", "ioa-rpc:cli-command")

    @property
    def install_krp(self) -> ioa_rpc.InstallKrpNode:
        from .ioa_rpc import InstallKrpNode
        return InstallKrpNode(self._client, f"{self._path}/ioa-rpc:install-krp", "ioa-rpc:install-krp")

    @property
    def delete_isk(self) -> ioa_rpc.DeleteIskNode:
        from .ioa_rpc import DeleteIskNode
        return DeleteIskNode(self._client, f"{self._path}/ioa-rpc:delete-isk", "ioa-rpc:delete-isk")

    @property
    def get_log(self) -> ioa_rpc.GetLogNode:
        from .ioa_rpc import GetLogNode
        return GetLogNode(self._client, f"{self._path}/ioa-rpc:get-log", "ioa-rpc:get-log")

    @property
    def clear_log(self) -> ioa_rpc.ClearLogNode:
        from .ioa_rpc import ClearLogNode
        return ClearLogNode(self._client, f"{self._path}/ioa-rpc:clear-log", "ioa-rpc:clear-log")

    @property
    def change_ztp_mode(self) -> ioa_rpc.ChangeZtpModeNode:
        from .ioa_rpc import ChangeZtpModeNode
        return ChangeZtpModeNode(self._client, f"{self._path}/ioa-rpc:change-ztp-mode", "ioa-rpc:change-ztp-mode")

    @property
    def enable_led(self) -> ioa_rpc.EnableLedNode:
        from .ioa_rpc import EnableLedNode
        return EnableLedNode(self._client, f"{self._path}/ioa-rpc:enable-led", "ioa-rpc:enable-led")

    @property
    def disable_led(self) -> ioa_rpc.DisableLedNode:
        from .ioa_rpc import DisableLedNode
        return DisableLedNode(self._client, f"{self._path}/ioa-rpc:disable-led", "ioa-rpc:disable-led")

    @property
    def profile_control(self) -> ioa_rpc.ProfileControlNode:
        from .ioa_rpc import ProfileControlNode
        return ProfileControlNode(self._client, f"{self._path}/ioa-rpc:profile-control", "ioa-rpc:profile-control")

    @property
    def start_otdr_measurement(self) -> ioa_rpc.StartOtdrMeasurementNode:
        from .ioa_rpc import StartOtdrMeasurementNode
        return StartOtdrMeasurementNode(self._client, f"{self._path}/ioa-rpc:start-otdr-measurement", "ioa-rpc:start-otdr-measurement")

    @property
    def stop_otdr_measurement(self) -> ioa_rpc.StopOtdrMeasurementNode:
        from .ioa_rpc import StopOtdrMeasurementNode
        return StopOtdrMeasurementNode(self._client, f"{self._path}/ioa-rpc:stop-otdr-measurement", "ioa-rpc:stop-otdr-measurement")

    @property
    def stop_cable_id(self) -> ioa_rpc.StopCableIdNode:
        from .ioa_rpc import StopCableIdNode
        return StopCableIdNode(self._client, f"{self._path}/ioa-rpc:stop-cable-id", "ioa-rpc:stop-cable-id")

    @property
    def calibrate(self) -> ioa_rpc.CalibrateNode:
        from .ioa_rpc import CalibrateNode
        return CalibrateNode(self._client, f"{self._path}/ioa-rpc:calibrate", "ioa-rpc:calibrate")

    @property
    def simulate(self) -> ioa_rpc.SimulateNode:
        from .ioa_rpc import SimulateNode
        return SimulateNode(self._client, f"{self._path}/ioa-rpc:simulate", "ioa-rpc:simulate")

    @property
    def restart(self) -> ioa_rpc.RestartNode:
        from .ioa_rpc import RestartNode
        return RestartNode(self._client, f"{self._path}/ioa-rpc:restart", "ioa-rpc:restart")

    @property
    def appctl(self) -> ioa_rpc.AppctlNode:
        from .ioa_rpc import AppctlNode
        return AppctlNode(self._client, f"{self._path}/ioa-rpc:appctl", "ioa-rpc:appctl")

    @property
    def ping(self) -> ioa_rpc.PingNode:
        from .ioa_rpc import PingNode
        return PingNode(self._client, f"{self._path}/ioa-rpc:ping", "ioa-rpc:ping")

    @property
    def traceroute(self) -> ioa_rpc.TracerouteNode:
        from .ioa_rpc import TracerouteNode
        return TracerouteNode(self._client, f"{self._path}/ioa-rpc:traceroute", "ioa-rpc:traceroute")

    @property
    def clear_ospf_instance(self) -> ioa_rpc.ClearOspfInstanceNode:
        from .ioa_rpc import ClearOspfInstanceNode
        return ClearOspfInstanceNode(self._client, f"{self._path}/ioa-rpc:clear-ospf-instance", "ioa-rpc:clear-ospf-instance")

    @property
    def clear_topology(self) -> ioa_rpc.ClearTopologyNode:
        from .ioa_rpc import ClearTopologyNode
        return ClearTopologyNode(self._client, f"{self._path}/ioa-rpc:clear-topology", "ioa-rpc:clear-topology")

    @property
    def clear_system(self) -> ioa_rpc.ClearSystemNode:
        from .ioa_rpc import ClearSystemNode
        return ClearSystemNode(self._client, f"{self._path}/ioa-rpc:clear-system", "ioa-rpc:clear-system")

    @property
    def download(self) -> ioa_rpc.DownloadNode:
        from .ioa_rpc import DownloadNode
        return DownloadNode(self._client, f"{self._path}/ioa-rpc:download", "ioa-rpc:download")

    @property
    def upload(self) -> ioa_rpc.UploadNode:
        from .ioa_rpc import UploadNode
        return UploadNode(self._client, f"{self._path}/ioa-rpc:upload", "ioa-rpc:upload")

    @property
    def import_certificate(self) -> ioa_rpc.ImportCertificateNode:
        from .ioa_rpc import ImportCertificateNode
        return ImportCertificateNode(self._client, f"{self._path}/ioa-rpc:import-certificate", "ioa-rpc:import-certificate")

    @property
    def prepare_upgrade(self) -> ioa_rpc.PrepareUpgradeNode:
        from .ioa_rpc import PrepareUpgradeNode
        return PrepareUpgradeNode(self._client, f"{self._path}/ioa-rpc:prepare-upgrade", "ioa-rpc:prepare-upgrade")

    @property
    def activate_file(self) -> ioa_rpc.ActivateFileNode:
        from .ioa_rpc import ActivateFileNode
        return ActivateFileNode(self._client, f"{self._path}/ioa-rpc:activate-file", "ioa-rpc:activate-file")

    @property
    def cancel_upgrade(self) -> ioa_rpc.CancelUpgradeNode:
        from .ioa_rpc import CancelUpgradeNode
        return CancelUpgradeNode(self._client, f"{self._path}/ioa-rpc:cancel-upgrade", "ioa-rpc:cancel-upgrade")

    @property
    def set_time(self) -> ioa_rpc.SetTimeNode:
        from .ioa_rpc import SetTimeNode
        return SetTimeNode(self._client, f"{self._path}/ioa-rpc:set-time", "ioa-rpc:set-time")

    @property
    def password(self) -> ioa_rpc.PasswordNode:
        from .ioa_rpc import PasswordNode
        return PasswordNode(self._client, f"{self._path}/ioa-rpc:password", "ioa-rpc:password")

    @property
    def clear_recover_mode(self) -> ioa_rpc.ClearRecoverModeNode:
        from .ioa_rpc import ClearRecoverModeNode
        return ClearRecoverModeNode(self._client, f"{self._path}/ioa-rpc:clear-recover-mode", "ioa-rpc:clear-recover-mode")

    @property
    def run_task(self) -> ioa_rpc.RunTaskNode:
        from .ioa_rpc import RunTaskNode
        return RunTaskNode(self._client, f"{self._path}/ioa-rpc:run-task", "ioa-rpc:run-task")

    @property
    def take_snapshot(self) -> ioa_rpc.TakeSnapshotNode:
        from .ioa_rpc import TakeSnapshotNode
        return TakeSnapshotNode(self._client, f"{self._path}/ioa-rpc:take-snapshot", "ioa-rpc:take-snapshot")

    @property
    def get_script(self) -> ioa_rpc.GetScriptNode:
        from .ioa_rpc import GetScriptNode
        return GetScriptNode(self._client, f"{self._path}/ioa-rpc:get-script", "ioa-rpc:get-script")

    @property
    def run_script(self) -> ioa_rpc.RunScriptNode:
        from .ioa_rpc import RunScriptNode
        return RunScriptNode(self._client, f"{self._path}/ioa-rpc:run-script", "ioa-rpc:run-script")

    @property
    def manual_switchover(self) -> ioa_rpc.ManualSwitchoverNode:
        from .ioa_rpc import ManualSwitchoverNode
        return ManualSwitchoverNode(self._client, f"{self._path}/ioa-rpc:manual-switchover", "ioa-rpc:manual-switchover")

    @property
    def file_operation(self) -> ioa_rpc.FileOperationNode:
        from .ioa_rpc import FileOperationNode
        return FileOperationNode(self._client, f"{self._path}/ioa-rpc:file-operation", "ioa-rpc:file-operation")

    @property
    def call_home(self) -> ioa_rpc.CallHomeNode:
        from .ioa_rpc import CallHomeNode
        return CallHomeNode(self._client, f"{self._path}/ioa-rpc:call-home", "ioa-rpc:call-home")

    @property
    def activate_fw(self) -> ioa_rpc.ActivateFwNode:
        from .ioa_rpc import ActivateFwNode
        return ActivateFwNode(self._client, f"{self._path}/ioa-rpc:activate-fw", "ioa-rpc:activate-fw")

    @property
    def re_key(self) -> ioa_rpc.ReKeyNode:
        from .ioa_rpc import ReKeyNode
        return ReKeyNode(self._client, f"{self._path}/ioa-rpc:re-key", "ioa-rpc:re-key")

    @property
    def re_auth(self) -> ioa_rpc.ReAuthNode:
        from .ioa_rpc import ReAuthNode
        return ReAuthNode(self._client, f"{self._path}/ioa-rpc:re-auth", "ioa-rpc:re-auth")

    @property
    def clear_diagnostics(self) -> ioa_rpc.ClearDiagnosticsNode:
        from .ioa_rpc import ClearDiagnosticsNode
        return ClearDiagnosticsNode(self._client, f"{self._path}/ioa-rpc:clear-diagnostics", "ioa-rpc:clear-diagnostics")

    @property
    def get_file(self) -> ioa_rpc.GetFileNode:
        from .ioa_rpc import GetFileNode
        return GetFileNode(self._client, f"{self._path}/ioa-rpc:get-file", "ioa-rpc:get-file")

    @property
    def apply_template(self) -> ioa_rpc.ApplyTemplateNode:
        from .ioa_rpc import ApplyTemplateNode
        return ApplyTemplateNode(self._client, f"{self._path}/ioa-rpc:apply-template", "ioa-rpc:apply-template")

    @property
    def bert(self) -> ioa_rpc.BertNode:
        from .ioa_rpc import BertNode
        return BertNode(self._client, f"{self._path}/ioa-rpc:bert", "ioa-rpc:bert")

    @property
    def db_migrate(self) -> ioa_rpc.DbMigrateNode:
        from .ioa_rpc import DbMigrateNode
        return DbMigrateNode(self._client, f"{self._path}/ioa-rpc:db-migrate", "ioa-rpc:db-migrate")

    @property
    def status(self) -> ioa_rpc.StatusNode:
        from .ioa_rpc import StatusNode
        return StatusNode(self._client, f"{self._path}/ioa-rpc:status", "ioa-rpc:status")

    @property
    def config(self) -> ioa_rpc.ConfigNode:
        from .ioa_rpc import ConfigNode
        return ConfigNode(self._client, f"{self._path}/ioa-rpc:config", "ioa-rpc:config")

    @property
    def get_possible_values(self) -> ioa_rpc.GetPossibleValuesNode:
        from .ioa_rpc import GetPossibleValuesNode
        return GetPossibleValuesNode(self._client, f"{self._path}/ioa-rpc:get-possible-values", "ioa-rpc:get-possible-values")

    @property
    def get_default(self) -> ioa_rpc.GetDefaultNode:
        from .ioa_rpc import GetDefaultNode
        return GetDefaultNode(self._client, f"{self._path}/ioa-rpc:get-default", "ioa-rpc:get-default")

    @property
    def display_access(self) -> ioa_rpc.DisplayAccessNode:
        from .ioa_rpc import DisplayAccessNode
        return DisplayAccessNode(self._client, f"{self._path}/ioa-rpc:display-access", "ioa-rpc:display-access")

    @property
    def get_commit(self) -> ioa_rpc.GetCommitNode:
        from .ioa_rpc import GetCommitNode
        return GetCommitNode(self._client, f"{self._path}/ioa-rpc:get-commit", "ioa-rpc:get-commit")

    @property
    def rollback(self) -> ioa_rpc.RollbackNode:
        from .ioa_rpc import RollbackNode
        return RollbackNode(self._client, f"{self._path}/ioa-rpc:rollback", "ioa-rpc:rollback")

    @property
    def auto_discovery(self) -> ioa_rpc.AutoDiscoveryNode:
        from .ioa_rpc import AutoDiscoveryNode
        return AutoDiscoveryNode(self._client, f"{self._path}/ioa-rpc:auto-discovery", "ioa-rpc:auto-discovery")

    @property
    def create_xcon(self) -> ioa_services.CreateXconNode:
        from .ioa_services import CreateXconNode
        return CreateXconNode(self._client, f"{self._path}/ioa-services:create-xcon", "ioa-services:create-xcon")

    @property
    def get_pm(self) -> ioa_pm.GetPmNode:
        from .ioa_pm import GetPmNode
        return GetPmNode(self._client, f"{self._path}/ioa-pm:get-pm", "ioa-pm:get-pm")

    @property
    def clear_pm(self) -> ioa_pm.ClearPmNode:
        from .ioa_pm import ClearPmNode
        return ClearPmNode(self._client, f"{self._path}/ioa-pm:clear-pm", "ioa-pm:clear-pm")

    @property
    def protection_switch(self) -> ioa_protection.ProtectionSwitchNode:
        from .ioa_protection import ProtectionSwitchNode
        return ProtectionSwitchNode(self._client, f"{self._path}/ioa-protection:protection-switch", "ioa-protection:protection-switch")

    @property
    def set_alarm_state(self) -> ioa_alarm.SetAlarmStateNode:
        from .ioa_alarm import SetAlarmStateNode
        return SetAlarmStateNode(self._client, f"{self._path}/ioa-alarm:set-alarm-state", "ioa-alarm:set-alarm-state")

    @property
    def clear_alarm(self) -> ioa_alarm.ClearAlarmNode:
        from .ioa_alarm import ClearAlarmNode
        return ClearAlarmNode(self._client, f"{self._path}/ioa-alarm:clear-alarm", "ioa-alarm:clear-alarm")

    @property
    def get_conditions(self) -> ioa_alarm.GetConditionsNode:
        from .ioa_alarm import GetConditionsNode
        return GetConditionsNode(self._client, f"{self._path}/ioa-alarm:get-conditions", "ioa-alarm:get-conditions")
