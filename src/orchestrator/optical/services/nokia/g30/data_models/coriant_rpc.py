"""Auto-generated Pydantic models from YANG schemas"""

import re
from decimal import Decimal
from enum import Enum
from typing import Annotated, Any, TypeVar

from pydantic import AfterValidator, BaseModel, BeforeValidator, ConfigDict, Field, PlainSerializer

from ._base import YangBaseModel


# RFC 7951: 64-bit numbers MUST be represented as JSON strings.
# here we use PlainSerializer to ensure string output during JSON serialization (mode='json').
def format_at_least_two_places(v: Decimal) -> str:
    # Normalize to remove unnecessary trailing zeros (e.g., 1.500 -> 1.5)
    v = v.normalize()

    # Exponent 0 = integer (1), -1 = one decimal (1.1), -2 = two decimals (1.11)
    # If it's greater than -2, it means we have 0 or 1 decimal places.
    if v.as_tuple().exponent > -2:
        return format(v.quantize(Decimal("0.01")), "f")

    # Otherwise, return the normalized string (keeps 3+ decimal places)
    return format(v, "f")


Decimal64 = Annotated[Decimal, PlainSerializer(format_at_least_two_places, return_type=str)]
Uint64 = Annotated[int, PlainSerializer(lambda v: str(v), return_type=str)]
Int64 = Annotated[int, PlainSerializer(lambda v: str(v), return_type=str)]


def check_pattern(pattern: str, v: str) -> str:
    if isinstance(v, str) and not re.match(pattern, v):
        raise ValueError(f"Value does not match pattern: {pattern}")
    return v


T = TypeVar("T")


def restconf_list_validator(v: Any) -> Any:
    """RESTCONF quirk: Truncated lists (via depth) often return {} instead of [].
    Also handles 'None' or missing data if needed.
    """
    if isinstance(v, dict) and not v:
        return []
    # In some truly cursed implementations, a single item list is returned as an object
    # but we will stick to the 'empty dict to list' fix for now.
    return v


# Define a reusable type for RESTCONF lists
RestconfList = Annotated[list[T], BeforeValidator(restconf_list_validator)]


class NoOp(BaseModel):
    """RPC: no-op"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class StatusEnum(str, Enum):
    """Enumeration for StatusEnum

    Values:
      * Successful
      * Failed
      * In-progress
    """

    SUCCESSFUL = "Successful"
    FAILED = "Failed"
    IN_PROGRESS = "In-progress"


class DefaultInput(YangBaseModel):
    """Input: None"""

    entity_id: RestconfList[str] = Field(
        json_schema_extra={"is_config": None},
        description="Instances to be defaulted. Supported objects: pm-thresholds-value and alarm-profile-entry",
        alias="entity-id",
    )


class DefaultOutput(YangBaseModel):
    """Output: None"""

    status: StatusEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Successful, Failed or In-progress",
        default=StatusEnum.SUCCESSFUL,
    )
    status_message: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Gives a more detailed status.",
        min_length=0,
        max_length=256,
        default=None,
        alias="status-message",
    )


class Default(BaseModel):
    """RPC: default"""

    input: DefaultInput
    output: DefaultOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class FiletypeEnum(str, Enum):
    """Enumeration for FiletypeEnum

    Values:
      * database: Database
      * swimage: SW Image
      * file: download 3rd party FW file
      * trustedcert: trusted certificate
      * certificate: local host certificate
    """

    DATABASE = "database"
    SWIMAGE = "swimage"
    FILE = "file"
    TRUSTEDCERT = "trustedcert"
    CERTIFICATE = "certificate"


class AutoDownloadCertificateChainEnum(str, Enum):
    """Enumeration for AutoDownloadCertificateChainEnum

    Values:
      * none: Do not use AIA extension to download parent certificates.
      * intermediate-only: Use AIA extension to download all intermediate certificates. The certificates are only installed if the corresponding root certificate is already installed as a trusted certificate, and the chain verification is successful.
      * all: Use AIA extension to download all certificates of the certificate chain, including the root certificate.
    """

    NONE = "none"
    INTERMEDIATE_ONLY = "intermediate-only"
    ALL = "all"


class DownloadInput(YangBaseModel):
    """Input: None"""

    filetype: FiletypeEnum = Field(
        json_schema_extra={"is_config": None}, description="Predefined filetype available for download"
    )
    trusted_cert_group_name: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_:\\.]*)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="Specifies the trusted certificate group name in the keystore.\n\nCondition (when): ../filetype = 'trustedcert'",
        min_length=1,
        max_length=128,
        default=None,
        alias="trusted-cert-group-name",
    )
    trusted_cert_name: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_:\\.]*)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="Specifies the trusted certificate group name in the keystore.\n\nCondition (when): ../filetype = 'trustedcert'",
        min_length=1,
        max_length=128,
        default=None,
        alias="trusted-cert-name",
    )
    key_name: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_:\\.]*)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="Specifies the key name in the keystore.\n\nCondition (when): ../filetype = 'certificate'",
        min_length=1,
        max_length=128,
        default=None,
        alias="key-name",
    )
    auto_download_certificate_chain: AutoDownloadCertificateChainEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Specifies how to use the AIA extension and which certificates in the certificate chain should be downloaded and installed.\n\nCondition (when): ../filetype = 'certificate'",
        default=AutoDownloadCertificateChainEnum.NONE,
        alias="auto-download-certificate-chain",
    )
    certificate_name: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_:\\.]*)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="Specifies the certificate name under a key in the keystore.\n\nCondition (when): ../filetype = 'certificate'",
        min_length=1,
        max_length=128,
        default=None,
        alias="certificate-name",
    )
    source: Annotated[
        str, AfterValidator(lambda v: check_pattern("^(?:((ftp|sftp|ftps|scp|http):/)?/[^\\s/$.?#'].[^\\s']*)$", v))
    ] = Field(
        json_schema_extra={"is_config": None},
        description="Source of the download ([sftp|scp|http]://[user@]hostname/directorypath/filename)",
        min_length=1,
        max_length=1024,
    )
    destination: str | None = Field(
        json_schema_extra={"is_config": None}, description="Condition (when): ../filetype = 'file'", default=None
    )
    password: str | None = Field(
        json_schema_extra={"is_config": None},
        description="SFTP/SCP password\n\nCondition (when): starts-with(../source,'scp') or starts-with(../source,'sftp')",
        min_length=1,
        max_length=255,
        default=None,
    )
    certificate_password: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Specifies the password of the certificate.\n\nCondition (when): ../filetype = 'certificate'",
        min_length=0,
        max_length=255,
        default=None,
        alias="certificate-password",
    )


class DownloadOutput(YangBaseModel):
    """Output: None"""

    download_result: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Result of the download operation",
        default=None,
        alias="download-result",
    )


class Download(BaseModel):
    """RPC: download"""

    input: DownloadInput
    output: DownloadOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class FileOperationEnum(str, Enum):
    """Enumeration for FileOperationEnum

    Values:
      * rename: Renames a file or directory.
      * delete: Deletes a file.
      * view: Does listing for a file or directory.
      * sha256sum: Generates SHA256 hash checksum of a file.
      * md5sum: Generates md5 hash checksum of a file.
    """

    RENAME = "rename"
    DELETE = "delete"
    VIEW = "view"
    SHA256SUM = "sha256sum"
    MD5SUM = "md5sum"


class FileInput(YangBaseModel):
    """Input: None"""

    file_operation: FileOperationEnum | None = Field(
        json_schema_extra={"is_config": None}, description="File operations to do.", default=None
    )
    file_path: str = Field(
        json_schema_extra={"is_config": None},
        description="Current file path.",
        min_length=0,
        max_length=255,
        alias="file-path",
    )
    new_file_path: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/\\.]*)$", v))] | None = (
        Field(
            json_schema_extra={"is_config": None},
            description="New file path.\n\nCondition (when): ../file_operation = 'rename'",
            min_length=0,
            max_length=255,
            default=None,
            alias="new-file-path",
        )
    )


class FileOutput(YangBaseModel):
    """Output: None"""

    result: str | None = Field(
        json_schema_extra={"is_config": None}, description="The file operation result.", default=None
    )


class File(BaseModel):
    """RPC: file"""

    input: FileInput
    output: FileOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class CertGenInput(YangBaseModel):
    """Input: None"""

    days: int = Field(
        json_schema_extra={"is_config": None}, description="number of days a certificate is valid for.", ge=0
    )
    country_code: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Country Code.",
        min_length=2,
        max_length=2,
        default=None,
        alias="country-code",
    )
    state: str | None = Field(
        json_schema_extra={"is_config": None}, description="State.", min_length=1, max_length=128, default=None
    )
    locality: str | None = Field(
        json_schema_extra={"is_config": None}, description="Locality.", min_length=1, max_length=128, default=None
    )
    org_name: str = Field(
        json_schema_extra={"is_config": None},
        description="Organization Name.",
        min_length=1,
        max_length=64,
        alias="org-name",
    )
    common_name: str = Field(
        json_schema_extra={"is_config": None},
        description="Name to identify the server.",
        min_length=1,
        max_length=64,
        alias="common-name",
    )
    san: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:((IP:|DNS:)(?!([^,]*(IP:|DNS:)))[A-Za-z0-9\\-\\.:]+(,(IP:|DNS:)(?!([^,]*(IP:|DNS:)))[A-Za-z0-9\\-\\.:]+)*)?)$",
                    v,
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="The certificate SAN (Subject Alternative Name) fields.\nSANs are specified as a sequence of 'IP:' or 'DNS:' prefixed strings separated by a comma ','.\nIn each field, only letters, digits, '-', '.' and ':' are allowed. All other characters generate a syntax error.\nAn empty string is also allowed and it is the default value.\nExample OK: 'IP:127.0.0.1,DNS:localhost,IP:2001:db8::f:64'\nExample OK: ''\nExample incorrect: 'ip:127.0.0.1,dns:my_website.com'",
        min_length=0,
        max_length=1024,
        default=None,
    )
    key_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_:\\.]*)$", v))] = (
        Field(
            json_schema_extra={"is_config": None},
            description="Specifies the key name in the keystore.",
            min_length=1,
            max_length=128,
            alias="key-name",
        )
    )
    certificate_name: Annotated[
        str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_:\\.]*)$", v))
    ] = Field(
        json_schema_extra={"is_config": None},
        description="Specifies the certificate name under a key in the keystore.",
        min_length=1,
        max_length=128,
        alias="certificate-name",
    )


class CertGenOutput(YangBaseModel):
    """Output: None"""

    status: StatusEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Successful, Failed or In-progress",
        default=StatusEnum.SUCCESSFUL,
    )
    status_message: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Gives a more detailed status.",
        min_length=0,
        max_length=256,
        default=None,
        alias="status-message",
    )


class CertGen(BaseModel):
    """RPC: cert-gen"""

    input: CertGenInput
    output: CertGenOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class RestartTypeEnum(str, Enum):
    """Enumeration for RestartTypeEnum

    Values:
      * warm
      * cold
    """

    WARM = "warm"
    COLD = "cold"


class RestartInput(YangBaseModel):
    """Input: None"""

    entity_id: str = Field(json_schema_extra={"is_config": None}, description="Entity to restart", alias="entity-id")
    restart_type: RestartTypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Restart type",
        default=RestartTypeEnum.WARM,
        alias="restart-type",
    )
    fpga_upgrade: bool | None = Field(
        json_schema_extra={"is_config": None},
        description="Hitless upgrade FPGA selection\n\nCondition (when): ../restart-type = 'warm'",
        default=None,
        alias="fpga-upgrade",
    )
    dsp_upgrade: bool | None = Field(
        json_schema_extra={"is_config": None},
        description="Hitless upgrade dsp selection\n\nCondition (when): ../restart-type = 'warm'",
        default=None,
        alias="dsp-upgrade",
    )


class RestartOutput(YangBaseModel):
    """Output: None"""

    status: StatusEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Successful, Failed or In-progress",
        default=StatusEnum.SUCCESSFUL,
    )
    status_message: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Gives a more detailed status.",
        min_length=0,
        max_length=256,
        default=None,
        alias="status-message",
    )


class Restart(BaseModel):
    """RPC: restart"""

    input: RestartInput
    output: RestartOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class FiletypeEnum_1(str, Enum):
    """Enumeration for FiletypeEnum

    Values:
      * pmhistlog: PM History Log
      * securitylog: Security Log
      * database: Database
      * diagnosticslog: Diagnostic Data
      * summarylog: Summary log files including configlog, almlog and eventlog
      * httpscert: https server certificate
      * otdr: otdr measurement result
      * certificate: local certificate
      * csr: Certificate Signing Request
    """

    PMHISTLOG = "pmhistlog"
    SECURITYLOG = "securitylog"
    DATABASE = "database"
    DIAGNOSTICSLOG = "diagnosticslog"
    SUMMARYLOG = "summarylog"
    HTTPSCERT = "httpscert"
    OTDR = "otdr"
    CERTIFICATE = "certificate"
    CSR = "csr"


class UploadInput(YangBaseModel):
    """Input: None"""

    filetype: FiletypeEnum_1 = Field(json_schema_extra={"is_config": None}, description="Filetype available for upload")
    target_entity: str | None = Field(
        json_schema_extra={"is_config": None},
        description="The target entity of otdr measurement result to be uploaded\n\nCondition (when): ../filetype = 'otdr'",
        default=None,
        alias="target-entity",
    )
    file_description: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-\\.]*)$", v))] | None = (
        Field(
            json_schema_extra={"is_config": None},
            description="The additional description of the file\n\nCondition (when): ../filetype = 'otdr'",
            min_length=0,
            max_length=64,
            default=None,
            alias="file-description",
        )
    )
    key_name: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_:\\.]*)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="Specifies the key name in the keystore.\n\nCondition (when): ../filetype = 'certificate'",
        min_length=1,
        max_length=128,
        default=None,
        alias="key-name",
    )
    certificate_name: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9][a-zA-Z0-9\\-_:\\.]*)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="Specifies the certificate name under a key in the keystore.\n\nCondition (when): ../filetype = 'certificate'",
        min_length=1,
        max_length=128,
        default=None,
        alias="certificate-name",
    )
    shelf: int | None = Field(
        json_schema_extra={"is_config": None},
        description="The shelf ID for which to collect diagnostic logs. Value 0 indicates all available shelves.\n\nCondition (when): ../filetype = 'diagnosticslog'",
        ge=0,
        le=32,
        default=0,
    )
    destination: Annotated[
        str, AfterValidator(lambda v: check_pattern("^(?:((ftp|sftp|ftps|scp|http):/)?/[^\\s/$.?#'].[^\\s']*)$", v))
    ] = Field(
        json_schema_extra={"is_config": None},
        description="Destination of the upload ([sftp|scp]://user@hostname/directorypath/filename)",
        min_length=1,
        max_length=1024,
    )
    password: str = Field(
        json_schema_extra={"is_config": None},
        description="SFTP/SCP password for both destination and csr-conf-file",
        min_length=1,
        max_length=255,
    )
    csr_key_id: str | None = Field(
        json_schema_extra={"is_config": None},
        description="The private key to generate CSR.\n\nCondition (when): ../filetype = 'csr'",
        default=None,
        alias="csr-key-id",
    )
    csr_subj: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Specifies the subject of CSR used by openssl command.\n\nCondition (when): ../filetype = 'csr'",
        min_length=0,
        max_length=512,
        default=None,
        alias="csr-subj",
    )
    csr_conf_file: (
        Annotated[
            str, AfterValidator(lambda v: check_pattern("^(?:((ftp|sftp|ftps|scp|http):/)?/[^\\s/$.?#'].[^\\s']*)$", v))
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="File server path of openssl CNF file to be downloaded for the CSR generation\n([sftp|scp]://user@hostname/directorypath/filename), this parameter is necessary if more\ninformation than csr-subj is needed for the CSR generation, e.g., X509v3 Subject Alternative Names;\ncsr-conf-file must be on the same file server of the destination parameter, i.e., same file transfer protocol,\nsame server hostname, and the same user name on the server.\n\nCondition (when): ../filetype = 'csr'",
        min_length=1,
        max_length=1024,
        default=None,
        alias="csr-conf-file",
    )


class UploadOutput(YangBaseModel):
    """Output: None"""

    result: str | None = Field(
        json_schema_extra={"is_config": None}, description="Result of the upload operation", default=None
    )


class Upload(BaseModel):
    """RPC: upload"""

    input: UploadInput
    output: UploadOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class SetTimeInput(YangBaseModel):
    """Input: None"""

    new_time: Annotated[
        str,
        AfterValidator(
            lambda v: check_pattern(
                "^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v
            )
        ),
    ] = Field(json_schema_extra={"is_config": None}, description="Time to set in the system", alias="new-time")


class SetTimeOutput(YangBaseModel):
    """Output: None"""

    status: StatusEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Successful, Failed or In-progress",
        default=StatusEnum.SUCCESSFUL,
    )
    status_message: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Gives a more detailed status.",
        min_length=0,
        max_length=256,
        default=None,
        alias="status-message",
    )


class SetTime(BaseModel):
    """RPC: set-time"""

    input: SetTimeInput
    output: SetTimeOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class ConfigurableLedTypesEnum(str, Enum):
    """Enumeration for ConfigurableLedTypesEnum

    Values:
      * led-test: Tests all the system LEDs
      * location-led: Enables the location LED
    """

    LED_TEST = "led-test"
    LOCATION_LED = "location-led"


class LedTestOperationEnum(str, Enum):
    """Enumeration for LedTestOperationEnum

    Values:
      * flash
      * solid
    """

    FLASH = "flash"
    SOLID = "solid"


class EnableLedInput(YangBaseModel):
    """Input: None"""

    led_type: ConfigurableLedTypesEnum = Field(
        json_schema_extra={"is_config": None}, description="The type of LED to be activated", alias="led-type"
    )
    led_entity: str | None = Field(
        json_schema_extra={"is_config": None},
        description="The LED test entity. Shelf means enable all LED on the shelf.\nCard or subcard will enable the specific card or subcard module only.\nWithout any input will be shelf\n\nCondition (when): ../led-type = 'led-test'",
        default=None,
        alias="led-entity",
    )
    led_test_operation: LedTestOperationEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="The LED test operation:\nflash will selected entity flash by 1Hz frequency;\nsolid will hold on light.\nWithout any input will be solid.\n\nCondition (when): ../led-type = 'led-test'",
        default=None,
        alias="led-test-operation",
    )
    led_timer: int | None = Field(
        json_schema_extra={"is_config": None},
        description="The time the LED should be activated. Zero disables the timer (LED status statically on).\nLED can be disabled using the disable-led RPC.",
        ge=0,
        le=120,
        default=30,
        alias="led-timer",
    )


class EnableLedOutput(YangBaseModel):
    """Output: None"""

    status: StatusEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Successful, Failed or In-progress",
        default=StatusEnum.SUCCESSFUL,
    )
    status_message: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Gives a more detailed status.",
        min_length=0,
        max_length=256,
        default=None,
        alias="status-message",
    )


class EnableLed(BaseModel):
    """RPC: enable-led"""

    input: EnableLedInput
    output: EnableLedOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class DisableLedInput(YangBaseModel):
    """Input: None"""

    led_type: ConfigurableLedTypesEnum = Field(
        json_schema_extra={"is_config": None}, description="The type of LED to be deactivated", alias="led-type"
    )
    led_entity: str | None = Field(
        json_schema_extra={"is_config": None},
        description="The LED test entity. Shelf means disable all LED on the shelf.\nCard or subcard will disable the specific card or subcard module only.\nWithout any input will be shelf\n\nCondition (when): ../led-type = 'led-test'",
        default=None,
        alias="led-entity",
    )


class DisableLedOutput(YangBaseModel):
    """Output: None"""

    status: StatusEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Successful, Failed or In-progress",
        default=StatusEnum.SUCCESSFUL,
    )
    status_message: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Gives a more detailed status.",
        min_length=0,
        max_length=256,
        default=None,
        alias="status-message",
    )


class DisableLed(BaseModel):
    """RPC: disable-led"""

    input: DisableLedInput
    output: DisableLedOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class OtdrFiletypeEnum(str, Enum):
    """Enumeration for OtdrFiletypeEnum

    Values:
      * CSV: CSV Readable file format
    """

    CSV = "CSV"


class StartOtdrMeasurementInput(YangBaseModel):
    """Input: None"""

    target_entity: str = Field(
        json_schema_extra={"is_config": None},
        description="Indicates the OTDR port that will start the measurement.",
        alias="target-entity",
    )
    otdr_filetype: OtdrFiletypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Result filetype for otdr testing result",
        default=OtdrFiletypeEnum.CSV,
        alias="otdr-filetype",
    )


class StartOtdrMeasurementOutput(YangBaseModel):
    """Output: None"""

    status: StatusEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Successful, Failed or In-progress",
        default=StatusEnum.SUCCESSFUL,
    )
    status_message: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Gives a more detailed status.",
        min_length=0,
        max_length=256,
        default=None,
        alias="status-message",
    )


class StartOtdrMeasurement(BaseModel):
    """RPC: start-otdr-measurement"""

    input: StartOtdrMeasurementInput
    output: StartOtdrMeasurementOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class StopOtdrMeasurementInput(YangBaseModel):
    """Input: None"""

    target_entity: str = Field(
        json_schema_extra={"is_config": None},
        description="Indicates the OTDR port that will have its measurement cancelled",
        alias="target-entity",
    )


class StopOtdrMeasurementOutput(YangBaseModel):
    """Output: None"""

    status: StatusEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Successful, Failed or In-progress",
        default=StatusEnum.SUCCESSFUL,
    )
    status_message: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Gives a more detailed status.",
        min_length=0,
        max_length=256,
        default=None,
        alias="status-message",
    )


class StopOtdrMeasurement(BaseModel):
    """RPC: stop-otdr-measurement"""

    input: StopOtdrMeasurementInput
    output: StopOtdrMeasurementOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class Activate3rdpartyFwInput(YangBaseModel):
    """Input: None"""

    target_entity: str = Field(
        json_schema_extra={"is_config": None},
        description="Indicates the pluggable that need upgrdate firmware.",
        alias="target-entity",
    )
    fw_image_name: str = Field(
        json_schema_extra={"is_config": None},
        description="FW file name",
        min_length=0,
        max_length=255,
        alias="fw-image-name",
    )


class Activate3rdpartyFwOutput(YangBaseModel):
    """Output: None"""

    download_result: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Result of the upgrade operation",
        default=None,
        alias="download-result",
    )


class Activate3rdpartyFw(BaseModel):
    """RPC: activate-3rdparty-fw"""

    input: Activate3rdpartyFwInput
    output: Activate3rdpartyFwOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class FiletypeEnum_2(str, Enum):
    """Enumeration for FiletypeEnum

    Values:
      * database: Database
      * swimage: Software Image
    """

    DATABASE = "database"
    SWIMAGE = "swimage"


class DbActionEnum(str, Enum):
    """Enumeration for DbActionEnum

    Values:
      * swap-db: Activate software image with swapping to the database of new software image instead of migrating the current database.
      * upgrade-db: Activate software image with upgrading the current database.
      * auto: Activate software image by processing database with system default behavior.
    """

    SWAP_DB = "swap-db"
    UPGRADE_DB = "upgrade-db"
    AUTO = "auto"


class ActivateFileInput(YangBaseModel):
    """Input: None"""

    filetype: FiletypeEnum_2 = Field(
        json_schema_extra={"is_config": None}, description="Predefined filetype available for upload"
    )
    restart_type: RestartTypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Restart type for the activation operation, cold reboot\nwill be needed if the target database has removed object comparing to the current one.\n\nCondition (when): ../filetype = 'database'",
        default=RestartTypeEnum.COLD,
        alias="restart-type",
    )
    db_action: DbActionEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Specify the expected database operation during activating software image.\n\nCondition (when): ../filetype = 'swimage'",
        default=DbActionEnum.AUTO,
        alias="db-action",
    )


class ActivateFileOutput(YangBaseModel):
    """Output: None"""

    status: StatusEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Successful, Failed or In-progress",
        default=StatusEnum.SUCCESSFUL,
    )
    status_message: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Gives a more detailed status.",
        min_length=0,
        max_length=256,
        default=None,
        alias="status-message",
    )


class ActivateFile(BaseModel):
    """RPC: activate-file"""

    input: ActivateFileInput
    output: ActivateFileOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class FiletypeEnum_3(str, Enum):
    """Enumeration for FiletypeEnum

    Values:
      * configuration: Configuration Log
      * alarm: Alarm Log
      * event: Event Log
    """

    CONFIGURATION = "configuration"
    ALARM = "alarm"
    EVENT = "event"


class ClearLogInput(YangBaseModel):
    """Input: None"""

    filetype: FiletypeEnum_3 = Field(
        json_schema_extra={"is_config": None}, description="Predefined filetype that supports clearing"
    )


class ClearLogOutput(YangBaseModel):
    """Output: None"""

    status: StatusEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Successful, Failed or In-progress",
        default=StatusEnum.SUCCESSFUL,
    )
    status_message: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Gives a more detailed status.",
        min_length=0,
        max_length=256,
        default=None,
        alias="status-message",
    )


class ClearLog(BaseModel):
    """RPC: clear-log"""

    input: ClearLogInput
    output: ClearLogOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class ClearTypeEnum(str, Enum):
    """Enumeration for ClearTypeEnum

    Values:
      * keep-networking: Keeps IP addresses for simplified recommissioning
      * full: Full wipe of DB contents; reset to factory defaults
      * factory-default: Reset to factory defaults include DB and file system; delete logs, PM and system configurations
      * ssp-zeroization: The SSPs and configurations other than IP addresses will be cleared.Please note that the configuration can never be restored from backup DB any longer.
    """

    KEEP_NETWORKING = "keep-networking"
    FULL = "full"
    FACTORY_DEFAULT = "factory-default"
    SSP_ZEROIZATION = "ssp-zeroization"


class ClearDatabaseInput(YangBaseModel):
    """Input: None"""

    clear_type: ClearTypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Defines the type of 'clear database' that the system must do.",
        default=ClearTypeEnum.KEEP_NETWORKING,
        alias="clear-type",
    )


class ClearDatabaseOutput(YangBaseModel):
    """Output: None"""

    status: StatusEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Successful, Failed or In-progress",
        default=StatusEnum.SUCCESSFUL,
    )
    status_message: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Gives a more detailed status.",
        min_length=0,
        max_length=256,
        default=None,
        alias="status-message",
    )


class ClearDatabase(BaseModel):
    """RPC: clear-database"""

    input: ClearDatabaseInput
    output: ClearDatabaseOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class PingInput(YangBaseModel):
    """Input: None"""

    ping_count: int | None = Field(
        json_schema_extra={"is_config": None},
        description="Stops after sending 'count' ECHO_REQUEST packets.",
        ge=1,
        le=10,
        default=4,
        alias="ping-count",
    )
    ping_timeout: int | None = Field(
        json_schema_extra={"is_config": None},
        description="Specify the timeout, in seconds, before ping exits.",
        ge=1,
        le=20,
        default=10,
        alias="ping-timeout",
    )
    ping_pktsize: int | None = Field(
        json_schema_extra={"is_config": None},
        description="Specifies the number of bytes to be sent. Default is 56, plus 8 bytes of ICMP header for a total packet size of 64 bytes.",
        ge=0,
        default=56,
        alias="ping-pktsize",
    )
    ping_ifname: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Specifies the source interface name.",
        min_length=1,
        max_length=64,
        default=None,
        alias="ping-ifname",
    )
    ping_dest: str = Field(
        json_schema_extra={"is_config": None}, description="IP address of the destination node.", alias="ping-dest"
    )


class PingOutput(YangBaseModel):
    """Output: None"""

    result: str | None = Field(json_schema_extra={"is_config": None}, description="Result of ping.", default=None)


class Ping(BaseModel):
    """RPC: ping"""

    input: PingInput
    output: PingOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class TracerouteInput(YangBaseModel):
    """Input: None"""

    tr_hopcnt: int | None = Field(
        json_schema_extra={"is_config": None},
        description="Specifies the maximum number of hops (max time-to-live value) traceroute will probe. The default is 10.",
        ge=1,
        le=30,
        default=10,
        alias="tr-hopcnt",
    )
    tr_timeout: int | None = Field(
        json_schema_extra={"is_config": None},
        description="Specify the timeout, in seconds, before trace route exits.",
        ge=1,
        le=10,
        default=1,
        alias="tr-timeout",
    )
    tr_ifname: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Specifies the source interface name.",
        min_length=1,
        max_length=64,
        default=None,
        alias="tr-ifname",
    )
    tr_dest: str = Field(
        json_schema_extra={"is_config": None}, description="IPv4 address of the destination node.", alias="tr-dest"
    )
    tr_pktsize: int | None = Field(
        json_schema_extra={"is_config": None},
        description="Specifies the total  size  of  the  probing packet (default 60 bytes for IPv4).",
        ge=0,
        default=60,
        alias="tr-pktsize",
    )


class TracerouteOutput(YangBaseModel):
    """Output: None"""

    result: str | None = Field(
        json_schema_extra={"is_config": None}, description="Result of trace route.", default=None
    )


class Traceroute(BaseModel):
    """RPC: traceroute"""

    input: TracerouteInput
    output: TracerouteOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class CommandEnum(str, Enum):
    """Enumeration for CommandEnum

    Values:
      * update
      * cancel
    """

    UPDATE = "update"
    CANCEL = "cancel"


class UpdatePskMapInput(YangBaseModel):
    """Input: None"""

    psk_map: str = Field(json_schema_extra={"is_config": None}, description="psk-map to be updated.", alias="psk-map")
    command: CommandEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="specifies whether the system security is operating in compliance with FIPS.",
        default=CommandEnum.UPDATE,
    )
    candidate_key: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([0-9a-fA-F]{2}(:[0-9a-fA-F]{2})*)?)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="The candidate key to be activated.\n\nCondition (when): ../command = 'update'",
        default=None,
        alias="candidate-key",
    )
    psk_info: str | None = Field(
        json_schema_extra={"is_config": None},
        description="The label of the psk-map.",
        min_length=0,
        max_length=255,
        default=None,
        alias="psk-info",
    )
    warning_timer: int | None = Field(
        json_schema_extra={"is_config": None},
        description="Warning Time before psk-map updating completes.",
        ge=1,
        le=240,
        default=None,
        alias="warning-timer",
    )
    critical_timer: int | None = Field(
        json_schema_extra={"is_config": None},
        description="Critical time before psk-map updating completes.",
        ge=1,
        le=480,
        default=None,
        alias="critical-timer",
    )
    traffic_off_timer: int | None = Field(
        json_schema_extra={"is_config": None},
        description="Traffic off time before psk-map updating completes.",
        ge=1,
        le=1440,
        default=None,
        alias="traffic-off-timer",
    )


class UpdatePskMapOutput(YangBaseModel):
    """Output: None"""

    status: StatusEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Successful, Failed or In-progress",
        default=StatusEnum.SUCCESSFUL,
    )
    status_message: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Gives a more detailed status.",
        min_length=0,
        max_length=256,
        default=None,
        alias="status-message",
    )


class UpdatePskMap(BaseModel):
    """RPC: update-psk-map"""

    input: UpdatePskMapInput
    output: UpdatePskMapOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class PmBinTypeEnum(str, Enum):
    """Enumeration for PmBinTypeEnum

    Values:
      * current
      * history
      * all
    """

    CURRENT = "current"
    HISTORY = "history"
    ALL = "all"


class PmpTypeEnum(str, Enum):
    """Enumeration for PmpTypeEnum

    Values:
      * not-applicable: not applicable
      * odu-nend-egress: PM point of ODU at near end and egress
      * odu-nend-ingress: PM point of ODU at near end and ingress
      * otu-nend-ingress: PM point of OTU at near end and ingress
      * delay-measurement-odu: delay measurement PM point of ODU
      * coherent-optical-interface: PM point of coherent optical interface
      * optical-power: PM point of optical power
      * loss: PM point of LOS seconds
      * ethernet-nend-ingress: PM point of Ethernet at near end and ingress
      * ethernet-nend-egress: PM point of Ethernet at near end and egress
      * fec: PM point of FEC
      * fc-nend-ingress: PM point of FC at near end and ingress
      * sonet-s-nend-ingress: PM point of OCn at near end and ingress
      * sdh-rs-nend-ingress: PM point of STMn at near end and egress
      * sonet-s-nend-egress: PM point of OCn at near end and ingress
      * sdh-rs-nend-egress: PM point of STMn at near end and egress
      * shelf-temperature: PM point of shelf temperature
      * equipment-temperature: PM point of equipment temperature
      * optical-power-lane: PM point of optical power with multiple lanes
      * protection-switch: PM point of protection switch
      * loss-txrx: PM point of LOS seconds - Rx and Tx
      * optical-power-ingress: PM point of received optical power
      * optical-power-egress: PM point of transmitted optical power
      * odu-encryption: PM point of ODU encryption
      * pilot-tone: PM point of pilot tone
      * loss-tx: PM point of LOS seconds - TX only
      * return-loss: PM point of optical return loss
      * pcs-nend-ingress: PM point of Ethernet PSC layer at near end and ingress
      * mac-nend-ingress: IEEE PM point of Ethernet MAC layer at near end and ingress
      * mac-nend-egress: IEEE PM point of Ethernet MAC layer at near end and egress
      * ethernet-error-ingress: IEEE PM point of Ethernet MAC layer ERROR at near end and ingress
      * ethernet-error-egress: IEEE PM point of Ethernet MAC layer ERROR at near end and egress
      * rtd-osc: PM point of Round Trip Delay Measurement over OSC
      * oc3-osc: PM point of OC3 OSC digital pm
      * all: ALL
    """

    NOT_APPLICABLE = "not-applicable"
    ODU_NEND_EGRESS = "odu-nend-egress"
    ODU_NEND_INGRESS = "odu-nend-ingress"
    OTU_NEND_INGRESS = "otu-nend-ingress"
    DELAY_MEASUREMENT_ODU = "delay-measurement-odu"
    COHERENT_OPTICAL_INTERFACE = "coherent-optical-interface"
    OPTICAL_POWER = "optical-power"
    LOSS = "loss"
    ETHERNET_NEND_INGRESS = "ethernet-nend-ingress"
    ETHERNET_NEND_EGRESS = "ethernet-nend-egress"
    FEC = "fec"
    FC_NEND_INGRESS = "fc-nend-ingress"
    SONET_S_NEND_INGRESS = "sonet-s-nend-ingress"
    SDH_RS_NEND_INGRESS = "sdh-rs-nend-ingress"
    SONET_S_NEND_EGRESS = "sonet-s-nend-egress"
    SDH_RS_NEND_EGRESS = "sdh-rs-nend-egress"
    SHELF_TEMPERATURE = "shelf-temperature"
    EQUIPMENT_TEMPERATURE = "equipment-temperature"
    OPTICAL_POWER_LANE = "optical-power-lane"
    PROTECTION_SWITCH = "protection-switch"
    LOSS_TXRX = "loss-txrx"
    OPTICAL_POWER_INGRESS = "optical-power-ingress"
    OPTICAL_POWER_EGRESS = "optical-power-egress"
    ODU_ENCRYPTION = "odu-encryption"
    PILOT_TONE = "pilot-tone"
    LOSS_TX = "loss-tx"
    RETURN_LOSS = "return-loss"
    PCS_NEND_INGRESS = "pcs-nend-ingress"
    MAC_NEND_INGRESS = "mac-nend-ingress"
    MAC_NEND_EGRESS = "mac-nend-egress"
    ETHERNET_ERROR_INGRESS = "ethernet-error-ingress"
    ETHERNET_ERROR_EGRESS = "ethernet-error-egress"
    RTD_OSC = "rtd-osc"
    OC3_OSC = "oc3-osc"
    ALL = "all"


class PmParameterEnum(str, Enum):
    """Enumeration for PmParameterEnum

    Values:
      * all: all pm-parameters
      * EB: Errored Block
      * ES: Errored Seconds
      * SES: Severely Errored Seconds
      * UAS: Unavailable Seconds
      * DELAY: Value of Delay Measurement time on ODU
      * DELAY-max: Max value of Delay Measurement time on ODU
      * DELAY-min: Min value of Delay Measurement time on ODU
      * DGD: Value of Differential Group Delay
      * DGD-max: Maximum of Differential Group Delay
      * DGD-min: Minimum of Differential Group Delay
      * CD: Value of Chromatic Dispersion
      * CD-max: Maximum of Chromatic Dispersion
      * CD-min: Minimum of Chromatic Dispersion
      * OSNR:  Current value of OSNR, The result could be OSNR value in dB
      * OSNR-max: Maximum of OSNR. The result could be OSNR value in dB
      * OSNR-min: Minimum of OSNR. The result could be OSNR value in dB
      * Q-factor: Current value of Q-factor
      * Q-factor-max: Maximum of Q-factor
      * Q-factor-min: Minimum of Q-factor
      * OPR: Current Value of OPR    Optical Power Received
      * OPR-max: Maximum of OPR Optical Power Received
      * OPR-min: Minimum of OPR Optical Power Receive
      * LOSS: Loss of Signal Seconds
      * SE: SymbolErrors
      * DropEvents: DropEvents
      * Octets: Octets
      * Pkts: Pkts
      * BroadcastPkts: BroadcastPkts
      * MulticastPkts: MulticastPkts
      * CRCAlignErrors: CRCAlignErrors
      * UndersizePkts: UndersizePkts
      * OversizePkts: OversizePkts
      * Fragments: Fragmentsments
      * Jabbers: Jabbers
      * Pkts64Octets: Pkts64Octets
      * Pkts65to127Octets: Pkts65to127Octets
      * Pkts128to255Octets: Pkts128to255Octets
      * Pkts256to511Octets: Pkts256to511Octets
      * Pkts512to1023Octets: Pkts512to1023Octets
      * Pkts1024to1518Octets: Pkts1024to1518Octets
      * Utilization: Utilization
      * Utilization-max: Maximum of Utilization
      * Utilization-min: Minimum of Utilization
      * BE-FEC: Bit Error Forward Error Correction
      * UBE-FEC: Uncorrected Block Error Forward Error Correction
      * BER-FEC: Bit Error Rate before Forward Error Correction
      * BER-FEC-max: Maximum of Bit Error Rate before Forward Error Correction
      * BER-FEC-min: Minimum of Bit Error Rate before Forward Error Correction
      * OPT: Current Value of OPT    Optical Power Transmitted
      * OPT-max: Maximum of OPT Optical Power Transmitted
      * OPT-min: Minimum of OPT Optical Power Transmitted
      * PDL: Current value of Polarization Dependent Loss
      * PDL-max: Maximum of Polarization Dependent Loss
      * PDL-min: Minimum of Polarization Dependent Loss
      * OFT: Current Value of OFT Optical Frequency Transmitted
      * OFT-max: Maximum of OFT Optical Frequency Transmitted
      * OFT-min: Minimum of OFT Optical Frequency Transmitted
      * OFR: Current Value of OFR Optical Frequency Received
      * OFR-max: Maximum of OFR Optical Frequency Received
      * OFR-min: Minimum of OFR Optical Frequency Received
      * BBE: Background Block Error
      * OFS: Out of Frame Seconds
      * CV: Coding Violation
      * SEFS: Severely Errored Frame Second
      * OPR-lane-high: Current Value of the highest lane Optical Power received for multiple lanes
      * OPR-lane-high-max: Maximum of the highest lane Optical Power received for multiple lanes
      * OPR-lane-high-min: Minimum of the highest lane Optical Power received for multiple lanes
      * OPR-lane-low: Current Value of the lowest lane Optical Power received for multiple lanes
      * OPR-lane-low-max: Maximum of the lowest lane Optical Power received for multiple lanes
      * OPR-lane-low-min: Minimum of the lowest lane Optical Power received for multiple lanes
      * OPR-total: Current Value of total Optical Power received for multiple lanes
      * OPR-total-max: Maximum of total Optical Power received for multiple lanes
      * OPR-total-min: Minimum of total Optical Power received for multiple lanes
      * OPT-lane-high: Current Value of the highest lane Optical Power transmitted for multiple lanes
      * OPT-lane-high-max: Maximum of the highest lane Optical Power transmitted for multiple lanes
      * OPT-lane-high-min: Minimum of the highest lane Optical Power transmitted for multiple lanes
      * OPT-lane-low: Current Value of the lowest lane Optical Power transmitted for multiple lanes
      * OPT-lane-low-max: Maximum of the lowest lane Optical Power transmitted for multiple lanes
      * OPT-lane-low-min: Minimum of the lowest lane Optical Power transmitted for multiple lanes
      * OPT-total: Current Value of total Optical Power transmitted for multiple lanes
      * OPT-total-max: Maximum of total Optical Power transmitted for multiple lanes
      * OPT-total-min: Minimum of total Optical Power transmitted for multiple lanes
      * Tmodule: The module temperature
      * Tinlet: The inlet temperature
      * Toutlet: The outlet temperature
      * Tmodule-max: Maximum of the module temperature
      * Tmodule-min: Minimum of the module temperature
      * Tinlet-max: Maximum of the inlet temperature
      * Tinlet-min: Minimum of the inlet temperature
      * Toutlet-max: Maximum of the outlet temperature
      * Toutlet-min: Minimum of the outlet temperature
      * BER-POST-FEC: Bit Error Rate Post Forward Error Correction
      * BER-POST-FEC-max: Maximum of Bit Error Rate Post Forward Error Correction
      * BER-POST-FEC-min: Minimum of Bit Error Rate Post Forward Error Correction
      * PSD: Protection Switch Duration
      * PSC: Protection Switch Count
      * LOSS-Tx: Loss of Signal Seconds of Transmit side
      * LOSS-Rx: Loss of Signal Seconds of Receive side
      * Encryption-fail-rx: Encryption frame fail.
      * PTFS: Pilot Tone Failed Seconds
      * ORL: Optical return loss
      * ORL-max: Maximum of Optical return loss
      * ORL-min: Minimum of Optical return loss
      * ORL-avg: Average of Optical return loss
      * DELAY-avg: Average value of Delay Measurement time on ODU
      * DGD-avg: Average of Differential Group Delay
      * CD-avg: Average of Chromatic Dispersion
      * OSNR-avg: Average of OSNR. The result could be OSNR value in dB
      * Q-factor-avg: Average of Q-factor
      * OPR-avg: Average of OPR Optical Power Receive
      * OPT-avg: Average of OPT Optical Power Transmitted
      * BER-FEC-avg: Average of Bit Error Rate before Forward Error Correction
      * BER-POST-FEC-avg: Average of Bit Error Rate Post Forward Error Correction
      * PDL-avg: Average of Polarization Dependent Loss
      * OFT-avg: Average of OFT Optical Frequency Transmitted
      * OFR-avg: Average of OFR Optical Frequency Received
      * OPR-lane-high-avg: Average of the highest lane Optical Power received for multiple lanes
      * OPR-lane-low-avg: Average of the lowest lane Optical Power received for multiple lanes
      * OPR-total-avg: Average of total Optical Power received for multiple lanes
      * OPT-lane-high-avg: Average of the highest lane Optical Power transmitted for multiple lanes
      * OPT-lane-low-avg: Average of the lowest lane Optical Power transmitted for multiple lanes
      * OPT-total-avg: Average of total Optical Power transmitted for multiple lanes
      * Tmodule-avg: Average of the module temperature
      * Tinlet-avg: Average of the inlet temperature
      * Toutlet-avg: Average of the outlet temperature
      * Utilization-avg: Average of Utilization
      * DELAY-frame: Value of Delay Measurement frame on ODU
      * DELAY-frame-max: Max value of Delay Measurement frame on ODU
      * DELAY-frame-min: Min value of Delay Measurement frame on ODU
      * DELAY-frame-avg: Average value of Delay Measurement frame on ODU
      * CBE-FEC: Corrected Block Error Forward Error Correction
      * FEB: Farend Error Block counter, Backward Error Indicator
      * IAE: Incoming Alignment Error seconds
      * BIAE: Backward Incoming Alignment Error seconds
      * BE: BIP error
      * PktsERR: Errored Packets
      * BBER: Background Block Error Rate
      * BBER-max: Max value of Background Block Error Rate
      * BBER-min: Min value of Background Block Error Rate
      * BBER-avg: AVG value of Background Block Error Rate
      * SESR: Severely Errored Seconds Rate
      * SESR-max: Max value of Severely Errored Seconds Rate
      * SESR-min: Min value of Severely Errored Seconds Rate
      * SESR-avg: Avg value of Severely Errored Seconds Rate
      * SOP: SOP Change Rate
      * SOP_max: Max value of SOP Change Rate
      * SOP_min: Min value of SOP Change Rate
      * SOP_avg: Avg value of SOP Change Rate
      * DM-Distance: Delay Measurement Distance
      * DM-Distance-max: Max value of RTD Delay Measurement Distance
      * DM-Distance-min: Min value of RTD Delay Measurement Distance
      * DM-Distance-avg: Avg value of RTD Delay Measurement Distance
      * RTD: Round Trip Delay
      * RTD-max: Max value of Round Trip Delay
      * RTD-min: Min value of Round Trip Delay
      * RTD-avg: Avg value of Round Trip Delay
      * RTD-Baseline: Round Trip Delay Baseline
      * RTD-Baseline-max: Max value of Round Trip Delay Baseline
      * RTD-Baseline-min: Min value of Round Trip Delay Baseline
      * RTD-Baseline-avg: Avg value of Round Trip Delay Baseline
    """

    ALL = "all"
    EB = "EB"
    ES = "ES"
    SES = "SES"
    UAS = "UAS"
    DELAY = "DELAY"
    DELAY_MAX = "DELAY-max"
    DELAY_MIN = "DELAY-min"
    DGD = "DGD"
    DGD_MAX = "DGD-max"
    DGD_MIN = "DGD-min"
    CD = "CD"
    CD_MAX = "CD-max"
    CD_MIN = "CD-min"
    OSNR = "OSNR"
    OSNR_MAX = "OSNR-max"
    OSNR_MIN = "OSNR-min"
    Q_FACTOR = "Q-factor"
    Q_FACTOR_MAX = "Q-factor-max"
    Q_FACTOR_MIN = "Q-factor-min"
    OPR = "OPR"
    OPR_MAX = "OPR-max"
    OPR_MIN = "OPR-min"
    LOSS = "LOSS"
    SE = "SE"
    DROPEVENTS = "DropEvents"
    OCTETS = "Octets"
    PKTS = "Pkts"
    BROADCASTPKTS = "BroadcastPkts"
    MULTICASTPKTS = "MulticastPkts"
    CRCALIGNERRORS = "CRCAlignErrors"
    UNDERSIZEPKTS = "UndersizePkts"
    OVERSIZEPKTS = "OversizePkts"
    FRAGMENTS = "Fragments"
    JABBERS = "Jabbers"
    PKTS64OCTETS = "Pkts64Octets"
    PKTS65TO127OCTETS = "Pkts65to127Octets"
    PKTS128TO255OCTETS = "Pkts128to255Octets"
    PKTS256TO511OCTETS = "Pkts256to511Octets"
    PKTS512TO1023OCTETS = "Pkts512to1023Octets"
    PKTS1024TO1518OCTETS = "Pkts1024to1518Octets"
    UTILIZATION = "Utilization"
    UTILIZATION_MAX = "Utilization-max"
    UTILIZATION_MIN = "Utilization-min"
    BE_FEC = "BE-FEC"
    UBE_FEC = "UBE-FEC"
    BER_FEC = "BER-FEC"
    BER_FEC_MAX = "BER-FEC-max"
    BER_FEC_MIN = "BER-FEC-min"
    OPT = "OPT"
    OPT_MAX = "OPT-max"
    OPT_MIN = "OPT-min"
    PDL = "PDL"
    PDL_MAX = "PDL-max"
    PDL_MIN = "PDL-min"
    OFT = "OFT"
    OFT_MAX = "OFT-max"
    OFT_MIN = "OFT-min"
    OFR = "OFR"
    OFR_MAX = "OFR-max"
    OFR_MIN = "OFR-min"
    BBE = "BBE"
    OFS = "OFS"
    CV = "CV"
    SEFS = "SEFS"
    OPR_LANE_HIGH = "OPR-lane-high"
    OPR_LANE_HIGH_MAX = "OPR-lane-high-max"
    OPR_LANE_HIGH_MIN = "OPR-lane-high-min"
    OPR_LANE_LOW = "OPR-lane-low"
    OPR_LANE_LOW_MAX = "OPR-lane-low-max"
    OPR_LANE_LOW_MIN = "OPR-lane-low-min"
    OPR_TOTAL = "OPR-total"
    OPR_TOTAL_MAX = "OPR-total-max"
    OPR_TOTAL_MIN = "OPR-total-min"
    OPT_LANE_HIGH = "OPT-lane-high"
    OPT_LANE_HIGH_MAX = "OPT-lane-high-max"
    OPT_LANE_HIGH_MIN = "OPT-lane-high-min"
    OPT_LANE_LOW = "OPT-lane-low"
    OPT_LANE_LOW_MAX = "OPT-lane-low-max"
    OPT_LANE_LOW_MIN = "OPT-lane-low-min"
    OPT_TOTAL = "OPT-total"
    OPT_TOTAL_MAX = "OPT-total-max"
    OPT_TOTAL_MIN = "OPT-total-min"
    TMODULE = "Tmodule"
    TINLET = "Tinlet"
    TOUTLET = "Toutlet"
    TMODULE_MAX = "Tmodule-max"
    TMODULE_MIN = "Tmodule-min"
    TINLET_MAX = "Tinlet-max"
    TINLET_MIN = "Tinlet-min"
    TOUTLET_MAX = "Toutlet-max"
    TOUTLET_MIN = "Toutlet-min"
    BER_POST_FEC = "BER-POST-FEC"
    BER_POST_FEC_MAX = "BER-POST-FEC-max"
    BER_POST_FEC_MIN = "BER-POST-FEC-min"
    PSD = "PSD"
    PSC = "PSC"
    LOSS_TX = "LOSS-Tx"
    LOSS_RX = "LOSS-Rx"
    ENCRYPTION_FAIL_RX = "Encryption-fail-rx"
    PTFS = "PTFS"
    ORL = "ORL"
    ORL_MAX = "ORL-max"
    ORL_MIN = "ORL-min"
    ORL_AVG = "ORL-avg"
    DELAY_AVG = "DELAY-avg"
    DGD_AVG = "DGD-avg"
    CD_AVG = "CD-avg"
    OSNR_AVG = "OSNR-avg"
    Q_FACTOR_AVG = "Q-factor-avg"
    OPR_AVG = "OPR-avg"
    OPT_AVG = "OPT-avg"
    BER_FEC_AVG = "BER-FEC-avg"
    BER_POST_FEC_AVG = "BER-POST-FEC-avg"
    PDL_AVG = "PDL-avg"
    OFT_AVG = "OFT-avg"
    OFR_AVG = "OFR-avg"
    OPR_LANE_HIGH_AVG = "OPR-lane-high-avg"
    OPR_LANE_LOW_AVG = "OPR-lane-low-avg"
    OPR_TOTAL_AVG = "OPR-total-avg"
    OPT_LANE_HIGH_AVG = "OPT-lane-high-avg"
    OPT_LANE_LOW_AVG = "OPT-lane-low-avg"
    OPT_TOTAL_AVG = "OPT-total-avg"
    TMODULE_AVG = "Tmodule-avg"
    TINLET_AVG = "Tinlet-avg"
    TOUTLET_AVG = "Toutlet-avg"
    UTILIZATION_AVG = "Utilization-avg"
    DELAY_FRAME = "DELAY-frame"
    DELAY_FRAME_MAX = "DELAY-frame-max"
    DELAY_FRAME_MIN = "DELAY-frame-min"
    DELAY_FRAME_AVG = "DELAY-frame-avg"
    CBE_FEC = "CBE-FEC"
    FEB = "FEB"
    IAE = "IAE"
    BIAE = "BIAE"
    BE = "BE"
    PKTSERR = "PktsERR"
    BBER = "BBER"
    BBER_MAX = "BBER-max"
    BBER_MIN = "BBER-min"
    BBER_AVG = "BBER-avg"
    SESR = "SESR"
    SESR_MAX = "SESR-max"
    SESR_MIN = "SESR-min"
    SESR_AVG = "SESR-avg"
    SOP = "SOP"
    SOP_MAX = "SOP_max"
    SOP_MIN = "SOP_min"
    SOP_AVG = "SOP_avg"
    DM_DISTANCE = "DM-Distance"
    DM_DISTANCE_MAX = "DM-Distance-max"
    DM_DISTANCE_MIN = "DM-Distance-min"
    DM_DISTANCE_AVG = "DM-Distance-avg"
    RTD = "RTD"
    RTD_MAX = "RTD-max"
    RTD_MIN = "RTD-min"
    RTD_AVG = "RTD-avg"
    RTD_BASELINE = "RTD-Baseline"
    RTD_BASELINE_MAX = "RTD-Baseline-max"
    RTD_BASELINE_MIN = "RTD-Baseline-min"
    RTD_BASELINE_AVG = "RTD-Baseline-avg"


class ManagementTimePeriodEnum(str, Enum):
    """Enumeration for ManagementTimePeriodEnum

    Values:
      * not-applicable
      * 15min
      * 24h
      * all
      * 1min
      * 1h
    """

    NOT_APPLICABLE = "not-applicable"
    _15MIN = "15min"
    _24H = "24h"
    ALL = "all"
    _1MIN = "1min"
    _1H = "1h"


class FilterItem(YangBaseModel):
    """Optional filter list, which allows to provide more complex filters.
    Instead of using the parameters in the RPC base input, this list can be
    used instead.
    """

    filter_id: int = Field(
        json_schema_extra={"is_config": None},
        description="An identifier of the filter instance.",
        ge=0,
        alias="filter-id",
    )
    pm_entity: str | None = Field(
        json_schema_extra={"is_config": None},
        description="The management object instance the performance monitoring data are collected for, if not input it means 'all pm entities'",
        default=None,
        alias="pm-entity",
    )
    pmp_type: PmpTypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="The management object type of the performance monitoring.",
        default=None,
        alias="pmp-type",
    )
    pm_parameter: PmParameterEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Performance Monitoring parameter, which could be a counter or gauge parameter, the later support current, max and min values.",
        default=None,
        alias="pm-parameter",
    )


class UnitOfValueEnum(str, Enum):
    """Enumeration for UnitOfValueEnum

    Values:
      * not-applicable
      * dBm
      * Microseconds
      * ps
      * ps/nm
      * dB
      * Seconds
      * Packets
      * Events
      * Octets
      * Bits
      * Bits/s
      * Blocks
      * Times
      * Percentage
      * Bit-ratio
      * MHz
      * Celsius
      * Frames
      * rads/s
      * Kilometers
    """

    NOT_APPLICABLE = "not-applicable"
    DBM = "dBm"
    MICROSECONDS = "Microseconds"
    PS = "ps"
    PS_NM = "ps/nm"
    DB = "dB"
    SECONDS = "Seconds"
    PACKETS = "Packets"
    EVENTS = "Events"
    OCTETS = "Octets"
    BITS = "Bits"
    BITS_S = "Bits/s"
    BLOCKS = "Blocks"
    TIMES = "Times"
    PERCENTAGE = "Percentage"
    BIT_RATIO = "Bit-ratio"
    MHZ = "MHz"
    CELSIUS = "Celsius"
    FRAMES = "Frames"
    RADS_S = "rads/s"
    KILOMETERS = "Kilometers"


class ValidityTypeEnum(str, Enum):
    """Enumeration for ValidityTypeEnum

    Values:
      * complete: PM Data collection are completed in the bin.
      * partial: PM Data collection are partial in the bin.
      * not-available: PM parameter not supported or PM data not available.
    """

    COMPLETE = "complete"
    PARTIAL = "partial"
    NOT_AVAILABLE = "not-available"


class PmDataItem(YangBaseModel):
    """Defines the get-pm output of record performance data"""

    pm_time_period: ManagementTimePeriodEnum = Field(
        json_schema_extra={"is_config": None},
        description="Specifies the time-period increments during which PM data are collected.\nAll means all available pm-time-period'",
        alias="pm-time-period",
    )
    monitoring_date_time: Annotated[
        str,
        AfterValidator(
            lambda v: check_pattern(
                "^(?:(\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))|(all))$", v
            )
        ),
    ] = Field(
        json_schema_extra={"is_config": None}, description="Monitoring data and time'", alias="monitoring-date-time"
    )
    pm_entity: str = Field(
        json_schema_extra={"is_config": None},
        description="The management object instance the performance monitoring data are collected for, if not input it means 'all pm entities'",
        alias="pm-entity",
    )
    pmp_type: PmpTypeEnum = Field(
        json_schema_extra={"is_config": None},
        description="The management object type of the performance monitoring.",
        alias="pmp-type",
    )
    pm_parameter: PmParameterEnum = Field(
        json_schema_extra={"is_config": None},
        description="Performance Monitoring parameter, which could be a counter or gauge parameter, the later support current, max and min values.",
        alias="pm-parameter",
    )
    number_of_bin: int | None = Field(
        json_schema_extra={"is_config": None},
        description="Indicates the sequence number of the bin, numbering sequentially from the latest history bin(bin 0).",
        ge=0,
        default=None,
        alias="number-of-bin",
    )
    pm_value: str | None = Field(
        json_schema_extra={"is_config": None},
        description="PM counter or gauge value of the PM parameter.",
        min_length=1,
        max_length=32,
        default=None,
        alias="pm-value",
    )
    pm_unit: UnitOfValueEnum | None = Field(
        json_schema_extra={"is_config": None}, description="Unit of PM value.", default=None, alias="pm-unit"
    )
    validity: ValidityTypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Indicates whether or not a performance monitoring value is valid.",
        default=None,
    )


class GetPmInput(YangBaseModel):
    """Input: None"""

    pm_bin_type: PmBinTypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Indicates the type of the performance monitoring data bin.",
        default=PmBinTypeEnum.CURRENT,
        alias="pm-bin-type",
    )
    pm_entity: str | None = Field(
        json_schema_extra={"is_config": None},
        description="The management object instance the performance monitoring data are collected for, if not input it means 'all pm entities'",
        default=None,
        alias="pm-entity",
    )
    pmp_type: PmpTypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="The management object type of the performance monitoring.",
        default=PmpTypeEnum.ALL,
        alias="pmp-type",
    )
    pm_parameter: PmParameterEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Performance Monitoring parameter, which could be a counter or gauge parameter, the later support current, max and min values.",
        default=PmParameterEnum.ALL,
        alias="pm-parameter",
    )
    pm_time_period: ManagementTimePeriodEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Specifies the time-period increments during which PM data are collected.\nAll means all available pm-time-period'",
        default=ManagementTimePeriodEnum.ALL,
        alias="pm-time-period",
    )
    monitoring_date_time: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:(\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))|(all))$", v
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="Monitoring data and time'",
        default="all",
        alias="monitoring-date-time",
    )
    number_of_records: int | None = Field(
        json_schema_extra={"is_config": None},
        description="Restrict the number of pm data records that will be\nretrieved. Only applicable for 'history' retrieval.\n\nCondition (when): ../pm-bin-type = 'history'",
        ge=0,
        default=None,
        alias="number-of-records",
    )
    start_monitoring_date_time: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:(\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))|(all))$", v
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="Start Monitoring data and time'\n\nCondition (when): ../pm-bin-type = 'history'",
        default=None,
        alias="start-monitoring-date-time",
    )
    end_monitoring_date_time: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:(\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))|(all))$", v
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="End Monitoring data and time'\n\nCondition (when): ../pm-bin-type = 'history'",
        default=None,
        alias="end-monitoring-date-time",
    )
    start_number_of_bin: int | None = Field(
        json_schema_extra={"is_config": None},
        description="Restrict the start number of pm data bin that will be\nretrieved. Only applicable for 'history' retrieval.\n\nCondition (when): ../pm-bin-type = 'history'",
        ge=0,
        default=None,
        alias="start-number-of-bin",
    )
    end_number_of_bin: int | None = Field(
        json_schema_extra={"is_config": None},
        description="Restrict the end number of pm data bin that will be\nretrieved. Only applicable for 'history' retrieval.\n\nCondition (when): ../pm-bin-type = 'history'",
        ge=0,
        default=None,
        alias="end-number-of-bin",
    )
    filter: RestconfList[FilterItem] | None = Field(
        json_schema_extra={"is_config": None},
        description="Optional filter list, which allows to provide more complex filters.\nInstead of using the parameters in the RPC base input, this list can be\nused instead.",
        default=None,
    )


class GetPmOutput(YangBaseModel):
    """Output: None"""

    pm_data: RestconfList[PmDataItem] | None = Field(
        json_schema_extra={"is_config": None},
        description="Defines the get-pm output of record performance data",
        default=None,
        alias="pm-data",
    )


class GetPm(BaseModel):
    """RPC: get-pm"""

    input: GetPmInput
    output: GetPmOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class PmEntityListItem(YangBaseModel):
    """The list for the rpc with multi pm entitiy request. It could be empty"""

    pm_entity: str = Field(
        json_schema_extra={"is_config": None},
        description="The management object instance the performance monitoring data are collected for, if not input it means 'all pm entities'",
        alias="pm-entity",
    )
    pmp_type: PmpTypeEnum = Field(
        json_schema_extra={"is_config": None},
        description="The management object type of the performance monitoring.",
        alias="pmp-type",
    )
    pm_parameter: PmParameterEnum = Field(
        json_schema_extra={"is_config": None},
        description="Performance Monitoring parameter, which could be a counter or gauge parameter, the later support current, max and min values.",
        alias="pm-parameter",
    )


class ClearPmDataInput(YangBaseModel):
    """Input: None"""

    pm_bin_type: PmBinTypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Indicates the type of the performance monitoring data bin.",
        default=PmBinTypeEnum.CURRENT,
        alias="pm-bin-type",
    )
    pm_entity: str | None = Field(
        json_schema_extra={"is_config": None},
        description="The management object instance the performance monitoring data are collected for, if not input it means 'all pm entities'",
        default=None,
        alias="pm-entity",
    )
    pmp_type: PmpTypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="The management object type of the performance monitoring.",
        default=PmpTypeEnum.ALL,
        alias="pmp-type",
    )
    pm_parameter: PmParameterEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Performance Monitoring parameter, which could be a counter or gauge parameter, the later support current, max and min values.",
        default=PmParameterEnum.ALL,
        alias="pm-parameter",
    )
    pm_time_period: ManagementTimePeriodEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Specifies the time-period increments during which PM data are collected.\nAll means all available pm-time-period'",
        default=ManagementTimePeriodEnum.ALL,
        alias="pm-time-period",
    )
    monitoring_date_time: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:(\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))|(all))$", v
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="Monitoring data and time'",
        default="all",
        alias="monitoring-date-time",
    )
    pm_entity_list: RestconfList[PmEntityListItem] | None = Field(
        json_schema_extra={"is_config": None},
        description="The list for the rpc with multi pm entitiy request. It could be empty",
        default=None,
        alias="pm-entity-list",
    )


class ClearPmDataOutput(YangBaseModel):
    """Output: None"""

    status: StatusEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Successful, Failed or In-progress",
        default=StatusEnum.SUCCESSFUL,
    )
    status_message: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Gives a more detailed status.",
        min_length=0,
        max_length=256,
        default=None,
        alias="status-message",
    )


class ClearPmData(BaseModel):
    """RPC: clear-pm-data"""

    input: ClearPmDataInput
    output: ClearPmDataOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class ClearStatisticsDataInput(YangBaseModel):
    """Input: None"""

    statistics_entity: str | None = Field(
        json_schema_extra={"is_config": None},
        description="The management object instance the statistics performance monitoring data are collected for, if not input it means 'all entities'",
        default=None,
        alias="statistics-entity",
    )


class ClearStatisticsDataOutput(YangBaseModel):
    """Output: None"""

    status: StatusEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Successful, Failed or In-progress",
        default=StatusEnum.SUCCESSFUL,
    )
    status_message: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Gives a more detailed status.",
        min_length=0,
        max_length=256,
        default=None,
        alias="status-message",
    )


class ClearStatisticsData(BaseModel):
    """RPC: clear-statistics-data"""

    input: ClearStatisticsDataInput
    output: ClearStatisticsDataOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class ClearCertificateInput(YangBaseModel):
    """Input: None"""

    target: str = Field(json_schema_extra={"is_config": None})


class ClearCertificateOutput(YangBaseModel):
    """Output: None"""

    status: StatusEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Successful, Failed or In-progress",
        default=StatusEnum.SUCCESSFUL,
    )
    status_message: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Gives a more detailed status.",
        min_length=0,
        max_length=256,
        default=None,
        alias="status-message",
    )


class ClearCertificate(BaseModel):
    """RPC: clear-certificate"""

    input: ClearCertificateInput
    output: ClearCertificateOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class ClearTrustedCertificateInput(YangBaseModel):
    """Input: None"""

    target: str = Field(json_schema_extra={"is_config": None})


class ClearTrustedCertificateOutput(YangBaseModel):
    """Output: None"""

    status: StatusEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Successful, Failed or In-progress",
        default=StatusEnum.SUCCESSFUL,
    )
    status_message: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Gives a more detailed status.",
        min_length=0,
        max_length=256,
        default=None,
        alias="status-message",
    )


class ClearTrustedCertificate(BaseModel):
    """RPC: clear-trusted-certificate"""

    input: ClearTrustedCertificateInput
    output: ClearTrustedCertificateOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class KeyLengthEnum(str, Enum):
    """Enumeration for KeyLengthEnum

    Values:
      * 512
      * 1024
      * 2048
      * 3072
      * 256
      * 384
      * 521
    """

    _512 = "512"
    _1024 = "1024"
    _2048 = "2048"
    _3072 = "3072"
    _256 = "256"
    _384 = "384"
    _521 = "521"


class KeyTypeEnum(str, Enum):
    """Enumeration for KeyTypeEnum

    Values:
      * dsa
      * rsa
      * ecdsa
    """

    DSA = "dsa"
    RSA = "rsa"
    ECDSA = "ecdsa"


class SshKeygenInput(YangBaseModel):
    """Input: None"""

    key_length: KeyLengthEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Strength of the key used for regenerating the private-public key pair",
        default=KeyLengthEnum._1024,
        alias="key-length",
    )
    key_type: KeyTypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Type of key to generate",
        default=KeyTypeEnum.DSA,
        alias="key-type",
    )


class SshKeygenOutput(YangBaseModel):
    """Output: None"""

    result: str | None = Field(json_schema_extra={"is_config": None}, description="result of ssh-keygen.", default=None)


class SshKeygen(BaseModel):
    """RPC: ssh-keygen"""

    input: SshKeygenInput
    output: SshKeygenOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class PasswordInput(YangBaseModel):
    """Input: None"""

    new_password: str = Field(
        json_schema_extra={"is_config": None},
        description="user new password",
        min_length=1,
        max_length=128,
        alias="new-password",
    )
    repeat_new_password: str = Field(
        json_schema_extra={"is_config": None},
        description="user new password confirmation",
        min_length=1,
        max_length=128,
        alias="repeat-new-password",
    )
    # Choice: target
    # Case: other-user
    user_name: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[a-zA-Z_.][a-zA-Z0-9_\\-.]*[$]?)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="User name.",
        min_length=1,
        max_length=32,
        default=None,
        alias="user-name",
    )
    # Case: current-user
    old_password: str | None = Field(
        json_schema_extra={"is_config": None},
        description="user old password",
        min_length=1,
        max_length=128,
        default=None,
        alias="old-password",
    )


class PasswordOutput(YangBaseModel):
    """Output: None"""

    status: StatusEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Successful, Failed or In-progress",
        default=StatusEnum.SUCCESSFUL,
    )
    status_message: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Gives a more detailed status.",
        min_length=0,
        max_length=256,
        default=None,
        alias="status-message",
    )


class Password(BaseModel):
    """RPC: password"""

    input: PasswordInput
    output: PasswordOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class ResetTestSignalStatusInput(YangBaseModel):
    """Input: None"""

    entity_id: str = Field(
        json_schema_extra={"is_config": None},
        description="Instance ID of the entity to be addressed",
        alias="entity-id",
    )


class ResetTestSignalStatusOutput(YangBaseModel):
    """Output: None"""

    status: StatusEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Successful, Failed or In-progress",
        default=StatusEnum.SUCCESSFUL,
    )
    status_message: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Gives a more detailed status.",
        min_length=0,
        max_length=256,
        default=None,
        alias="status-message",
    )


class ResetTestSignalStatus(BaseModel):
    """RPC: reset-test-signal-status"""

    input: ResetTestSignalStatusInput
    output: ResetTestSignalStatusOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class PortModeEnum(str, Enum):
    """Enumeration for PortModeEnum

    Values:
      * not-applicable: No service mode
      * 10GBE: IEEE802.3ae 10 gigabits per second LAN Ethernet signal
      * 40GBE: IEEE802.3ae 40 gigabits per second Ethernet signal
      * 100GBE: IEEE802.3ae 100 gigabits per second Ethernet signal
      * subport: The logical port for break down channel signal type
      * QPSK_100G: 100G rate class och-os signal with DP-QPSK modulation format
      * 8QAM_300G: 150G rate class otsi signal with DP-8QAM modulation format
      * 16QAM_200G: 200G rate class och-os signal with DP-16QAM modulation format
      * FC16G: 16 gigabits per second rates Fiber Channel signal
      * FC8G: 8 gigabits per second rates Fiber Channel signal
      * OTU4: ITUT G.709 112 gigabits per second Optical channel Transport Unit
      * OTU2: ITUT G.709 10.70 gigabits per second Optical channel Transport Unit
      * OTU2e: ITUT G.709 11.09 gigabits per second Optical channel Transport Unit
      * OC192: 9.95 gigabits per second SONET signal
      * STM64: 9.95 gigabits per second SDH signal
      * OCHOS_OTU2: 10G rate class och-os signal with NRZ modulation format
      * OCHOS_OTU2e: 11G rate class och-os signal with NRZ modulation format
      * 8QAM_200G: 200G rate class och-os signal with DP-8QAM modulation format
      * 10GWAN_SONET: IEEE802.3ae 10 gigabits per second WAN Ethernet signal with SOENT overhead
      * 10GWAN_SDH: IEEE802.3ae 10 gigabits per second WAN Ethernet signal with SDH overhead
      * 64QAM_600G: 600G rate class och-os signal with DP-64QAM modulation format
      * 400GBE: IEEE802.3ae 400 gigabits per second Ethernet signal
      * SPQPSK_100G: 100G rate class och-os signal with DP-SPQPSK modulation format
      * SPQPSK_QPSK_100G: 100G rate class och-os signal with DP-SPQPSK-QPSK modulation format
      * QPSK_200G: 200G rate class och-os signal with DP-QPSK modulation format
      * SP16QAM_200G: 200G rate class och-os signal with DP-SP16QAM modulation format
      * 32QAM_200G: 200G rate class och-os signal with DP-32QAM modulation format
      * QPSK_SP16QAM_200G: 200G rate class och-os signal with DP-QPSK-SP16QAM modulation format
      * 16QAM_300G: 300G rate class och-os signal with DP-16QAM modulation format
      * SP16QAM_300G: 300G rate class och-os signal with DP-SP16QAM modulation format
      * 32QAM_300G: 300G rate class och-os signal with DP-32QAM modulation format
      * 64QAM_300G: 300G rate class och-os signal with DP-64QAM modulation format
      * SP16QAM_16QAM_300G: 300G rate class och-os signal with DP-SP16QAM-16QAM modulation format
      * 16QAM_400G: 400G rate class och-os signal with DP-16QAM modulation format
      * 32QAM_400G: 400G rate class och-os signal with DP-32QAM modulation format
      * 64QAM_400G: 400G rate class och-os signal with DP-64QAM modulation format
      * 16QAM_32QAM_400G: 400G rate class och-os signal with DP-16QAM-32QAM modulation format
      * 32QAM_500G: 500G rate class och-os signal with DP-32QAM modulation format
      * 64QAM_500G: 500G rate class och-os signal with DP-64QAM modulation format
      * 32QAM_64QAM_500G: 500G rate class och-os signal with DP-32QAM-64QAM modulation format
      * OTU4_TRANSPARENT: ITUT G.709 112 gigabits per second Optical channel Transport Unit with transparent mode
      * QPSK_100G_TRANSPARENT: 100G rate class och-os signal with DP-QPSK modulation format and transparent mode
      * SP16QAM_16QAM_200G: 200G rate class och-os signal with DP-SP16QAM-16QAM modulation format
      * 32QAM_64QAM_600G: 600G rate class och-os signal with DP-32QAM-64QAM modulation format
      * 1GBE: IEEE802.3ae 1 gigabits per second LAN Ethernet signal
      * OC48: 2.5 gigabits per second SONET signal
      * STM16: 2.5 gigabits per second SDH signal
      * SP16QAM_300G_C: couple 2*150G rate class och-os signal with DP-SP16QAM modulation format
      * QPSK_SP16QAM_300G_C: couple 2*150G rate class och-os signal with DP-QPSK-SP16QAM modulation format
      * 16QAM_32QAM_500G_C: couple 2*250G rate class och-os signal with DP-16QAM-32QAM modulation format
      * 16QAM_500G_C: couple 2*250G rate class och-os signal with DP-16QAM modulation format
      * SP16QAM_500G_C: couple 2*250G rate class och-os signal with DP-SP16QAM modulation format
      * QPSK_SP16QAM_500G_C: couple 2*250G rate class och-os signal with DP-QPSK-SP16QAM modulation format
      * 32QAM_64QAM_700G_C: couple 2*350G rate class och-os signal with DP-32QAM-64QAM modulation format
      * 16QAM_700G_C: couple 2*350G rate class och-os signal with DP-16QAM modulation format
      * SP16QAM_16QAM_700G_C: couple 2*350G rate class och-os signal with DP-SP16QAM-16QAM modulation format
      * 32QAM_900G_C: couple 2*450G rate class och-os signal with DP-32QAM modulation format
      * 16QAM_32QAM_900G_C: couple 2*450G rate class och-os signal with DP-16QAM-32QAM modulation format
      * 32QAM_64QAM_1100G_C: couple 2*550G rate class och-os signal with DP-32QAM-64QAM modulation format
      * SPQPSK_QPSK_200G: 200G rate class och-os signal with DP-SPQPSK-QPSK modulation format
      * QPSK_SP16QAM_300G: 300G rate class och-os signal with DP-QPSK-SP16QAM modulation format
      * SP16QAM_16QAM_400G: 400G rate class och-os signal with DP-SP16QAM-16QAM modulation format
      * 16QAM_32QAM_500G: 500G rate class och-os signal with DP-16QAM-32QAM modulation format
      * FC1G: 1 gigabits per second rates Fiber Channel signal
      * FC4G: 4 gigabits per second rates Fiber Channel signal
    """

    NOT_APPLICABLE = "not-applicable"
    _10GBE = "10GBE"
    _40GBE = "40GBE"
    _100GBE = "100GBE"
    SUBPORT = "subport"
    QPSK_100G = "QPSK_100G"
    _8QAM_300G = "8QAM_300G"
    _16QAM_200G = "16QAM_200G"
    FC16G = "FC16G"
    FC8G = "FC8G"
    OTU4 = "OTU4"
    OTU2 = "OTU2"
    OTU2E = "OTU2e"
    OC192 = "OC192"
    STM64 = "STM64"
    OCHOS_OTU2 = "OCHOS_OTU2"
    OCHOS_OTU2E = "OCHOS_OTU2e"
    _8QAM_200G = "8QAM_200G"
    _10GWAN_SONET = "10GWAN_SONET"
    _10GWAN_SDH = "10GWAN_SDH"
    _64QAM_600G = "64QAM_600G"
    _400GBE = "400GBE"
    SPQPSK_100G = "SPQPSK_100G"
    SPQPSK_QPSK_100G = "SPQPSK_QPSK_100G"
    QPSK_200G = "QPSK_200G"
    SP16QAM_200G = "SP16QAM_200G"
    _32QAM_200G = "32QAM_200G"
    QPSK_SP16QAM_200G = "QPSK_SP16QAM_200G"
    _16QAM_300G = "16QAM_300G"
    SP16QAM_300G = "SP16QAM_300G"
    _32QAM_300G = "32QAM_300G"
    _64QAM_300G = "64QAM_300G"
    SP16QAM_16QAM_300G = "SP16QAM_16QAM_300G"
    _16QAM_400G = "16QAM_400G"
    _32QAM_400G = "32QAM_400G"
    _64QAM_400G = "64QAM_400G"
    _16QAM_32QAM_400G = "16QAM_32QAM_400G"
    _32QAM_500G = "32QAM_500G"
    _64QAM_500G = "64QAM_500G"
    _32QAM_64QAM_500G = "32QAM_64QAM_500G"
    OTU4_TRANSPARENT = "OTU4_TRANSPARENT"
    QPSK_100G_TRANSPARENT = "QPSK_100G_TRANSPARENT"
    SP16QAM_16QAM_200G = "SP16QAM_16QAM_200G"
    _32QAM_64QAM_600G = "32QAM_64QAM_600G"
    _1GBE = "1GBE"
    OC48 = "OC48"
    STM16 = "STM16"
    SP16QAM_300G_C = "SP16QAM_300G_C"
    QPSK_SP16QAM_300G_C = "QPSK_SP16QAM_300G_C"
    _16QAM_32QAM_500G_C = "16QAM_32QAM_500G_C"
    _16QAM_500G_C = "16QAM_500G_C"
    SP16QAM_500G_C = "SP16QAM_500G_C"
    QPSK_SP16QAM_500G_C = "QPSK_SP16QAM_500G_C"
    _32QAM_64QAM_700G_C = "32QAM_64QAM_700G_C"
    _16QAM_700G_C = "16QAM_700G_C"
    SP16QAM_16QAM_700G_C = "SP16QAM_16QAM_700G_C"
    _32QAM_900G_C = "32QAM_900G_C"
    _16QAM_32QAM_900G_C = "16QAM_32QAM_900G_C"
    _32QAM_64QAM_1100G_C = "32QAM_64QAM_1100G_C"
    SPQPSK_QPSK_200G = "SPQPSK_QPSK_200G"
    QPSK_SP16QAM_300G = "QPSK_SP16QAM_300G"
    SP16QAM_16QAM_400G = "SP16QAM_16QAM_400G"
    _16QAM_32QAM_500G = "16QAM_32QAM_500G"
    FC1G = "FC1G"
    FC4G = "FC4G"


class CreateCardServicesInput(YangBaseModel):
    """Input: None"""

    card_instance: str = Field(
        json_schema_extra={"is_config": None},
        description="Target card for the command. Must exist.",
        alias="card-instance",
    )
    line_mode: PortModeEnum = Field(
        json_schema_extra={"is_config": None},
        description="Desired port-mode for all line ports in the card.",
        alias="line-mode",
    )
    client_mode: PortModeEnum = Field(
        json_schema_extra={"is_config": None},
        description="Desired port-mode for all client ports (or subports) in the card.",
        alias="client-mode",
    )


class CreateCardServicesOutput(YangBaseModel):
    """Output: None"""

    status: StatusEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Successful, Failed or In-progress",
        default=StatusEnum.SUCCESSFUL,
    )
    status_message: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Gives a more detailed status.",
        min_length=0,
        max_length=256,
        default=None,
        alias="status-message",
    )


class CreateCardServices(BaseModel):
    """RPC: create-card-services"""

    input: CreateCardServicesInput
    output: CreateCardServicesOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class DeleteCardServicesInput(YangBaseModel):
    """Input: None"""

    card_instance: str = Field(
        json_schema_extra={"is_config": None},
        description="Target card for the command. Must exist.",
        alias="card-instance",
    )
    reset_ports: bool | None = Field(
        json_schema_extra={"is_config": None},
        description="Obsolete option (used to be 'reset port' option, now is default behavior).",
        default=False,
        alias="reset-ports",
    )


class DeleteCardServicesOutput(YangBaseModel):
    """Output: None"""

    status: StatusEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Successful, Failed or In-progress",
        default=StatusEnum.SUCCESSFUL,
    )
    status_message: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Gives a more detailed status.",
        min_length=0,
        max_length=256,
        default=None,
        alias="status-message",
    )


class DeleteCardServices(BaseModel):
    """RPC: delete-card-services"""

    input: DeleteCardServicesInput
    output: DeleteCardServicesOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class P2pTypeEnum(str, Enum):
    """Enumeration for P2pTypeEnum

    Values:
      * gcc0
      * oscx
    """

    GCC0 = "gcc0"
    OSCX = "oscx"


class OscxChannelEnum(str, Enum):
    """Enumeration for OscxChannelEnum

    Values:
      * 1
      * 2
    """

    _1 = "1"
    _2 = "2"


class IfconfigInput(YangBaseModel):
    """Input: None"""

    interface_name: str = Field(
        json_schema_extra={"is_config": None}, description="Interface to configure", alias="interface-name"
    )
    # Choice: mode
    # Case: static-ip
    static_ip: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(%[\\d\\w]+)?)$",
                    v,
                )
            ),
        ]
        | None
    ) = Field(json_schema_extra={"is_config": None}, description="New IP", default=None, alias="static-ip")
    prefix_length: int | None = Field(
        json_schema_extra={"is_config": None},
        description="New IP prefix length",
        ge=0,
        le=32,
        default=None,
        alias="prefix-length",
    )
    netmask: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(%[\\d\\w]+)?)$",
                    v,
                )
            ),
        ]
        | None
    ) = Field(json_schema_extra={"is_config": None}, description="IP netmask", default=None)
    gateway_ip: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(%[\\d\\w]+)?)$",
                    v,
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="If a new default route is to be defined, the gateway-ip needs to be provided.",
        default=None,
        alias="gateway-ip",
    )
    # Case: p2p
    p2p_type: P2pTypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Specifies the link type associated with the p2p interface.",
        default=None,
        alias="p2p-type",
    )
    gcc0_resource_id: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Reference of the lower layer resource associated with this interface.\n\nCondition (when): ../p2p-type='gcc0'",
        default=None,
        alias="gcc0-resource-id",
    )
    oscx_resource_id: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Reference of the lower layer resource associated with this interface.\n\nCondition (when): ../p2p-type='oscx'",
        default=None,
        alias="oscx-resource-id",
    )
    parent_interface_name: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Name of the parent interface",
        min_length=1,
        max_length=64,
        default=None,
        alias="parent-interface-name",
    )
    oscx_channel: OscxChannelEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Condition (when): ../p2p-type='oscx'",
        default=OscxChannelEnum._1,
        alias="oscx-channel",
    )
    # Case: static-ip6
    static_ip6: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:((:|[0-9a-fA-F]{0,4}):)([0-9a-fA-F]{0,4}:){0,5}((([0-9a-fA-F]{0,4}:)?(:|[0-9a-fA-F]{0,4}))|(((25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])))(%[\\d\\w]+)?)$",
                    v,
                )
            ),
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:(([^:]+:){6}(([^:]+:[^:]+)|(.*\\..*)))|((([^:]+:)*[^:]+)?::(([^:]+:)*[^:]+)?)(%.+)?)$", v
                )
            ),
        ]
        | None
    ) = Field(json_schema_extra={"is_config": None}, description="New IP", default=None, alias="static-ip6")
    prefix_length6: int | None = Field(
        json_schema_extra={"is_config": None},
        description="New IP prefix length",
        ge=0,
        le=128,
        default=None,
        alias="prefix-length6",
    )
    gateway_ip6: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:((:|[0-9a-fA-F]{0,4}):)([0-9a-fA-F]{0,4}:){0,5}((([0-9a-fA-F]{0,4}:)?(:|[0-9a-fA-F]{0,4}))|(((25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])))(%[\\d\\w]+)?)$",
                    v,
                )
            ),
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:(([^:]+:){6}(([^:]+:[^:]+)|(.*\\..*)))|((([^:]+:)*[^:]+)?::(([^:]+:)*[^:]+)?)(%.+)?)$", v
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="If a new default route is to be defined, the gateway-ip needs to be provided.",
        default=None,
        alias="gateway-ip6",
    )


class IfconfigOutput(YangBaseModel):
    """Output: None"""

    status: StatusEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Successful, Failed or In-progress",
        default=StatusEnum.SUCCESSFUL,
    )
    status_message: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Gives a more detailed status.",
        min_length=0,
        max_length=256,
        default=None,
        alias="status-message",
    )


class Ifconfig(BaseModel):
    """RPC: ifconfig"""

    input: IfconfigInput
    output: IfconfigOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class Delete2Input(YangBaseModel):
    """Input: None"""

    target_node: str = Field(json_schema_extra={"is_config": None}, alias="target-node")


class Delete2(BaseModel):
    """RPC: delete2"""

    input: Delete2Input

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class CreateRollbackPointInput(YangBaseModel):
    """Input: None"""

    backup: bool | None = Field(
        json_schema_extra={"is_config": None},
        description="Creates a 'backup' rollback-point; only one backup rollback-point may exist at a time",
        default=False,
    )
    description: str | None = Field(
        json_schema_extra={"is_config": None},
        description="An optional description for the generated rollback-point",
        min_length=0,
        max_length=200,
        default=None,
    )


class CreateRollbackPointOutput(YangBaseModel):
    """Output: None"""

    created_rollback_point_id: int | None = Field(
        json_schema_extra={"is_config": None},
        description="ID of the created rollback-point",
        ge=0,
        default=None,
        alias="created-rollback-point-id",
    )


class CreateRollbackPoint(BaseModel):
    """RPC: create-rollback-point"""

    input: CreateRollbackPointInput
    output: CreateRollbackPointOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class DiffInput(YangBaseModel):
    """Input: None"""

    table_view: bool | None = Field(
        json_schema_extra={"is_config": None},
        description="In CLI, provides the diff in a table format. Ignored for other protocols.",
        default=None,
        alias="table-view",
    )
    command_view: bool | None = Field(
        json_schema_extra={"is_config": None},
        description="In CLI, provides the diff as CLI commands. Ignored for other protocols.",
        default=None,
        alias="command-view",
    )
    # Choice: config-target
    # Case: target-rollback-point
    target_rollback_point: str | None = Field(
        json_schema_extra={"is_config": None},
        description="rollback-point instance",
        default=None,
        alias="target-rollback-point",
    )
    # Case: candidate
    candidate: bool | None = Field(
        json_schema_extra={"is_config": None}, description="The candidate datastore configuration.", default=None
    )


class DiffOutput(YangBaseModel):
    """Output: None"""

    differences: Any | None = Field(
        json_schema_extra={"is_config": None},
        description="List of differences between the rollback point or candidate and the current system configuration.\nIs composedsubset that matches the running datastore hierarchy, annotated with two metadata attributes:\n- old-value, which in case of attribute value changes, represents the old value of the attribute.\n- operation, which represent MO creation and deletion in the context of the diff\nBoth old-value and operation are metadata annotations in accordance to RFC7952, and are qualified with the\nsame namespace as the datastore they are related with.\nAs such, these annotations will be encoded in XML/JSON in accordance to RFC7952.",
        default=None,
    )


class Diff(BaseModel):
    """RPC: diff"""

    input: DiffInput
    output: DiffOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class RollbackInput(YangBaseModel):
    """Input: None"""

    target_rollback_point: str = Field(
        json_schema_extra={"is_config": None}, description="rollback-point instance", alias="target-rollback-point"
    )


class RollbackOutput(YangBaseModel):
    """Output: None"""

    status: StatusEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Successful, Failed or In-progress",
        default=StatusEnum.SUCCESSFUL,
    )
    status_message: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Gives a more detailed status.",
        min_length=0,
        max_length=256,
        default=None,
        alias="status-message",
    )


class Rollback(BaseModel):
    """RPC: rollback"""

    input: RollbackInput
    output: RollbackOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class OperationTypeEnum(str, Enum):
    """Enumeration for OperationTypeEnum

    Values:
      * force: Forced switch to a target, e.g. working or protection.
      * lockout: Lockout of protection.
      * manual: Manual switch to a target, e.g. working or protection.
      * release: Release current command.
    """

    FORCE = "force"
    LOCKOUT = "lockout"
    MANUAL = "manual"
    RELEASE = "release"


class SwitchTargetEnum(str, Enum):
    """Enumeration for SwitchTargetEnum

    Values:
      * working
      * protection
    """

    WORKING = "working"
    PROTECTION = "protection"


class ProtectionSwitchInput(YangBaseModel):
    """Input: None"""

    protection_group: str = Field(
        json_schema_extra={"is_config": None}, description="The target of the switch command.", alias="protection-group"
    )
    operation_type: OperationTypeEnum = Field(
        json_schema_extra={"is_config": None},
        description="The type of protection switch command",
        alias="operation-type",
    )
    switch_target: SwitchTargetEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="The target of the switch command, which is not needed for release and lockout operation.\n\nCondition (when): (../operation-type != 'lockout') and (../operation-type != 'release')",
        default=None,
        alias="switch-target",
    )
    declarative: bool | None = Field(
        json_schema_extra={"is_config": None},
        description="If true, it tries to push the entire script/commands as a replace operation",
        default=False,
    )


class ProtectionSwitchOutput(YangBaseModel):
    """Output: None"""

    status: StatusEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Successful, Failed or In-progress",
        default=StatusEnum.SUCCESSFUL,
    )
    status_message: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Gives a more detailed status.",
        min_length=0,
        max_length=256,
        default=None,
        alias="status-message",
    )


class ProtectionSwitch(BaseModel):
    """RPC: protection-switch"""

    input: ProtectionSwitchInput
    output: ProtectionSwitchOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class EchoEnum(str, Enum):
    """Enumeration for EchoEnum

    Values:
      * on
      * off
    """

    ON = "on"
    OFF = "off"


class ErrorOptionEnum(str, Enum):
    """Enumeration for ErrorOptionEnum

    Values:
      * stop-on-error: The server will stop on errors.
      * continue-on-error: The server may continue on errors.
      * rollback-on-error: The server will roll back on errors (all-or-nothing behavior)
    """

    STOP_ON_ERROR = "stop-on-error"
    CONTINUE_ON_ERROR = "continue-on-error"
    ROLLBACK_ON_ERROR = "rollback-on-error"


class CliCommandInput(YangBaseModel):
    """Input: None"""

    echo: EchoEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="If echo on, result includes commands and their output;\notherwise it will only include the commands output",
        default=EchoEnum.ON,
    )
    error_option: ErrorOptionEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="How the command execution should behave when errors occur.",
        default=ErrorOptionEnum.ROLLBACK_ON_ERROR,
        alias="error-option",
    )
    replace: bool | None = Field(
        json_schema_extra={"is_config": None},
        description="If true, it tries to push the entire script/commands as a replace operation",
        default=False,
    )
    auto_delete_script_file: bool | None = Field(
        json_schema_extra={"is_config": None},
        description="If true, will automatically delete the script file that was just executed.\nOnly applicable if a script-file is provided as input; otherwise, flag is ignored.\nNote: this auto-delete occurs even if the script execution has errors.",
        default=False,
        alias="auto-delete-script-file",
    )
    # Choice: source
    # Case: script-file
    script_file: str | None = Field(
        json_schema_extra={"is_config": None},
        description="The filepath of the previously downloaded CLI script",
        default=None,
        alias="script-file",
    )
    # Case: commands
    commands: str | None = Field(
        json_schema_extra={"is_config": None},
        description="CLI commands to execute; multiple commands can be provided, one per line",
        default=None,
    )


class CliCommandOutput(YangBaseModel):
    """Output: None"""

    result: str | None = Field(
        json_schema_extra={"is_config": None}, description="Output of the CLI script", default=None
    )
    error_location: int | None = Field(
        json_schema_extra={"is_config": None},
        description="Line number that locates the command that caused the error.\nIf no error occurred, this output parameter is omitted.\nIf multiple errors occur, show only the first command that caused the error.",
        ge=0,
        default=None,
        alias="error-location",
    )
    change_log: str | None = Field(
        json_schema_extra={"is_config": None},
        description="For 'replace' scripts (declarative config), provide a change log of this command.\nChange log is a multi-line string containing individual changes, following the same\nformat as syslog event log. May be empty if no changes occurred.\nExample:\n<change-log>\nCHANGE;ntp;ntp-enabled;false;\nCHANGE;pm-point-shelf-1/shelf-temperature/15min;supervision-switch;disabled;\n</change-log>\n\nCondition (when): ../replace = 'true'",
        default=None,
        alias="change-log",
    )


class CliCommand(BaseModel):
    """RPC: cli-command"""

    input: CliCommandInput
    output: CliCommandOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class MeasurementTypeEnum(str, Enum):
    """Enumeration for MeasurementTypeEnum

    Values:
      * constellation: Constellation.
    """

    CONSTELLATION = "constellation"


class MeasureInput(YangBaseModel):
    """Input: None"""

    measurement_type: MeasurementTypeEnum = Field(
        json_schema_extra={"is_config": None},
        description="Predefined measurement type for measurement.\nFor example, 'measure constellation port-1/1/1'.\nNote that the measurement is only supported on coherent port.",
        alias="measurement-type",
    )
    port_instance: str = Field(
        json_schema_extra={"is_config": None},
        description="Target card for the command. Must exist.",
        alias="port-instance",
    )


class MeasureOutput(YangBaseModel):
    """Output: None"""

    data_response: str | None = Field(
        json_schema_extra={"is_config": None},
        description="The output data for measurement result",
        min_length=1,
        max_length=164000,
        default=None,
        alias="data-response",
    )


class Measure(BaseModel):
    """RPC: measure"""

    input: MeasureInput
    output: MeasureOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class RpcTypeEnum(str, Enum):
    """Enumeration for RpcTypeEnum

    Values:
      * sync
      * async
    """

    SYNC = "sync"
    ASYNC = "async"


class StatusEnum_1(str, Enum):
    """Enumeration for StatusEnum

    Values:
      * Successful
      * Failed
    """

    SUCCESSFUL = "Successful"
    FAILED = "Failed"


class DbBackupInput(YangBaseModel):
    """Input: None"""

    filename: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Path and file name is used with back-up.(xxx.DBS)",
        min_length=5,
        max_length=255,
        default=None,
    )
    rpc_type: RpcTypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Swith the RPC between Synchonization and Asynchonization type. Default shall be async type",
        default=None,
        alias="rpc-type",
    )


class DbBackupOutput(YangBaseModel):
    """Output: None"""

    status: StatusEnum_1 = Field(json_schema_extra={"is_config": None}, description="Successful or Failed")
    status_message: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Gives a more detailed status",
        default=None,
        alias="status-message",
    )


class DbBackup(BaseModel):
    """RPC: db-backup"""

    input: DbBackupInput
    output: DbBackupOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class TriggerEnum(str, Enum):
    """Enumeration for TriggerEnum

    Values:
      * raise-alarm
      * clear-alarm
    """

    RAISE_ALARM = "raise-alarm"
    CLEAR_ALARM = "clear-alarm"


class ConditionTypeEnum(str, Enum):
    """Enumeration for ConditionTypeEnum

    Values:
      * IDP: ID Prom Failure
      * RUP-DEG: Replaceable Unit Problem - Degrade
      * RUP-FAIL: Replaceable Unit Problem - Failed
      * MEA-HWVM: Mismatch of Equipment - Hardware version Mismatch
      * MEA: Mismatch of Equipment, Equipment not support on this slot or this configuration type
      * PWRA: Power Feed A problem
      * PWRB: Power Feed B problem
      * RUP-MISS: Replaceable Unit Missing
      * SBANR: Software Boot Abnormal
      * SDF: Software Download Failure
      * THERMAL: Thermal Problem
      * SDCARDMISS: SD Card Missing
      * SDCARDFAIL: SD Card Failure
      * MGMTRST: Database Down or Corruption
      * PROGFLT: Software fault or failure
      * NTPPU: NTP Sever Unreachable
      * LINKDOWN: Link Down
      * LOS: Loss Of Signal
      * LOL: Loss of Lock
      * LOF-OTU: Loss Of Frame - OTU
      * LOM-OTU: Loss of Multiframe - OTU
      * TIM-OTU: Trace identifier Mismatch on OTU
      * BDI-OTU: Backward Defect Indication - OTU
      * BERSD-OTU: Bit Error Rate Signal Degrade - OTU
      * AIS-OTU: Alarm Indication Signal - OTU
      * BERSD-ODU: Bit Error Rate Signal Degrade - ODU
      * LCK-ODU: Locked
      * OCI-ODU: Open Connection Indication
      * AIS-ODU: Alarm Indication Signal - ODU
      * BDI-ODU: Backward Defect Indication - ODU
      * TIM-ODU: Trace identifier Mismatch on ODU
      * PLM-ODU: Payload Label Mismatch - ODU
      * LOOMFI: Loss of OPU MultiFrame Identifier
      * MSIM: Multiplex Structure Identifier Mismatch
      * LOFLOM: Loss of Frame and Loss of Multiframe
      * CSF-OPU: Client Signal Fail - Optical Payload Unit
      * LOSYNC: Loss of Synchronization
      * LF: Local Fault
      * RF: Remote Fault
      * CSF-LOS-GFP: Client Signal Failure - Loss of Signal
      * CSF-LOSYNC-GFP: Client Signal Failure - Loss of Synchronization
      * CSF-FDI-GFP: Client Signal Failure - Local fault
      * CSF-RDI-GFP: Client Signal Failure - Remote Defect Indication
      * LOFD-GFP: Loss Of Frame Delineation
      * PLM-GFP: Payload Label Mismatch - ODU
      * LPBKFACILITY: Loopback, Facility
      * LPBKFTERM: Loopback, Terminal
      * CONTCOM: Control Communications Failure
      * LATCH-OPEN: Latch status is open
      * LOF: Loss of Frame
      * AIS-L: Alarm Indication Signal -Line
      * MS-AIS: Alarm indication signal - Multiplex Section
      * TIM-R: Trace identifier Mismatch - Regen Section
      * RS-TIM: Trace identifier Mismatch - Regenerator Section
      * RFI-L: Remote Failure Indication - Line
      * MS-RFI: Remote Failure Indication - Multiplex Section
      * CABS: Connection Absent
      * OOG: Out of Gain
      * CONNECT-FAIL: Connection failed
      * ENCRYPT-FAIL: Encryption failed
      * KEYEX-FAIL: Key exchange failed
      * BDI: Backward Defect Indication
      * BDI-O: Backward Defect Indication - Overhead
      * AUTOSHUTOFF: Optical amplifier automatically shutoff
      * FIBRCONN-MISS: Fiber Connection is Missing
      * BDI-P: Backward Defect Indication - Payload
      * LOS-MSA: Loss of Signal - Middle Stage Access
      * PROTNA: Protection Not Available
      * SWITCH-THRES: Switching Threshold Crossed
      * LOSYNC-CD: Loss of Synchronization - Chromatic Dispersion Measurement
      * UPDATE-PSK-FAIL: Updating an existing psk-map failed
      * ENC-TRAFFIC-SQUELCH: Encryption Traffic Squelched
      * OPTPWR-DIFF-HIGH: Optical Power Difference High
      * PT-FAIL: Pilot Tone is Failed
      * PT-DEG: Pilot Tone is Degraded
      * PSK-MISMATCH: PSK mismatch detected
      * VOATC: VOA Threshold Crossing
      * SPAN-DEG: Span Degrade
      * LOA: Loss of Lock
      * TOPO-MISM: Topology Mismatch.
      * FIPS-SELFTEST-FAIL: FIPS Self-Test Failure.
      * LOS-OPR: Loss of Optical Power Received
      * DEG-OPR: Degraded of Optical Power Received
      * HORL: High Reflection/ Low Optical Return Loss
      * AUTOSHUTOFF-DIS: Optical amplifier automatically shutoff disabled
      * OLF: Optical line failure
      * SW-MISM: The active software version in subshelf different from main shelf
      * POWER-TOO-HIGH: If the NMC power is below the minimum or above the maximum values of the configured range, raise the alarm. The exact same range is used as for the RCD checks, which is defined without tolerance with respect to min and max border.
      * POWER-TOO-LOW: If the NMC power is below the minimum or above the maximum values of the configured range, raise the alarm. The exact same range is used as for the RCD checks, which is defined without tolerance with respect to min and max border.
      * FDI: Forward Defect Indication
      * FW-INSTAL-FAIL: 3rd party firmware install fail
      * TIM-OTS: Trace identifier Mismatch on OTS
      * MEMORY-LOW: Chassis free memory is low
      * T-SE: Symbol Error During Carrier
      * T-DROPEVENTS: Drop Events
      * T-OCTETS: Octets
      * T-PKTS: Packets
      * T-BROADCASTPKTS: Broadcast Packets
      * T-MULTICASTPKTS: Multicast Packets
      * T-CRCALIGNERRORS: CRC Alignment Errors
      * T-UNDERSIZEPKTS: Undersize Packets
      * T-OVERSIZEPKTS: Oversize Packets
      * T-FRAGMENTS: Fragments
      * T-JABBERS: Jabbers
      * T-PKTS64OCTETS: Packets with 64 octets in length
      * T-PKTS65TO127OCTETS: Packets with between 65 and 127 octets in length inclusive
      * T-PKTS128TO255OCTETS: Packets with between 128 and 255 octets in length inclusive
      * T-PKTS256TO511OCTETS: Packets with between 256 and 511 octets in length inclusive
      * T-PKTS512TO1023OCTETS: Packets with between 512 and 1023 octets in length inclusive
      * T-PKTS1024TO1518OCTETS: Packets with between 1024 and 1518 octets in length inclusive
      * T-UTIL-HT: Utilization
      * T-BE-FEC: Bit Error Forward Error Correction
      * T-UBE-FEC: Uncorrectable Block Error Forward Error Correction
      * T-BER-FEC-HT: Bit Error Rate before Forward Error Correction - High Threshold
      * T-EB-OTU: Error Block Count - Optical Transport Unit
      * T-ES-OTU: Errored Second - Optical Transport Unit
      * T-SES-OTU: Severely Errored Second - Optical Transport Unit
      * T-UAS-OTU: Unavailable Second - Optical Transport Unit
      * T-EB-ODU: Error Block Count - Optical Data Unit
      * T-ES-ODU: Errored Second - Optical Data Unit
      * T-SES-ODU: Severely Errored Second - Optical Data Unit
      * T-UAS-ODU: Unavailable Second - Optical Data Unit
      * T-DELAY-ODU-HT: Delay measurement - Optical Data Unit - High Threshold
      * T-DELAY-ODU-LT: Delay measurement - Optical Data Unit - Low Threshold
      * T-DGD-HT: Differential Group Delay - High Threshold
      * T-CD-LT: Chromatic Dispersion - Low Threshold
      * T-CD-HT: Chromatic Dispersion - High Threshold
      * T-OSNR-LT: Optical Signal to Noise Ratio - Low Threshold
      * T-LOSS: Loss of Signal Seconds count
      * T-OPR-HT: Optical Power Received level - High Threshold
      * T-OPR-LT: Optical Power Received level - Low Threshold
      * T-QFACTOR-LT: Quality factor - Low Threshold
      * T-OPT-HT: Optical Power Transmitted level - High Threshold
      * T-OPT-LT: Optical Power Transmitted level - Low Threshold
      * T-PDL-HT: Polarization Dependent Loss - High Threshold
      * T-OFT-HT: Optical Frequency Transmitted level - High Threshold
      * T-OFT-LT: Optical Frequency Transmitted level - Low Threshold
      * T-OFR-HT: Optical Frequency Received level - High Threshold
      * T-OFR-LT: Optical Frequency Received level - Low Threshold
      * T-CV-S: Coding Violation - SONET Section
      * T-ES-S: Errored Second - SONET Section
      * T-SES-S: Severely Errored Seconds - SONET Section
      * T-UAS-S: Unavailable Second - SONET Section
      * T-SEFS: Severely Errored Frame Second - SONET
      * T-BBE-RS: Background Block Error - RS
      * T-ES-RS: Errored Second - SDH RS
      * T-SES-RS: Severely Errored Seconds - SDH RS
      * T-UAS-RS: Unavailable Second - SDH RS
      * T-OFS: Out of Frame Seconds - SDH
      * T-OPR-LANE-HT: Optical Power Received level, lane - High Threshold
      * T-OPR-LANE-LT: Optical Power Received level, lane - Low Threshold
      * T-OPR-TOTAL-HT: Optical Power Received level, aggregation - High Threshold
      * T-OPR-TOTAL-LT: Optical Power Received level, aggregation - Low Threshold
      * T-OPT-LANE-HT: Optical Power Transmitted level, lane - High Threshold
      * T-OPT-LANE-LT: Optical Power Transmitted level, lane - Low Threshold
      * T-OPT-TOTAL-HT: Optical Power Transmitted level, total - High Threshold
      * T-OPT-TOTAL-LT: Optical Power Transmitted level, aggregation - Low Threshold
      * T-LOSS-Tx: Loss of Signal Seconds count - Transmit
      * T-LOSS-Rx: Loss of Signal Seconds count - Receive
      * T-PTFS: Pilot Tone Failed Seconds count
      * T-ORL-HT: Optical Return Loss - High Threshold
      * T-CV-PCS: Coding Violation - Ethernet PCS
      * T-ES-PCS: Errored Second - Ethernet PCS
      * T-SES-PCS: Severely Errored Seconds - Ethernet PCS
      * T-UAS-PCS: Unavailable Second - Ethernet PCS
      * T-CBE-FEC: Corrected Block Error Forward Error Correction
      * T-FEB: Farend Error Block counter, Backward Error Indicator
      * T-IAE: Incoming Alignment Error
      * T-BIAE: Backward Incoming Alignment Error
      * T-BE: BIP error
      * T-PktsERR: Errored Packets
      * T-DM-Distance-HT: RDT Delay Measurement Distance - High Threshold
      * T-DM-Distance-LT: RDT Delay Measurement Distance - Low Threshold
      * INIT: Initialization
      * SWUPG-COMPLD: Software Upgrade completed
      * SWUPG-FAIL: Software Upgrade has failed
      * SWUPG-ROLLBACK: Software Upgrade roll back
      * UPG-COMPLD: Module has completed software upgrade
      * UPG-FAIL: Module has failed software upgrade
      * INTRUSION: Unknown account attempt
      * USERLOCK: User suspended
      * SWUPG-IP: Software Upgrade In-Progress
      * ZTC-FAIL: Zero Touch Commissioning Failed
      * ZTC-COMPLETE: Zero Touch Commissioning Complete Successfully
      * DBACT-FAIL: Database Activation Failed
      * INACTIVE: User Inactive
      * RESTART: System restart
      * FSTOPROT: Force switch to protect
      * FSTOWKG: Force switch to working
      * LOCKOUT: Lockout of protection
      * MANTOPROT: Manual switch to protect
      * MANTOWKG: Manual switch to working
      * NOREQ: No Request
      * SDONPROT: Signal degrade on protect
      * SDONWKG: Signal degrade on working
      * SFONPROT: Signal fail on protect
      * SFONWKG: Signal fail on working
      * WKSWPR: Working Switch to Protect
      * PRSWWK: Protect Switch to Working
      * WTR: Wait to Restore
      * DNR: Do Not Revert
      * AUTHN-FAILED: Authentication failed
      * LOGIN-FAILED: Login failed
      * CANDIDATE-PSK-MISMATCH: The candidate psk mismatched with peer NE
      * UPDATE-PSK-COMPLD: Updating an existing psk-map completed
      * CANDIDATE-PSK-AUTHENTICATED: The candidate psk has been authenticated with peer NE
      * UPDATE-PSK-REQ-RCV: Update psk-map request received
      * PULLOUT-TRIGGERED: Pull-out is triggered
      * FIPS-SELFTEST-PASSED: FIPS Self-Test Passed
      * FW-CRASH: Firmware Crash
      * POWER-ARRAY-QUITE-AREA: power array quite area
    """

    IDP = "IDP"
    RUP_DEG = "RUP-DEG"
    RUP_FAIL = "RUP-FAIL"
    MEA_HWVM = "MEA-HWVM"
    MEA = "MEA"
    PWRA = "PWRA"
    PWRB = "PWRB"
    RUP_MISS = "RUP-MISS"
    SBANR = "SBANR"
    SDF = "SDF"
    THERMAL = "THERMAL"
    SDCARDMISS = "SDCARDMISS"
    SDCARDFAIL = "SDCARDFAIL"
    MGMTRST = "MGMTRST"
    PROGFLT = "PROGFLT"
    NTPPU = "NTPPU"
    LINKDOWN = "LINKDOWN"
    LOS = "LOS"
    LOL = "LOL"
    LOF_OTU = "LOF-OTU"
    LOM_OTU = "LOM-OTU"
    TIM_OTU = "TIM-OTU"
    BDI_OTU = "BDI-OTU"
    BERSD_OTU = "BERSD-OTU"
    AIS_OTU = "AIS-OTU"
    BERSD_ODU = "BERSD-ODU"
    LCK_ODU = "LCK-ODU"
    OCI_ODU = "OCI-ODU"
    AIS_ODU = "AIS-ODU"
    BDI_ODU = "BDI-ODU"
    TIM_ODU = "TIM-ODU"
    PLM_ODU = "PLM-ODU"
    LOOMFI = "LOOMFI"
    MSIM = "MSIM"
    LOFLOM = "LOFLOM"
    CSF_OPU = "CSF-OPU"
    LOSYNC = "LOSYNC"
    LF = "LF"
    RF = "RF"
    CSF_LOS_GFP = "CSF-LOS-GFP"
    CSF_LOSYNC_GFP = "CSF-LOSYNC-GFP"
    CSF_FDI_GFP = "CSF-FDI-GFP"
    CSF_RDI_GFP = "CSF-RDI-GFP"
    LOFD_GFP = "LOFD-GFP"
    PLM_GFP = "PLM-GFP"
    LPBKFACILITY = "LPBKFACILITY"
    LPBKFTERM = "LPBKFTERM"
    CONTCOM = "CONTCOM"
    LATCH_OPEN = "LATCH-OPEN"
    LOF = "LOF"
    AIS_L = "AIS-L"
    MS_AIS = "MS-AIS"
    TIM_R = "TIM-R"
    RS_TIM = "RS-TIM"
    RFI_L = "RFI-L"
    MS_RFI = "MS-RFI"
    CABS = "CABS"
    OOG = "OOG"
    CONNECT_FAIL = "CONNECT-FAIL"
    ENCRYPT_FAIL = "ENCRYPT-FAIL"
    KEYEX_FAIL = "KEYEX-FAIL"
    BDI = "BDI"
    BDI_O = "BDI-O"
    AUTOSHUTOFF = "AUTOSHUTOFF"
    FIBRCONN_MISS = "FIBRCONN-MISS"
    BDI_P = "BDI-P"
    LOS_MSA = "LOS-MSA"
    PROTNA = "PROTNA"
    SWITCH_THRES = "SWITCH-THRES"
    LOSYNC_CD = "LOSYNC-CD"
    UPDATE_PSK_FAIL = "UPDATE-PSK-FAIL"
    ENC_TRAFFIC_SQUELCH = "ENC-TRAFFIC-SQUELCH"
    OPTPWR_DIFF_HIGH = "OPTPWR-DIFF-HIGH"
    PT_FAIL = "PT-FAIL"
    PT_DEG = "PT-DEG"
    PSK_MISMATCH = "PSK-MISMATCH"
    VOATC = "VOATC"
    SPAN_DEG = "SPAN-DEG"
    LOA = "LOA"
    TOPO_MISM = "TOPO-MISM"
    FIPS_SELFTEST_FAIL = "FIPS-SELFTEST-FAIL"
    LOS_OPR = "LOS-OPR"
    DEG_OPR = "DEG-OPR"
    HORL = "HORL"
    AUTOSHUTOFF_DIS = "AUTOSHUTOFF-DIS"
    OLF = "OLF"
    SW_MISM = "SW-MISM"
    POWER_TOO_HIGH = "POWER-TOO-HIGH"
    POWER_TOO_LOW = "POWER-TOO-LOW"
    FDI = "FDI"
    FW_INSTAL_FAIL = "FW-INSTAL-FAIL"
    TIM_OTS = "TIM-OTS"
    MEMORY_LOW = "MEMORY-LOW"
    T_SE = "T-SE"
    T_DROPEVENTS = "T-DROPEVENTS"
    T_OCTETS = "T-OCTETS"
    T_PKTS = "T-PKTS"
    T_BROADCASTPKTS = "T-BROADCASTPKTS"
    T_MULTICASTPKTS = "T-MULTICASTPKTS"
    T_CRCALIGNERRORS = "T-CRCALIGNERRORS"
    T_UNDERSIZEPKTS = "T-UNDERSIZEPKTS"
    T_OVERSIZEPKTS = "T-OVERSIZEPKTS"
    T_FRAGMENTS = "T-FRAGMENTS"
    T_JABBERS = "T-JABBERS"
    T_PKTS64OCTETS = "T-PKTS64OCTETS"
    T_PKTS65TO127OCTETS = "T-PKTS65TO127OCTETS"
    T_PKTS128TO255OCTETS = "T-PKTS128TO255OCTETS"
    T_PKTS256TO511OCTETS = "T-PKTS256TO511OCTETS"
    T_PKTS512TO1023OCTETS = "T-PKTS512TO1023OCTETS"
    T_PKTS1024TO1518OCTETS = "T-PKTS1024TO1518OCTETS"
    T_UTIL_HT = "T-UTIL-HT"
    T_BE_FEC = "T-BE-FEC"
    T_UBE_FEC = "T-UBE-FEC"
    T_BER_FEC_HT = "T-BER-FEC-HT"
    T_EB_OTU = "T-EB-OTU"
    T_ES_OTU = "T-ES-OTU"
    T_SES_OTU = "T-SES-OTU"
    T_UAS_OTU = "T-UAS-OTU"
    T_EB_ODU = "T-EB-ODU"
    T_ES_ODU = "T-ES-ODU"
    T_SES_ODU = "T-SES-ODU"
    T_UAS_ODU = "T-UAS-ODU"
    T_DELAY_ODU_HT = "T-DELAY-ODU-HT"
    T_DELAY_ODU_LT = "T-DELAY-ODU-LT"
    T_DGD_HT = "T-DGD-HT"
    T_CD_LT = "T-CD-LT"
    T_CD_HT = "T-CD-HT"
    T_OSNR_LT = "T-OSNR-LT"
    T_LOSS = "T-LOSS"
    T_OPR_HT = "T-OPR-HT"
    T_OPR_LT = "T-OPR-LT"
    T_QFACTOR_LT = "T-QFACTOR-LT"
    T_OPT_HT = "T-OPT-HT"
    T_OPT_LT = "T-OPT-LT"
    T_PDL_HT = "T-PDL-HT"
    T_OFT_HT = "T-OFT-HT"
    T_OFT_LT = "T-OFT-LT"
    T_OFR_HT = "T-OFR-HT"
    T_OFR_LT = "T-OFR-LT"
    T_CV_S = "T-CV-S"
    T_ES_S = "T-ES-S"
    T_SES_S = "T-SES-S"
    T_UAS_S = "T-UAS-S"
    T_SEFS = "T-SEFS"
    T_BBE_RS = "T-BBE-RS"
    T_ES_RS = "T-ES-RS"
    T_SES_RS = "T-SES-RS"
    T_UAS_RS = "T-UAS-RS"
    T_OFS = "T-OFS"
    T_OPR_LANE_HT = "T-OPR-LANE-HT"
    T_OPR_LANE_LT = "T-OPR-LANE-LT"
    T_OPR_TOTAL_HT = "T-OPR-TOTAL-HT"
    T_OPR_TOTAL_LT = "T-OPR-TOTAL-LT"
    T_OPT_LANE_HT = "T-OPT-LANE-HT"
    T_OPT_LANE_LT = "T-OPT-LANE-LT"
    T_OPT_TOTAL_HT = "T-OPT-TOTAL-HT"
    T_OPT_TOTAL_LT = "T-OPT-TOTAL-LT"
    T_LOSS_TX = "T-LOSS-Tx"
    T_LOSS_RX = "T-LOSS-Rx"
    T_PTFS = "T-PTFS"
    T_ORL_HT = "T-ORL-HT"
    T_CV_PCS = "T-CV-PCS"
    T_ES_PCS = "T-ES-PCS"
    T_SES_PCS = "T-SES-PCS"
    T_UAS_PCS = "T-UAS-PCS"
    T_CBE_FEC = "T-CBE-FEC"
    T_FEB = "T-FEB"
    T_IAE = "T-IAE"
    T_BIAE = "T-BIAE"
    T_BE = "T-BE"
    T_PKTSERR = "T-PktsERR"
    T_DM_DISTANCE_HT = "T-DM-Distance-HT"
    T_DM_DISTANCE_LT = "T-DM-Distance-LT"
    INIT = "INIT"
    SWUPG_COMPLD = "SWUPG-COMPLD"
    SWUPG_FAIL = "SWUPG-FAIL"
    SWUPG_ROLLBACK = "SWUPG-ROLLBACK"
    UPG_COMPLD = "UPG-COMPLD"
    UPG_FAIL = "UPG-FAIL"
    INTRUSION = "INTRUSION"
    USERLOCK = "USERLOCK"
    SWUPG_IP = "SWUPG-IP"
    ZTC_FAIL = "ZTC-FAIL"
    ZTC_COMPLETE = "ZTC-COMPLETE"
    DBACT_FAIL = "DBACT-FAIL"
    INACTIVE = "INACTIVE"
    RESTART = "RESTART"
    FSTOPROT = "FSTOPROT"
    FSTOWKG = "FSTOWKG"
    LOCKOUT = "LOCKOUT"
    MANTOPROT = "MANTOPROT"
    MANTOWKG = "MANTOWKG"
    NOREQ = "NOREQ"
    SDONPROT = "SDONPROT"
    SDONWKG = "SDONWKG"
    SFONPROT = "SFONPROT"
    SFONWKG = "SFONWKG"
    WKSWPR = "WKSWPR"
    PRSWWK = "PRSWWK"
    WTR = "WTR"
    DNR = "DNR"
    AUTHN_FAILED = "AUTHN-FAILED"
    LOGIN_FAILED = "LOGIN-FAILED"
    CANDIDATE_PSK_MISMATCH = "CANDIDATE-PSK-MISMATCH"
    UPDATE_PSK_COMPLD = "UPDATE-PSK-COMPLD"
    CANDIDATE_PSK_AUTHENTICATED = "CANDIDATE-PSK-AUTHENTICATED"
    UPDATE_PSK_REQ_RCV = "UPDATE-PSK-REQ-RCV"
    PULLOUT_TRIGGERED = "PULLOUT-TRIGGERED"
    FIPS_SELFTEST_PASSED = "FIPS-SELFTEST-PASSED"
    FW_CRASH = "FW-CRASH"
    POWER_ARRAY_QUITE_AREA = "POWER-ARRAY-QUITE-AREA"


class ManagementLocationEnum(str, Enum):
    """Enumeration for ManagementLocationEnum

    Values:
      * near-end
      * far-end
      * not-applicable
    """

    NEAR_END = "near-end"
    FAR_END = "far-end"
    NOT_APPLICABLE = "not-applicable"


class SimulateInput(YangBaseModel):
    """Input: None"""

    trigger: TriggerEnum = Field(
        json_schema_extra={"is_config": None}, description="The alarm event trigger to simulate."
    )
    alarmed_entity: str | None = Field(
        json_schema_extra={"is_config": None},
        description="The entity affected by the alarm; if ommitted when clearing alarms, all simulated alarms are cleared.",
        default=None,
        alias="alarmed-entity",
    )
    alarm_type: ConditionTypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="The alarm type to be simulated; if ommitted when clearing alarms, all simulated alarms are cleared.",
        default=None,
        alias="alarm-type",
    )
    alarm_location: ManagementLocationEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="The location of the simulated alarm",
        default=ManagementLocationEnum.NEAR_END,
        alias="alarm-location",
    )


class Simulate(BaseModel):
    """RPC: simulate"""

    input: SimulateInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)


class OperationEnum(str, Enum):
    """Enumeration for OperationEnum

    Values:
      * read: Read repair-info
      * write: Write repair-info
    """

    READ = "read"
    WRITE = "write"


class RepairInfoInput(YangBaseModel):
    """Input: None"""

    entity_id: str = Field(
        json_schema_extra={"is_config": None},
        description="The addressed device: a shelf, or a card.\nOnly the following cards support this information:\n- CHMx\nAll chassis (G30) support this information.",
        alias="entity-id",
    )
    operation: OperationEnum = Field(json_schema_extra={"is_config": None})
    repair_info: str | None = Field(
        json_schema_extra={"is_config": None},
        description="The repair-info to be stored in the device.\n\nCondition (when): ../operation='write'",
        default=None,
        alias="repair-info",
    )


class RepairInfoOutput(YangBaseModel):
    """Output: None"""

    status: StatusEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Successful, Failed or In-progress",
        default=StatusEnum.SUCCESSFUL,
    )
    status_message: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Gives a more detailed status.",
        min_length=0,
        max_length=256,
        default=None,
        alias="status-message",
    )
    result_info: str | None = Field(
        json_schema_extra={"is_config": None},
        description="The repair information as stored in the device's EEPROM is returned when\noperation is 'read'\n\nCondition (when): ../operation = 'read'",
        default=None,
        alias="result-info",
    )


class RepairInfo(BaseModel):
    """RPC: repair-info"""

    input: RepairInfoInput
    output: RepairInfoOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, validate_default=True, defer_build=True)
