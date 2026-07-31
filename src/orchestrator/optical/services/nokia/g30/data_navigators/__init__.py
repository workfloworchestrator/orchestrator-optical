from __future__ import annotations

from typing import TYPE_CHECKING

from ._base import Node

if TYPE_CHECKING:
    from . import coriant_rpc, ne


class Data(Node):
    """Navigator for data nodes."""

    @property
    def ne_ne(self) -> ne.NeNode:
        from .ne import NeNode

        return NeNode(self._client, f"{self._path}/ne:ne", "ne:ne")


class Operations(Node):
    """Navigator for RPC operations."""

    @property
    def no_op(self) -> coriant_rpc.NoOpNode:
        from .coriant_rpc import NoOpNode

        return NoOpNode(self._client, f"{self._path}/coriant-rpc:no-op", "coriant-rpc:no-op")

    @property
    def default(self) -> coriant_rpc.DefaultNode:
        from .coriant_rpc import DefaultNode

        return DefaultNode(self._client, f"{self._path}/coriant-rpc:default", "coriant-rpc:default")

    @property
    def download(self) -> coriant_rpc.DownloadNode:
        from .coriant_rpc import DownloadNode

        return DownloadNode(self._client, f"{self._path}/coriant-rpc:download", "coriant-rpc:download")

    @property
    def file(self) -> coriant_rpc.FileNode:
        from .coriant_rpc import FileNode

        return FileNode(self._client, f"{self._path}/coriant-rpc:file", "coriant-rpc:file")

    @property
    def cert_gen(self) -> coriant_rpc.CertGenNode:
        from .coriant_rpc import CertGenNode

        return CertGenNode(self._client, f"{self._path}/coriant-rpc:cert-gen", "coriant-rpc:cert-gen")

    @property
    def restart(self) -> coriant_rpc.RestartNode:
        from .coriant_rpc import RestartNode

        return RestartNode(self._client, f"{self._path}/coriant-rpc:restart", "coriant-rpc:restart")

    @property
    def upload(self) -> coriant_rpc.UploadNode:
        from .coriant_rpc import UploadNode

        return UploadNode(self._client, f"{self._path}/coriant-rpc:upload", "coriant-rpc:upload")

    @property
    def set_time(self) -> coriant_rpc.SetTimeNode:
        from .coriant_rpc import SetTimeNode

        return SetTimeNode(self._client, f"{self._path}/coriant-rpc:set-time", "coriant-rpc:set-time")

    @property
    def enable_led(self) -> coriant_rpc.EnableLedNode:
        from .coriant_rpc import EnableLedNode

        return EnableLedNode(self._client, f"{self._path}/coriant-rpc:enable-led", "coriant-rpc:enable-led")

    @property
    def disable_led(self) -> coriant_rpc.DisableLedNode:
        from .coriant_rpc import DisableLedNode

        return DisableLedNode(self._client, f"{self._path}/coriant-rpc:disable-led", "coriant-rpc:disable-led")

    @property
    def start_otdr_measurement(self) -> coriant_rpc.StartOtdrMeasurementNode:
        from .coriant_rpc import StartOtdrMeasurementNode

        return StartOtdrMeasurementNode(
            self._client, f"{self._path}/coriant-rpc:start-otdr-measurement", "coriant-rpc:start-otdr-measurement"
        )

    @property
    def stop_otdr_measurement(self) -> coriant_rpc.StopOtdrMeasurementNode:
        from .coriant_rpc import StopOtdrMeasurementNode

        return StopOtdrMeasurementNode(
            self._client, f"{self._path}/coriant-rpc:stop-otdr-measurement", "coriant-rpc:stop-otdr-measurement"
        )

    @property
    def activate_3rdparty_fw(self) -> coriant_rpc.Activate3rdpartyFwNode:
        from .coriant_rpc import Activate3rdpartyFwNode

        return Activate3rdpartyFwNode(
            self._client, f"{self._path}/coriant-rpc:activate-3rdparty-fw", "coriant-rpc:activate-3rdparty-fw"
        )

    @property
    def activate_file(self) -> coriant_rpc.ActivateFileNode:
        from .coriant_rpc import ActivateFileNode

        return ActivateFileNode(self._client, f"{self._path}/coriant-rpc:activate-file", "coriant-rpc:activate-file")

    @property
    def clear_log(self) -> coriant_rpc.ClearLogNode:
        from .coriant_rpc import ClearLogNode

        return ClearLogNode(self._client, f"{self._path}/coriant-rpc:clear-log", "coriant-rpc:clear-log")

    @property
    def clear_database(self) -> coriant_rpc.ClearDatabaseNode:
        from .coriant_rpc import ClearDatabaseNode

        return ClearDatabaseNode(self._client, f"{self._path}/coriant-rpc:clear-database", "coriant-rpc:clear-database")

    @property
    def ping(self) -> coriant_rpc.PingNode:
        from .coriant_rpc import PingNode

        return PingNode(self._client, f"{self._path}/coriant-rpc:ping", "coriant-rpc:ping")

    @property
    def traceroute(self) -> coriant_rpc.TracerouteNode:
        from .coriant_rpc import TracerouteNode

        return TracerouteNode(self._client, f"{self._path}/coriant-rpc:traceroute", "coriant-rpc:traceroute")

    @property
    def update_psk_map(self) -> coriant_rpc.UpdatePskMapNode:
        from .coriant_rpc import UpdatePskMapNode

        return UpdatePskMapNode(self._client, f"{self._path}/coriant-rpc:update-psk-map", "coriant-rpc:update-psk-map")

    @property
    def get_pm(self) -> coriant_rpc.GetPmNode:
        from .coriant_rpc import GetPmNode

        return GetPmNode(self._client, f"{self._path}/coriant-rpc:get-pm", "coriant-rpc:get-pm")

    @property
    def clear_pm_data(self) -> coriant_rpc.ClearPmDataNode:
        from .coriant_rpc import ClearPmDataNode

        return ClearPmDataNode(self._client, f"{self._path}/coriant-rpc:clear-pm-data", "coriant-rpc:clear-pm-data")

    @property
    def clear_statistics_data(self) -> coriant_rpc.ClearStatisticsDataNode:
        from .coriant_rpc import ClearStatisticsDataNode

        return ClearStatisticsDataNode(
            self._client, f"{self._path}/coriant-rpc:clear-statistics-data", "coriant-rpc:clear-statistics-data"
        )

    @property
    def clear_certificate(self) -> coriant_rpc.ClearCertificateNode:
        from .coriant_rpc import ClearCertificateNode

        return ClearCertificateNode(
            self._client, f"{self._path}/coriant-rpc:clear-certificate", "coriant-rpc:clear-certificate"
        )

    @property
    def clear_trusted_certificate(self) -> coriant_rpc.ClearTrustedCertificateNode:
        from .coriant_rpc import ClearTrustedCertificateNode

        return ClearTrustedCertificateNode(
            self._client, f"{self._path}/coriant-rpc:clear-trusted-certificate", "coriant-rpc:clear-trusted-certificate"
        )

    @property
    def ssh_keygen(self) -> coriant_rpc.SshKeygenNode:
        from .coriant_rpc import SshKeygenNode

        return SshKeygenNode(self._client, f"{self._path}/coriant-rpc:ssh-keygen", "coriant-rpc:ssh-keygen")

    @property
    def password(self) -> coriant_rpc.PasswordNode:
        from .coriant_rpc import PasswordNode

        return PasswordNode(self._client, f"{self._path}/coriant-rpc:password", "coriant-rpc:password")

    @property
    def reset_test_signal_status(self) -> coriant_rpc.ResetTestSignalStatusNode:
        from .coriant_rpc import ResetTestSignalStatusNode

        return ResetTestSignalStatusNode(
            self._client, f"{self._path}/coriant-rpc:reset-test-signal-status", "coriant-rpc:reset-test-signal-status"
        )

    @property
    def create_card_services(self) -> coriant_rpc.CreateCardServicesNode:
        from .coriant_rpc import CreateCardServicesNode

        return CreateCardServicesNode(
            self._client, f"{self._path}/coriant-rpc:create-card-services", "coriant-rpc:create-card-services"
        )

    @property
    def delete_card_services(self) -> coriant_rpc.DeleteCardServicesNode:
        from .coriant_rpc import DeleteCardServicesNode

        return DeleteCardServicesNode(
            self._client, f"{self._path}/coriant-rpc:delete-card-services", "coriant-rpc:delete-card-services"
        )

    @property
    def ifconfig(self) -> coriant_rpc.IfconfigNode:
        from .coriant_rpc import IfconfigNode

        return IfconfigNode(self._client, f"{self._path}/coriant-rpc:ifconfig", "coriant-rpc:ifconfig")

    @property
    def delete2(self) -> coriant_rpc.Delete2Node:
        from .coriant_rpc import Delete2Node

        return Delete2Node(self._client, f"{self._path}/coriant-rpc:delete2", "coriant-rpc:delete2")

    @property
    def create_rollback_point(self) -> coriant_rpc.CreateRollbackPointNode:
        from .coriant_rpc import CreateRollbackPointNode

        return CreateRollbackPointNode(
            self._client, f"{self._path}/coriant-rpc:create-rollback-point", "coriant-rpc:create-rollback-point"
        )

    @property
    def diff(self) -> coriant_rpc.DiffNode:
        from .coriant_rpc import DiffNode

        return DiffNode(self._client, f"{self._path}/coriant-rpc:diff", "coriant-rpc:diff")

    @property
    def rollback(self) -> coriant_rpc.RollbackNode:
        from .coriant_rpc import RollbackNode

        return RollbackNode(self._client, f"{self._path}/coriant-rpc:rollback", "coriant-rpc:rollback")

    @property
    def protection_switch(self) -> coriant_rpc.ProtectionSwitchNode:
        from .coriant_rpc import ProtectionSwitchNode

        return ProtectionSwitchNode(
            self._client, f"{self._path}/coriant-rpc:protection-switch", "coriant-rpc:protection-switch"
        )

    @property
    def cli_command(self) -> coriant_rpc.CliCommandNode:
        from .coriant_rpc import CliCommandNode

        return CliCommandNode(self._client, f"{self._path}/coriant-rpc:cli-command", "coriant-rpc:cli-command")

    @property
    def measure(self) -> coriant_rpc.MeasureNode:
        from .coriant_rpc import MeasureNode

        return MeasureNode(self._client, f"{self._path}/coriant-rpc:measure", "coriant-rpc:measure")

    @property
    def db_backup(self) -> coriant_rpc.DbBackupNode:
        from .coriant_rpc import DbBackupNode

        return DbBackupNode(self._client, f"{self._path}/coriant-rpc:db-backup", "coriant-rpc:db-backup")

    @property
    def simulate(self) -> coriant_rpc.SimulateNode:
        from .coriant_rpc import SimulateNode

        return SimulateNode(self._client, f"{self._path}/coriant-rpc:simulate", "coriant-rpc:simulate")

    @property
    def repair_info(self) -> coriant_rpc.RepairInfoNode:
        from .coriant_rpc import RepairInfoNode

        return RepairInfoNode(self._client, f"{self._path}/coriant-rpc:repair-info", "coriant-rpc:repair-info")
