from __future__ import annotations

import dataclasses
import enum
from typing import Optional

from . import dom, network, page, runtime
from .common import filter_unset_parameters


@dataclasses.dataclass
class AffectedCookie:
    """Information about a cookie that is affected by an inspector issue.

    Attributes
    ----------
    name: str
            The following three properties uniquely identify a cookie
    path: str
    domain: str
    """

    name: str
    path: str
    domain: str

    @classmethod
    def from_json(cls, json: dict) -> AffectedCookie:
        return cls(json["name"], json["path"], json["domain"])


@dataclasses.dataclass
class AffectedRequest:
    """Information about a request that is affected by an inspector issue.

    Attributes
    ----------
    requestId: network.RequestId
            The unique request id.
    url: Optional[str]
    """

    requestId: network.RequestId
    url: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> AffectedRequest:
        return cls(network.RequestId(json["requestId"]), json.get("url"))


@dataclasses.dataclass
class AffectedFrame:
    """Information about the frame affected by an inspector issue.

    Attributes
    ----------
    frameId: page.FrameId
    """

    frameId: page.FrameId

    @classmethod
    def from_json(cls, json: dict) -> AffectedFrame:
        return cls(page.FrameId(json["frameId"]))


class SameSiteCookieExclusionReason(enum.Enum):
    """"""

    EXCLUDE_SAME_SITE_UNSPECIFIED_TREATED_AS_LAX = (
        "ExcludeSameSiteUnspecifiedTreatedAsLax"
    )
    EXCLUDE_SAME_SITE_NONE_INSECURE = "ExcludeSameSiteNoneInsecure"
    EXCLUDE_SAME_SITE_LAX = "ExcludeSameSiteLax"
    EXCLUDE_SAME_SITE_STRICT = "ExcludeSameSiteStrict"


class SameSiteCookieWarningReason(enum.Enum):
    """"""

    WARN_SAME_SITE_UNSPECIFIED_CROSS_SITE_CONTEXT = (
        "WarnSameSiteUnspecifiedCrossSiteContext"
    )
    WARN_SAME_SITE_NONE_INSECURE = "WarnSameSiteNoneInsecure"
    WARN_SAME_SITE_UNSPECIFIED_LAX_ALLOW_UNSAFE = (
        "WarnSameSiteUnspecifiedLaxAllowUnsafe"
    )
    WARN_SAME_SITE_STRICT_LAX_DOWNGRADE_STRICT = "WarnSameSiteStrictLaxDowngradeStrict"
    WARN_SAME_SITE_STRICT_CROSS_DOWNGRADE_STRICT = (
        "WarnSameSiteStrictCrossDowngradeStrict"
    )
    WARN_SAME_SITE_STRICT_CROSS_DOWNGRADE_LAX = "WarnSameSiteStrictCrossDowngradeLax"
    WARN_SAME_SITE_LAX_CROSS_DOWNGRADE_STRICT = "WarnSameSiteLaxCrossDowngradeStrict"
    WARN_SAME_SITE_LAX_CROSS_DOWNGRADE_LAX = "WarnSameSiteLaxCrossDowngradeLax"


class SameSiteCookieOperation(enum.Enum):
    """"""

    SET_COOKIE = "SetCookie"
    READ_COOKIE = "ReadCookie"


@dataclasses.dataclass
class SameSiteCookieIssueDetails:
    """This information is currently necessary, as the front-end has a difficult
    time finding a specific cookie. With this, we can convey specific error
    information without the cookie.

    Attributes
    ----------
    cookie: AffectedCookie
    cookieWarningReasons: list[SameSiteCookieWarningReason]
    cookieExclusionReasons: list[SameSiteCookieExclusionReason]
    operation: SameSiteCookieOperation
            Optionally identifies the site-for-cookies and the cookie url, which
            may be used by the front-end as additional context.
    siteForCookies: Optional[str]
    cookieUrl: Optional[str]
    request: Optional[AffectedRequest]
    """

    cookie: AffectedCookie
    cookieWarningReasons: list[SameSiteCookieWarningReason]
    cookieExclusionReasons: list[SameSiteCookieExclusionReason]
    operation: SameSiteCookieOperation
    siteForCookies: Optional[str] = None
    cookieUrl: Optional[str] = None
    request: Optional[AffectedRequest] = None

    @classmethod
    def from_json(cls, json: dict) -> SameSiteCookieIssueDetails:
        return cls(
            AffectedCookie.from_json(json["cookie"]),
            [SameSiteCookieWarningReason(x) for x in json["cookieWarningReasons"]],
            [SameSiteCookieExclusionReason(x) for x in json["cookieExclusionReasons"]],
            SameSiteCookieOperation(json["operation"]),
            json.get("siteForCookies"),
            json.get("cookieUrl"),
            AffectedRequest.from_json(json["request"]) if "request" in json else None,
        )


class MixedContentResolutionStatus(enum.Enum):
    """"""

    MIXED_CONTENT_BLOCKED = "MixedContentBlocked"
    MIXED_CONTENT_AUTOMATICALLY_UPGRADED = "MixedContentAutomaticallyUpgraded"
    MIXED_CONTENT_WARNING = "MixedContentWarning"


class MixedContentResourceType(enum.Enum):
    """"""

    AUDIO = "Audio"
    BEACON = "Beacon"
    CSP_REPORT = "CSPReport"
    DOWNLOAD = "Download"
    EVENT_SOURCE = "EventSource"
    FAVICON = "Favicon"
    FONT = "Font"
    FORM = "Form"
    FRAME = "Frame"
    IMAGE = "Image"
    IMPORT = "Import"
    MANIFEST = "Manifest"
    PING = "Ping"
    PLUGIN_DATA = "PluginData"
    PLUGIN_RESOURCE = "PluginResource"
    PREFETCH = "Prefetch"
    RESOURCE = "Resource"
    SCRIPT = "Script"
    SERVICE_WORKER = "ServiceWorker"
    SHARED_WORKER = "SharedWorker"
    STYLESHEET = "Stylesheet"
    TRACK = "Track"
    VIDEO = "Video"
    WORKER = "Worker"
    XML_HTTP_REQUEST = "XMLHttpRequest"
    XSLT = "XSLT"


@dataclasses.dataclass
class MixedContentIssueDetails:
    """
    Attributes
    ----------
    resolutionStatus: MixedContentResolutionStatus
            The way the mixed content issue is being resolved.
    insecureURL: str
            The unsafe http url causing the mixed content issue.
    mainResourceURL: str
            The url responsible for the call to an unsafe url.
    resourceType: Optional[MixedContentResourceType]
            The type of resource causing the mixed content issue (css, js, iframe,
            form,...). Marked as optional because it is mapped to from
            blink::mojom::RequestContextType, which will be replaced
            by network::mojom::RequestDestination
    request: Optional[AffectedRequest]
            The mixed content request.
            Does not always exist (e.g. for unsafe form submission urls).
    frame: Optional[AffectedFrame]
            Optional because not every mixed content issue is necessarily linked to a frame.
    """

    resolutionStatus: MixedContentResolutionStatus
    insecureURL: str
    mainResourceURL: str
    resourceType: Optional[MixedContentResourceType] = None
    request: Optional[AffectedRequest] = None
    frame: Optional[AffectedFrame] = None

    @classmethod
    def from_json(cls, json: dict) -> MixedContentIssueDetails:
        return cls(
            MixedContentResolutionStatus(json["resolutionStatus"]),
            json["insecureURL"],
            json["mainResourceURL"],
            MixedContentResourceType(json["resourceType"])
            if "resourceType" in json
            else None,
            AffectedRequest.from_json(json["request"]) if "request" in json else None,
            AffectedFrame.from_json(json["frame"]) if "frame" in json else None,
        )


class BlockedByResponseReason(enum.Enum):
    """Enum indicating the reason a response has been blocked. These reasons are
    refinements of the net error BLOCKED_BY_RESPONSE.
    """

    COEP_FRAME_RESOURCE_NEEDS_COEP_HEADER = "CoepFrameResourceNeedsCoepHeader"
    COOP_SANDBOXED_I_FRAME_CANNOT_NAVIGATE_TO_COOP_PAGE = (
        "CoopSandboxedIFrameCannotNavigateToCoopPage"
    )
    CORP_NOT_SAME_ORIGIN = "CorpNotSameOrigin"
    CORP_NOT_SAME_ORIGIN_AFTER_DEFAULTED_TO_SAME_ORIGIN_BY_COEP = (
        "CorpNotSameOriginAfterDefaultedToSameOriginByCoep"
    )
    CORP_NOT_SAME_SITE = "CorpNotSameSite"


@dataclasses.dataclass
class BlockedByResponseIssueDetails:
    """Details for a request that has been blocked with the BLOCKED_BY_RESPONSE
    code. Currently only used for COEP/COOP, but may be extended to include
    some CSP errors in the future.

    Attributes
    ----------
    request: AffectedRequest
    reason: BlockedByResponseReason
    parentFrame: Optional[AffectedFrame]
    blockedFrame: Optional[AffectedFrame]
    """

    request: AffectedRequest
    reason: BlockedByResponseReason
    parentFrame: Optional[AffectedFrame] = None
    blockedFrame: Optional[AffectedFrame] = None

    @classmethod
    def from_json(cls, json: dict) -> BlockedByResponseIssueDetails:
        return cls(
            AffectedRequest.from_json(json["request"]),
            BlockedByResponseReason(json["reason"]),
            AffectedFrame.from_json(json["parentFrame"])
            if "parentFrame" in json
            else None,
            AffectedFrame.from_json(json["blockedFrame"])
            if "blockedFrame" in json
            else None,
        )


class HeavyAdResolutionStatus(enum.Enum):
    """"""

    HEAVY_AD_BLOCKED = "HeavyAdBlocked"
    HEAVY_AD_WARNING = "HeavyAdWarning"


class HeavyAdReason(enum.Enum):
    """"""

    NETWORK_TOTAL_LIMIT = "NetworkTotalLimit"
    CPU_TOTAL_LIMIT = "CpuTotalLimit"
    CPU_PEAK_LIMIT = "CpuPeakLimit"


@dataclasses.dataclass
class HeavyAdIssueDetails:
    """
    Attributes
    ----------
    resolution: HeavyAdResolutionStatus
            The resolution status, either blocking the content or warning.
    reason: HeavyAdReason
            The reason the ad was blocked, total network or cpu or peak cpu.
    frame: AffectedFrame
            The frame that was blocked.
    """

    resolution: HeavyAdResolutionStatus
    reason: HeavyAdReason
    frame: AffectedFrame

    @classmethod
    def from_json(cls, json: dict) -> HeavyAdIssueDetails:
        return cls(
            HeavyAdResolutionStatus(json["resolution"]),
            HeavyAdReason(json["reason"]),
            AffectedFrame.from_json(json["frame"]),
        )


class ContentSecurityPolicyViolationType(enum.Enum):
    """"""

    K_INLINE_VIOLATION = "kInlineViolation"
    K_EVAL_VIOLATION = "kEvalViolation"
    K_URL_VIOLATION = "kURLViolation"
    K_TRUSTED_TYPES_SINK_VIOLATION = "kTrustedTypesSinkViolation"
    K_TRUSTED_TYPES_POLICY_VIOLATION = "kTrustedTypesPolicyViolation"


@dataclasses.dataclass
class SourceCodeLocation:
    """
    Attributes
    ----------
    url: str
    lineNumber: int
    columnNumber: int
    scriptId: Optional[runtime.ScriptId]
    """

    url: str
    lineNumber: int
    columnNumber: int
    scriptId: Optional[runtime.ScriptId] = None

    @classmethod
    def from_json(cls, json: dict) -> SourceCodeLocation:
        return cls(
            json["url"],
            json["lineNumber"],
            json["columnNumber"],
            runtime.ScriptId(json["scriptId"]) if "scriptId" in json else None,
        )


@dataclasses.dataclass
class ContentSecurityPolicyIssueDetails:
    """
    Attributes
    ----------
    violatedDirective: str
            Specific directive that is violated, causing the CSP issue.
    isReportOnly: bool
    contentSecurityPolicyViolationType: ContentSecurityPolicyViolationType
    blockedURL: Optional[str]
            The url not included in allowed sources.
    frameAncestor: Optional[AffectedFrame]
    sourceCodeLocation: Optional[SourceCodeLocation]
    violatingNodeId: Optional[dom.BackendNodeId]
    """

    violatedDirective: str
    isReportOnly: bool
    contentSecurityPolicyViolationType: ContentSecurityPolicyViolationType
    blockedURL: Optional[str] = None
    frameAncestor: Optional[AffectedFrame] = None
    sourceCodeLocation: Optional[SourceCodeLocation] = None
    violatingNodeId: Optional[dom.BackendNodeId] = None

    @classmethod
    def from_json(cls, json: dict) -> ContentSecurityPolicyIssueDetails:
        return cls(
            json["violatedDirective"],
            json["isReportOnly"],
            ContentSecurityPolicyViolationType(
                json["contentSecurityPolicyViolationType"]
            ),
            json.get("blockedURL"),
            AffectedFrame.from_json(json["frameAncestor"])
            if "frameAncestor" in json
            else None,
            SourceCodeLocation.from_json(json["sourceCodeLocation"])
            if "sourceCodeLocation" in json
            else None,
            dom.BackendNodeId(json["violatingNodeId"])
            if "violatingNodeId" in json
            else None,
        )


class SharedArrayBufferIssueType(enum.Enum):
    """"""

    TRANSFER_ISSUE = "TransferIssue"
    CREATION_ISSUE = "CreationIssue"


@dataclasses.dataclass
class SharedArrayBufferIssueDetails:
    """Details for a request that has been blocked with the BLOCKED_BY_RESPONSE
    code. Currently only used for COEP/COOP, but may be extended to include
    some CSP errors in the future.

    Attributes
    ----------
    sourceCodeLocation: SourceCodeLocation
    isWarning: bool
    type: SharedArrayBufferIssueType
    """

    sourceCodeLocation: SourceCodeLocation
    isWarning: bool
    type: SharedArrayBufferIssueType

    @classmethod
    def from_json(cls, json: dict) -> SharedArrayBufferIssueDetails:
        return cls(
            SourceCodeLocation.from_json(json["sourceCodeLocation"]),
            json["isWarning"],
            SharedArrayBufferIssueType(json["type"]),
        )


class TwaQualityEnforcementViolationType(enum.Enum):
    """"""

    K_HTTP_ERROR = "kHttpError"
    K_UNAVAILABLE_OFFLINE = "kUnavailableOffline"
    K_DIGITAL_ASSET_LINKS = "kDigitalAssetLinks"


@dataclasses.dataclass
class TrustedWebActivityIssueDetails:
    """
    Attributes
    ----------
    url: str
            The url that triggers the violation.
    violationType: TwaQualityEnforcementViolationType
    httpStatusCode: Optional[int]
    packageName: Optional[str]
            The package name of the Trusted Web Activity client app. This field is
            only used when violation type is kDigitalAssetLinks.
    signature: Optional[str]
            The signature of the Trusted Web Activity client app. This field is only
            used when violation type is kDigitalAssetLinks.
    """

    url: str
    violationType: TwaQualityEnforcementViolationType
    httpStatusCode: Optional[int] = None
    packageName: Optional[str] = None
    signature: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> TrustedWebActivityIssueDetails:
        return cls(
            json["url"],
            TwaQualityEnforcementViolationType(json["violationType"]),
            json.get("httpStatusCode"),
            json.get("packageName"),
            json.get("signature"),
        )


@dataclasses.dataclass
class LowTextContrastIssueDetails:
    """
    Attributes
    ----------
    violatingNodeId: dom.BackendNodeId
    violatingNodeSelector: str
    contrastRatio: float
    thresholdAA: float
    thresholdAAA: float
    fontSize: str
    fontWeight: str
    """

    violatingNodeId: dom.BackendNodeId
    violatingNodeSelector: str
    contrastRatio: float
    thresholdAA: float
    thresholdAAA: float
    fontSize: str
    fontWeight: str

    @classmethod
    def from_json(cls, json: dict) -> LowTextContrastIssueDetails:
        return cls(
            dom.BackendNodeId(json["violatingNodeId"]),
            json["violatingNodeSelector"],
            json["contrastRatio"],
            json["thresholdAA"],
            json["thresholdAAA"],
            json["fontSize"],
            json["fontWeight"],
        )


class InspectorIssueCode(enum.Enum):
    """A unique identifier for the type of issue. Each type may use one of the
    optional fields in InspectorIssueDetails to convey more specific
    information about the kind of issue.
    """

    SAME_SITE_COOKIE_ISSUE = "SameSiteCookieIssue"
    MIXED_CONTENT_ISSUE = "MixedContentIssue"
    BLOCKED_BY_RESPONSE_ISSUE = "BlockedByResponseIssue"
    HEAVY_AD_ISSUE = "HeavyAdIssue"
    CONTENT_SECURITY_POLICY_ISSUE = "ContentSecurityPolicyIssue"
    SHARED_ARRAY_BUFFER_ISSUE = "SharedArrayBufferIssue"
    TRUSTED_WEB_ACTIVITY_ISSUE = "TrustedWebActivityIssue"
    LOW_TEXT_CONTRAST_ISSUE = "LowTextContrastIssue"


@dataclasses.dataclass
class InspectorIssueDetails:
    """This struct holds a list of optional fields with additional information
    specific to the kind of issue. When adding a new issue code, please also
    add a new optional field to this type.

    Attributes
    ----------
    sameSiteCookieIssueDetails: Optional[SameSiteCookieIssueDetails]
    mixedContentIssueDetails: Optional[MixedContentIssueDetails]
    blockedByResponseIssueDetails: Optional[BlockedByResponseIssueDetails]
    heavyAdIssueDetails: Optional[HeavyAdIssueDetails]
    contentSecurityPolicyIssueDetails: Optional[ContentSecurityPolicyIssueDetails]
    sharedArrayBufferIssueDetails: Optional[SharedArrayBufferIssueDetails]
    twaQualityEnforcementDetails: Optional[TrustedWebActivityIssueDetails]
    lowTextContrastIssueDetails: Optional[LowTextContrastIssueDetails]
    """

    sameSiteCookieIssueDetails: Optional[SameSiteCookieIssueDetails] = None
    mixedContentIssueDetails: Optional[MixedContentIssueDetails] = None
    blockedByResponseIssueDetails: Optional[BlockedByResponseIssueDetails] = None
    heavyAdIssueDetails: Optional[HeavyAdIssueDetails] = None
    contentSecurityPolicyIssueDetails: Optional[
        ContentSecurityPolicyIssueDetails
    ] = None
    sharedArrayBufferIssueDetails: Optional[SharedArrayBufferIssueDetails] = None
    twaQualityEnforcementDetails: Optional[TrustedWebActivityIssueDetails] = None
    lowTextContrastIssueDetails: Optional[LowTextContrastIssueDetails] = None

    @classmethod
    def from_json(cls, json: dict) -> InspectorIssueDetails:
        return cls(
            SameSiteCookieIssueDetails.from_json(json["sameSiteCookieIssueDetails"])
            if "sameSiteCookieIssueDetails" in json
            else None,
            MixedContentIssueDetails.from_json(json["mixedContentIssueDetails"])
            if "mixedContentIssueDetails" in json
            else None,
            BlockedByResponseIssueDetails.from_json(
                json["blockedByResponseIssueDetails"]
            )
            if "blockedByResponseIssueDetails" in json
            else None,
            HeavyAdIssueDetails.from_json(json["heavyAdIssueDetails"])
            if "heavyAdIssueDetails" in json
            else None,
            ContentSecurityPolicyIssueDetails.from_json(
                json["contentSecurityPolicyIssueDetails"]
            )
            if "contentSecurityPolicyIssueDetails" in json
            else None,
            SharedArrayBufferIssueDetails.from_json(
                json["sharedArrayBufferIssueDetails"]
            )
            if "sharedArrayBufferIssueDetails" in json
            else None,
            TrustedWebActivityIssueDetails.from_json(
                json["twaQualityEnforcementDetails"]
            )
            if "twaQualityEnforcementDetails" in json
            else None,
            LowTextContrastIssueDetails.from_json(json["lowTextContrastIssueDetails"])
            if "lowTextContrastIssueDetails" in json
            else None,
        )


@dataclasses.dataclass
class InspectorIssue:
    """An inspector issue reported from the back-end.

    Attributes
    ----------
    code: InspectorIssueCode
    details: InspectorIssueDetails
    """

    code: InspectorIssueCode
    details: InspectorIssueDetails

    @classmethod
    def from_json(cls, json: dict) -> InspectorIssue:
        return cls(
            InspectorIssueCode(json["code"]),
            InspectorIssueDetails.from_json(json["details"]),
        )


def get_encoded_response(
    requestId: network.RequestId,
    encoding: str,
    quality: Optional[float] = None,
    sizeOnly: Optional[bool] = None,
):
    """Returns the response body and size if it were re-encoded with the specified settings. Only
    applies to images.

    Parameters
    ----------
    requestId: network.RequestId
            Identifier of the network request to get content for.
    encoding: str
            The encoding to use.
    quality: Optional[float]
            The quality of the encoding (0-1). (defaults to 1)
    sizeOnly: Optional[bool]
            Whether to only return the size information (defaults to false).

    Returns
    -------
    body: Optional[str]
            The encoded body as a base64 string. Omitted if sizeOnly is true. (Encoded as a base64 string when passed over JSON)
    originalSize: int
            Size before re-encoding.
    encodedSize: int
            Size after re-encoding.
    """
    return filter_unset_parameters(
        {
            "method": "Audits.getEncodedResponse",
            "params": {
                "requestId": requestId,
                "encoding": encoding,
                "quality": quality,
                "sizeOnly": sizeOnly,
            },
        }
    )


def disable():
    """Disables issues domain, prevents further issues from being reported to the client."""
    return {"method": "Audits.disable", "params": {}}


def enable():
    """Enables issues domain, sends the issues collected so far to the client by means of the
    `issueAdded` event.
    """
    return {"method": "Audits.enable", "params": {}}


def check_contrast():
    """Runs the contrast check for the target page. Found issues are reported
    using Audits.issueAdded event.
    """
    return {"method": "Audits.checkContrast", "params": {}}
