from __future__ import annotations

import dataclasses
import enum
from typing import Optional

from . import network
from .common import Type, filter_unset_parameters


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
class CertificateSecurityState(Type):
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
    keyExchangeGroup: Optional[str] = None
            (EC)DH group used by the connection, if applicable.
    mac: Optional[str] = None
            TLS MAC. Note that AEAD ciphers do not have separate MACs.
    certificateNetworkError: Optional[str] = None
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


class SafetyTipStatus(enum.Enum):
    """"""

    BAD_REPUTATION = "badReputation"
    LOOKALIKE = "lookalike"


@dataclasses.dataclass
class SafetyTipInfo(Type):
    """
    Attributes
    ----------
    safetyTipStatus: SafetyTipStatus
            Describes whether the page triggers any safety tips or reputation warnings. Default is unknown.
    safeUrl: Optional[str] = None
            The URL the safety tip suggested ("Did you mean?"). Only filled in for lookalike matches.
    """

    safetyTipStatus: SafetyTipStatus
    safeUrl: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> SafetyTipInfo:
        return cls(SafetyTipStatus(json["safetyTipStatus"]), json.get("safeUrl"))


@dataclasses.dataclass
class VisibleSecurityState(Type):
    """Security state information about the page.

    Attributes
    ----------
    securityState: SecurityState
            The security level of the page.
    securityStateIssueIds: list[str]
            Array of security state issues ids.
    certificateSecurityState: Optional[CertificateSecurityState] = None
            Security state details about the page certificate.
    safetyTipInfo: Optional[SafetyTipInfo] = None
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


@dataclasses.dataclass
class SecurityStateExplanation(Type):
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
    recommendations: Optional[list[str]] = None
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


@dataclasses.dataclass
class InsecureContentStatus(Type):
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


class CertificateErrorAction(enum.Enum):
    """The action to take when a certificate error occurs. continue will continue processing the
    request and cancel will cancel the request.
    """

    CONTINUE = "continue"
    CANCEL = "cancel"


def disable():
    """Disables tracking security state changes."""
    return {"method": "Security.disable", "params": {}}


def enable():
    """Enables tracking security state changes."""
    return {"method": "Security.enable", "params": {}}


def set_ignore_certificate_errors(ignore: bool):
    """Enable/disable whether all certificate errors should be ignored.

    **Experimental**

    Parameters
    ----------
    ignore: bool
            If true, all certificate errors will be ignored.
    """
    return {
        "method": "Security.setIgnoreCertificateErrors",
        "params": {"ignore": ignore},
    }


def handle_certificate_error(eventId: int, action: CertificateErrorAction):
    """Handles a certificate error that fired a certificateError event.

    **Deprectated**

    Parameters
    ----------
    eventId: int
            The ID of the event.
    action: CertificateErrorAction
            The action to take on the certificate error.
    """
    return {
        "method": "Security.handleCertificateError",
        "params": {"eventId": eventId, "action": action},
    }


def set_override_certificate_errors(override: bool):
    """Enable/disable overriding certificate errors. If enabled, all certificate error events need to
    be handled by the DevTools client and should be answered with `handleCertificateError` commands.

    **Deprectated**

    Parameters
    ----------
    override: bool
            If true, certificate errors will be overridden.
    """
    return {
        "method": "Security.setOverrideCertificateErrors",
        "params": {"override": override},
    }