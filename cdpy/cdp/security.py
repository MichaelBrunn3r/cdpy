from __future__ import annotations

import dataclasses
import enum
from typing import Optional

from deprecated.sphinx import deprecated

from . import network
from ._utils import filter_none


class CertificateId(int):
    """An internal certificate ID value."""

    def __repr__(self):
        return f"CertificateId({super().__repr__()})"


class MixedContentType(enum.Enum):
    """A description of mixed content (HTTP resources on HTTPS pages), as defined by
    https://www.w3.org/TR/mixed-content/#categories
    """

    BLOCKABLE = "blockable"
    OPTIONALLY_BLOCKABLE = "optionally-blockable"
    NONE = "none"


class SecurityState(enum.Enum):
    """The security level of a page or resource."""

    UNKNOWN = "unknown"
    NEUTRAL = "neutral"
    INSECURE = "insecure"
    SECURE = "secure"
    INFO = "info"
    INSECURE_BROKEN = "insecure-broken"


@dataclasses.dataclass
class CertificateSecurityState:
    """Details about the security state of the page certificate.

    Attributes
    ----------
    protocol: str
            Protocol name (e.g. "TLS 1.2" or "QUIC").
    keyExchange: str
            Key Exchange used by the connection, or the empty string if not applicable.
    cipher: str
            Cipher name.
    certificate: list[str]
            Page certificate.
    subjectName: str
            Certificate subject name.
    issuer: str
            Name of the issuing CA.
    validFrom: network.TimeSinceEpoch
            Certificate valid from date.
    validTo: network.TimeSinceEpoch
            Certificate valid to (expiration) date
    certificateHasWeakSignature: bool
            True if the certificate uses a weak signature aglorithm.
    certificateHasSha1Signature: bool
            True if the certificate has a SHA1 signature in the chain.
    modernSSL: bool
            True if modern SSL
    obsoleteSslProtocol: bool
            True if the connection is using an obsolete SSL protocol.
    obsoleteSslKeyExchange: bool
            True if the connection is using an obsolete SSL key exchange.
    obsoleteSslCipher: bool
            True if the connection is using an obsolete SSL cipher.
    obsoleteSslSignature: bool
            True if the connection is using an obsolete SSL signature.
    keyExchangeGroup: Optional[str]
            (EC)DH group used by the connection, if applicable.
    mac: Optional[str]
            TLS MAC. Note that AEAD ciphers do not have separate MACs.
    certificateNetworkError: Optional[str]
            The highest priority network error code, if the certificate has an error.
    """

    protocol: str
    keyExchange: str
    cipher: str
    certificate: list[str]
    subjectName: str
    issuer: str
    validFrom: network.TimeSinceEpoch
    validTo: network.TimeSinceEpoch
    certificateHasWeakSignature: bool
    certificateHasSha1Signature: bool
    modernSSL: bool
    obsoleteSslProtocol: bool
    obsoleteSslKeyExchange: bool
    obsoleteSslCipher: bool
    obsoleteSslSignature: bool
    keyExchangeGroup: Optional[str] = None
    mac: Optional[str] = None
    certificateNetworkError: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> CertificateSecurityState:
        return cls(
            json["protocol"],
            json["keyExchange"],
            json["cipher"],
            json["certificate"],
            json["subjectName"],
            json["issuer"],
            network.TimeSinceEpoch(json["validFrom"]),
            network.TimeSinceEpoch(json["validTo"]),
            json["certificateHasWeakSignature"],
            json["certificateHasSha1Signature"],
            json["modernSSL"],
            json["obsoleteSslProtocol"],
            json["obsoleteSslKeyExchange"],
            json["obsoleteSslCipher"],
            json["obsoleteSslSignature"],
            json.get("keyExchangeGroup"),
            json.get("mac"),
            json.get("certificateNetworkError"),
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "protocol": self.protocol,
                "keyExchange": self.keyExchange,
                "cipher": self.cipher,
                "certificate": self.certificate,
                "subjectName": self.subjectName,
                "issuer": self.issuer,
                "validFrom": float(self.validFrom),
                "validTo": float(self.validTo),
                "certificateHasWeakSignature": self.certificateHasWeakSignature,
                "certificateHasSha1Signature": self.certificateHasSha1Signature,
                "modernSSL": self.modernSSL,
                "obsoleteSslProtocol": self.obsoleteSslProtocol,
                "obsoleteSslKeyExchange": self.obsoleteSslKeyExchange,
                "obsoleteSslCipher": self.obsoleteSslCipher,
                "obsoleteSslSignature": self.obsoleteSslSignature,
                "keyExchangeGroup": self.keyExchangeGroup,
                "mac": self.mac,
                "certificateNetworkError": self.certificateNetworkError,
            }
        )


class SafetyTipStatus(enum.Enum):
    """"""

    BAD_REPUTATION = "badReputation"
    LOOKALIKE = "lookalike"


@dataclasses.dataclass
class SafetyTipInfo:
    """
    Attributes
    ----------
    safetyTipStatus: SafetyTipStatus
            Describes whether the page triggers any safety tips or reputation warnings. Default is unknown.
    safeUrl: Optional[str]
            The URL the safety tip suggested ("Did you mean?"). Only filled in for lookalike matches.
    """

    safetyTipStatus: SafetyTipStatus
    safeUrl: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> SafetyTipInfo:
        return cls(SafetyTipStatus(json["safetyTipStatus"]), json.get("safeUrl"))

    def to_json(self) -> dict:
        return filter_none(
            {"safetyTipStatus": self.safetyTipStatus.value, "safeUrl": self.safeUrl}
        )


@dataclasses.dataclass
class VisibleSecurityState:
    """Security state information about the page.

    Attributes
    ----------
    securityState: SecurityState
            The security level of the page.
    securityStateIssueIds: list[str]
            Array of security state issues ids.
    certificateSecurityState: Optional[CertificateSecurityState]
            Security state details about the page certificate.
    safetyTipInfo: Optional[SafetyTipInfo]
            The type of Safety Tip triggered on the page. Note that this field will be set even if the Safety Tip UI was not actually shown.
    """

    securityState: SecurityState
    securityStateIssueIds: list[str]
    certificateSecurityState: Optional[CertificateSecurityState] = None
    safetyTipInfo: Optional[SafetyTipInfo] = None

    @classmethod
    def from_json(cls, json: dict) -> VisibleSecurityState:
        return cls(
            SecurityState(json["securityState"]),
            json["securityStateIssueIds"],
            CertificateSecurityState.from_json(json["certificateSecurityState"])
            if "certificateSecurityState" in json
            else None,
            SafetyTipInfo.from_json(json["safetyTipInfo"])
            if "safetyTipInfo" in json
            else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "securityState": self.securityState.value,
                "securityStateIssueIds": self.securityStateIssueIds,
                "certificateSecurityState": self.certificateSecurityState.to_json()
                if self.certificateSecurityState
                else None,
                "safetyTipInfo": self.safetyTipInfo.to_json()
                if self.safetyTipInfo
                else None,
            }
        )


@dataclasses.dataclass
class SecurityStateExplanation:
    """An explanation of an factor contributing to the security state.

    Attributes
    ----------
    securityState: SecurityState
            Security state representing the severity of the factor being explained.
    title: str
            Title describing the type of factor.
    summary: str
            Short phrase describing the type of factor.
    description: str
            Full text explanation of the factor.
    mixedContentType: MixedContentType
            The type of mixed content described by the explanation.
    certificate: list[str]
            Page certificate.
    recommendations: Optional[list[str]]
            Recommendations to fix any issues.
    """

    securityState: SecurityState
    title: str
    summary: str
    description: str
    mixedContentType: MixedContentType
    certificate: list[str]
    recommendations: Optional[list[str]] = None

    @classmethod
    def from_json(cls, json: dict) -> SecurityStateExplanation:
        return cls(
            SecurityState(json["securityState"]),
            json["title"],
            json["summary"],
            json["description"],
            MixedContentType(json["mixedContentType"]),
            json["certificate"],
            json.get("recommendations"),
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "securityState": self.securityState.value,
                "title": self.title,
                "summary": self.summary,
                "description": self.description,
                "mixedContentType": self.mixedContentType.value,
                "certificate": self.certificate,
                "recommendations": self.recommendations,
            }
        )


@dataclasses.dataclass
class InsecureContentStatus:
    """Information about insecure content on the page.

    Attributes
    ----------
    ranMixedContent: bool
            Always false.
    displayedMixedContent: bool
            Always false.
    containedMixedForm: bool
            Always false.
    ranContentWithCertErrors: bool
            Always false.
    displayedContentWithCertErrors: bool
            Always false.
    ranInsecureContentStyle: SecurityState
            Always set to unknown.
    displayedInsecureContentStyle: SecurityState
            Always set to unknown.
    """

    ranMixedContent: bool
    displayedMixedContent: bool
    containedMixedForm: bool
    ranContentWithCertErrors: bool
    displayedContentWithCertErrors: bool
    ranInsecureContentStyle: SecurityState
    displayedInsecureContentStyle: SecurityState

    @classmethod
    def from_json(cls, json: dict) -> InsecureContentStatus:
        return cls(
            json["ranMixedContent"],
            json["displayedMixedContent"],
            json["containedMixedForm"],
            json["ranContentWithCertErrors"],
            json["displayedContentWithCertErrors"],
            SecurityState(json["ranInsecureContentStyle"]),
            SecurityState(json["displayedInsecureContentStyle"]),
        )

    def to_json(self) -> dict:
        return {
            "ranMixedContent": self.ranMixedContent,
            "displayedMixedContent": self.displayedMixedContent,
            "containedMixedForm": self.containedMixedForm,
            "ranContentWithCertErrors": self.ranContentWithCertErrors,
            "displayedContentWithCertErrors": self.displayedContentWithCertErrors,
            "ranInsecureContentStyle": self.ranInsecureContentStyle.value,
            "displayedInsecureContentStyle": self.displayedInsecureContentStyle.value,
        }


class CertificateErrorAction(enum.Enum):
    """The action to take when a certificate error occurs. continue will continue processing the
    request and cancel will cancel the request.
    """

    CONTINUE = "continue"
    CANCEL = "cancel"


def disable() -> dict:
    """Disables tracking security state changes."""
    return {"method": "Security.disable", "params": {}}


def enable() -> dict:
    """Enables tracking security state changes."""
    return {"method": "Security.enable", "params": {}}


def set_ignore_certificate_errors(ignore: bool) -> dict:
    """Enable/disable whether all certificate errors should be ignored.

    Parameters
    ----------
    ignore: bool
            If true, all certificate errors will be ignored.

    **Experimental**
    """
    return {
        "method": "Security.setIgnoreCertificateErrors",
        "params": {"ignore": ignore},
    }


@deprecated(version="1.3")
def handle_certificate_error(eventId: int, action: CertificateErrorAction) -> dict:
    """Handles a certificate error that fired a certificateError event.

    Parameters
    ----------
    eventId: int
            The ID of the event.
    action: CertificateErrorAction
            The action to take on the certificate error.
    """
    return {
        "method": "Security.handleCertificateError",
        "params": {"eventId": eventId, "action": action.value},
    }


@deprecated(version="1.3")
def set_override_certificate_errors(override: bool) -> dict:
    """Enable/disable overriding certificate errors. If enabled, all certificate error events need to
    be handled by the DevTools client and should be answered with `handleCertificateError` commands.

    Parameters
    ----------
    override: bool
            If true, certificate errors will be overridden.
    """
    return {
        "method": "Security.setOverrideCertificateErrors",
        "params": {"override": override},
    }


@dataclasses.dataclass
class CertificateError:
    """There is a certificate error. If overriding certificate errors is enabled, then it should be
    handled with the `handleCertificateError` command. Note: this event does not fire if the
    certificate error has been allowed internally. Only one client per target should override
    certificate errors at the same time.

    Attributes
    ----------
    eventId: int
            The ID of the event.
    errorType: str
            The type of the error.
    requestURL: str
            The url that was requested.
    """

    eventId: int
    errorType: str
    requestURL: str

    @classmethod
    def from_json(cls, json: dict) -> CertificateError:
        return cls(json["eventId"], json["errorType"], json["requestURL"])


@dataclasses.dataclass
class VisibleSecurityStateChanged:
    """The security state of the page changed.

    Attributes
    ----------
    visibleSecurityState: VisibleSecurityState
            Security state information about the page.
    """

    visibleSecurityState: VisibleSecurityState

    @classmethod
    def from_json(cls, json: dict) -> VisibleSecurityStateChanged:
        return cls(VisibleSecurityState.from_json(json["visibleSecurityState"]))


@dataclasses.dataclass
class SecurityStateChanged:
    """The security state of the page changed.

    Attributes
    ----------
    securityState: SecurityState
            Security state.
    schemeIsCryptographic: bool
            True if the page was loaded over cryptographic transport such as HTTPS.
    explanations: list[SecurityStateExplanation]
            List of explanations for the security state. If the overall security state is `insecure` or
            `warning`, at least one corresponding explanation should be included.
    insecureContentStatus: InsecureContentStatus
            Information about insecure content on the page.
    summary: Optional[str]
            Overrides user-visible description of the state.
    """

    securityState: SecurityState
    schemeIsCryptographic: bool
    explanations: list[SecurityStateExplanation]
    insecureContentStatus: InsecureContentStatus
    summary: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> SecurityStateChanged:
        return cls(
            SecurityState(json["securityState"]),
            json["schemeIsCryptographic"],
            [SecurityStateExplanation.from_json(e) for e in json["explanations"]],
            InsecureContentStatus.from_json(json["insecureContentStatus"]),
            json.get("summary"),
        )
