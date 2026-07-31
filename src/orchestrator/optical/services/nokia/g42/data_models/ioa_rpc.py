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

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class DefaultInput(YangBaseModel):
    """Input: None"""

    entity_id: RestconfList[str] = Field(
        json_schema_extra={"is_config": None}, description="Instances to be defaulted.", alias="entity-id"
    )
    attribute: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": None},
        description="Attribute names to be defaulted. If empty, default all entities' attributes.",
        default=None,
    )


class Default(BaseModel):
    """RPC: default"""

    input: DefaultInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class TypeSelectEnum(str, Enum):
    """Enumeration for TypeSelectEnum

    Values:
      * fiber-connection: Verify fiber-connection using cable-id function. Only supported in some card types.
    """

    FIBER_CONNECTION = "fiber-connection"


class VerifyInput(YangBaseModel):
    """Input: None"""

    type_select: TypeSelectEnum = Field(
        json_schema_extra={"is_config": None}, description="Type of verification.", alias="type-select"
    )
    target_select: str | None = Field(
        json_schema_extra={"is_config": None},
        description="For fiber-connection verification, this identifies the port of the cable-id capable card to be verified, or enter 'all' to  verify all possible ports of the cable-ID capable card.",
        default="all",
        alias="target-select",
    )
    allow_switching: bool | None = Field(
        json_schema_extra={"is_config": None},
        description="cable-id switch is allowed to initiate switching on OPSM to complete the optical path for verification.",
        default=False,
        alias="allow-switching",
    )


class VerifyOutput(YangBaseModel):
    """Output: None"""

    verify_result: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Result of the verification operation.",
        default=None,
        alias="verify-result",
    )


class Verify(BaseModel):
    """RPC: verify"""

    input: VerifyInput
    output: VerifyOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class TypeEnum(str, Enum):
    """Enumeration for TypeEnum

    Values:
      * span-loss-alarm-threshold: Updates the OTS attribute span-loss-alarm-threshold
      * filter-insertion-date-now: Updates chassis filter-insertion date with current date/time.
      * set-under-commissioning: Set entity to be Under Commissioning state.
      * clear-under-commissioning: Set entity to be Ready for Service state.
    """

    SPAN_LOSS_ALARM_THRESHOLD = "span-loss-alarm-threshold"
    FILTER_INSERTION_DATE_NOW = "filter-insertion-date-now"
    SET_UNDER_COMMISSIONING = "set-under-commissioning"
    CLEAR_UNDER_COMMISSIONING = "clear-under-commissioning"


class UpdateInput(YangBaseModel):
    """Input: None"""

    type: TypeEnum = Field(json_schema_extra={"is_config": None}, description="Type of update.")
    entity_id: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": None},
        description="Instance(s) for the required update.",
        default=None,
        alias="entity-id",
    )


class Update(BaseModel):
    """RPC: update"""

    input: UpdateInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class FtsFiletypeEnum(str, Enum):
    """Enumeration for FtsFiletypeEnum

    Values:
      * database: Database
      * swimage: SW Image
      * krp: Key replacement package (KRP)
      * script:  Scripts to download from the remote Server
      * debug-log: Debug Logs
      * pm-logs: PM Logs
      * local-certificate: Either an x509 certificate in PKCS#12 format (with password-protected private key) or PKCS#7 format.
      * trusted-certificate: x509v3 PKCS#7 trusted certificate, either Root or Intermediate CA
      * fdr-log: Flight Data Recorder(FDR) Logs
      * logs: Specific logs
      * file: Generic file
      * peer-certificate: An x509v3 certificate in PKCS#12 format (with password-protected private key)
      * crl: Certificate Revocation List (CRL) in PEM format
      * otdr-result: Otdr result
    """

    DATABASE = "database"
    SWIMAGE = "swimage"
    KRP = "krp"
    SCRIPT = "script"
    DEBUG_LOG = "debug-log"
    PM_LOGS = "pm-logs"
    LOCAL_CERTIFICATE = "local-certificate"
    TRUSTED_CERTIFICATE = "trusted-certificate"
    FDR_LOG = "fdr-log"
    LOGS = "logs"
    FILE = "file"
    PEER_CERTIFICATE = "peer-certificate"
    CRL = "crl"
    OTDR_RESULT = "otdr-result"


class ClearFileInput(YangBaseModel):
    """Input: None"""

    filetype: FtsFiletypeEnum = Field(
        json_schema_extra={"is_config": None}, description="Predefined filetype available for clearing the file"
    )
    target_file: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Filepath of the file to be deleted\n\nCondition (when): ../filetype != 'krp'",
        default=None,
        alias="target-file",
    )


class ClearFileOutput(YangBaseModel):
    """Output: None"""

    clear_result: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Result of the clear operation",
        default=None,
        alias="clear-result",
    )


class ClearFile(BaseModel):
    """RPC: clear-file"""

    input: ClearFileInput
    output: ClearFileOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class ClearAppInput(YangBaseModel):
    """Input: None"""

    app_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": None},
        description="Third party app name.",
        min_length=1,
        max_length=64,
        alias="app-name",
    )


class ClearApp(BaseModel):
    """RPC: clear-app"""

    input: ClearAppInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class ClearTypeEnum(str, Enum):
    """Enumeration for ClearTypeEnum

    Values:
      * full: Full wipe of DB contents; reset to factory defaults
      * keep-networking: Full wipe of DB contents, but keep network configuration; in this case, new-admin-user and new-admin-password must be provided to auto-create the new admin user after clearing the database.
    """

    FULL = "full"
    KEEP_NETWORKING = "keep-networking"


class ClearDatabaseInput(YangBaseModel):
    """Input: None"""

    clear_type: ClearTypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Defines the type of 'clear database' that the system must do.",
        default=ClearTypeEnum.FULL,
        alias="clear-type",
    )
    new_admin_user: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[a-zA-Z_.][a-zA-Z0-9_\\-.]*[$]?)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="The user-name that is auto-configured after the database is wiped.\nMandatory when clearing database with keep-networking.\n\nCondition (when): ../clear-type = 'keep-networking'",
        min_length=1,
        max_length=64,
        default=None,
        alias="new-admin-user",
    )
    new_admin_password: str | None = Field(
        json_schema_extra={"is_config": None},
        description="The password for the new-user-admin that is auto-configured after the database is wiped.\nCan be provided as a password hash (\nformat $<id>$<salt>$<hash>;\nonly id 6 (SHA512) is supported;\nsalt size is between 2 and 16 chars),\nor as plain text.\nMandatory when clearing database with keep-networking.\n\nCondition (when): ../clear-type = 'keep-networking'",
        default=None,
        alias="new-admin-password",
    )


class ClearDatabase(BaseModel):
    """RPC: clear-database"""

    input: ClearDatabaseInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class CriteriaEnum(str, Enum):
    """Enumeration for CriteriaEnum

    Values:
      * all-sessions: Kills all sessions (including the current one).
      * all-other-sessions: Kills all sessions except the current one.
      * all-other-users: Kills all sessions belonging to all users except the current one.
      * all-remote-sessions: Kills all remote sessions (e.g. all except local CRAFT or serial console sessions). May include the current session if that is a remote session.
    """

    ALL_SESSIONS = "all-sessions"
    ALL_OTHER_SESSIONS = "all-other-sessions"
    ALL_OTHER_USERS = "all-other-users"
    ALL_REMOTE_SESSIONS = "all-remote-sessions"


class SessionTypeEnum(str, Enum):
    """Enumeration for SessionTypeEnum

    Values:
      * none
      * cli
      * snmp
      * netconf
      * restconf
      * webgui
      * gnmi
      * tl1
      * gnmi-gnoi
    """

    NONE = "none"
    CLI = "cli"
    SNMP = "snmp"
    NETCONF = "netconf"
    RESTCONF = "restconf"
    WEBGUI = "webgui"
    GNMI = "gnmi"
    TL1 = "tl1"
    GNMI_GNOI = "gnmi-gnoi"


class KillSessionInput(YangBaseModel):
    """Input: None"""

    # Choice: kill-target
    # Case: criteria
    criteria: CriteriaEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Selects sessions based on a particular criteria.",
        default=None,
    )
    # Case: session-type
    session_type: SessionTypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Kills all sessions of this particular type (cli, netconf, etc).",
        default=None,
        alias="session-type",
    )
    # Case: session-user
    session_user: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[a-zA-Z_.][a-zA-Z0-9_\\-.]*[$]?)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="User-name of a user with established sessions; all of this user's sessions will be killed.",
        min_length=1,
        max_length=64,
        default=None,
        alias="session-user",
    )
    # Case: session-id
    session_id: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Identifier of the session that will be killed.\nSupports wildcard to select multiple session-ids (for example, based on IP address).",
        default=None,
        alias="session-id",
    )


class KillSession(BaseModel):
    """RPC: kill-session"""

    input: KillSessionInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class TypeEnum_1(str, Enum):
    """Enumeration for TypeEnum

    Values:
      * trusted: Deletes a trusted certificate.
      * peer: Deletes a peer certificate.
      * local: Deletes a local certificate.
      * purge-all-invalid: Purges all revoked, expired, untrusted, and unsupported certificates.
      * purge-expired: Purges all expired certificates.
      * purge-local-unused: Purges unused local certificates.
      * purge-peer-unused: Purges unused peer certificates.
      * purge-all-unused: Purges all unused local, peer, and trusted certificates.
    """

    TRUSTED = "trusted"
    PEER = "peer"
    LOCAL = "local"
    PURGE_ALL_INVALID = "purge-all-invalid"
    PURGE_EXPIRED = "purge-expired"
    PURGE_LOCAL_UNUSED = "purge-local-unused"
    PURGE_PEER_UNUSED = "purge-peer-unused"
    PURGE_ALL_UNUSED = "purge-all-unused"


class ClearCertificateInput(YangBaseModel):
    """Input: None"""

    type: TypeEnum_1 = Field(
        json_schema_extra={"is_config": None},
        description="Defines the type of 'clear certificate' that the system must do.",
    )
    id: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_.,/@][A-Za-z0-9_\\-.,/@]*))$", v))]
        | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="Foreign Key pointing to the id of the certificate to delete.\n\nCondition (when): ../type = 'trusted' or ../type = 'local' or ../type = 'peer'",
        min_length=1,
        max_length=128,
        default=None,
    )


class ClearCertificateOutput(YangBaseModel):
    """Output: None"""

    clear_result: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Result of the clear operation.",
        min_length=0,
        max_length=13096,
        default=None,
        alias="clear-result",
    )


class ClearCertificate(BaseModel):
    """RPC: clear-certificate"""

    input: ClearCertificateInput
    output: ClearCertificateOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class DisplayTypeEnum(str, Enum):
    """Enumeration for DisplayTypeEnum

    Values:
      * certificate-details: Displays details of the certificate or CSR in human-readable form.
      * certificate-hierarchy: Displays a tree reflecting the trust-chain of a specified certificate.
      * all-certificate-hierarchy: Displays a tree reflecting the full trust graph including all certificates.
    """

    CERTIFICATE_DETAILS = "certificate-details"
    CERTIFICATE_HIERARCHY = "certificate-hierarchy"
    ALL_CERTIFICATE_HIERARCHY = "all-certificate-hierarchy"


class DisplayCertInput(YangBaseModel):
    """Input: None"""

    display_type: DisplayTypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Defines the requested type of display operation.",
        default=DisplayTypeEnum.CERTIFICATE_DETAILS,
        alias="display-type",
    )
    certificate: str | None = Field(
        json_schema_extra={"is_config": None},
        description="The target certificate to display details or trust-chain.\n\nCondition (when): ../display-type != 'all-certificate-hierarchy'",
        default=None,
    )


class DisplayCertOutput(YangBaseModel):
    """Output: None"""

    result: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Certificate or CSR in text form, or tree reflecting trust-chain(s).",
        default=None,
    )


class DisplayCert(BaseModel):
    """RPC: display-cert"""

    input: DisplayCertInput
    output: DisplayCertOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class ClearTargetEnum(str, Enum):
    """Enumeration for ClearTargetEnum

    Values:
      * single-crl: Deletes a single CRL.
      * purge-invalid-crls: Purges all invalid CRL.
      * purge-cached-crls: Purges all CRLs that were automatically cached from a configured CDP or certificate CDP extension.
      * purge-all-crls: Purges all CRLs.
    """

    SINGLE_CRL = "single-crl"
    PURGE_INVALID_CRLS = "purge-invalid-crls"
    PURGE_CACHED_CRLS = "purge-cached-crls"
    PURGE_ALL_CRLS = "purge-all-crls"


class ClearCrlInput(YangBaseModel):
    """Input: None"""

    clear_target: ClearTargetEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Defines the target CRL(s) of the clear operation.",
        default=ClearTargetEnum.SINGLE_CRL,
        alias="clear-target",
    )
    crl_name: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Name of the CRL to delete.\n\nCondition (when): ../clear-target = 'single-crl'",
        default=None,
        alias="crl-name",
    )


class ClearCrlOutput(YangBaseModel):
    """Output: None"""

    removed_crls: str | None = Field(
        json_schema_extra={"is_config": None},
        description="List of CRL(s) that have been removed.",
        min_length=0,
        max_length=2048,
        default=None,
        alias="removed-crls",
    )


class ClearCrl(BaseModel):
    """RPC: clear-crl"""

    input: ClearCrlInput
    output: ClearCrlOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class KeyLengthEnum(str, Enum):
    """Enumeration for KeyLengthEnum

    Values:
      * 2048
      * 3072
      * 4096
      * 256
      * 384
      * 521
    """

    _2048 = "2048"
    _3072 = "3072"
    _4096 = "4096"
    _256 = "256"
    _384 = "384"
    _521 = "521"


class PublicKeyTypesEnum(str, Enum):
    """Enumeration for PublicKeyTypesEnum

    Values:
      * rsa
      * ecdsa
    """

    RSA = "rsa"
    ECDSA = "ecdsa"


class SshKeygenInput(YangBaseModel):
    """Input: None"""

    key_length: KeyLengthEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Strength of the key used for regenerating the private-public key pair",
        default=KeyLengthEnum._2048,
        alias="key-length",
    )
    key_type: PublicKeyTypesEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Type of key to generate",
        default=PublicKeyTypesEnum.RSA,
        alias="key-type",
    )
    key_label: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Label associated with the key. If no value provided, label will be the value of ne-id",
        min_length=0,
        max_length=255,
        default=None,
        alias="key-label",
    )


class SshKeygen(BaseModel):
    """RPC: ssh-keygen"""

    input: SshKeygenInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class CertGenInput(YangBaseModel):
    """Input: None"""

    certificate_name: Annotated[
        str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_.,/@][A-Za-z0-9_\\-.,/@]*))$", v))
    ] = Field(
        json_schema_extra={"is_config": None},
        description="Specifies the name of the certificate to be generated.",
        min_length=1,
        max_length=128,
        alias="certificate-name",
    )
    days: int | None = Field(
        json_schema_extra={"is_config": None},
        description="Number of days a certificate is valid for.",
        ge=1,
        le=36525,
        default=365,
    )
    org_name: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Organization Name.",
        min_length=1,
        max_length=64,
        default=None,
        alias="org-name",
    )
    common_name: str | None = Field(
        json_schema_extra={"is_config": None},
        description="IP or hostname to identify the server.",
        min_length=1,
        max_length=64,
        default=None,
        alias="common-name",
    )
    subject: str | None = Field(
        json_schema_extra={"is_config": None},
        description="The full certificate subject name",
        min_length=1,
        max_length=1024,
        default=None,
    )
    SAN: str | None = Field(
        json_schema_extra={"is_config": None},
        description="The certificate SAN (Subject Alternate Name) fields.\nSANs are specified as Type-Value comma separated list. Valid types are 'IP', 'DNS' and 'otherName'.\nExamples: IP:127.0.0.1,DNS:localhost\n dns:GX-10-4,otherName:1.3.6.1.4.1.21296.1.2.2.1.2;UTF8:GX-10-4",
        min_length=0,
        max_length=1024,
        default=None,
    )
    auto_install: bool | None = Field(
        json_schema_extra={"is_config": None},
        description="Auto-assign certificate to any secure-application without active certificate.",
        default=True,
        alias="auto-install",
    )


class CertGenOutput(YangBaseModel):
    """Output: None"""

    result: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Output status of the self-sign process.",
        min_length=0,
        max_length=256,
        default=None,
    )


class CertGen(BaseModel):
    """RPC: cert-gen"""

    input: CertGenInput
    output: CertGenOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class KeyAlgorithmEnum(str, Enum):
    """Enumeration for KeyAlgorithmEnum

    Values:
      * rsa4096: RSA (Rivest-Shamir-Adleman) public-key cryptosystem algorithm with key size 4096.
      * rsa3072: RSA (Rivest-Shamir-Adleman) public-key cryptosystem algorithm with key size 3072.
      * rsa2048: RSA (Rivest-Shamir-Adleman) public-key cryptosystem algorithm with key size 2048.
      * eccp256: ECC (Elliptic Curve Cryptography) 256-bit prime field Weierstrass curve - prime256v1.
      * eccp384: ECC (Elliptic Curve Cryptography) 384-bit prime field Weierstrass curve - secp384r1.
      * eccp521: ECC (Elliptic Curve Cryptography) 521-bit prime field Weierstrass curve - ecp521r1.
    """

    RSA4096 = "rsa4096"
    RSA3072 = "rsa3072"
    RSA2048 = "rsa2048"
    ECCP256 = "eccp256"
    ECCP384 = "eccp384"
    ECCP521 = "eccp521"


class SignatureHashAlgorithmTypeEnum(str, Enum):
    """Enumeration for SignatureHashAlgorithmTypeEnum

    Values:
      * sha256: Secure Hash Algorithm 2, digest size 256 bits.
      * sha384: Secure Hash Algorithm 2, digest size 384 bits.
      * sha512: Secure Hash Algorithm 2, digest size 512 bits.
      * sha1: Secure Hash Algorithm 1
    """

    SHA256 = "sha256"
    SHA384 = "sha384"
    SHA512 = "sha512"
    SHA1 = "sha1"


class MetadataTemplateEnum(str, Enum):
    """Enumeration for MetadataTemplateEnum

    Values:
      * from-existing-certificate: Metadata is provided/copied from existing a certificate.
      * from-openssl-cnf: Metadata is provided from an openssl .cnf file.
      * generic: Metadata intended for a large variety of applications and scenarios.
      * generic-tls-server: Metadata intended for a server secure-application.
      * generic-tls-client: Metadata intended for a client secure-application.
      * generic-ikev2-identity: Metadata intended for ikev2 node identity.
    """

    FROM_EXISTING_CERTIFICATE = "from-existing-certificate"
    FROM_OPENSSL_CNF = "from-openssl-cnf"
    GENERIC = "generic"
    GENERIC_TLS_SERVER = "generic-tls-server"
    GENERIC_TLS_CLIENT = "generic-tls-client"
    GENERIC_IKEV2_IDENTITY = "generic-ikev2-identity"


class KeyUsageTypeEnum(str, Enum):
    """Enumeration for KeyUsageTypeEnum

    Values:
      * digitalSignature: Allows using public key with a digital sign mechanism.
      * nonRepudiation: Allows using public key for verifying digital signatures.
      * keyEncipherment: Allows usage with a protocol that uses encryption keys from public key.
      * dataEncipherment: Allows public key usage to encrypt user data.
      * keyAgreement: Allows deriving of a session key from the public key.
      * keyCertSign: Allows public key to verify signature of certificates.
      * cRLSign: Allows public key to verify signature of revocation information.
      * encipherOnly: For keyEncipherment, allows the public key to be use for encryption only.
      * decipherOnly: For keyEncipherment, allows the public key to be use for decryption only.
    """

    DIGITALSIGNATURE = "digitalSignature"
    NONREPUDIATION = "nonRepudiation"
    KEYENCIPHERMENT = "keyEncipherment"
    DATAENCIPHERMENT = "dataEncipherment"
    KEYAGREEMENT = "keyAgreement"
    KEYCERTSIGN = "keyCertSign"
    CRLSIGN = "cRLSign"
    ENCIPHERONLY = "encipherOnly"
    DECIPHERONLY = "decipherOnly"


class ExtendedKeyUsageTypeEnum(str, Enum):
    """Enumeration for ExtendedKeyUsageTypeEnum

    Values:
      * serverAuth: TLS WWW Server Authentication.
      * clientAuth: TLS WWW Client Authentication.
      * codeSigning: Code Signing.
      * emailProtection: E-mail Protection (S/MIME).
      * timeStamping: Trusted Timestamping.
      * OCSPSigning: OCSP Signing.
    """

    SERVERAUTH = "serverAuth"
    CLIENTAUTH = "clientAuth"
    CODESIGNING = "codeSigning"
    EMAILPROTECTION = "emailProtection"
    TIMESTAMPING = "timeStamping"
    OCSPSIGNING = "OCSPSigning"


class CsrGenInput(YangBaseModel):
    """Input: None"""

    certificate_name: Annotated[
        str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_.,/@][A-Za-z0-9_\\-.,/@]*))$", v))
    ] = Field(
        json_schema_extra={"is_config": None},
        description="Specifies the name of the certificate to be generated. Using existing name implies rotation.\nNOTE: When importing the signed certificate at a later step, the exact same certificate-name needs to be used.",
        min_length=1,
        max_length=128,
        alias="certificate-name",
    )
    signature_hash_algorithm: SignatureHashAlgorithmTypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Hash algorithm to be used. Default value depends on the selected key-algorithm.",
        default=SignatureHashAlgorithmTypeEnum.SHA512,
        alias="signature-hash-algorithm",
    )
    metadata_template: MetadataTemplateEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Selects the possible sources for the CSR metadata, including reusing it from\nan existing certificate, loading from an openssl cnf file, or using a generic template which\ndefines the metadata defaults.\nIn all cases except for 'from-openssl-cnf', it is possible to override the metadata individual\nparameters by providing the metadata parameters (subject, SAN, etc) explicitly.",
        default=MetadataTemplateEnum.GENERIC,
        alias="metadata-template",
    )
    metadata_from_certificate: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_.,/@][A-Za-z0-9_\\-.,/@]*))$", v))]
        | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="A local-certificate id to be used as metadata source. Metadata details can be overridden separately.\n\nCondition (when): ../metadata-template = 'from-existing-certificate'",
        min_length=1,
        max_length=128,
        default=None,
        alias="metadata-from-certificate",
    )
    metadata_from_cnf: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Multi-line string input of cnf with metadata. Metadata details can be overridden separately.\n\nCondition (when): ../metadata-template = 'from-openssl-cnf'",
        min_length=0,
        max_length=4096,
        default=None,
        alias="metadata-from-cnf",
    )
    subject: str | None = Field(
        json_schema_extra={"is_config": None},
        description="The certificate subject. The common name (CN) RDN is *mandatory*. Each relative DN must have a prefix slash (/).\nExample a minimal valid subject (contains CN only):\n   '/CN=Nokia'\nAn example with all supported RDN fields:\n   '/CN=NokiaRoot/C=US/ST=California/L=Sunnyvale/O=NokiaCorporation/OU=NokiaR&D'\n\nCondition (when): ../metadata-template != 'from-openssl-cnf'",
        min_length=1,
        max_length=1024,
        default=None,
    )
    SAN: str | None = Field(
        json_schema_extra={"is_config": None},
        description="The certificate SAN (Subject Alternate Name) fields.\nSANs are specified as Type-Value comma separated list. Valid types are 'IP', 'DNS' and 'otherName'.\nExamples: IP:127.0.0.1,DNS:localhost\n dns:GX-10-4,otherName:1.3.6.1.4.1.21296.1.2.2.1.2;UTF8:GX-10-4\n\nCondition (when): ../metadata-template != 'from-openssl-cnf'",
        min_length=0,
        max_length=1024,
        default=None,
    )
    key_usage: RestconfList[KeyUsageTypeEnum] | None = Field(
        json_schema_extra={"is_config": None},
        description="The Key Usage type(s) for the certificate.\nDefault is derived from the metadata-template parameter.\n\nCondition (when): ../metadata-template != 'from-openssl-cnf'",
        default=None,
        alias="key-usage",
    )
    extended_key_usage: RestconfList[ExtendedKeyUsageTypeEnum] | None = Field(
        json_schema_extra={"is_config": None},
        description="The Extended Key Usage type(s) for the certificate.\nDefault is derived from the metadata-template parameter.\n\nCondition (when): ../metadata-template != 'from-openssl-cnf'",
        default=None,
        alias="extended-key-usage",
    )
    # Choice: key-source
    # Case: key-algorithm
    key_algorithm: KeyAlgorithmEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Specifies the algorithm to be used for a new key pair for this CSR.",
        default=KeyAlgorithmEnum.ECCP256,
        alias="key-algorithm",
    )
    # Case: key-from-certificate
    key_from_certificate: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_.,/@][A-Za-z0-9_\\-.,/@]*))$", v))]
        | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="Allows to reuse the key pair from an existing local-certificate.",
        min_length=1,
        max_length=128,
        default=None,
        alias="key-from-certificate",
    )


class CsrGenOutput(YangBaseModel):
    """Output: None"""

    csr_bytes: str | None = Field(
        json_schema_extra={"is_config": None},
        description="PKCS#10 output of the CSR process in PEM format.",
        min_length=0,
        max_length=8192,
        default=None,
        alias="csr-bytes",
    )


class CsrGen(BaseModel):
    """RPC: csr-gen"""

    input: CsrGenInput
    output: CsrGenOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class DiffInput(YangBaseModel):
    """Input: None"""

    # Choice: diff-type
    # Case: candidate
    candidate: bool | None = Field(
        json_schema_extra={"is_config": None}, description="The candidate datastore configuration.", default=None
    )
    # Case: commit
    commit: bool | None = Field(
        json_schema_extra={"is_config": None}, description="The commit datastore configuration.", default=None
    )
    commit_id: str | None = Field(
        json_schema_extra={"is_config": None}, description="Specifies the commit ID.", default=None, alias="commit-id"
    )
    base_id: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Optional commit base-id, if not provided diff is between commit-id and current config whereas if it is provided, it is between both commit ids.",
        default=None,
        alias="base-id",
    )


class DiffOutput(YangBaseModel):
    """Output: None"""

    differences: Any | None = Field(
        json_schema_extra={"is_config": None},
        description="List of differences between the rollback point and the current system configuration.\nIs composedsubset that matches the running datastore hierarchy, annotated with two metadata attributes:\n- old-value, which in case of attribute value changes, represents the old value of the attribute.\n- operation, which represent MO creation and deletion in the context of the diff\nBoth old-value and operation are metadata annotations in accordance to RFC7952, and are qualified with the\nsame namespace as the datastore they are related with.\nAs such, these annotations will be encoded in XML/JSON in accordance to RFC7952.",
        default=None,
    )


class Diff(BaseModel):
    """RPC: diff"""

    input: DiffInput
    output: DiffOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


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
        default=ErrorOptionEnum.CONTINUE_ON_ERROR,
        alias="error-option",
    )
    replace: bool | None = Field(
        json_schema_extra={"is_config": None},
        description="If true, it tries to push the entire script/commands as a replace operation",
        default=False,
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


class CliCommand(BaseModel):
    """RPC: cli-command"""

    input: CliCommandInput
    output: CliCommandOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class InstallKrpInput(YangBaseModel):
    """Input: None"""

    krp_name: str = Field(
        json_schema_extra={"is_config": None}, description="Key replacement package name", alias="krp-name"
    )


class InstallKrpOutput(YangBaseModel):
    """Output: None"""

    install_krp_result: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Result of the install-krp operation",
        default=None,
        alias="install-krp-result",
    )


class InstallKrp(BaseModel):
    """RPC: install-krp"""

    input: InstallKrpInput
    output: InstallKrpOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class DeleteIskInput(YangBaseModel):
    """Input: None"""

    key_name: str = Field(
        json_schema_extra={"is_config": None},
        description="Image Signing Key (ISK) name",
        min_length=0,
        max_length=64,
        alias="key-name",
    )


class DeleteIskOutput(YangBaseModel):
    """Output: None"""

    delete_isk_result: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Result of the delete-isk operation",
        default=None,
        alias="delete-isk-result",
    )


class DeleteIsk(BaseModel):
    """RPC: delete-isk"""

    input: DeleteIskInput
    output: DeleteIskOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class FormatEnum(str, Enum):
    """Enumeration for FormatEnum

    Values:
      * log-format: Logs are shown in their native format.
      * structured: Logs are shown in a structured format (xml/json).
    """

    LOG_FORMAT = "log-format"
    STRUCTURED = "structured"


class GetLogInput(YangBaseModel):
    """Input: None"""

    log_file_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-]*)$", v))] = Field(
        json_schema_extra={"is_config": None},
        description="The log file to read; must match a currently configured log-file.",
        min_length=1,
        max_length=128,
        alias="log-file-name",
    )
    start_time: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="Returns log entries starting from this timestamp.\nIf not provided, consider the oldest available logs.",
        default=None,
        alias="start-time",
    )
    end_time: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="Returns log entries ending at this timestamp.\nIf not provided, consider all the logs until the most recent timestamp.",
        default=None,
        alias="end-time",
    )
    number_of_entries: str | int | None = Field(
        json_schema_extra={"is_config": None},
        description="Describes the amount of log entries that are to be returned.",
        default="500",
        alias="number-of-entries",
    )
    pattern_match: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Allows to provide a regex that filters log entries.",
        default=None,
        alias="pattern-match",
    )
    format: FormatEnum | None = Field(
        json_schema_extra={"is_config": None}, description="Selects output format.", default=FormatEnum.LOG_FORMAT
    )


class GetLogOutput(YangBaseModel):
    """Output: None"""

    log_entries: str | None = Field(
        json_schema_extra={"is_config": None},
        description="The resulting log entries when input format = 'log-format'.",
        default=None,
        alias="log-entries",
    )
    structured_log_entries: Any | None = Field(
        json_schema_extra={"is_config": None},
        description="The resulting log entries in a structured format, when input format = 'structured'",
        default=None,
        alias="structured-log-entries",
    )


class GetLog(BaseModel):
    """RPC: get-log"""

    input: GetLogInput
    output: GetLogOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class ClearTargetEnum_1(str, Enum):
    """Enumeration for ClearTargetEnum

    Values:
      * single-log: Clears a single log file.
      * all: Clears all logs. Only possible when privacy-mode is true.
    """

    SINGLE_LOG = "single-log"
    ALL = "all"


class ClearLogInput(YangBaseModel):
    """Input: None"""

    clear_target: ClearTargetEnum_1 | None = Field(
        json_schema_extra={"is_config": None},
        description="Defines the target log of the clear operation.",
        default=ClearTargetEnum_1.SINGLE_LOG,
        alias="clear-target",
    )
    log_file_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-]*)$", v))] | None = Field(
        json_schema_extra={"is_config": None},
        description="The log file to clear; file will still exist, but with empty content.\n\nCondition (when): ../clear-target = 'single-log'",
        min_length=1,
        max_length=128,
        default=None,
        alias="log-file-name",
    )


class ClearLog(BaseModel):
    """RPC: clear-log"""

    input: ClearLogInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class ZtpModeEnum(str, Enum):
    """Enumeration for ZtpModeEnum

    Values:
      * disabled
      * enabled
    """

    DISABLED = "disabled"
    ENABLED = "enabled"


class ChangeZtpModeInput(YangBaseModel):
    """Input: None"""

    ztp_mode: ZtpModeEnum = Field(
        json_schema_extra={"is_config": None}, description="Selects new ztp mode.", alias="ztp-mode"
    )


class ChangeZtpMode(BaseModel):
    """RPC: change-ztp-mode"""

    input: ChangeZtpModeInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class LedModeEnum(str, Enum):
    """Enumeration for LedModeEnum

    Values:
      * flash: Led color flashing.
      * solid: Led color solid.
    """

    FLASH = "flash"
    SOLID = "solid"


class EnableLedInput(YangBaseModel):
    """Input: None"""

    entity: str = Field(
        json_schema_extra={"is_config": None},
        description="Targets a specific entity in the system for enabling its location led test.\nCan be a chassis or a card.",
    )
    timeout: int | None = Field(
        json_schema_extra={"is_config": None},
        description="Specify the timeout, in seconds, before enable-led terminates.\n0 means no timeout.",
        ge=0,
        le=120,
        default=0,
    )
    led_mode: LedModeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Selects the led flash pattern.",
        default=LedModeEnum.FLASH,
        alias="led-mode",
    )


class EnableLed(BaseModel):
    """RPC: enable-led"""

    input: EnableLedInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class DisableLedInput(YangBaseModel):
    """Input: None"""

    entity: str = Field(
        json_schema_extra={"is_config": None},
        description="Targets a specific entity in the system for having its location led test disabled.\nCan be a chassis or a card.",
    )


class DisableLed(BaseModel):
    """RPC: disable-led"""

    input: DisableLedInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class TypeEnum_2(str, Enum):
    """Enumeration for TypeEnum

    Values:
      * write-attenuation-profile: Writes an attenuation-profile for an entity that supports it.
      * read-attenuation-profile: Reads an attenuation-profile for an entity that supports it.
      * create-power-profile: Creates a power-profile snapshot for an entity that supports it.
      * read-power-profile: Reads a power-profile snapshot for an entity that supports it.
      * read-ocm-power: Reads the ocm data from oms entity.
    """

    WRITE_ATTENUATION_PROFILE = "write-attenuation-profile"
    READ_ATTENUATION_PROFILE = "read-attenuation-profile"
    CREATE_POWER_PROFILE = "create-power-profile"
    READ_POWER_PROFILE = "read-power-profile"
    READ_OCM_POWER = "read-ocm-power"


class DirectionEnum(str, Enum):
    """Enumeration for DirectionEnum

    Values:
      * tx: Transmit.
      * rx: Receive.
    """

    TX = "tx"
    RX = "rx"


class ProfileControlInput(YangBaseModel):
    """Input: None"""

    type: TypeEnum_2 = Field(json_schema_extra={"is_config": None}, description="Generic profile interface for IPM.")
    entity: str = Field(
        json_schema_extra={"is_config": None}, description="The entity to which the profile-control applies."
    )
    direction: DirectionEnum = Field(
        json_schema_extra={"is_config": None},
        description="Direction associated with the entity; only applicable for some type of control requests.",
    )
    profile_data: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Profile data to be inputted; details are specific of the type of profile being considered, and only for 'write' requests.",
        default=None,
        alias="profile-data",
    )


class ProfileControlOutput(YangBaseModel):
    """Output: None"""

    result: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Generic output, differs depending on the control request type.",
        default=None,
    )


class ProfileControl(BaseModel):
    """RPC: profile-control"""

    input: ProfileControlInput
    output: ProfileControlOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class StartOtdrMeasurementInput(YangBaseModel):
    """Input: None"""

    entity: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": None},
        description="Targets a specific otdr port in the system to start new test measurement.",
        min_length=1,
        max_length=64,
    )
    otdr_file_prefix: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Indicating the file name prefix of the current OTDR test result. If not specified, ne-name will be used.",
        min_length=0,
        max_length=256,
        default=None,
        alias="otdr-file-prefix",
    )


class StartOtdrMeasurement(BaseModel):
    """RPC: start-otdr-measurement"""

    input: StartOtdrMeasurementInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class StopOtdrMeasurementInput(YangBaseModel):
    """Input: None"""

    entity: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = Field(
        json_schema_extra={"is_config": None},
        description="Targets a specific otdr port in the system to stop the test for measurement if running.",
        min_length=1,
        max_length=64,
    )


class StopOtdrMeasurement(BaseModel):
    """RPC: stop-otdr-measurement"""

    input: StopOtdrMeasurementInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class StopCableIdInput(YangBaseModel):
    """Input: None"""

    target: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Targets a specific port or all ports in the system to stop the Cable ID test if it is currently running. Currently, only the value 'all' is supported.",
        default="all",
    )


class StopCableId(BaseModel):
    """RPC: stop-cable-id"""

    input: StopCableIdInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class TypeEnum_3(str, Enum):
    """Enumeration for TypeEnum

    Values:
      * raman: Triggers calibration on raman cards.
    """

    RAMAN = "raman"


class TriggerEnum(str, Enum):
    """Enumeration for TriggerEnum

    Values:
      * start: Starts the Raman gain calibration for the OTS span.
      * stop: Stops the Raman gain calibration for the OTS span.
      * status: Status of the Raman gain calibration for the OTS span.
    """

    START = "start"
    STOP = "stop"
    STATUS = "status"


class CalibrateInput(YangBaseModel):
    """Input: None"""

    type: TypeEnum_3 = Field(json_schema_extra={"is_config": None}, description="Type of calibration.")
    trigger: TriggerEnum | None = Field(
        json_schema_extra={"is_config": None}, description="Action triggered for the RPC.", default=TriggerEnum.STATUS
    )
    entity: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Select the entity to be calibrated. Type of entity depends on 'type' parameter; for 'raman' calibration, entity may be an ots-r entity.",
        default=None,
    )


class CalibrateOutput(YangBaseModel):
    """Output: None"""

    status: str | None = Field(
        json_schema_extra={"is_config": None}, description="Ongoing status based on the actions.", default=None
    )
    result: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": None},
        description="A human readable result containing the text based information.",
        default=None,
    )


class Calibrate(BaseModel):
    """RPC: calibrate"""

    input: CalibrateInput
    output: CalibrateOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class TriggerEnum_1(str, Enum):
    """Enumeration for TriggerEnum

    Values:
      * raise-alarm: Simulates the raising of an alarm.
      * clear-alarm: Clears a simulated alarm.
      * plug-in-fru: Simulates the plugin of equipment.
      * plug-out-fru: Simulates the plugout of equipment.
    """

    RAISE_ALARM = "raise-alarm"
    CLEAR_ALARM = "clear-alarm"
    PLUG_IN_FRU = "plug-in-fru"
    PLUG_OUT_FRU = "plug-out-fru"


class SimulateInput(YangBaseModel):
    """Input: None"""

    trigger: TriggerEnum_1 = Field(
        json_schema_extra={"is_config": None}, description="The alarm event trigger to simulate."
    )
    # Choice: simulation-type
    # Case: equipment
    holder_AID: str | None = Field(
        json_schema_extra={"is_config": None},
        description="AID of the equipment holder (slot or port) where the equipment will be simulated.",
        min_length=1,
        max_length=64,
        default=None,
        alias="holder-AID",
    )
    type: str | None = Field(
        json_schema_extra={"is_config": None}, description="The type of the equipment to be simulated.", default=None
    )
    subtype: str | None = Field(
        json_schema_extra={"is_config": None}, description="The subtype of the equipment to be simulated.", default=None
    )
    # Case: alarm
    alarmed_entity: str | None = Field(
        json_schema_extra={"is_config": None},
        description="The entity affected by the alarm; if ommitted when clearing alarms, all simulated alarms are cleared.",
        default=None,
        alias="alarmed-entity",
    )
    alarm_type: str | None = Field(
        json_schema_extra={"is_config": None},
        description="The alarm type to be simulated; if ommitted when clearing alarms, all simulated alarms are cleared.",
        default=None,
        alias="alarm-type",
    )
    alarm_direction: str | None = Field(
        json_schema_extra={"is_config": None},
        description="The direction of the simulated alarm. If ommitted, system selects direction automatically.",
        default="auto",
        alias="alarm-direction",
    )
    alarm_location: str | None = Field(
        json_schema_extra={"is_config": None},
        description="The location of the simulated alarm. If ommitted, system selects location automatically.",
        default="auto",
        alias="alarm-location",
    )


class Simulate(BaseModel):
    """RPC: simulate"""

    input: SimulateInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class TypeEnum_4(str, Enum):
    """Enumeration for TypeEnum

    Values:
      * warm: Warm starts a FRU
      * cold: Cold reboots a FRU.
      * shutdown: Shuts down a FRU for controlled removal.
    """

    WARM = "warm"
    COLD = "cold"
    SHUTDOWN = "shutdown"


class RestartInput(YangBaseModel):
    """Input: None"""

    resource: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Resource to restart.\nIf not provided, by default restarts the node controller.",
        default=None,
    )
    type: TypeEnum_4 | None = Field(
        json_schema_extra={"is_config": None}, description="Restart type", default=TypeEnum_4.WARM
    )
    sub_component: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Allows to target a card sub-component to restart.",
        default=None,
        alias="sub-component",
    )


class Restart(BaseModel):
    """RPC: restart"""

    input: RestartInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class CommandEnum(str, Enum):
    """Enumeration for CommandEnum

    Values:
      * restart: Restarts the third party application.
      * netls: Shows the list of subnet networks used by the containers.
      * exec:  execute third party application operation in  params
    """

    RESTART = "restart"
    NETLS = "netls"
    EXEC = "exec"


class AppctlInput(YangBaseModel):
    """Input: None"""

    command: CommandEnum = Field(json_schema_extra={"is_config": None}, description="Application control commands.")
    app_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = Field(
        json_schema_extra={"is_config": None},
        description="Third party app name.",
        min_length=1,
        max_length=64,
        default=None,
        alias="app-name",
    )
    target: str | None = Field(
        json_schema_extra={"is_config": None}, description="Entire system or chassis/card AID.", default="system"
    )
    parameters: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": None},
        description="Optional parameters to be passed in the command.\n\nCondition (when): ../command = 'restart' or ../command = 'exec'",
        default=None,
    )


class AppctlOutput(YangBaseModel):
    """Output: None"""

    appctl_result: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Result of appctl command action.",
        default=None,
        alias="appctl-result",
    )


class Appctl(BaseModel):
    """RPC: appctl"""

    input: AppctlInput
    output: AppctlOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class PingInput(YangBaseModel):
    """Input: None"""

    ping_count: int | None = Field(
        json_schema_extra={"is_config": None},
        description="Stops after sending 'count' ECHO_REQUEST packets.",
        ge=1,
        le=100,
        default=4,
        alias="ping-count",
    )
    ping_timeout: int | None = Field(
        json_schema_extra={"is_config": None},
        description="Specify the timeout, in seconds, before ping exits.",
        ge=1,
        le=20,
        default=2,
        alias="ping-timeout",
    )
    ping_pktsize: int | None = Field(
        json_schema_extra={"is_config": None},
        description="Specifies the number of bytes to be sent. Default is 56, exclusive of headers.",
        ge=0,
        default=56,
        alias="ping-pktsize",
    )
    ping_dest: str = Field(
        json_schema_extra={"is_config": None},
        description="IP address or FQDN of the destination node.",
        alias="ping-dest",
    )
    # Choice: source
    # Case: ping-interface
    ping_interface: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Specify source interface name",
        min_length=1,
        max_length=64,
        default=None,
        alias="ping-interface",
    )
    # Case: ping-vrf
    ping_vrf: str | None = Field(
        json_schema_extra={"is_config": None},
        description="VRF to use. If not provided, defaults to MGMT.",
        default="MGMT",
        alias="ping-vrf",
    )


class PingOutput(YangBaseModel):
    """Output: None"""

    result: str | None = Field(json_schema_extra={"is_config": None}, description="Result of ping.", default=None)


class Ping(BaseModel):
    """RPC: ping"""

    input: PingInput
    output: PingOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class TracerouteInput(YangBaseModel):
    """Input: None"""

    tr_hopcnt: int | None = Field(
        json_schema_extra={"is_config": None},
        description="Specifies the maximum number of hops (max time-to-live value) traceroute will probe. The default is 10.",
        ge=1,
        le=255,
        default=30,
        alias="tr-hopcnt",
    )
    tr_timeout: int | None = Field(
        json_schema_extra={"is_config": None},
        description="Specify the timeout, in seconds, before trace route exits.",
        ge=1,
        le=10,
        default=2,
        alias="tr-timeout",
    )
    tr_dest: str = Field(
        json_schema_extra={"is_config": None},
        description="IPv4/v6 address or FQDN of the destination node.",
        alias="tr-dest",
    )
    tr_pktsize: int | None = Field(
        json_schema_extra={"is_config": None},
        description="Specifies the total  size  of  the  probing packet (default 60 bytes for IPv4).",
        ge=0,
        default=60,
        alias="tr-pktsize",
    )
    # Choice: source
    # Case: tr-interface
    tr_interface: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Specify source interface name",
        min_length=1,
        max_length=64,
        default=None,
        alias="tr-interface",
    )
    # Case: tr-vrf
    tr_vrf: str | None = Field(
        json_schema_extra={"is_config": None},
        description="VRF to use. If not provided, defaults to MGMT.",
        default="MGMT",
        alias="tr-vrf",
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

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class ClearOspfInstanceInput(YangBaseModel):
    """Input: None"""

    instance: int = Field(
        json_schema_extra={"is_config": None},
        description="OSPF protocol instance which need to be re-started.",
        ge=0,
        le=255,
    )


class ClearOspfInstance(BaseModel):
    """RPC: clear-ospf-instance"""

    input: ClearOspfInstanceInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class ClearTopologyInput(YangBaseModel):
    """Input: None"""

    target: str = Field(
        json_schema_extra={"is_config": None},
        description="Target instance to be cleared. May be a lldp-neighbor, a carrier-neighbor, a lldp-port-statistics instance or a autoD-neighbor.",
    )


class ClearTopology(BaseModel):
    """RPC: clear-topology"""

    input: ClearTopologyInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class TypeEnum_5(str, Enum):
    """Enumeration for TypeEnum

    Values:
      * factory-reset: Reset the system or a particular equipment to factory configuration.
      * full-wipe: Clean the entire system and reinstall the SW on the controller and the line-cards.
      * inactive: Clear/copy the inactive software partition.
    """

    FACTORY_RESET = "factory-reset"
    FULL_WIPE = "full-wipe"
    INACTIVE = "inactive"


class RestartBehaviorEnum(str, Enum):
    """Enumeration for RestartBehaviorEnum

    Values:
      * restart: Restart the system after the clean.
      * shutdown: Shutdown the system after the clean.
    """

    RESTART = "restart"
    SHUTDOWN = "shutdown"


class ActionEnum(str, Enum):
    """Enumeration for ActionEnum

    Values:
      * delete: delete the partition.
      * copy: Action to take against the inactive partition.
    """

    DELETE = "delete"
    COPY = "copy"


class ClearSystemInput(YangBaseModel):
    """Input: None"""

    type: TypeEnum_5 = Field(json_schema_extra={"is_config": None}, description="Clear system type.")
    target: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Entire system (main controller chassis) or specific chassis/card AID.\n\nCondition (when): ../type = 'factory-reset' or ../type = 'full-wipe'",
        default="system",
    )
    restart_behavior: RestartBehaviorEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Action to do after the clean operation.\n\nCondition (when): ../type='factory-reset'",
        default=RestartBehaviorEnum.RESTART,
        alias="restart-behavior",
    )
    action: ActionEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Action to clean the partition.\n\nCondition (when): ../type='inactive'",
        default=ActionEnum.DELETE,
    )


class ClearSystemOutput(YangBaseModel):
    """Output: None"""

    clear_system_result: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Result of the clear system operation",
        default=None,
        alias="clear-system-result",
    )


class ClearSystem(BaseModel):
    """RPC: clear-system"""

    input: ClearSystemInput
    output: ClearSystemOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class DbActionEnum(str, Enum):
    """Enumeration for DbActionEnum

    Values:
      * empty-db: Activate software image with empty database.
      * upgrade-db: Activate software image with upgrading the current database.
      * rollback: Rollback to previous active software image.
    """

    EMPTY_DB = "empty-db"
    UPGRADE_DB = "upgrade-db"
    ROLLBACK = "rollback"


class DownloadInput(YangBaseModel):
    """Input: None"""

    filetype: FtsFiletypeEnum = Field(
        json_schema_extra={"is_config": None}, description="Predefined filetype available for download"
    )
    passphrase: str | None = Field(
        json_schema_extra={"is_config": None},
        description="To decode encrypted input files.\n\nCondition (when): ../filetype = 'local-certificate' or ../filetype = 'trusted-certificate'",
        min_length=1,
        max_length=1024,
        default=None,
    )
    certificate_name: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_.,/@][A-Za-z0-9_\\-.,/@]*))$", v))]
        | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="X509v3 local/trusted/peer certificate id.\n\nCondition (when): ../filetype = 'local-certificate' or ../filetype = 'trusted-certificate' or ../filetype = 'peer-certificate'",
        min_length=1,
        max_length=128,
        default=None,
        alias="certificate-name",
    )
    intermediate_import: bool | None = Field(
        json_schema_extra={"is_config": None},
        description="Allow to import any intermediate certificates present in a certificate file bundle. If certificate-name\nis not provided, it will be auto-generated from the topmost certificate Issuer CN plus a numeric suffix.\n\nCondition (when): ../filetype = 'local-certificate' or ../filetype = 'trusted-certificate' or ../filetype = 'peer-certificate'",
        default=False,
        alias="intermediate-import",
    )
    unattended: bool | None = Field(
        json_schema_extra={"is_config": None},
        description="Auto prepare and auto activate file after a successful download.\nOnly some files support 'activation'; others just ignore this flag.",
        default=None,
    )
    async_: bool | None = Field(
        json_schema_extra={"is_config": None}, description="Download asynchronously.", default=None, alias="async"
    )
    skip_secure_verification: bool | None = Field(
        json_schema_extra={"is_config": None},
        description="For HTTPS transfers, skip TLS verification. For SCP/SFTP transfers, skip ssh known host checking.\nIf flag not set, verification is done according with current security-policy.",
        default=None,
        alias="skip-secure-verification",
    )
    sanity_check_override: bool | None = Field(
        json_schema_extra={"is_config": None},
        description="If true, skips the sanity check override when downloading a database snapshot.\n\nCondition (when): ../filetype = 'database'",
        default=False,
        alias="sanity-check-override",
    )
    destination: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Allows user to provide the destination for the downloaded file, including directory and/or filename.\nThis is only applicable when file-type is 'file', representing a generic file transfer.\nThe parameter can be:\n- omitted: means file is downloaded to the default directory with the original file-name\n- a file-name only: uses default directory with the new file-name\n- a relative path: uses the default directory as starting path, plus relative path\n- an absolute path: Absolute path for the user accessible directories can be used\nIt is necessary for the user to have write access to the destination path for the download to succeed.\nTip: use 'show transfer' to see what is the default storage directory.\nFor generic file transfer, no further activity occurs after download, so the 'unattended' flag will be ignored.\n\nCondition (when): ../filetype = 'file'",
        default=None,
    )
    password: str | None = Field(
        json_schema_extra={"is_config": None},
        description="SFTP/SCP/FTP/HTTP/HTTPS password",
        min_length=1,
        max_length=255,
        default=None,
    )
    db_passphrase: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[0-9a-zA-Z.\\-:+=^!/*?&<>()\\[\\]{}@%$#]*)$", v))]
        | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="Passphrase used for encrypting and decrypting DB snapshots.\nFor each command associated with DB snapshots (backup, restore, etc),\nthis db-passphrase will be used, except when it is directly provided in each command.\nAutomatic DB snapshots will not be enabled until this parameter is set.\n\nCondition (when): filetype = 'database'",
        default=None,
        alias="db-passphrase",
    )
    db_action: DbActionEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Specify the expected database operation during activating software image.\n\nCondition (when): filetype = 'swimage' and unattended = 'true'",
        default=DbActionEnum.UPGRADE_DB,
        alias="db-action",
    )
    clear_type: ClearTypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Defines the type of 'clear database' that the system must do.\n\nCondition (when): db-action = 'empty-db'",
        default=ClearTypeEnum.FULL,
        alias="clear-type",
    )
    new_admin_user: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[a-zA-Z_.][a-zA-Z0-9_\\-.]*[$]?)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="The user-name that is auto-configured after the database is wiped.\nMandatory when clearing database with keep-networking.\n\nCondition (when): ../clear-type = 'keep-networking'",
        min_length=1,
        max_length=64,
        default=None,
        alias="new-admin-user",
    )
    new_admin_password: str | None = Field(
        json_schema_extra={"is_config": None},
        description="The password for the new-user-admin that is auto-configured after the database is wiped.\nCan be provided as a password hash (\nformat $<id>$<salt>$<hash>;\nonly id 6 (SHA512) is supported;\nsalt size is between 2 and 16 chars),\nor as plain text.\nMandatory when clearing database with keep-networking.\n\nCondition (when): ../clear-type = 'keep-networking'",
        default=None,
        alias="new-admin-password",
    )
    # Choice: target
    # Case: source
    source: (
        Annotated[
            str,
            AfterValidator(lambda v: check_pattern("^(?:((ftp|sftp|scp|http|https|file):/)?/[^\\s/$.?#].[^\\s]*)$", v)),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="Source of the download ([sftp|scp|http|https|ftp|file]://[user@]hostname/directorypath/filename)",
        min_length=1,
        max_length=1024,
        default=None,
    )
    # Case: file-server-based
    file_server: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": None},
            description="The preconfigured file-server name.",
            min_length=1,
            max_length=64,
            default=None,
            alias="file-server",
        )
    )
    path: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Path (directory and filename) of the remote file.",
        min_length=0,
        max_length=512,
        default=None,
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

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class DbInstanceTypeEnum(str, Enum):
    """Enumeration for DbInstanceTypeEnum

    Values:
      * active
      * onehour
      * oneday
      * oneweek
      * temp
      * manual
      * rollback
    """

    ACTIVE = "active"
    ONEHOUR = "onehour"
    ONEDAY = "oneday"
    ONEWEEK = "oneweek"
    TEMP = "temp"
    MANUAL = "manual"
    ROLLBACK = "rollback"


class UploadInput(YangBaseModel):
    """Input: None"""

    filetype: FtsFiletypeEnum = Field(
        json_schema_extra={"is_config": None}, description="Predefined filetype available for upload"
    )
    source: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Allows user to provide the source for the file to be uploaded, including directory and/or filename.\nThis is only applicable when file-type is 'file', representing a generic file transfer.\nCan be a path relative to the default user directory, or an absolute path - as long as\nuser has access to the target file.\n\nCondition (when): ../filetype = 'file'",
        min_length=0,
        max_length=255,
        default=None,
    )
    async_: bool | None = Field(
        json_schema_extra={"is_config": None}, description="Uploads asynchronously.", default=None, alias="async"
    )
    skip_secure_verification: bool | None = Field(
        json_schema_extra={"is_config": None},
        description="For HTTPS transfers, skip TLS verification. For SCP/SFTP transfers, skip ssh known host checking.\nIf flag not set, verification is done according with current security-policy.",
        default=None,
        alias="skip-secure-verification",
    )
    debug_entity: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": None},
        description="Targets a specific entity in the system for having its Logs to be collected. Can be a chassis or a card\n\nCondition (when): ../filetype = 'debug-log' or ../filetype = 'fdr-log' or ../filetype = 'pm-logs' or ../filetype = 'logs' or ../filetype = 'otdr-result'",
        default=None,
        alias="debug-entity",
    )
    password: str | None = Field(
        json_schema_extra={"is_config": None},
        description="SFTP/SCP/FTP/HTTP/HTTPS password",
        min_length=1,
        max_length=255,
        default=None,
    )
    period: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Time period for PM data.\n\nCondition (when): filetype = 'pm-logs'",
        default=None,
    )
    optional_content: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": None},
        description="List of files to be included for debug-log upload.\n\nCondition (when): ../filetype = 'debug-log'",
        min_length=0,
        max_length=64,
        default=None,
        alias="optional-content",
    )
    log_file_list: (
        RestconfList[Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-]*)$", v))]] | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="List of log files to be uploaded. If empty all available logs are selected.\n\nCondition (when): ../filetype = 'logs'",
        min_length=1,
        max_length=128,
        default=None,
        alias="log-file-list",
    )
    start_time: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Start time from where the logs should be collected. It can be a timestamp or\na time interval from the actual time (now). If empty all log history is selected\n\nCondition (when): ../filetype = 'logs' or ../filetype = 'pm-logs'",
        default=None,
        alias="start-time",
    )
    db_instance: DbInstanceTypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Selected DB instance\n\nCondition (when): ../filetype = 'database'",
        default=DbInstanceTypeEnum.ACTIVE,
        alias="db-instance",
    )
    db_passphrase: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[0-9a-zA-Z.\\-:+=^!/*?&<>()\\[\\]{}@%$#]*)$", v))]
        | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="Passphrase used for encrypting and decrypting DB snapshots.\nFor each command associated with DB snapshots (backup, restore, etc),\nthis db-passphrase will be used, except when it is directly provided in each command.\nAutomatic DB snapshots will not be enabled until this parameter is set.\n\nCondition (when): filetype = 'database'",
        default=None,
        alias="db-passphrase",
    )
    # Choice: target
    # Case: destination
    destination: (
        Annotated[
            str,
            AfterValidator(lambda v: check_pattern("^(?:((ftp|sftp|scp|file|https|http):/)?/[^\\s/$.?#].[^\\s]*)$", v)),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="Destination of the upload ([sftp|scp|ftp|https|http|file]://[user@]hostname/directorypath/filename)",
        min_length=1,
        max_length=1024,
        default=None,
    )
    # Case: file-server-based
    file_server: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": None},
            description="The preconfigured file-server name.",
            min_length=1,
            max_length=64,
            default=None,
            alias="file-server",
        )
    )
    path: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Path (directory and filename) to be used in the remote file-server.\nIf not provided, the file-server initial-path is used, with system defined filename.\nIf the path targets a directory (e.g. /path/ ), the filename is dynamically generated.\nOtherwise, the user defined filename may use some placeholders %t and %m (representing\ntimestamp and ne-name respectively).",
        min_length=0,
        max_length=512,
        default=None,
    )


class UploadOutput(YangBaseModel):
    """Output: None"""

    upload_result: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Result of the upload operation",
        default=None,
        alias="upload-result",
    )


class Upload(BaseModel):
    """RPC: upload"""

    input: UploadInput
    output: UploadOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class TypeEnum_6(str, Enum):
    """Enumeration for TypeEnum

    Values:
      * local-certificate: Either an x509 certificate in PKCS#12 format (with password-protected private key) or PKCS#7 format.
      * peer-certificate: An x509v3 certificate in PKCS#12 format (with password-protected private key).
      * trusted-certificate: x509v3 PKCS#7 trusted certificate, either Root or Intermediate CA.
    """

    LOCAL_CERTIFICATE = "local-certificate"
    PEER_CERTIFICATE = "peer-certificate"
    TRUSTED_CERTIFICATE = "trusted-certificate"


class ImportCertificateInput(YangBaseModel):
    """Input: None"""

    type: TypeEnum_6 = Field(
        json_schema_extra={"is_config": None}, description="Certificate types available for import."
    )
    certificate_name: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_.,/@][A-Za-z0-9_\\-.,/@]*))$", v))]
        | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="X509v3 local/peer/trusted certificate ID.",
        min_length=1,
        max_length=128,
        default=None,
        alias="certificate-name",
    )
    certificate_pem: str = Field(
        json_schema_extra={"is_config": None},
        description="Certificate bytes or certificates bundle in PEM format.",
        min_length=1,
        max_length=81920,
        alias="certificate-pem",
    )
    passphrase: str | None = Field(
        json_schema_extra={"is_config": None},
        description="To decode encrypted input certificates.\n\nCondition (when): ../type = 'local-certificate' or ../type = 'trusted-certificate'",
        min_length=1,
        max_length=1024,
        default=None,
    )
    intermediate_import: bool | None = Field(
        json_schema_extra={"is_config": None},
        description="Allow to import any intermediate certificates present in a PEM string bundle. If certificate-name\nis not provided, it will be auto-generated from the topmost certificate issuer CN plus a numeric suffix.",
        default=False,
        alias="intermediate-import",
    )


class ImportCertificateOutput(YangBaseModel):
    """Output: None"""

    import_result: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Result of the import operation.",
        min_length=0,
        max_length=128,
        default=None,
        alias="import-result",
    )


class ImportCertificate(BaseModel):
    """RPC: import-certificate"""

    input: ImportCertificateInput
    output: ImportCertificateOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class OptionEnum(str, Enum):
    """Enumeration for OptionEnum

    Values:
      * validate: Validate
      * apply: Apply
    """

    VALIDATE = "validate"
    APPLY = "apply"


class PrepareUpgradeInput(YangBaseModel):
    """Input: None"""

    option: OptionEnum = Field(
        json_schema_extra={"is_config": None}, description="Predefined options available for prepare-upgrade"
    )
    manifest: str = Field(
        json_schema_extra={"is_config": None},
        description="manifest to be prepared for upgrade",
        min_length=0,
        max_length=256,
    )
    ignore_precheck_failures: bool | None = Field(
        json_schema_extra={"is_config": None},
        description="Ignore validation failures.",
        default=False,
        alias="ignore-precheck-failures",
    )
    unattended: bool | None = Field(
        json_schema_extra={"is_config": None},
        description="Auto activate software after prepare upgrade.\n\nCondition (when): ../option = 'apply'",
        default=None,
    )
    db_action: DbActionEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Specify the expected database operation during activating software image.\n\nCondition (when): unattended = 'true'",
        default=DbActionEnum.UPGRADE_DB,
        alias="db-action",
    )
    clear_type: ClearTypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Defines the type of 'clear database' that the system must do.\n\nCondition (when): db-action = 'empty-db'",
        default=ClearTypeEnum.FULL,
        alias="clear-type",
    )
    new_admin_user: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[a-zA-Z_.][a-zA-Z0-9_\\-.]*[$]?)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="The user-name that is auto-configured after the database is wiped.\nMandatory when clearing database with keep-networking.\n\nCondition (when): ../clear-type = 'keep-networking'",
        min_length=1,
        max_length=64,
        default=None,
        alias="new-admin-user",
    )
    new_admin_password: str | None = Field(
        json_schema_extra={"is_config": None},
        description="The password for the new-user-admin that is auto-configured after the database is wiped.\nCan be provided as a password hash (\nformat $<id>$<salt>$<hash>;\nonly id 6 (SHA512) is supported;\nsalt size is between 2 and 16 chars),\nor as plain text.\nMandatory when clearing database with keep-networking.\n\nCondition (when): ../clear-type = 'keep-networking'",
        default=None,
        alias="new-admin-password",
    )


class PrepareUpgradeOutput(YangBaseModel):
    """Output: None"""

    prepare_upgrade_result: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Result of the prepare-upgrade operation",
        default=None,
        alias="prepare-upgrade-result",
    )


class PrepareUpgrade(BaseModel):
    """RPC: prepare-upgrade"""

    input: PrepareUpgradeInput
    output: PrepareUpgradeOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class ActivateFileInput(YangBaseModel):
    """Input: None"""

    filetype: FtsFiletypeEnum = Field(
        json_schema_extra={"is_config": None}, description="Predefined filetype available for upload"
    )
    db_action: DbActionEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Specify the expected database operation during activating software image.\n\nCondition (when): filetype = 'swimage'",
        default=DbActionEnum.UPGRADE_DB,
        alias="db-action",
    )
    clear_type: ClearTypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Defines the type of 'clear database' that the system must do.\n\nCondition (when): db-action = 'empty-db'",
        default=ClearTypeEnum.FULL,
        alias="clear-type",
    )
    new_admin_user: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[a-zA-Z_.][a-zA-Z0-9_\\-.]*[$]?)$", v))] | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="The user-name that is auto-configured after the database is wiped.\nMandatory when clearing database with keep-networking.\n\nCondition (when): ../clear-type = 'keep-networking'",
        min_length=1,
        max_length=64,
        default=None,
        alias="new-admin-user",
    )
    new_admin_password: str | None = Field(
        json_schema_extra={"is_config": None},
        description="The password for the new-user-admin that is auto-configured after the database is wiped.\nCan be provided as a password hash (\nformat $<id>$<salt>$<hash>;\nonly id 6 (SHA512) is supported;\nsalt size is between 2 and 16 chars),\nor as plain text.\nMandatory when clearing database with keep-networking.\n\nCondition (when): ../clear-type = 'keep-networking'",
        default=None,
        alias="new-admin-password",
    )
    label: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Label to be activated\n\nCondition (when): ../filetype = 'swimage'",
        default=None,
    )
    db_passphrase: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[0-9a-zA-Z.\\-:+=^!/*?&<>()\\[\\]{}@%$#]*)$", v))]
        | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="Passphrase used for encrypting and decrypting DB snapshots.\nFor each command associated with DB snapshots (backup, restore, etc),\nthis db-passphrase will be used, except when it is directly provided in each command.\nAutomatic DB snapshots will not be enabled until this parameter is set.\n\nCondition (when): filetype = 'database'",
        default=None,
        alias="db-passphrase",
    )
    db_instance: DbInstanceTypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Database instance name to activate.\n\nCondition (when): ../filetype = 'database'",
        default=DbInstanceTypeEnum.TEMP,
        alias="db-instance",
    )
    sanity_check_override: bool | None = Field(
        json_schema_extra={"is_config": None},
        description="Allows user to skip the database/swimage sanity check.\n\nCondition (when): ../filetype = 'database' or ../filetype = 'swimage'",
        default=False,
        alias="sanity-check-override",
    )
    validate_again: bool | None = Field(
        json_schema_extra={"is_config": None},
        description="Allows user to repeat validation check done as part of apply, before activation too.\n\nCondition (when): ../filetype = 'swimage'",
        default=False,
        alias="validate-again",
    )


class ActivateFileOutput(YangBaseModel):
    """Output: None"""

    activate_file_result: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Result of the activate-file operation",
        default=None,
        alias="activate-file-result",
    )


class ActivateFile(BaseModel):
    """RPC: activate-file"""

    input: ActivateFileInput
    output: ActivateFileOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class CancelUpgradeOutput(YangBaseModel):
    """Output: None"""

    cancel_upgrade_result: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Result of the cancel-upgrade operation",
        default=None,
        alias="cancel-upgrade-result",
    )


class CancelUpgrade(BaseModel):
    """RPC: cancel-upgrade"""

    output: CancelUpgradeOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


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


class SetTime(BaseModel):
    """RPC: set-time"""

    input: SetTimeInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class PasswordInput(YangBaseModel):
    """Input: None"""

    old_password: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] = Field(
        json_schema_extra={"is_config": None},
        description="The current password.",
        min_length=0,
        max_length=200,
        alias="old-password",
    )
    new_password: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[ -~]*)$", v))] = Field(
        json_schema_extra={"is_config": None},
        description="The new password.",
        min_length=0,
        max_length=200,
        alias="new-password",
    )


class Password(BaseModel):
    """RPC: password"""

    input: PasswordInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class ClearRecoverMode(BaseModel):
    """RPC: clear-recover-mode"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class RunTaskInput(YangBaseModel):
    """Input: None"""

    task_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = Field(
        json_schema_extra={"is_config": None},
        description="The task name to be executed.",
        min_length=1,
        max_length=64,
        default=None,
        alias="task-name",
    )


class RunTask(BaseModel):
    """RPC: run-task"""

    input: RunTaskInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class TypeEnum_7(str, Enum):
    """Enumeration for TypeEnum

    Values:
      * db-backup: Stores the current state of the Configuration database into one of the available backup slots.
      * system-backup: Perform a system backup into the chassis storage.
    """

    DB_BACKUP = "db-backup"
    SYSTEM_BACKUP = "system-backup"


class TakeSnapshotInput(YangBaseModel):
    """Input: None"""

    type: TypeEnum_7 | None = Field(
        json_schema_extra={"is_config": None},
        description="Location where the snapshot will be stored.",
        default=TypeEnum_7.DB_BACKUP,
    )
    db_instance: DbInstanceTypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Target db-instance name which will hold the DB snapshot.\n\nCondition (when): ../type = 'db-backup'",
        default=DbInstanceTypeEnum.TEMP,
        alias="db-instance",
    )
    db_passphrase: (
        Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[0-9a-zA-Z.\\-:+=^!/*?&<>()\\[\\]{}@%$#]*)$", v))]
        | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="Passphrase used for encrypting and decrypting DB snapshots.\nFor each command associated with DB snapshots (backup, restore, etc),\nthis db-passphrase will be used, except when it is directly provided in each command.\nAutomatic DB snapshots will not be enabled until this parameter is set.\n\nCondition (when): type = 'db-backup'",
        default=None,
        alias="db-passphrase",
    )
    description: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Optional description for this DB snapshot.\n\nCondition (when): ../type = 'db-backup'",
        min_length=0,
        max_length=128,
        default=None,
    )


class TakeSnapshot(BaseModel):
    """RPC: take-snapshot"""

    input: TakeSnapshotInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class ScriptListItem(YangBaseModel):
    """List with the existing scripts."""

    script: str = Field(json_schema_extra={"is_config": None}, description="Script name.")
    script_type: str | None = Field(
        json_schema_extra={"is_config": None}, description="Script type.", default=None, alias="script-type"
    )
    file_size: int | None = Field(
        json_schema_extra={"is_config": None}, description="Fize size.", ge=0, default=None, alias="file-size"
    )
    created: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v
                )
            ),
        ]
        | None
    ) = Field(json_schema_extra={"is_config": None}, description="Creation date.", default=None)
    description: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Script description defined on the begining of the file.",
        default=None,
    )


class GetScriptInput(YangBaseModel):
    """Input: None"""

    # Choice: option
    # Case: list-scripts
    list_scripts: bool | None = Field(
        json_schema_extra={"is_config": None},
        description="List all existing scripts.",
        default=None,
        alias="list-scripts",
    )
    # Case: script-name
    script_name: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Get the content of an existing script. The script name is a relative path to the script directory.",
        default=None,
        alias="script-name",
    )


class GetScriptOutput(YangBaseModel):
    """Output: None"""

    script_list: RestconfList[ScriptListItem] | None = Field(
        json_schema_extra={"is_config": None},
        description="List with the existing scripts.",
        default=None,
        alias="script-list",
    )
    script_content: str | None = Field(
        json_schema_extra={"is_config": None}, description="Script content.", default=None, alias="script-content"
    )


class GetScript(BaseModel):
    """RPC: get-script"""

    input: GetScriptInput
    output: GetScriptOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class RunScriptInput(YangBaseModel):
    """Input: None"""

    script_name: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Script absolute or relative path from the script directory.",
        default=None,
        alias="script-name",
    )
    arguments: str | None = Field(
        json_schema_extra={"is_config": None}, description="Optional arguments to the script.", default=None
    )


class RunScriptOutput(YangBaseModel):
    """Output: None"""

    success: bool | None = Field(
        json_schema_extra={"is_config": None}, description="Script was executed with success.", default=None
    )
    result: str | None = Field(
        json_schema_extra={"is_config": None}, description="Returns the output of the script.", default=None
    )


class RunScript(BaseModel):
    """RPC: run-script"""

    input: RunScriptInput
    output: RunScriptOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class ManualSwitchoverInput(YangBaseModel):
    """Input: None"""

    resource: str = Field(json_schema_extra={"is_config": None}, description="Active controller card to switchover.")


class ManualSwitchover(BaseModel):
    """RPC: manual-switchover"""

    input: ManualSwitchoverInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class OperationEnum(str, Enum):
    """Enumeration for OperationEnum

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


class FileOperationInput(YangBaseModel):
    """Input: None"""

    operation: OperationEnum = Field(json_schema_extra={"is_config": None}, description="File operations to do.")
    file_path: str = Field(json_schema_extra={"is_config": None}, description="Current file path.", alias="file-path")
    new_file_path: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:[A-Za-z0-9_\\-/\\.]*)$", v))] | None = (
        Field(
            json_schema_extra={"is_config": None},
            description="New file path.\n\nCondition (when): ../operation = 'rename'",
            default=None,
            alias="new-file-path",
        )
    )


class FileOperationOutput(YangBaseModel):
    """Output: None"""

    result: str | None = Field(
        json_schema_extra={"is_config": None}, description="The file operation result.", default=None
    )


class FileOperation(BaseModel):
    """RPC: file-operation"""

    input: FileOperationInput
    output: FileOperationOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class CallHomeInput(YangBaseModel):
    """Input: None"""

    dial_out_server_name: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] = (
        Field(
            json_schema_extra={"is_config": None},
            description="The dial-out-server to connect to.",
            min_length=1,
            max_length=64,
            alias="dial-out-server-name",
        )
    )


class CallHome(BaseModel):
    """RPC: call-home"""

    input: CallHomeInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class ActivateFwInput(YangBaseModel):
    """Input: None"""

    fw_image_name: str = Field(
        json_schema_extra={"is_config": None},
        description="FW file name",
        min_length=0,
        max_length=64,
        alias="fw-image-name",
    )
    resource: RestconfList[str] = Field(
        json_schema_extra={"is_config": None}, description="List of equipment to be activated."
    )


class ActivateFw(BaseModel):
    """RPC: activate-fw"""

    input: ActivateFwInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class ReKeyInput(YangBaseModel):
    """Input: None"""

    # Choice: re-key-type
    # Case: ipsec-security-association
    ipsec_security_association: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Points to IPsec SPD entry object (Child SA).",
        default=None,
        alias="ipsec-security-association",
    )
    # Case: ikev2-peer
    ikev2_peer: str | None = Field(
        json_schema_extra={"is_config": None},
        description="A reference to the IKE peer object (IKE SA).",
        default=None,
        alias="ikev2-peer",
    )
    # Case: secure-entity
    secure_entity: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Points to secure entity object (Child SA).",
        default=None,
        alias="secure-entity",
    )


class ReKey(BaseModel):
    """RPC: re-key"""

    input: ReKeyInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class ReAuthInput(YangBaseModel):
    """Input: None"""

    ikev2_peer: str = Field(
        json_schema_extra={"is_config": None},
        description="A reference to the IKE peer object (IKE SA).",
        alias="ikev2-peer",
    )


class ReAuth(BaseModel):
    """RPC: re-auth"""

    input: ReAuthInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class TestSignalDirectionEnum(str, Enum):
    """Enumeration for TestSignalDirectionEnum

    Values:
      * ingress
      * egress
      * auto
    """

    INGRESS = "ingress"
    EGRESS = "egress"
    AUTO = "auto"


class ClearDiagnosticsInput(YangBaseModel):
    """Input: None"""

    entity_id: str = Field(
        json_schema_extra={"is_config": None},
        description="Target entity for the command. Must exist.",
        alias="entity-id",
    )
    test_signal_direction: TestSignalDirectionEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="The test signal direction. If not specified, the counter for the enabled direction would be cleared.",
        default=TestSignalDirectionEnum.AUTO,
        alias="test-signal-direction",
    )


class ClearDiagnostics(BaseModel):
    """RPC: clear-diagnostics"""

    input: ClearDiagnosticsInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class DirectoryListItem(YangBaseModel):
    """List with the existing scripts."""

    path: str = Field(json_schema_extra={"is_config": None}, description="File name.")
    path_type: str | None = Field(
        json_schema_extra={"is_config": None},
        description="'-' for file, 'd' for directory and 'l' for link",
        min_length=1,
        max_length=1,
        default=None,
        alias="path-type",
    )
    permissions: int | None = Field(
        json_schema_extra={"is_config": None},
        description="Read, Write and Exec permissions for user.\nRepresented as the octal format of standard UNIX\nex. 775: user read/write/execute, group read/write/execute,\nglobal read/execute.",
        ge=0,
        default=None,
    )
    size: Uint64 | None = Field(
        json_schema_extra={"is_config": None}, description="File size.", ge=0, le=18446744073709551615, default=None
    )
    last_changed: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v
                )
            ),
        ]
        | None
    ) = Field(json_schema_extra={"is_config": None}, description="Creation date.", default=None, alias="last-changed")
    umask: int | None = Field(
        json_schema_extra={"is_config": None},
        description="File creation mask. Represented as the octal\nformat of standard UNIX. ex. 22: group and global\nwill not have write permissions over newly created files",
        ge=0,
        default=None,
    )


class GetFileInput(YangBaseModel):
    """Input: None"""

    path_name: str | None = Field(
        json_schema_extra={"is_config": None},
        description="If name is a directory, display its list, if name is a file, display its\ncontents. The path can be relative to the /storage directory or absolute.",
        default="/storage",
        alias="path-name",
    )


class GetFileOutput(YangBaseModel):
    """Output: None"""

    # Choice: path-contents
    # Case: directory-list
    directory_list: RestconfList[DirectoryListItem] | None = Field(
        json_schema_extra={"is_config": None},
        description="List with the existing scripts.",
        default=None,
        alias="directory-list",
    )
    # Case: file-content
    file_content: str | None = Field(
        json_schema_extra={"is_config": None},
        description="File content. Limited to 1MB.",
        default=None,
        alias="file-content",
    )


class GetFile(BaseModel):
    """RPC: get-file"""

    input: GetFileInput
    output: GetFileOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class TemplateTypeEnum(str, Enum):
    """Enumeration for TemplateTypeEnum

    Values:
      * serdes-template: Applies all existing serdes-templates to the provided TOM list as the 'applicable-tom' parameter. If no specific TOMs are provided, all TOMs are considered for template application.
      * config: Applies one or more config templates, effectively acting as a 'set' request for the attributes targetted in the templates.
    """

    SERDES_TEMPLATE = "serdes-template"
    CONFIG = "config"


class ApplyTemplateInput(YangBaseModel):
    """Input: None"""

    template_type: TemplateTypeEnum = Field(
        json_schema_extra={"is_config": None},
        description="The type of template to apply. Other parameters may be required depending on the template type.",
        alias="template-type",
    )
    applicable_tom: RestconfList[str] | None = Field(
        json_schema_extra={"is_config": None},
        description="List of TOMs to which to apply serdes-templates against.\n   If not provided (e.g. list is empty), all system TOMs will be considered for application.\n\nCondition (when): ../template-type = 'serdes-template'",
        default=None,
        alias="applicable-tom",
    )
    template_group: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))] | None = (
        Field(
            json_schema_extra={"is_config": None},
            description="The name of the template-group to apply.\nIf not provided, the currently enabled template-group is auto-selected.\n\nCondition (when): ../template-type = 'config'",
            min_length=1,
            max_length=64,
            default=None,
            alias="template-group",
        )
    )
    template_entry: str | None = Field(
        json_schema_extra={"is_config": None},
        description="The name of the template entry to apply.\nNeeds to exist within the provided template-group.\nWildcard ('*') is usable to pick multiple template entries.\nIf not provided, all entries in the template-group are applied.\n\nCondition (when): ../template-type = 'config'",
        default=None,
        alias="template-entry",
    )
    dry_run: bool | None = Field(
        json_schema_extra={"is_config": None},
        description="If set to true, command provides a description of what changes would occur,\n   but doesn't actually apply them.\n   Otherwise, templates are applied (e.g. have impact on system configuration).\n\nCondition (when): ../template-type = 'config'",
        default=False,
        alias="dry-run",
    )


class ApplyTemplateOutput(YangBaseModel):
    """Output: None"""

    result: str | None = Field(
        json_schema_extra={"is_config": None}, description="Result of the command - if applicable.", default=None
    )


class ApplyTemplate(BaseModel):
    """RPC: apply-template"""

    input: ApplyTemplateInput
    output: ApplyTemplateOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class OperationEnum_1(str, Enum):
    """Enumeration for OperationEnum

    Values:
      * start: Starts BERT.
      * stop: Stops ongoing BERT.
      * get: Retrieves results for one or more BERT.
      * delete: Deletes results for a completed or stopped BERT.
    """

    START = "start"
    STOP = "stop"
    GET = "get"
    DELETE = "delete"


class TestSignalTypeEnum(str, Enum):
    """Enumeration for TestSignalTypeEnum

    Values:
      * none
      * PRBS31
      * PRBS31NONINV
      * scrambled-idles
      * packet-PRBS31: MAC layer framed packet.
    """

    NONE = "none"
    PRBS31 = "PRBS31"
    PRBS31NONINV = "PRBS31NONINV"
    SCRAMBLED_IDLES = "scrambled-idles"
    PACKET_PRBS31 = "packet-PRBS31"


class TestSignalDirectionEnum_1(str, Enum):
    """Enumeration for TestSignalDirectionEnum

    Values:
      * na
      * ingress
      * egress
    """

    NA = "na"
    INGRESS = "ingress"
    EGRESS = "egress"


class TestSignalMonitoringTypeEnum(str, Enum):
    """Enumeration for TestSignalMonitoringTypeEnum

    Values:
      * none
      * PRBS31
      * PRBS31NONINV
      * scrambled-idles
      * fec-frames
      * packet-PRBS31: MAC layer framed packet.
    """

    NONE = "none"
    PRBS31 = "PRBS31"
    PRBS31NONINV = "PRBS31NONINV"
    SCRAMBLED_IDLES = "scrambled-idles"
    FEC_FRAMES = "fec-frames"
    PACKET_PRBS31 = "packet-PRBS31"


class TestStatusEnum(str, Enum):
    """Enumeration for TestStatusEnum

    Values:
      * in-progress: Test is in progress.
      * completed: Test Completed Sucessfully.
      * aborted: Test is aborted.
      * preparing-to-complete: Test is waiting for hold off time to stop genarated signal.
    """

    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    ABORTED = "aborted"
    PREPARING_TO_COMPLETE = "preparing-to-complete"


class TestResultEnum(str, Enum):
    """Enumeration for TestResultEnum

    Values:
      * not-applicable: Result Not applicable.
      * pass: Passed the criteria for test.
      * fail: Failed the criteria for test.
    """

    NOT_APPLICABLE = "not-applicable"
    PASS = "pass"
    FAIL = "fail"


class RecordItem(YangBaseModel):
    """Record entry. Content will depend on the operation provided.
    Full data is only provided in the 'get' operation.
    """

    test_id: str = Field(
        json_schema_extra={"is_config": None},
        description="Test id of this BERT.\nIf not provided as explicit input, system will generate an id automatically, and include it in the\noutput of the RPC.",
        min_length=1,
        max_length=24,
        alias="test-id",
    )
    resource: str | None = Field(
        json_schema_extra={"is_config": None}, description="Existing system resource.", default=None
    )
    resource_type: str | None = Field(
        json_schema_extra={"is_config": None}, description="Type of resource.", default=None, alias="resource-type"
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.",
        min_length=1,
        max_length=64,
        default=None,
    )
    test_signal_type: TestSignalTypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Generated Signal Type for the BERT.",
        default=TestSignalTypeEnum.NONE,
        alias="test-signal-type",
    )
    test_signal_direction: TestSignalDirectionEnum_1 | None = Field(
        json_schema_extra={"is_config": None},
        description="Direction of the facility to which the test-pattern shall be generated.\nMandatory except if test-signal-type is 'none'.",
        default=TestSignalDirectionEnum_1.NA,
        alias="test-signal-direction",
    )
    test_signal_monitoring_type: TestSignalMonitoringTypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Monitoring Signal Type for this BERT.",
        default=TestSignalMonitoringTypeEnum.NONE,
        alias="test-signal-monitoring-type",
    )
    test_signal_monitoring_direction: TestSignalDirectionEnum_1 | None = Field(
        json_schema_extra={"is_config": None},
        description="Direction of the facility from which the test-pattern shall be monitored.\nMandatory except if test-signal-monitoring-type is 'none'.",
        default=TestSignalDirectionEnum_1.NA,
        alias="test-signal-monitoring-direction",
    )
    test_duration: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Duration of the test to run.",
        default="na",
        alias="test-duration",
    )
    test_status: TestStatusEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Status of the BERT as a result of an operation trigger.",
        default=None,
        alias="test-status",
    )
    test_result: TestResultEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="The test result. Not applicable if test is still ongoing.",
        default=TestResultEnum.NOT_APPLICABLE,
        alias="test-result",
    )
    start_time: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="Timestamp when the test was started.",
        default=None,
        alias="start-time",
    )
    stop_time: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Timestamp when the test was stopped.\nWill be empty if test is still ongoing.",
        default=None,
        alias="stop-time",
    )
    cumulative_error_count: Uint64 | None = Field(
        json_schema_extra={"is_config": None},
        description="Total number of bit errors accumulated since lock was established.",
        ge=0,
        le=18446744073709551615,
        default=None,
        alias="cumulative-error-count",
    )
    peer_lock_established: bool | None = Field(
        json_schema_extra={"is_config": None},
        description="Indicates whether BERT peer lock was established at least once during the test.",
        default=False,
        alias="peer-lock-established",
    )
    peer_lock_established_time: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="The moment in time the peer-lock was first established.\n\nCondition (when): ../peer-lock-established = 'true'",
        default=None,
        alias="peer-lock-established-time",
    )
    peer_lock_lost: bool | None = Field(
        json_schema_extra={"is_config": None},
        description="Indicates whether BERT peer lock was lost at least once during the test, after\npeer-lock-established was set to true.",
        default=False,
        alias="peer-lock-lost",
    )
    peer_lock_lost_time: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="The moment in time the peer-lock was first lost.\n\nCondition (when): ../peer-lock-lost = 'true'",
        default=None,
        alias="peer-lock-lost-time",
    )
    peer_lock_lost_duration: Uint64 | None = Field(
        json_schema_extra={"is_config": None},
        description="Duration of the time window where peer lock was lost (after it was established).",
        ge=0,
        le=18446744073709551615,
        default=None,
        alias="peer-lock-lost-duration",
    )
    error_rate: Decimal64 | None = Field(
        json_schema_extra={"is_config": None},
        description="Average error rate accumulated since lock was established.",
        default=None,
        alias="error-rate",
    )
    elapsed_time: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:(((1000)|(0*\\d{1,3}))w)? *(((1000)|(0*\\d{1,3}))d)? *(((1000)|(0*\\d{1,3}))h)? *(((1000)|(0*\\d{1,3}))m)? *(((1000)|(0*\\d{1,3}))s)?)$",
                    v,
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="Time elapsed since the test has started.",
        min_length=0,
        max_length=32,
        default=None,
        alias="elapsed-time",
    )


class BertInput(YangBaseModel):
    """Input: None"""

    operation: OperationEnum_1 = Field(json_schema_extra={"is_config": None}, description="BERT operation.")
    test_id: Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-*.]*))$", v))] | None = Field(
        json_schema_extra={"is_config": None},
        description="Test id for this BERT, used to perform start/stop operations for the same BERT instance.\nThis parameter is optional when starting BERT operation - system will provide a generated test-id if so.\nFor other operations, this parameter is mandatory.",
        min_length=1,
        max_length=24,
        default=None,
        alias="test-id",
    )
    resource: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Existing system resource.\n\nCondition (when): operation != 'stop'",
        default=None,
    )
    resource_type: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Type of resource.\n\nCondition (when): operation != 'stop'",
        default=None,
        alias="resource-type",
    )
    AID: str | None = Field(
        json_schema_extra={"is_config": False},
        description="Resource Access Identifier (AID). Identifies an instance within a specific resource type.\n\nCondition (when): operation != 'stop'",
        min_length=1,
        max_length=64,
        default=None,
    )
    test_signal_type: TestSignalTypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Generated Signal Type for the BERT.\n\nCondition (when): operation = 'start'",
        default=TestSignalTypeEnum.NONE,
        alias="test-signal-type",
    )
    test_signal_direction: TestSignalDirectionEnum_1 | None = Field(
        json_schema_extra={"is_config": None},
        description="Direction of the facility to which the test-pattern shall be generated.\nMandatory except if test-signal-type is 'none'.\n\nCondition (when): operation = 'start'",
        default=TestSignalDirectionEnum_1.NA,
        alias="test-signal-direction",
    )
    test_signal_monitoring_type: TestSignalMonitoringTypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Monitoring Signal Type for this BERT.\n\nCondition (when): operation = 'start'",
        default=TestSignalMonitoringTypeEnum.NONE,
        alias="test-signal-monitoring-type",
    )
    test_signal_monitoring_direction: TestSignalDirectionEnum_1 | None = Field(
        json_schema_extra={"is_config": None},
        description="Direction of the facility from which the test-pattern shall be monitored.\nMandatory except if test-signal-monitoring-type is 'none'.\n\nCondition (when): operation = 'start'",
        default=TestSignalDirectionEnum_1.NA,
        alias="test-signal-monitoring-direction",
    )
    test_duration: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Duration of the test to run.\n\nCondition (when): operation = 'start'",
        default="na",
        alias="test-duration",
    )


class BertOutput(YangBaseModel):
    """Output: None"""

    record: RestconfList[RecordItem] | None = Field(
        json_schema_extra={"is_config": None},
        description="Record entry. Content will depend on the operation provided.\nFull data is only provided in the 'get' operation.",
        default=None,
    )


class Bert(BaseModel):
    """RPC: bert"""

    input: BertInput
    output: BertOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class TypeEnum_8(str, Enum):
    """Enumeration for TypeEnum

    Values:
      * encryption-with-integrity: Change DB to Encryption + Integrity support.
      * encryption: Change DB to Only Encryption support.
    """

    ENCRYPTION_WITH_INTEGRITY = "encryption-with-integrity"
    ENCRYPTION = "encryption"


class DbMigrateInput(YangBaseModel):
    """Input: None"""

    type: TypeEnum_8 = Field(json_schema_extra={"is_config": None}, description="Type of db Protection scheme.")


class DbMigrate(BaseModel):
    """RPC: db-migrate"""

    input: DbMigrateInput

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class DashboardEnum(str, Enum):
    """Enumeration for DashboardEnum

    Values:
      * system: System Summary dashboard.
      * L1-traffic: Layer 1 Traffic Port Summary dashboard.
      * equipment: Equipment Summary dashboard.
      * L0-oxcon: Layer 0 OXCON Summary dashboard.
      * L0-ocm: Layer 0 OCM Summary dashboard.
      * power: Equipment Power Summary dashboard.
    """

    SYSTEM = "system"
    L1_TRAFFIC = "L1-traffic"
    EQUIPMENT = "equipment"
    L0_OXCON = "L0-oxcon"
    L0_OCM = "L0-ocm"
    POWER = "power"


class PortSummaryItem(YangBaseModel):
    """List provided when dashboard is 'L1-traffic';
    represents traffic port summmary according with the provided filter.
    Only configured ports will appear in the list.
    Note: not applicable or not available parameters appear as '---'.
    """

    port_id: str = Field(json_schema_extra={"is_config": None}, description="The port AID.", alias="port-id")
    mode: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Represents in which mode the port is; depending on the port-type, this will represent something different.",
        default=None,
    )
    alarms: str | None = Field(
        json_schema_extra={"is_config": None},
        description="A summary view of the alarms associated with the port.\nPossible values are: 'none' if no alarms are raised, or the highest severity alarm-type (if multiple, system picks one of them).\nIf more than one alarm is raised, the alarm-type is suffixed with the character '+'\nDoes not include not-reported alarms.",
        default=None,
    )
    oper_state: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Can be 'ok' or 'not ok' depending on whether any facility associated with the port is disabled.",
        default=None,
        alias="oper-state",
    )
    admin_state: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Can be 'unlocked' or 'not ok'; if at least one of the facilities associated with the port is not unlocked,\nthis value will be 'not ok'; otherwise will be 'unlocked'.",
        default=None,
        alias="admin-state",
    )
    rx_power: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Received power - if applicable for this port.",
        default=None,
        alias="rx-power",
    )
    rx_frequency: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Received frequency - if applicable for this port.",
        default=None,
        alias="rx-frequency",
    )
    osnr: str | None = Field(
        json_schema_extra={"is_config": None}, description="OSNR value - if applicable for this port.", default=None
    )
    pre_fec_ber: str | None = Field(
        json_schema_extra={"is_config": None},
        description="pre-fec-ber value - if applicable for this port.",
        default=None,
        alias="pre-fec-ber",
    )
    pre_fec_q: str | None = Field(
        json_schema_extra={"is_config": None},
        description="pre-fec-q value - if applicable for this port.",
        default=None,
        alias="pre-fec-q",
    )
    corrected_words: str | None = Field(
        json_schema_extra={"is_config": None},
        description="corrected-words value - if applicable for this port.",
        default=None,
        alias="corrected-words",
    )
    uncorrected_words: str | None = Field(
        json_schema_extra={"is_config": None},
        description="uncorrected-words value - if applicable for this port.",
        default=None,
        alias="uncorrected-words",
    )
    cd: str | None = Field(
        json_schema_extra={"is_config": None}, description="cd value - if applicable for this port.", default=None
    )
    dgd: str | None = Field(
        json_schema_extra={"is_config": None}, description="dgd value - if applicable for this port.", default=None
    )
    tx_power: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Transmitted power - if applicable for this port.",
        default=None,
        alias="tx-power",
    )
    tx_frequency: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Transmitted frequency - if applicable for this port.",
        default=None,
        alias="tx-frequency",
    )
    bit_rate: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Bit rate - if applicable for this port.",
        default=None,
        alias="bit-rate",
    )
    baud_rate: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Baud rate - if applicable for this port.",
        default=None,
        alias="baud-rate",
    )
    fec_type: str | None = Field(
        json_schema_extra={"is_config": None},
        description="fec-type associated with this port if applicable.",
        default=None,
        alias="fec-type",
    )
    modulation_format: str | None = Field(
        json_schema_extra={"is_config": None},
        description="modulation-format associated with this port if applicable.",
        default=None,
        alias="modulation-format",
    )


class StatusInput(YangBaseModel):
    """Input: None"""

    dashboard: DashboardEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="Type of dashboard to display. Each dashboard provides different details.\nSystem summary dashboard is provided by default.",
        default=DashboardEnum.SYSTEM,
    )
    filter: str | None = Field(
        json_schema_extra={"is_config": None},
        description="For some dashboards, allows to specify an AID filter, reducing the scope of the output.\nFor the 'equipment' and 'power' dashboards, the filter needs to be an existing chassis id.\nFor the 'L1-traffic' dashboard, the filter can be a specific port AID, or a wildcard based AID,\nwhere the * needs to be the last character.\nExample: 1-4-* is allowed, but 1-*-T1 is not allowed.\nFor the 'oxcon' and 'ocm' dashboards, the filter needs to be a specific degree number.\nIf filter is not provided, all applicable instances are provided in the dashboard output.\n\nCondition (when): ../dashboard != 'system'",
        default=None,
    )


class StatusOutput(YangBaseModel):
    """Output: None"""

    result: str | None = Field(
        json_schema_extra={"is_config": None},
        description="A human readable result containing the text based dashboard information.",
        default=None,
    )
    port_summary: RestconfList[PortSummaryItem] | None = Field(
        json_schema_extra={"is_config": None},
        description="List provided when dashboard is 'L1-traffic';\nrepresents traffic port summmary according with the provided filter.\nOnly configured ports will appear in the list.\nNote: not applicable or not available parameters appear as '---'.",
        default=None,
        alias="port-summary",
    )


class Status(BaseModel):
    """RPC: status"""

    input: StatusInput
    output: StatusOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class ActionEnum_1(str, Enum):
    """Enumeration for ActionEnum

    Values:
      * show: Shows current config as CLI script. Presence of CSPs is dependent on the csp-retrieval-encoding security policy.
      * save: Saves current config as a CLI script. Presence of CSPs is dependent on the csp-retrieval-encoding security policy.
      * apply: Applies config from file, replacing current config.
      * diff: Performs a diff between current config and provided config-file. Assumes config-file contains the config just as 'config show' command outputs it.
      * default: Applies default config for the system, effectively resetting it to factory default without a reboot. The 'keep' parameter can be used to provide an indication of what config to keep (users, etc).
    """

    SHOW = "show"
    SAVE = "save"
    APPLY = "apply"
    DIFF = "diff"
    DEFAULT = "default"


class KeepEnum(str, Enum):
    """Enumeration for KeepEnum

    Values:
      * users: Keep local user accounts. If this option is not provided, all local sers will be removed from the system, potentially causing the current session to be terminated. At this point, the system will only accept console-user access via serial console.
      * networking: Keep networking configuration, including IP addresses and routing settings. If this option is not provided, DHCP will be re-enabled, and system will may not be remotely accessible, which would mean networking could only be reconfigured via local (serial console or CRAFT interface) access.
      * equipment: Keep equipment configuration, including chassis and card configuration. If this option is not provided, all equipment configuration will be removed, including secondary chassis and non-default cards.
    """

    USERS = "users"
    NETWORKING = "networking"
    EQUIPMENT = "equipment"


class ConfigInput(YangBaseModel):
    """Input: None"""

    action: ActionEnum_1 = Field(
        json_schema_extra={"is_config": None}, description="Type of action to do to the config."
    )
    config_file: str | None = Field(
        json_schema_extra={"is_config": None},
        description="For save/apply/diff actions, provide the config-file as an absolute path.\nFor apply/diff, needs to match an existing config file.\nFor save, needs to match a valid file path which may or not exist; if it exists, this command will overwrite it.\nIf not provided, the default /storage/saved_config.cli is used.",
        default=None,
        alias="config-file",
    )
    keep: RestconfList[KeepEnum] | None = Field(
        json_schema_extra={"is_config": None},
        description="Configuration to keep when applying default config.\nMultiple options can be provided.\n\nCondition (when): ../action = 'default'",
        default=None,
    )


class ConfigOutput(YangBaseModel):
    """Output: None"""

    result: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Output of the command; will depend on input action.",
        default=None,
    )


class Config(BaseModel):
    """RPC: config"""

    input: ConfigInput
    output: ConfigOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class GetPossibleValuesInput(YangBaseModel):
    """Input: None"""

    config: Any | None = Field(
        json_schema_extra={"is_config": None},
        description="Configuration to take in consideration when obtaining the possible values.\nThe leaf that has no value is the target for the RPC.\nThis command has same syntax as NETCONF edit-config, where content-match nodes provide the\ncurrent command being edited, and selection nodes represent the leaf to obtain the possible values for.\nNote that only one selection node may exist in the command.\nExample of rpc input:\n<nc:rpc xmlns:nc='urn:ietf:params:xml:ns:netconf:base:1.0' message-id='1'>\n   <get-possible-values xmlns='http://infinera.com/yang/ioa/rpc' >\n       <config>\n           <ne xmlns=http://infinera.com/yang/ioa/ne>\n               <facilities>\n                   <trib-ptp>\n                       <name>1-4-T1</name>\n                       <service-type/>\n                       <admin-state>unlock</admin-state>\n                   </trib-ptp>\n               </facilities>\n           </ne>\n       </config>\n   </get-possible-values>\n</nc:rpc>\nIn the example above, the 'service-type' is the attribute being queried regarding possible-values,\nand the value of 'admin-state' is provided as context.",
        default=None,
    )


class GetPossibleValuesOutput(YangBaseModel):
    """Output: None"""

    possible_values: Any | None = Field(
        json_schema_extra={"is_config": None},
        description="Output in the form of a <get> response, where the target leaf is provided with a list of possible values.\nNote that this list may be empty (in which case it is not possible to edit this parameter), have one possibility, or more than one.\nIt will be encoded as if it was a leaf-list.\nIf the selection node was a free string/integer the value will be empty and annotated with\ncontextual help (string length, pattern and integer range).\nIf the provided value is annotated with current=true, then it is the current value of the attribute.\nLikewise if it corresponds to the default value it will be annotated with default=true\nExample of rpc output:\n<nc:rpc-reply xmlns:nc='urn:ietf:params:xml:ns:netconf:base:1.0' message-id='1'>\n<possible-values xmlns='http://infinera.com/yang/ioa/rpc'>\n<ne xmlns='http://infinera.com/yang/ioa/ne'>\n<facilities>\n   <trib-ptp>\n       <name>1-4-T1</name>\n       <service-type>100GBE</service-type>\n       <service-type>OTU4</service-type>\n   </trib-ptp>\n</facilities>\n</ne>\n</possible-values>\n</nc:rpc-reply>\nIn this case the 'service-type' attribute was the selection node and the output contains the possible configuration values",
        default=None,
        alias="possible-values",
    )


class GetPossibleValues(BaseModel):
    """RPC: get-possible-values"""

    input: GetPossibleValuesInput
    output: GetPossibleValuesOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class GetDefaultInput(YangBaseModel):
    """Input: None"""

    data: Any | None = Field(
        json_schema_extra={"is_config": None},
        description="Configuration of the object for which the default values are being retrieved.\nThe target attributes should be provided empty, non empty attributes will be used as a context when calculating the default values.\nExample:\n<nc:rpc xmlns:nc='urn:ietf:params:xml:ns:netconf:base:1.0' message-id='1'>\n   <get-default xmlns='http://infinera.com/yang/ioa/rpc'>\n       <data>\n           <ne xmlns='http://infinera.com/yang/ioa/ne'>\n               <system>\n               <security>\n                   <user>\n                       <user-name>John</user-name>\n                       <timeout>5</timeout>\n                       <suspension-time/>\n                       <enabled/>\n                   </user>\n               </security>\n               </system>\n           </ne>\n       </data>\n   </get-default>\n</nc:rpc>\nIn the example above, the attributes 'suspension-time' and 'enabled' are the defaults\nbeing retrieved, and timeout is an attribute provided as a support for the calculation of those defaults",
        default=None,
    )


class GetDefaultOutput(YangBaseModel):
    """Output: None"""

    result: Any | None = Field(
        json_schema_extra={"is_config": None},
        description="Output with the same content as the input but the attributes that were provided empty have the default values attached,\nunless they do not have a default value, in which case it remains empty.\nExample of rpc output:\n<nc:rpc-reply xmlns:nc='urn:ietf:params:xml:ns:netconf:base:1.0' message-id='1'>\n<result xmlns='http://infinera.com/yang/ioa/rpc'>\n<ne xmlns='http://infinera.com/yang/ioa/ne'>\n<system>\n<security>\n   <user>\n   <user-name>John</user-name>\n   <timeout>5</timeout>\n   <suspension-time>5</suspension-time>\n   <enabled>true</enabled>\n   </user>\n</security>\n</system>\n</ne>\n</result>\n</nc:rpc-reply>",
        default=None,
    )


class GetDefault(BaseModel):
    """RPC: get-default"""

    input: GetDefaultInput
    output: GetDefaultOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class DisplayAccessInput(YangBaseModel):
    """Input: None"""

    verbose: bool | None = Field(
        json_schema_extra={"is_config": None}, description="Provide detailed output.", default=False
    )
    access_target: str | None = Field(
        json_schema_extra={"is_config": None},
        description="The target entities to display access information.  This may be:\n- one of the enumerated values (e.g.: data-nodes)\n- the XPath representation of a data node in any enabled data-model (e.g.: /ne/system/security/user)\n- a notification (e.g.: /alarm-notification)\n- an RPC (e.g.: /restart)\n- a non-YANG-based command (e.g.: gNOI.Reboot)",
        default="all",
        alias="access-target",
    )
    # Choice: scope
    # Case: user-name
    user_name: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Name of user to target.",
        min_length=0,
        max_length=64,
        default=None,
        alias="user-name",
    )
    # Case: user-group
    user_group: (
        RestconfList[Annotated[str, AfterValidator(lambda v: check_pattern("^(?:([A-Za-z0-9_\\-.,]*))$", v))]] | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="One or more user groups to target.",
        min_length=1,
        max_length=64,
        default=None,
        alias="user-group",
    )


class DisplayAccessOutput(YangBaseModel):
    """Output: None"""

    result: Any | None = Field(
        json_schema_extra={"is_config": None}, description="Result of the display-access operation.", default=None
    )


class DisplayAccess(BaseModel):
    """RPC: display-access"""

    input: DisplayAccessInput
    output: DisplayAccessOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class CommandItem(YangBaseModel):
    """List of commands of commit record. Only available when using id."""

    commands: str = Field(json_schema_extra={"is_config": None}, description="Command of a commit record.")


class ReverseCommandItem(YangBaseModel):
    """List of reverse commands of commit record. Only available when using id."""

    reverse_commands: str = Field(
        json_schema_extra={"is_config": None},
        description="Reverse command of a commit record.",
        alias="reverse-commands",
    )


class CommitRecordItem(YangBaseModel):
    """Individual commit record."""

    commit_id: str = Field(json_schema_extra={"is_config": None}, description="ID of the commit.", alias="commit-id")
    timestamp: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": None},
        description="Maximum number of records that will be retrieved.",
        default=None,
    )
    user: str | None = Field(
        json_schema_extra={"is_config": None}, description="User that performed the commit.", default=None
    )
    commands: str | None = Field(
        json_schema_extra={"is_config": None}, description="Summary of commands applied in commit.", default=None
    )
    command: RestconfList[CommandItem] | None = Field(
        json_schema_extra={"is_config": None},
        description="List of commands of commit record. Only available when using id.",
        default=None,
    )
    reverse_command: RestconfList[ReverseCommandItem] | None = Field(
        json_schema_extra={"is_config": None},
        description="List of reverse commands of commit record. Only available when using id.",
        default=None,
        alias="reverse-command",
    )


class GetCommitInput(YangBaseModel):
    """Input: None"""

    # Choice: target
    # Case: number-of-records
    number_of_records: int | None = Field(
        json_schema_extra={"is_config": None},
        description="Number of records to be returned.",
        ge=1,
        default=50,
        alias="number-of-records",
    )
    # Case: since
    since: (
        Annotated[
            str,
            AfterValidator(
                lambda v: check_pattern(
                    "^(?:\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[\\+\\-]\\d{2}:\\d{2}))$", v
                )
            ),
        ]
        | None
    ) = Field(
        json_schema_extra={"is_config": None}, description="Returns the commits since this timestamp.", default=None
    )
    # Case: id
    id: Uint64 | None = Field(
        json_schema_extra={"is_config": None},
        description="Id of a commit record",
        ge=0,
        le=18446744073709551615,
        default=None,
    )


class GetCommitOutput(YangBaseModel):
    """Output: None"""

    additional_records: int | None = Field(
        json_schema_extra={"is_config": None},
        description="Number of commits not included in this response; only shown if 'number-of-records' was provided in the input.",
        ge=0,
        default=None,
        alias="additional-records",
    )
    commit_record: RestconfList[CommitRecordItem] | None = Field(
        json_schema_extra={"is_config": None},
        description="Individual commit record.",
        default=None,
        alias="commit-record",
    )


class GetCommit(BaseModel):
    """RPC: get-commit"""

    input: GetCommitInput
    output: GetCommitOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class RollbackInput(YangBaseModel):
    """Input: None"""

    # Choice: rollback-type
    # Case: commit
    commit: bool | None = Field(
        json_schema_extra={"is_config": None}, description="Rollback based on commit.", default=None
    )
    commit_id: Uint64 | None = Field(
        json_schema_extra={"is_config": None},
        description="The commit ID to rollback to. If not provided, the last commit ID is used.",
        ge=0,
        le=18446744073709551615,
        default=None,
        alias="commit-id",
    )


class RollbackOutput(YangBaseModel):
    """Output: None"""

    result: str | None = Field(
        json_schema_extra={"is_config": None}, description="Result of the rollback command.", default=None
    )


class Rollback(BaseModel):
    """RPC: rollback"""

    input: RollbackInput
    output: RollbackOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)


class OperationEnum_2(str, Enum):
    """Enumeration for OperationEnum

    Values:
      * start: Operation to trigger AutoD signaling on TXPDR/MXPDR/Coherent pluggable line port.
      * stop: operation to terminate AutoD signaling on TXPDR/MXPDR/Coherent pluggable line port.
      * get: To retrieve parameters supplied in 'start' and state operation.
    """

    START = "start"
    STOP = "stop"
    GET = "get"


class BandTypeEnum(str, Enum):
    """Enumeration for BandTypeEnum

    Values:
      * standardC-band: Standard C-band (4.85 THz).
      * superC-band: SuperC-band (6.1 THz).
    """

    STANDARDC_BAND = "standardC-band"
    SUPERC_BAND = "superC-band"


class PowerTypeEnum(str, Enum):
    """Enumeration for PowerTypeEnum

    Values:
      * default-tx-power: Power value to use on line side for AutoD (-15dBm).
    """

    DEFAULT_TX_POWER = "default-tx-power"


class StateEnum(str, Enum):
    """Enumeration for StateEnum

    Values:
      * suspended: Auto discovery is not running.
      * signaling: Auto discovery is in progress.
    """

    SUSPENDED = "suspended"
    SIGNALING = "signaling"


class AutodRecordItem(YangBaseModel):
    """List: autod-record"""

    resource: str = Field(
        json_schema_extra={"is_config": None}, description="Resource on which auto-discovery to be operated on."
    )
    band_type: BandTypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="This configuration results in selection of predetermined laser frequency for AutoD.",
        default=BandTypeEnum.SUPERC_BAND,
        alias="band-type",
    )
    power_type: PowerTypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="The power configuration in HW shall be applicable only when autoD Carrier mode is not configured.",
        default=PowerTypeEnum.DEFAULT_TX_POWER,
        alias="power-type",
    )
    timeout: int | None = Field(
        json_schema_extra={"is_config": None},
        description="Specify the timeout in minutes, Port should continue to source AutoD messages without any timeouts, 0 means no timeout.",
        ge=0,
        le=30,
        default=0,
    )
    state: StateEnum | None = Field(
        json_schema_extra={"is_config": None}, description="Auto disocvery state.", default=StateEnum.SUSPENDED
    )


class AutoDiscoveryInput(YangBaseModel):
    """Input: None"""

    operation: OperationEnum_2 = Field(
        json_schema_extra={"is_config": None}, description="Operation for the Auto Discovery RPC."
    )
    resource: str | None = Field(
        json_schema_extra={"is_config": None},
        description="Resource on which auto-discovery to be operated on.",
        default=None,
    )
    band_type: BandTypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="This configuration results in selection of predetermined laser frequency for AutoD.",
        default=BandTypeEnum.SUPERC_BAND,
        alias="band-type",
    )
    power_type: PowerTypeEnum | None = Field(
        json_schema_extra={"is_config": None},
        description="The power configuration in HW shall be applicable only when autoD Carrier mode is not configured.",
        default=PowerTypeEnum.DEFAULT_TX_POWER,
        alias="power-type",
    )
    timeout: int | None = Field(
        json_schema_extra={"is_config": None},
        description="Specify the timeout in minutes, Port should continue to source AutoD messages without any timeouts, 0 means no timeout.",
        ge=0,
        le=30,
        default=0,
    )


class AutoDiscoveryOutput(YangBaseModel):
    """Output: None"""

    autod_record: RestconfList[AutodRecordItem] | None = Field(
        json_schema_extra={"is_config": None}, default=None, alias="autod-record"
    )


class AutoDiscovery(BaseModel):
    """RPC: auto-discovery"""

    input: AutoDiscoveryInput
    output: AutoDiscoveryOutput | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", validate_assignment=True, defer_build=True)
