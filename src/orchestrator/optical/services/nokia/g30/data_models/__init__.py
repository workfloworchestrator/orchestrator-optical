from __future__ import annotations

"""Auto-generated Pydantic models from YANG schemas"""
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from . import coriant_rpc, ne


class Data(BaseModel):
    """Aggregate root data nodes (config and state)."""

    ne_ne: ne.Ne | None = Field(None, alias="ne:ne")

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class Operations(BaseModel):
    """Aggregate RPC operations."""

    no_op: coriant_rpc.NoOp | None = Field(None, alias="coriant-rpc:no-op")
    default: coriant_rpc.Default | None = Field(None, alias="coriant-rpc:default")
    download: coriant_rpc.Download | None = Field(None, alias="coriant-rpc:download")
    file: coriant_rpc.File | None = Field(None, alias="coriant-rpc:file")
    cert_gen: coriant_rpc.CertGen | None = Field(None, alias="coriant-rpc:cert-gen")
    restart: coriant_rpc.Restart | None = Field(None, alias="coriant-rpc:restart")
    upload: coriant_rpc.Upload | None = Field(None, alias="coriant-rpc:upload")
    set_time: coriant_rpc.SetTime | None = Field(None, alias="coriant-rpc:set-time")
    enable_led: coriant_rpc.EnableLed | None = Field(None, alias="coriant-rpc:enable-led")
    disable_led: coriant_rpc.DisableLed | None = Field(None, alias="coriant-rpc:disable-led")
    start_otdr_measurement: coriant_rpc.StartOtdrMeasurement | None = Field(
        None, alias="coriant-rpc:start-otdr-measurement"
    )
    stop_otdr_measurement: coriant_rpc.StopOtdrMeasurement | None = Field(
        None, alias="coriant-rpc:stop-otdr-measurement"
    )
    activate_3rdparty_fw: coriant_rpc.Activate3rdpartyFw | None = Field(None, alias="coriant-rpc:activate-3rdparty-fw")
    activate_file: coriant_rpc.ActivateFile | None = Field(None, alias="coriant-rpc:activate-file")
    clear_log: coriant_rpc.ClearLog | None = Field(None, alias="coriant-rpc:clear-log")
    clear_database: coriant_rpc.ClearDatabase | None = Field(None, alias="coriant-rpc:clear-database")
    ping: coriant_rpc.Ping | None = Field(None, alias="coriant-rpc:ping")
    traceroute: coriant_rpc.Traceroute | None = Field(None, alias="coriant-rpc:traceroute")
    update_psk_map: coriant_rpc.UpdatePskMap | None = Field(None, alias="coriant-rpc:update-psk-map")
    get_pm: coriant_rpc.GetPm | None = Field(None, alias="coriant-rpc:get-pm")
    clear_pm_data: coriant_rpc.ClearPmData | None = Field(None, alias="coriant-rpc:clear-pm-data")
    clear_statistics_data: coriant_rpc.ClearStatisticsData | None = Field(
        None, alias="coriant-rpc:clear-statistics-data"
    )
    clear_certificate: coriant_rpc.ClearCertificate | None = Field(None, alias="coriant-rpc:clear-certificate")
    clear_trusted_certificate: coriant_rpc.ClearTrustedCertificate | None = Field(
        None, alias="coriant-rpc:clear-trusted-certificate"
    )
    ssh_keygen: coriant_rpc.SshKeygen | None = Field(None, alias="coriant-rpc:ssh-keygen")
    password: coriant_rpc.Password | None = Field(None, alias="coriant-rpc:password")
    reset_test_signal_status: coriant_rpc.ResetTestSignalStatus | None = Field(
        None, alias="coriant-rpc:reset-test-signal-status"
    )
    create_card_services: coriant_rpc.CreateCardServices | None = Field(None, alias="coriant-rpc:create-card-services")
    delete_card_services: coriant_rpc.DeleteCardServices | None = Field(None, alias="coriant-rpc:delete-card-services")
    ifconfig: coriant_rpc.Ifconfig | None = Field(None, alias="coriant-rpc:ifconfig")
    delete2: coriant_rpc.Delete2 | None = Field(None, alias="coriant-rpc:delete2")
    create_rollback_point: coriant_rpc.CreateRollbackPoint | None = Field(
        None, alias="coriant-rpc:create-rollback-point"
    )
    diff: coriant_rpc.Diff | None = Field(None, alias="coriant-rpc:diff")
    rollback: coriant_rpc.Rollback | None = Field(None, alias="coriant-rpc:rollback")
    protection_switch: coriant_rpc.ProtectionSwitch | None = Field(None, alias="coriant-rpc:protection-switch")
    cli_command: coriant_rpc.CliCommand | None = Field(None, alias="coriant-rpc:cli-command")
    measure: coriant_rpc.Measure | None = Field(None, alias="coriant-rpc:measure")
    db_backup: coriant_rpc.DbBackup | None = Field(None, alias="coriant-rpc:db-backup")
    simulate: coriant_rpc.Simulate | None = Field(None, alias="coriant-rpc:simulate")
    repair_info: coriant_rpc.RepairInfo | None = Field(None, alias="coriant-rpc:repair-info")

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)
