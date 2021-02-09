from __future__ import annotations

import dataclasses
import enum
from typing import Optional

from . import debugger, emulation, io, page, runtime, security
from .common import filter_none, filter_unset_parameters


class ResourceType(enum.Enum):
    """Resource type as it was perceived by the rendering engine."""

    DOCUMENT = "Document"
    STYLESHEET = "Stylesheet"
    IMAGE = "Image"
    MEDIA = "Media"
    FONT = "Font"
    SCRIPT = "Script"
    TEXT_TRACK = "TextTrack"
    XHR = "XHR"
    FETCH = "Fetch"
    EVENT_SOURCE = "EventSource"
    WEB_SOCKET = "WebSocket"
    MANIFEST = "Manifest"
    SIGNED_EXCHANGE = "SignedExchange"
    PING = "Ping"
    CSP_VIOLATION_REPORT = "CSPViolationReport"
    PREFLIGHT = "Preflight"
    OTHER = "Other"


class LoaderId(str):
    """Unique loader identifier."""

    def __repr__(self):
        return f"LoaderId({super().__repr__()})"


class RequestId(str):
    """Unique request identifier."""

    def __repr__(self):
        return f"RequestId({super().__repr__()})"


class InterceptionId(str):
    """Unique intercepted request identifier."""

    def __repr__(self):
        return f"InterceptionId({super().__repr__()})"


class ErrorReason(enum.Enum):
    """Network level fetch failure reason."""

    FAILED = "Failed"
    ABORTED = "Aborted"
    TIMED_OUT = "TimedOut"
    ACCESS_DENIED = "AccessDenied"
    CONNECTION_CLOSED = "ConnectionClosed"
    CONNECTION_RESET = "ConnectionReset"
    CONNECTION_REFUSED = "ConnectionRefused"
    CONNECTION_ABORTED = "ConnectionAborted"
    CONNECTION_FAILED = "ConnectionFailed"
    NAME_NOT_RESOLVED = "NameNotResolved"
    INTERNET_DISCONNECTED = "InternetDisconnected"
    ADDRESS_UNREACHABLE = "AddressUnreachable"
    BLOCKED_BY_CLIENT = "BlockedByClient"
    BLOCKED_BY_RESPONSE = "BlockedByResponse"


class TimeSinceEpoch(float):
    """UTC time in seconds, counted from January 1, 1970."""

    def __repr__(self):
        return f"TimeSinceEpoch({super().__repr__()})"


class MonotonicTime(float):
    """Monotonically increasing time in seconds since an arbitrary point in the past."""

    def __repr__(self):
        return f"MonotonicTime({super().__repr__()})"


class Headers(dict):
    """Request / response headers as keys / values of JSON object."""

    def __repr__(self):
        return f"Headers({super().__repr__()})"


class ConnectionType(enum.Enum):
    """The underlying connection technology that the browser is supposedly using."""

    NONE = "none"
    CELLULAR2G = "cellular2g"
    CELLULAR3G = "cellular3g"
    CELLULAR4G = "cellular4g"
    BLUETOOTH = "bluetooth"
    ETHERNET = "ethernet"
    WIFI = "wifi"
    WIMAX = "wimax"
    OTHER = "other"


class CookieSameSite(enum.Enum):
    """Represents the cookie's 'SameSite' status:
    https://tools.ietf.org/html/draft-west-first-party-cookies
    """

    STRICT = "Strict"
    LAX = "Lax"
    NONE = "None"


class CookiePriority(enum.Enum):
    """Represents the cookie's 'Priority' status:
    https://tools.ietf.org/html/draft-west-cookie-priority-00
    """

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


@dataclasses.dataclass
class ResourceTiming:
    """Timing information for the request.

    Attributes
    ----------
    requestTime: float
            Timing's requestTime is a baseline in seconds, while the other numbers are ticks in
            milliseconds relatively to this requestTime.
    proxyStart: float
            Started resolving proxy.
    proxyEnd: float
            Finished resolving proxy.
    dnsStart: float
            Started DNS address resolve.
    dnsEnd: float
            Finished DNS address resolve.
    connectStart: float
            Started connecting to the remote host.
    connectEnd: float
            Connected to the remote host.
    sslStart: float
            Started SSL handshake.
    sslEnd: float
            Finished SSL handshake.
    workerStart: float
            Started running ServiceWorker.
    workerReady: float
            Finished Starting ServiceWorker.
    workerFetchStart: float
            Started fetch event.
    workerRespondWithSettled: float
            Settled fetch event respondWith promise.
    sendStart: float
            Started sending request.
    sendEnd: float
            Finished sending request.
    pushStart: float
            Time the server started pushing request.
    pushEnd: float
            Time the server finished pushing request.
    receiveHeadersEnd: float
            Finished receiving response headers.
    """

    requestTime: float
    proxyStart: float
    proxyEnd: float
    dnsStart: float
    dnsEnd: float
    connectStart: float
    connectEnd: float
    sslStart: float
    sslEnd: float
    workerStart: float
    workerReady: float
    workerFetchStart: float
    workerRespondWithSettled: float
    sendStart: float
    sendEnd: float
    pushStart: float
    pushEnd: float
    receiveHeadersEnd: float

    @classmethod
    def from_json(cls, json: dict) -> ResourceTiming:
        return cls(
            json["requestTime"],
            json["proxyStart"],
            json["proxyEnd"],
            json["dnsStart"],
            json["dnsEnd"],
            json["connectStart"],
            json["connectEnd"],
            json["sslStart"],
            json["sslEnd"],
            json["workerStart"],
            json["workerReady"],
            json["workerFetchStart"],
            json["workerRespondWithSettled"],
            json["sendStart"],
            json["sendEnd"],
            json["pushStart"],
            json["pushEnd"],
            json["receiveHeadersEnd"],
        )

    def to_json(self) -> dict:
        return {
            "requestTime": self.requestTime,
            "proxyStart": self.proxyStart,
            "proxyEnd": self.proxyEnd,
            "dnsStart": self.dnsStart,
            "dnsEnd": self.dnsEnd,
            "connectStart": self.connectStart,
            "connectEnd": self.connectEnd,
            "sslStart": self.sslStart,
            "sslEnd": self.sslEnd,
            "workerStart": self.workerStart,
            "workerReady": self.workerReady,
            "workerFetchStart": self.workerFetchStart,
            "workerRespondWithSettled": self.workerRespondWithSettled,
            "sendStart": self.sendStart,
            "sendEnd": self.sendEnd,
            "pushStart": self.pushStart,
            "pushEnd": self.pushEnd,
            "receiveHeadersEnd": self.receiveHeadersEnd,
        }


class ResourcePriority(enum.Enum):
    """Loading priority of a resource request."""

    VERY_LOW = "VeryLow"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    VERY_HIGH = "VeryHigh"


@dataclasses.dataclass
class PostDataEntry:
    """Post data entry for HTTP request

    Attributes
    ----------
    bytes: Optional[str]
    """

    bytes: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> PostDataEntry:
        return cls(json.get("bytes"))

    def to_json(self) -> dict:
        return filter_none({"bytes": self.bytes})


@dataclasses.dataclass
class Request:
    """HTTP request data.

    Attributes
    ----------
    url: str
            Request URL (without fragment).
    method: str
            HTTP request method.
    headers: Headers
            HTTP request headers.
    initialPriority: ResourcePriority
            Priority of the resource request at the time request is sent.
    referrerPolicy: str
            The referrer policy of the request, as defined in https://www.w3.org/TR/referrer-policy/
    urlFragment: Optional[str]
            Fragment of the requested URL starting with hash, if present.
    postData: Optional[str]
            HTTP POST request data.
    hasPostData: Optional[bool]
            True when the request has POST data. Note that postData might still be omitted when this flag is true when the data is too long.
    postDataEntries: Optional[list[PostDataEntry]]
            Request body elements. This will be converted from base64 to binary
    mixedContentType: Optional[security.MixedContentType]
            The mixed content type of the request.
    isLinkPreload: Optional[bool]
            Whether is loaded via link preload.
    trustTokenParams: Optional[TrustTokenParams]
            Set for requests when the TrustToken API is used. Contains the parameters
            passed by the developer (e.g. via "fetch") as understood by the backend.
    """

    url: str
    method: str
    headers: Headers
    initialPriority: ResourcePriority
    referrerPolicy: str
    urlFragment: Optional[str] = None
    postData: Optional[str] = None
    hasPostData: Optional[bool] = None
    postDataEntries: Optional[list[PostDataEntry]] = None
    mixedContentType: Optional[security.MixedContentType] = None
    isLinkPreload: Optional[bool] = None
    trustTokenParams: Optional[TrustTokenParams] = None

    @classmethod
    def from_json(cls, json: dict) -> Request:
        return cls(
            json["url"],
            json["method"],
            Headers(json["headers"]),
            ResourcePriority(json["initialPriority"]),
            json["referrerPolicy"],
            json.get("urlFragment"),
            json.get("postData"),
            json.get("hasPostData"),
            [PostDataEntry.from_json(p) for p in json["postDataEntries"]]
            if "postDataEntries" in json
            else None,
            security.MixedContentType(json["mixedContentType"])
            if "mixedContentType" in json
            else None,
            json.get("isLinkPreload"),
            TrustTokenParams.from_json(json["trustTokenParams"])
            if "trustTokenParams" in json
            else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "url": self.url,
                "method": self.method,
                "headers": dict(self.headers),
                "initialPriority": self.initialPriority.value,
                "referrerPolicy": self.referrerPolicy,
                "urlFragment": self.urlFragment,
                "postData": self.postData,
                "hasPostData": self.hasPostData,
                "postDataEntries": [p.to_json() for p in self.postDataEntries]
                if self.postDataEntries
                else None,
                "mixedContentType": self.mixedContentType.value
                if self.mixedContentType
                else None,
                "isLinkPreload": self.isLinkPreload,
                "trustTokenParams": self.trustTokenParams.to_json()
                if self.trustTokenParams
                else None,
            }
        )


@dataclasses.dataclass
class SignedCertificateTimestamp:
    """Details of a signed certificate timestamp (SCT).

    Attributes
    ----------
    status: str
            Validation status.
    origin: str
            Origin.
    logDescription: str
            Log name / description.
    logId: str
            Log ID.
    timestamp: TimeSinceEpoch
            Issuance date.
    hashAlgorithm: str
            Hash algorithm.
    signatureAlgorithm: str
            Signature algorithm.
    signatureData: str
            Signature data.
    """

    status: str
    origin: str
    logDescription: str
    logId: str
    timestamp: TimeSinceEpoch
    hashAlgorithm: str
    signatureAlgorithm: str
    signatureData: str

    @classmethod
    def from_json(cls, json: dict) -> SignedCertificateTimestamp:
        return cls(
            json["status"],
            json["origin"],
            json["logDescription"],
            json["logId"],
            TimeSinceEpoch(json["timestamp"]),
            json["hashAlgorithm"],
            json["signatureAlgorithm"],
            json["signatureData"],
        )

    def to_json(self) -> dict:
        return {
            "status": self.status,
            "origin": self.origin,
            "logDescription": self.logDescription,
            "logId": self.logId,
            "timestamp": float(self.timestamp),
            "hashAlgorithm": self.hashAlgorithm,
            "signatureAlgorithm": self.signatureAlgorithm,
            "signatureData": self.signatureData,
        }


@dataclasses.dataclass
class SecurityDetails:
    """Security details about a request.

    Attributes
    ----------
    protocol: str
            Protocol name (e.g. "TLS 1.2" or "QUIC").
    keyExchange: str
            Key Exchange used by the connection, or the empty string if not applicable.
    cipher: str
            Cipher name.
    certificateId: security.CertificateId
            Certificate ID value.
    subjectName: str
            Certificate subject name.
    sanList: list[str]
            Subject Alternative Name (SAN) DNS names and IP addresses.
    issuer: str
            Name of the issuing CA.
    validFrom: TimeSinceEpoch
            Certificate valid from date.
    validTo: TimeSinceEpoch
            Certificate valid to (expiration) date
    signedCertificateTimestampList: list[SignedCertificateTimestamp]
            List of signed certificate timestamps (SCTs).
    certificateTransparencyCompliance: CertificateTransparencyCompliance
            Whether the request complied with Certificate Transparency policy
    keyExchangeGroup: Optional[str]
            (EC)DH group used by the connection, if applicable.
    mac: Optional[str]
            TLS MAC. Note that AEAD ciphers do not have separate MACs.
    """

    protocol: str
    keyExchange: str
    cipher: str
    certificateId: security.CertificateId
    subjectName: str
    sanList: list[str]
    issuer: str
    validFrom: TimeSinceEpoch
    validTo: TimeSinceEpoch
    signedCertificateTimestampList: list[SignedCertificateTimestamp]
    certificateTransparencyCompliance: CertificateTransparencyCompliance
    keyExchangeGroup: Optional[str] = None
    mac: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> SecurityDetails:
        return cls(
            json["protocol"],
            json["keyExchange"],
            json["cipher"],
            security.CertificateId(json["certificateId"]),
            json["subjectName"],
            json["sanList"],
            json["issuer"],
            TimeSinceEpoch(json["validFrom"]),
            TimeSinceEpoch(json["validTo"]),
            [
                SignedCertificateTimestamp.from_json(s)
                for s in json["signedCertificateTimestampList"]
            ],
            CertificateTransparencyCompliance(
                json["certificateTransparencyCompliance"]
            ),
            json.get("keyExchangeGroup"),
            json.get("mac"),
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "protocol": self.protocol,
                "keyExchange": self.keyExchange,
                "cipher": self.cipher,
                "certificateId": int(self.certificateId),
                "subjectName": self.subjectName,
                "sanList": self.sanList,
                "issuer": self.issuer,
                "validFrom": float(self.validFrom),
                "validTo": float(self.validTo),
                "signedCertificateTimestampList": [
                    s.to_json() for s in self.signedCertificateTimestampList
                ],
                "certificateTransparencyCompliance": self.certificateTransparencyCompliance.value,
                "keyExchangeGroup": self.keyExchangeGroup,
                "mac": self.mac,
            }
        )


class CertificateTransparencyCompliance(enum.Enum):
    """Whether the request complied with Certificate Transparency policy."""

    UNKNOWN = "unknown"
    NOT_COMPLIANT = "not-compliant"
    COMPLIANT = "compliant"


class BlockedReason(enum.Enum):
    """The reason why request was blocked."""

    OTHER = "other"
    CSP = "csp"
    MIXED_CONTENT = "mixed-content"
    ORIGIN = "origin"
    INSPECTOR = "inspector"
    SUBRESOURCE_FILTER = "subresource-filter"
    CONTENT_TYPE = "content-type"
    COLLAPSED_BY_CLIENT = "collapsed-by-client"
    COEP_FRAME_RESOURCE_NEEDS_COEP_HEADER = "coep-frame-resource-needs-coep-header"
    COOP_SANDBOXED_IFRAME_CANNOT_NAVIGATE_TO_COOP_PAGE = (
        "coop-sandboxed-iframe-cannot-navigate-to-coop-page"
    )
    CORP_NOT_SAME_ORIGIN = "corp-not-same-origin"
    CORP_NOT_SAME_ORIGIN_AFTER_DEFAULTED_TO_SAME_ORIGIN_BY_COEP = (
        "corp-not-same-origin-after-defaulted-to-same-origin-by-coep"
    )
    CORP_NOT_SAME_SITE = "corp-not-same-site"


class CorsError(enum.Enum):
    """The reason why request was blocked."""

    DISALLOWED_BY_MODE = "DisallowedByMode"
    INVALID_RESPONSE = "InvalidResponse"
    WILDCARD_ORIGIN_NOT_ALLOWED = "WildcardOriginNotAllowed"
    MISSING_ALLOW_ORIGIN_HEADER = "MissingAllowOriginHeader"
    MULTIPLE_ALLOW_ORIGIN_VALUES = "MultipleAllowOriginValues"
    INVALID_ALLOW_ORIGIN_VALUE = "InvalidAllowOriginValue"
    ALLOW_ORIGIN_MISMATCH = "AllowOriginMismatch"
    INVALID_ALLOW_CREDENTIALS = "InvalidAllowCredentials"
    CORS_DISABLED_SCHEME = "CorsDisabledScheme"
    PREFLIGHT_INVALID_STATUS = "PreflightInvalidStatus"
    PREFLIGHT_DISALLOWED_REDIRECT = "PreflightDisallowedRedirect"
    PREFLIGHT_WILDCARD_ORIGIN_NOT_ALLOWED = "PreflightWildcardOriginNotAllowed"
    PREFLIGHT_MISSING_ALLOW_ORIGIN_HEADER = "PreflightMissingAllowOriginHeader"
    PREFLIGHT_MULTIPLE_ALLOW_ORIGIN_VALUES = "PreflightMultipleAllowOriginValues"
    PREFLIGHT_INVALID_ALLOW_ORIGIN_VALUE = "PreflightInvalidAllowOriginValue"
    PREFLIGHT_ALLOW_ORIGIN_MISMATCH = "PreflightAllowOriginMismatch"
    PREFLIGHT_INVALID_ALLOW_CREDENTIALS = "PreflightInvalidAllowCredentials"
    PREFLIGHT_MISSING_ALLOW_EXTERNAL = "PreflightMissingAllowExternal"
    PREFLIGHT_INVALID_ALLOW_EXTERNAL = "PreflightInvalidAllowExternal"
    INVALID_ALLOW_METHODS_PREFLIGHT_RESPONSE = "InvalidAllowMethodsPreflightResponse"
    INVALID_ALLOW_HEADERS_PREFLIGHT_RESPONSE = "InvalidAllowHeadersPreflightResponse"
    METHOD_DISALLOWED_BY_PREFLIGHT_RESPONSE = "MethodDisallowedByPreflightResponse"
    HEADER_DISALLOWED_BY_PREFLIGHT_RESPONSE = "HeaderDisallowedByPreflightResponse"
    REDIRECT_CONTAINS_CREDENTIALS = "RedirectContainsCredentials"
    INSECURE_PRIVATE_NETWORK = "InsecurePrivateNetwork"


@dataclasses.dataclass
class CorsErrorStatus:
    """
    Attributes
    ----------
    corsError: CorsError
    failedParameter: str
    """

    corsError: CorsError
    failedParameter: str

    @classmethod
    def from_json(cls, json: dict) -> CorsErrorStatus:
        return cls(CorsError(json["corsError"]), json["failedParameter"])

    def to_json(self) -> dict:
        return {
            "corsError": self.corsError.value,
            "failedParameter": self.failedParameter,
        }


class ServiceWorkerResponseSource(enum.Enum):
    """Source of serviceworker response."""

    CACHE_STORAGE = "cache-storage"
    HTTP_CACHE = "http-cache"
    FALLBACK_CODE = "fallback-code"
    NETWORK = "network"


@dataclasses.dataclass
class TrustTokenParams:
    """Determines what type of Trust Token operation is executed and
    depending on the type, some additional parameters. The values
    are specified in third_party/blink/renderer/core/fetch/trust_token.idl.

    Attributes
    ----------
    type: TrustTokenOperationType
    refreshPolicy: str
            Only set for "token-redemption" type and determine whether
            to request a fresh SRR or use a still valid cached SRR.
    issuers: Optional[list[str]]
            Origins of issuers from whom to request tokens or redemption
            records.
    """

    type: TrustTokenOperationType
    refreshPolicy: str
    issuers: Optional[list[str]] = None

    @classmethod
    def from_json(cls, json: dict) -> TrustTokenParams:
        return cls(
            TrustTokenOperationType(json["type"]),
            json["refreshPolicy"],
            json.get("issuers"),
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "type": self.type.value,
                "refreshPolicy": self.refreshPolicy,
                "issuers": self.issuers,
            }
        )


class TrustTokenOperationType(enum.Enum):
    """"""

    ISSUANCE = "Issuance"
    REDEMPTION = "Redemption"
    SIGNING = "Signing"


@dataclasses.dataclass
class Response:
    """HTTP response data.

    Attributes
    ----------
    url: str
            Response URL. This URL can be different from CachedResource.url in case of redirect.
    status: int
            HTTP response status code.
    statusText: str
            HTTP response status text.
    headers: Headers
            HTTP response headers.
    mimeType: str
            Resource mimeType as determined by the browser.
    connectionReused: bool
            Specifies whether physical connection was actually reused for this request.
    connectionId: float
            Physical connection id that was actually used for this request.
    encodedDataLength: float
            Total number of bytes received for this request so far.
    securityState: security.SecurityState
            Security state of the request resource.
    headersText: Optional[str]
            HTTP response headers text.
    requestHeaders: Optional[Headers]
            Refined HTTP request headers that were actually transmitted over the network.
    requestHeadersText: Optional[str]
            HTTP request headers text.
    remoteIPAddress: Optional[str]
            Remote IP address.
    remotePort: Optional[int]
            Remote port.
    fromDiskCache: Optional[bool]
            Specifies that the request was served from the disk cache.
    fromServiceWorker: Optional[bool]
            Specifies that the request was served from the ServiceWorker.
    fromPrefetchCache: Optional[bool]
            Specifies that the request was served from the prefetch cache.
    timing: Optional[ResourceTiming]
            Timing information for the given request.
    serviceWorkerResponseSource: Optional[ServiceWorkerResponseSource]
            Response source of response from ServiceWorker.
    responseTime: Optional[TimeSinceEpoch]
            The time at which the returned response was generated.
    cacheStorageCacheName: Optional[str]
            Cache Storage Cache Name.
    protocol: Optional[str]
            Protocol used to fetch this request.
    securityDetails: Optional[SecurityDetails]
            Security details for the request.
    """

    url: str
    status: int
    statusText: str
    headers: Headers
    mimeType: str
    connectionReused: bool
    connectionId: float
    encodedDataLength: float
    securityState: security.SecurityState
    headersText: Optional[str] = None
    requestHeaders: Optional[Headers] = None
    requestHeadersText: Optional[str] = None
    remoteIPAddress: Optional[str] = None
    remotePort: Optional[int] = None
    fromDiskCache: Optional[bool] = None
    fromServiceWorker: Optional[bool] = None
    fromPrefetchCache: Optional[bool] = None
    timing: Optional[ResourceTiming] = None
    serviceWorkerResponseSource: Optional[ServiceWorkerResponseSource] = None
    responseTime: Optional[TimeSinceEpoch] = None
    cacheStorageCacheName: Optional[str] = None
    protocol: Optional[str] = None
    securityDetails: Optional[SecurityDetails] = None

    @classmethod
    def from_json(cls, json: dict) -> Response:
        return cls(
            json["url"],
            json["status"],
            json["statusText"],
            Headers(json["headers"]),
            json["mimeType"],
            json["connectionReused"],
            json["connectionId"],
            json["encodedDataLength"],
            security.SecurityState(json["securityState"]),
            json.get("headersText"),
            Headers(json["requestHeaders"]) if "requestHeaders" in json else None,
            json.get("requestHeadersText"),
            json.get("remoteIPAddress"),
            json.get("remotePort"),
            json.get("fromDiskCache"),
            json.get("fromServiceWorker"),
            json.get("fromPrefetchCache"),
            ResourceTiming.from_json(json["timing"]) if "timing" in json else None,
            ServiceWorkerResponseSource(json["serviceWorkerResponseSource"])
            if "serviceWorkerResponseSource" in json
            else None,
            TimeSinceEpoch(json["responseTime"]) if "responseTime" in json else None,
            json.get("cacheStorageCacheName"),
            json.get("protocol"),
            SecurityDetails.from_json(json["securityDetails"])
            if "securityDetails" in json
            else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "url": self.url,
                "status": self.status,
                "statusText": self.statusText,
                "headers": dict(self.headers),
                "mimeType": self.mimeType,
                "connectionReused": self.connectionReused,
                "connectionId": self.connectionId,
                "encodedDataLength": self.encodedDataLength,
                "securityState": self.securityState.value,
                "headersText": self.headersText,
                "requestHeaders": dict(self.requestHeaders)
                if self.requestHeaders
                else None,
                "requestHeadersText": self.requestHeadersText,
                "remoteIPAddress": self.remoteIPAddress,
                "remotePort": self.remotePort,
                "fromDiskCache": self.fromDiskCache,
                "fromServiceWorker": self.fromServiceWorker,
                "fromPrefetchCache": self.fromPrefetchCache,
                "timing": self.timing.to_json() if self.timing else None,
                "serviceWorkerResponseSource": self.serviceWorkerResponseSource.value
                if self.serviceWorkerResponseSource
                else None,
                "responseTime": float(self.responseTime) if self.responseTime else None,
                "cacheStorageCacheName": self.cacheStorageCacheName,
                "protocol": self.protocol,
                "securityDetails": self.securityDetails.to_json()
                if self.securityDetails
                else None,
            }
        )


@dataclasses.dataclass
class WebSocketRequest:
    """WebSocket request data.

    Attributes
    ----------
    headers: Headers
            HTTP request headers.
    """

    headers: Headers

    @classmethod
    def from_json(cls, json: dict) -> WebSocketRequest:
        return cls(Headers(json["headers"]))

    def to_json(self) -> dict:
        return {"headers": dict(self.headers)}


@dataclasses.dataclass
class WebSocketResponse:
    """WebSocket response data.

    Attributes
    ----------
    status: int
            HTTP response status code.
    statusText: str
            HTTP response status text.
    headers: Headers
            HTTP response headers.
    headersText: Optional[str]
            HTTP response headers text.
    requestHeaders: Optional[Headers]
            HTTP request headers.
    requestHeadersText: Optional[str]
            HTTP request headers text.
    """

    status: int
    statusText: str
    headers: Headers
    headersText: Optional[str] = None
    requestHeaders: Optional[Headers] = None
    requestHeadersText: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> WebSocketResponse:
        return cls(
            json["status"],
            json["statusText"],
            Headers(json["headers"]),
            json.get("headersText"),
            Headers(json["requestHeaders"]) if "requestHeaders" in json else None,
            json.get("requestHeadersText"),
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "status": self.status,
                "statusText": self.statusText,
                "headers": dict(self.headers),
                "headersText": self.headersText,
                "requestHeaders": dict(self.requestHeaders)
                if self.requestHeaders
                else None,
                "requestHeadersText": self.requestHeadersText,
            }
        )


@dataclasses.dataclass
class WebSocketFrame:
    """WebSocket message data. This represents an entire WebSocket message, not just a fragmented frame as the name suggests.

    Attributes
    ----------
    opcode: float
            WebSocket message opcode.
    mask: bool
            WebSocket message mask.
    payloadData: str
            WebSocket message payload data.
            If the opcode is 1, this is a text message and payloadData is a UTF-8 string.
            If the opcode isn't 1, then payloadData is a base64 encoded string representing binary data.
    """

    opcode: float
    mask: bool
    payloadData: str

    @classmethod
    def from_json(cls, json: dict) -> WebSocketFrame:
        return cls(json["opcode"], json["mask"], json["payloadData"])

    def to_json(self) -> dict:
        return {
            "opcode": self.opcode,
            "mask": self.mask,
            "payloadData": self.payloadData,
        }


@dataclasses.dataclass
class CachedResource:
    """Information about the cached resource.

    Attributes
    ----------
    url: str
            Resource URL. This is the url of the original network request.
    type: ResourceType
            Type of this resource.
    bodySize: float
            Cached response body size.
    response: Optional[Response]
            Cached response data.
    """

    url: str
    type: ResourceType
    bodySize: float
    response: Optional[Response] = None

    @classmethod
    def from_json(cls, json: dict) -> CachedResource:
        return cls(
            json["url"],
            ResourceType(json["type"]),
            json["bodySize"],
            Response.from_json(json["response"]) if "response" in json else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "url": self.url,
                "type": self.type.value,
                "bodySize": self.bodySize,
                "response": self.response.to_json() if self.response else None,
            }
        )


@dataclasses.dataclass
class Initiator:
    """Information about the request initiator.

    Attributes
    ----------
    type: str
            Type of this initiator.
    stack: Optional[runtime.StackTrace]
            Initiator JavaScript stack trace, set for Script only.
    url: Optional[str]
            Initiator URL, set for Parser type or for Script type (when script is importing module) or for SignedExchange type.
    lineNumber: Optional[float]
            Initiator line number, set for Parser type or for Script type (when script is importing
            module) (0-based).
    columnNumber: Optional[float]
            Initiator column number, set for Parser type or for Script type (when script is importing
            module) (0-based).
    requestId: Optional[RequestId]
            Set if another request triggered this request (e.g. preflight).
    """

    type: str
    stack: Optional[runtime.StackTrace] = None
    url: Optional[str] = None
    lineNumber: Optional[float] = None
    columnNumber: Optional[float] = None
    requestId: Optional[RequestId] = None

    @classmethod
    def from_json(cls, json: dict) -> Initiator:
        return cls(
            json["type"],
            runtime.StackTrace.from_json(json["stack"]) if "stack" in json else None,
            json.get("url"),
            json.get("lineNumber"),
            json.get("columnNumber"),
            RequestId(json["requestId"]) if "requestId" in json else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "type": self.type,
                "stack": self.stack.to_json() if self.stack else None,
                "url": self.url,
                "lineNumber": self.lineNumber,
                "columnNumber": self.columnNumber,
                "requestId": str(self.requestId) if self.requestId else None,
            }
        )


@dataclasses.dataclass
class Cookie:
    """Cookie object

    Attributes
    ----------
    name: str
            Cookie name.
    value: str
            Cookie value.
    domain: str
            Cookie domain.
    path: str
            Cookie path.
    expires: float
            Cookie expiration date as the number of seconds since the UNIX epoch.
    size: int
            Cookie size.
    httpOnly: bool
            True if cookie is http-only.
    secure: bool
            True if cookie is secure.
    session: bool
            True in case of session cookie.
    priority: CookiePriority
            Cookie Priority
    sameParty: bool
            True if cookie is SameParty.
    sameSite: Optional[CookieSameSite]
            Cookie SameSite type.
    """

    name: str
    value: str
    domain: str
    path: str
    expires: float
    size: int
    httpOnly: bool
    secure: bool
    session: bool
    priority: CookiePriority
    sameParty: bool
    sameSite: Optional[CookieSameSite] = None

    @classmethod
    def from_json(cls, json: dict) -> Cookie:
        return cls(
            json["name"],
            json["value"],
            json["domain"],
            json["path"],
            json["expires"],
            json["size"],
            json["httpOnly"],
            json["secure"],
            json["session"],
            CookiePriority(json["priority"]),
            json["sameParty"],
            CookieSameSite(json["sameSite"]) if "sameSite" in json else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "name": self.name,
                "value": self.value,
                "domain": self.domain,
                "path": self.path,
                "expires": self.expires,
                "size": self.size,
                "httpOnly": self.httpOnly,
                "secure": self.secure,
                "session": self.session,
                "priority": self.priority.value,
                "sameParty": self.sameParty,
                "sameSite": self.sameSite.value if self.sameSite else None,
            }
        )


class SetCookieBlockedReason(enum.Enum):
    """Types of reasons why a cookie may not be stored from a response."""

    SECURE_ONLY = "SecureOnly"
    SAME_SITE_STRICT = "SameSiteStrict"
    SAME_SITE_LAX = "SameSiteLax"
    SAME_SITE_UNSPECIFIED_TREATED_AS_LAX = "SameSiteUnspecifiedTreatedAsLax"
    SAME_SITE_NONE_INSECURE = "SameSiteNoneInsecure"
    USER_PREFERENCES = "UserPreferences"
    SYNTAX_ERROR = "SyntaxError"
    SCHEME_NOT_SUPPORTED = "SchemeNotSupported"
    OVERWRITE_SECURE = "OverwriteSecure"
    INVALID_DOMAIN = "InvalidDomain"
    INVALID_PREFIX = "InvalidPrefix"
    UNKNOWN_ERROR = "UnknownError"
    SCHEMEFUL_SAME_SITE_STRICT = "SchemefulSameSiteStrict"
    SCHEMEFUL_SAME_SITE_LAX = "SchemefulSameSiteLax"
    SCHEMEFUL_SAME_SITE_UNSPECIFIED_TREATED_AS_LAX = (
        "SchemefulSameSiteUnspecifiedTreatedAsLax"
    )
    SAME_PARTY_FROM_CROSS_PARTY_CONTEXT = "SamePartyFromCrossPartyContext"
    SAME_PARTY_CONFLICTS_WITH_OTHER_ATTRIBUTES = "SamePartyConflictsWithOtherAttributes"


class CookieBlockedReason(enum.Enum):
    """Types of reasons why a cookie may not be sent with a request."""

    SECURE_ONLY = "SecureOnly"
    NOT_ON_PATH = "NotOnPath"
    DOMAIN_MISMATCH = "DomainMismatch"
    SAME_SITE_STRICT = "SameSiteStrict"
    SAME_SITE_LAX = "SameSiteLax"
    SAME_SITE_UNSPECIFIED_TREATED_AS_LAX = "SameSiteUnspecifiedTreatedAsLax"
    SAME_SITE_NONE_INSECURE = "SameSiteNoneInsecure"
    USER_PREFERENCES = "UserPreferences"
    UNKNOWN_ERROR = "UnknownError"
    SCHEMEFUL_SAME_SITE_STRICT = "SchemefulSameSiteStrict"
    SCHEMEFUL_SAME_SITE_LAX = "SchemefulSameSiteLax"
    SCHEMEFUL_SAME_SITE_UNSPECIFIED_TREATED_AS_LAX = (
        "SchemefulSameSiteUnspecifiedTreatedAsLax"
    )
    SAME_PARTY_FROM_CROSS_PARTY_CONTEXT = "SamePartyFromCrossPartyContext"


@dataclasses.dataclass
class BlockedSetCookieWithReason:
    """A cookie which was not stored from a response with the corresponding reason.

    Attributes
    ----------
    blockedReasons: list[SetCookieBlockedReason]
            The reason(s) this cookie was blocked.
    cookieLine: str
            The string representing this individual cookie as it would appear in the header.
            This is not the entire "cookie" or "set-cookie" header which could have multiple cookies.
    cookie: Optional[Cookie]
            The cookie object which represents the cookie which was not stored. It is optional because
            sometimes complete cookie information is not available, such as in the case of parsing
            errors.
    """

    blockedReasons: list[SetCookieBlockedReason]
    cookieLine: str
    cookie: Optional[Cookie] = None

    @classmethod
    def from_json(cls, json: dict) -> BlockedSetCookieWithReason:
        return cls(
            [SetCookieBlockedReason(b) for b in json["blockedReasons"]],
            json["cookieLine"],
            Cookie.from_json(json["cookie"]) if "cookie" in json else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "blockedReasons": [b.value for b in self.blockedReasons],
                "cookieLine": self.cookieLine,
                "cookie": self.cookie.to_json() if self.cookie else None,
            }
        )


@dataclasses.dataclass
class BlockedCookieWithReason:
    """A cookie with was not sent with a request with the corresponding reason.

    Attributes
    ----------
    blockedReasons: list[CookieBlockedReason]
            The reason(s) the cookie was blocked.
    cookie: Cookie
            The cookie object representing the cookie which was not sent.
    """

    blockedReasons: list[CookieBlockedReason]
    cookie: Cookie

    @classmethod
    def from_json(cls, json: dict) -> BlockedCookieWithReason:
        return cls(
            [CookieBlockedReason(b) for b in json["blockedReasons"]],
            Cookie.from_json(json["cookie"]),
        )

    def to_json(self) -> dict:
        return {
            "blockedReasons": [b.value for b in self.blockedReasons],
            "cookie": self.cookie.to_json(),
        }


@dataclasses.dataclass
class CookieParam:
    """Cookie parameter object

    Attributes
    ----------
    name: str
            Cookie name.
    value: str
            Cookie value.
    url: Optional[str]
            The request-URI to associate with the setting of the cookie. This value can affect the
            default domain and path values of the created cookie.
    domain: Optional[str]
            Cookie domain.
    path: Optional[str]
            Cookie path.
    secure: Optional[bool]
            True if cookie is secure.
    httpOnly: Optional[bool]
            True if cookie is http-only.
    sameSite: Optional[CookieSameSite]
            Cookie SameSite type.
    expires: Optional[TimeSinceEpoch]
            Cookie expiration date, session cookie if not set
    priority: Optional[CookiePriority]
            Cookie Priority.
    """

    name: str
    value: str
    url: Optional[str] = None
    domain: Optional[str] = None
    path: Optional[str] = None
    secure: Optional[bool] = None
    httpOnly: Optional[bool] = None
    sameSite: Optional[CookieSameSite] = None
    expires: Optional[TimeSinceEpoch] = None
    priority: Optional[CookiePriority] = None

    @classmethod
    def from_json(cls, json: dict) -> CookieParam:
        return cls(
            json["name"],
            json["value"],
            json.get("url"),
            json.get("domain"),
            json.get("path"),
            json.get("secure"),
            json.get("httpOnly"),
            CookieSameSite(json["sameSite"]) if "sameSite" in json else None,
            TimeSinceEpoch(json["expires"]) if "expires" in json else None,
            CookiePriority(json["priority"]) if "priority" in json else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "name": self.name,
                "value": self.value,
                "url": self.url,
                "domain": self.domain,
                "path": self.path,
                "secure": self.secure,
                "httpOnly": self.httpOnly,
                "sameSite": self.sameSite.value if self.sameSite else None,
                "expires": float(self.expires) if self.expires else None,
                "priority": self.priority.value if self.priority else None,
            }
        )


@dataclasses.dataclass
class AuthChallenge:
    """Authorization challenge for HTTP status code 401 or 407.

    Attributes
    ----------
    origin: str
            Origin of the challenger.
    scheme: str
            The authentication scheme used, such as basic or digest
    realm: str
            The realm of the challenge. May be empty.
    source: Optional[str]
            Source of the authentication challenge.
    """

    origin: str
    scheme: str
    realm: str
    source: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> AuthChallenge:
        return cls(json["origin"], json["scheme"], json["realm"], json.get("source"))

    def to_json(self) -> dict:
        return filter_none(
            {
                "origin": self.origin,
                "scheme": self.scheme,
                "realm": self.realm,
                "source": self.source,
            }
        )


@dataclasses.dataclass
class AuthChallengeResponse:
    """Response to an AuthChallenge.

    Attributes
    ----------
    response: str
            The decision on what to do in response to the authorization challenge.  Default means
            deferring to the default behavior of the net stack, which will likely either the Cancel
            authentication or display a popup dialog box.
    username: Optional[str]
            The username to provide, possibly empty. Should only be set if response is
            ProvideCredentials.
    password: Optional[str]
            The password to provide, possibly empty. Should only be set if response is
            ProvideCredentials.
    """

    response: str
    username: Optional[str] = None
    password: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> AuthChallengeResponse:
        return cls(json["response"], json.get("username"), json.get("password"))

    def to_json(self) -> dict:
        return filter_none(
            {
                "response": self.response,
                "username": self.username,
                "password": self.password,
            }
        )


class InterceptionStage(enum.Enum):
    """Stages of the interception to begin intercepting. Request will intercept before the request is
    sent. Response will intercept after the response is received.
    """

    REQUEST = "Request"
    HEADERS_RECEIVED = "HeadersReceived"


@dataclasses.dataclass
class RequestPattern:
    """Request pattern for interception.

    Attributes
    ----------
    urlPattern: Optional[str]
            Wildcards ('*' -> zero or more, '?' -> exactly one) are allowed. Escape character is
            backslash. Omitting is equivalent to "*".
    resourceType: Optional[ResourceType]
            If set, only requests for matching resource types will be intercepted.
    interceptionStage: Optional[InterceptionStage]
            Stage at wich to begin intercepting requests. Default is Request.
    """

    urlPattern: Optional[str] = None
    resourceType: Optional[ResourceType] = None
    interceptionStage: Optional[InterceptionStage] = None

    @classmethod
    def from_json(cls, json: dict) -> RequestPattern:
        return cls(
            json.get("urlPattern"),
            ResourceType(json["resourceType"]) if "resourceType" in json else None,
            InterceptionStage(json["interceptionStage"])
            if "interceptionStage" in json
            else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "urlPattern": self.urlPattern,
                "resourceType": self.resourceType.value if self.resourceType else None,
                "interceptionStage": self.interceptionStage.value
                if self.interceptionStage
                else None,
            }
        )


@dataclasses.dataclass
class SignedExchangeSignature:
    """Information about a signed exchange signature.
    https://wicg.github.io/webpackage/draft-yasskin-httpbis-origin-signed-exchanges-impl.html#rfc.section.3.1

    Attributes
    ----------
    label: str
            Signed exchange signature label.
    signature: str
            The hex string of signed exchange signature.
    integrity: str
            Signed exchange signature integrity.
    validityUrl: str
            Signed exchange signature validity Url.
    date: int
            Signed exchange signature date.
    expires: int
            Signed exchange signature expires.
    certUrl: Optional[str]
            Signed exchange signature cert Url.
    certSha256: Optional[str]
            The hex string of signed exchange signature cert sha256.
    certificates: Optional[list[str]]
            The encoded certificates.
    """

    label: str
    signature: str
    integrity: str
    validityUrl: str
    date: int
    expires: int
    certUrl: Optional[str] = None
    certSha256: Optional[str] = None
    certificates: Optional[list[str]] = None

    @classmethod
    def from_json(cls, json: dict) -> SignedExchangeSignature:
        return cls(
            json["label"],
            json["signature"],
            json["integrity"],
            json["validityUrl"],
            json["date"],
            json["expires"],
            json.get("certUrl"),
            json.get("certSha256"),
            json.get("certificates"),
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "label": self.label,
                "signature": self.signature,
                "integrity": self.integrity,
                "validityUrl": self.validityUrl,
                "date": self.date,
                "expires": self.expires,
                "certUrl": self.certUrl,
                "certSha256": self.certSha256,
                "certificates": self.certificates,
            }
        )


@dataclasses.dataclass
class SignedExchangeHeader:
    """Information about a signed exchange header.
    https://wicg.github.io/webpackage/draft-yasskin-httpbis-origin-signed-exchanges-impl.html#cbor-representation

    Attributes
    ----------
    requestUrl: str
            Signed exchange request URL.
    responseCode: int
            Signed exchange response code.
    responseHeaders: Headers
            Signed exchange response headers.
    signatures: list[SignedExchangeSignature]
            Signed exchange response signature.
    headerIntegrity: str
            Signed exchange header integrity hash in the form of "sha256-<base64-hash-value>".
    """

    requestUrl: str
    responseCode: int
    responseHeaders: Headers
    signatures: list[SignedExchangeSignature]
    headerIntegrity: str

    @classmethod
    def from_json(cls, json: dict) -> SignedExchangeHeader:
        return cls(
            json["requestUrl"],
            json["responseCode"],
            Headers(json["responseHeaders"]),
            [SignedExchangeSignature.from_json(s) for s in json["signatures"]],
            json["headerIntegrity"],
        )

    def to_json(self) -> dict:
        return {
            "requestUrl": self.requestUrl,
            "responseCode": self.responseCode,
            "responseHeaders": dict(self.responseHeaders),
            "signatures": [s.to_json() for s in self.signatures],
            "headerIntegrity": self.headerIntegrity,
        }


class SignedExchangeErrorField(enum.Enum):
    """Field type for a signed exchange related error."""

    SIGNATURE_SIG = "signatureSig"
    SIGNATURE_INTEGRITY = "signatureIntegrity"
    SIGNATURE_CERT_URL = "signatureCertUrl"
    SIGNATURE_CERT_SHA256 = "signatureCertSha256"
    SIGNATURE_VALIDITY_URL = "signatureValidityUrl"
    SIGNATURE_TIMESTAMPS = "signatureTimestamps"


@dataclasses.dataclass
class SignedExchangeError:
    """Information about a signed exchange response.

    Attributes
    ----------
    message: str
            Error message.
    signatureIndex: Optional[int]
            The index of the signature which caused the error.
    errorField: Optional[SignedExchangeErrorField]
            The field which caused the error.
    """

    message: str
    signatureIndex: Optional[int] = None
    errorField: Optional[SignedExchangeErrorField] = None

    @classmethod
    def from_json(cls, json: dict) -> SignedExchangeError:
        return cls(
            json["message"],
            json.get("signatureIndex"),
            SignedExchangeErrorField(json["errorField"])
            if "errorField" in json
            else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "message": self.message,
                "signatureIndex": self.signatureIndex,
                "errorField": self.errorField.value if self.errorField else None,
            }
        )


@dataclasses.dataclass
class SignedExchangeInfo:
    """Information about a signed exchange response.

    Attributes
    ----------
    outerResponse: Response
            The outer response of signed HTTP exchange which was received from network.
    header: Optional[SignedExchangeHeader]
            Information about the signed exchange header.
    securityDetails: Optional[SecurityDetails]
            Security details for the signed exchange header.
    errors: Optional[list[SignedExchangeError]]
            Errors occurred while handling the signed exchagne.
    """

    outerResponse: Response
    header: Optional[SignedExchangeHeader] = None
    securityDetails: Optional[SecurityDetails] = None
    errors: Optional[list[SignedExchangeError]] = None

    @classmethod
    def from_json(cls, json: dict) -> SignedExchangeInfo:
        return cls(
            Response.from_json(json["outerResponse"]),
            SignedExchangeHeader.from_json(json["header"])
            if "header" in json
            else None,
            SecurityDetails.from_json(json["securityDetails"])
            if "securityDetails" in json
            else None,
            [SignedExchangeError.from_json(e) for e in json["errors"]]
            if "errors" in json
            else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "outerResponse": self.outerResponse.to_json(),
                "header": self.header.to_json() if self.header else None,
                "securityDetails": self.securityDetails.to_json()
                if self.securityDetails
                else None,
                "errors": [e.to_json() for e in self.errors] if self.errors else None,
            }
        )


class PrivateNetworkRequestPolicy(enum.Enum):
    """"""

    ALLOW = "Allow"
    BLOCK_FROM_INSECURE_TO_MORE_PRIVATE = "BlockFromInsecureToMorePrivate"


class IPAddressSpace(enum.Enum):
    """"""

    LOCAL = "Local"
    PRIVATE = "Private"
    PUBLIC = "Public"
    UNKNOWN = "Unknown"


@dataclasses.dataclass
class ClientSecurityState:
    """
    Attributes
    ----------
    initiatorIsSecureContext: bool
    initiatorIPAddressSpace: IPAddressSpace
    privateNetworkRequestPolicy: PrivateNetworkRequestPolicy
    """

    initiatorIsSecureContext: bool
    initiatorIPAddressSpace: IPAddressSpace
    privateNetworkRequestPolicy: PrivateNetworkRequestPolicy

    @classmethod
    def from_json(cls, json: dict) -> ClientSecurityState:
        return cls(
            json["initiatorIsSecureContext"],
            IPAddressSpace(json["initiatorIPAddressSpace"]),
            PrivateNetworkRequestPolicy(json["privateNetworkRequestPolicy"]),
        )

    def to_json(self) -> dict:
        return {
            "initiatorIsSecureContext": self.initiatorIsSecureContext,
            "initiatorIPAddressSpace": self.initiatorIPAddressSpace.value,
            "privateNetworkRequestPolicy": self.privateNetworkRequestPolicy.value,
        }


class CrossOriginOpenerPolicyValue(enum.Enum):
    """"""

    SAME_ORIGIN = "SameOrigin"
    SAME_ORIGIN_ALLOW_POPUPS = "SameOriginAllowPopups"
    UNSAFE_NONE = "UnsafeNone"
    SAME_ORIGIN_PLUS_COEP = "SameOriginPlusCoep"


@dataclasses.dataclass
class CrossOriginOpenerPolicyStatus:
    """
    Attributes
    ----------
    value: CrossOriginOpenerPolicyValue
    reportOnlyValue: CrossOriginOpenerPolicyValue
    reportingEndpoint: Optional[str]
    reportOnlyReportingEndpoint: Optional[str]
    """

    value: CrossOriginOpenerPolicyValue
    reportOnlyValue: CrossOriginOpenerPolicyValue
    reportingEndpoint: Optional[str] = None
    reportOnlyReportingEndpoint: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> CrossOriginOpenerPolicyStatus:
        return cls(
            CrossOriginOpenerPolicyValue(json["value"]),
            CrossOriginOpenerPolicyValue(json["reportOnlyValue"]),
            json.get("reportingEndpoint"),
            json.get("reportOnlyReportingEndpoint"),
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "value": self.value.value,
                "reportOnlyValue": self.reportOnlyValue.value,
                "reportingEndpoint": self.reportingEndpoint,
                "reportOnlyReportingEndpoint": self.reportOnlyReportingEndpoint,
            }
        )


class CrossOriginEmbedderPolicyValue(enum.Enum):
    """"""

    NONE = "None"
    REQUIRE_CORP = "RequireCorp"


@dataclasses.dataclass
class CrossOriginEmbedderPolicyStatus:
    """
    Attributes
    ----------
    value: CrossOriginEmbedderPolicyValue
    reportOnlyValue: CrossOriginEmbedderPolicyValue
    reportingEndpoint: Optional[str]
    reportOnlyReportingEndpoint: Optional[str]
    """

    value: CrossOriginEmbedderPolicyValue
    reportOnlyValue: CrossOriginEmbedderPolicyValue
    reportingEndpoint: Optional[str] = None
    reportOnlyReportingEndpoint: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> CrossOriginEmbedderPolicyStatus:
        return cls(
            CrossOriginEmbedderPolicyValue(json["value"]),
            CrossOriginEmbedderPolicyValue(json["reportOnlyValue"]),
            json.get("reportingEndpoint"),
            json.get("reportOnlyReportingEndpoint"),
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "value": self.value.value,
                "reportOnlyValue": self.reportOnlyValue.value,
                "reportingEndpoint": self.reportingEndpoint,
                "reportOnlyReportingEndpoint": self.reportOnlyReportingEndpoint,
            }
        )


@dataclasses.dataclass
class SecurityIsolationStatus:
    """
    Attributes
    ----------
    coop: Optional[CrossOriginOpenerPolicyStatus]
    coep: Optional[CrossOriginEmbedderPolicyStatus]
    """

    coop: Optional[CrossOriginOpenerPolicyStatus] = None
    coep: Optional[CrossOriginEmbedderPolicyStatus] = None

    @classmethod
    def from_json(cls, json: dict) -> SecurityIsolationStatus:
        return cls(
            CrossOriginOpenerPolicyStatus.from_json(json["coop"])
            if "coop" in json
            else None,
            CrossOriginEmbedderPolicyStatus.from_json(json["coep"])
            if "coep" in json
            else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "coop": self.coop.to_json() if self.coop else None,
                "coep": self.coep.to_json() if self.coep else None,
            }
        )


@dataclasses.dataclass
class LoadNetworkResourcePageResult:
    """An object providing the result of a network resource load.

    Attributes
    ----------
    success: bool
    netError: Optional[float]
            Optional values used for error reporting.
    netErrorName: Optional[str]
    httpStatusCode: Optional[float]
    stream: Optional[io.StreamHandle]
            If successful, one of the following two fields holds the result.
    headers: Optional[Headers]
            Response headers.
    """

    success: bool
    netError: Optional[float] = None
    netErrorName: Optional[str] = None
    httpStatusCode: Optional[float] = None
    stream: Optional[io.StreamHandle] = None
    headers: Optional[Headers] = None

    @classmethod
    def from_json(cls, json: dict) -> LoadNetworkResourcePageResult:
        return cls(
            json["success"],
            json.get("netError"),
            json.get("netErrorName"),
            json.get("httpStatusCode"),
            io.StreamHandle(json["stream"]) if "stream" in json else None,
            Headers(json["headers"]) if "headers" in json else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "success": self.success,
                "netError": self.netError,
                "netErrorName": self.netErrorName,
                "httpStatusCode": self.httpStatusCode,
                "stream": str(self.stream) if self.stream else None,
                "headers": dict(self.headers) if self.headers else None,
            }
        )


@dataclasses.dataclass
class LoadNetworkResourceOptions:
    """An options object that may be extended later to better support CORS,
    CORB and streaming.

    Attributes
    ----------
    disableCache: bool
    includeCredentials: bool
    """

    disableCache: bool
    includeCredentials: bool

    @classmethod
    def from_json(cls, json: dict) -> LoadNetworkResourceOptions:
        return cls(json["disableCache"], json["includeCredentials"])

    def to_json(self) -> dict:
        return {
            "disableCache": self.disableCache,
            "includeCredentials": self.includeCredentials,
        }


def can_clear_browser_cache():
    """Tells whether clearing browser cache is supported.

    **Deprectated**

    Returns
    -------
    result: bool
            True if browser cache can be cleared.
    """
    return {"method": "Network.canClearBrowserCache", "params": {}}


def can_clear_browser_cookies():
    """Tells whether clearing browser cookies is supported.

    **Deprectated**

    Returns
    -------
    result: bool
            True if browser cookies can be cleared.
    """
    return {"method": "Network.canClearBrowserCookies", "params": {}}


def can_emulate_network_conditions():
    """Tells whether emulation of network conditions is supported.

    **Deprectated**

    Returns
    -------
    result: bool
            True if emulation of network conditions is supported.
    """
    return {"method": "Network.canEmulateNetworkConditions", "params": {}}


def clear_browser_cache():
    """Clears browser cache."""
    return {"method": "Network.clearBrowserCache", "params": {}}


def clear_browser_cookies():
    """Clears browser cookies."""
    return {"method": "Network.clearBrowserCookies", "params": {}}


def continue_intercepted_request(
    interceptionId: InterceptionId,
    errorReason: Optional[ErrorReason] = None,
    rawResponse: Optional[str] = None,
    url: Optional[str] = None,
    method: Optional[str] = None,
    postData: Optional[str] = None,
    headers: Optional[Headers] = None,
    authChallengeResponse: Optional[AuthChallengeResponse] = None,
):
    """Response to Network.requestIntercepted which either modifies the request to continue with any
    modifications, or blocks it, or completes it with the provided response bytes. If a network
    fetch occurs as a result which encounters a redirect an additional Network.requestIntercepted
    event will be sent with the same InterceptionId.
    Deprecated, use Fetch.continueRequest, Fetch.fulfillRequest and Fetch.failRequest instead.

    **Experimental**

    **Deprectated**

    Parameters
    ----------
    interceptionId: InterceptionId
    errorReason: Optional[ErrorReason]
            If set this causes the request to fail with the given reason. Passing `Aborted` for requests
            marked with `isNavigationRequest` also cancels the navigation. Must not be set in response
            to an authChallenge.
    rawResponse: Optional[str]
            If set the requests completes using with the provided base64 encoded raw response, including
            HTTP status line and headers etc... Must not be set in response to an authChallenge. (Encoded as a base64 string when passed over JSON)
    url: Optional[str]
            If set the request url will be modified in a way that's not observable by page. Must not be
            set in response to an authChallenge.
    method: Optional[str]
            If set this allows the request method to be overridden. Must not be set in response to an
            authChallenge.
    postData: Optional[str]
            If set this allows postData to be set. Must not be set in response to an authChallenge.
    headers: Optional[Headers]
            If set this allows the request headers to be changed. Must not be set in response to an
            authChallenge.
    authChallengeResponse: Optional[AuthChallengeResponse]
            Response to a requestIntercepted with an authChallenge. Must not be set otherwise.
    """
    return filter_unset_parameters(
        {
            "method": "Network.continueInterceptedRequest",
            "params": {
                "interceptionId": interceptionId,
                "errorReason": errorReason,
                "rawResponse": rawResponse,
                "url": url,
                "method": method,
                "postData": postData,
                "headers": headers,
                "authChallengeResponse": authChallengeResponse,
            },
        }
    )


def delete_cookies(
    name: str,
    url: Optional[str] = None,
    domain: Optional[str] = None,
    path: Optional[str] = None,
):
    """Deletes browser cookies with matching name and url or domain/path pair.

    Parameters
    ----------
    name: str
            Name of the cookies to remove.
    url: Optional[str]
            If specified, deletes all the cookies with the given name where domain and path match
            provided URL.
    domain: Optional[str]
            If specified, deletes only cookies with the exact domain.
    path: Optional[str]
            If specified, deletes only cookies with the exact path.
    """
    return filter_unset_parameters(
        {
            "method": "Network.deleteCookies",
            "params": {"name": name, "url": url, "domain": domain, "path": path},
        }
    )


def disable():
    """Disables network tracking, prevents network events from being sent to the client."""
    return {"method": "Network.disable", "params": {}}


def emulate_network_conditions(
    offline: bool,
    latency: float,
    downloadThroughput: float,
    uploadThroughput: float,
    connectionType: Optional[ConnectionType] = None,
):
    """Activates emulation of network conditions.

    Parameters
    ----------
    offline: bool
            True to emulate internet disconnection.
    latency: float
            Minimum latency from request sent to response headers received (ms).
    downloadThroughput: float
            Maximal aggregated download throughput (bytes/sec). -1 disables download throttling.
    uploadThroughput: float
            Maximal aggregated upload throughput (bytes/sec).  -1 disables upload throttling.
    connectionType: Optional[ConnectionType]
            Connection type if known.
    """
    return filter_unset_parameters(
        {
            "method": "Network.emulateNetworkConditions",
            "params": {
                "offline": offline,
                "latency": latency,
                "downloadThroughput": downloadThroughput,
                "uploadThroughput": uploadThroughput,
                "connectionType": connectionType,
            },
        }
    )


def enable(
    maxTotalBufferSize: Optional[int] = None,
    maxResourceBufferSize: Optional[int] = None,
    maxPostDataSize: Optional[int] = None,
):
    """Enables network tracking, network events will now be delivered to the client.

    Parameters
    ----------
    maxTotalBufferSize: Optional[int]
            Buffer size in bytes to use when preserving network payloads (XHRs, etc).
    maxResourceBufferSize: Optional[int]
            Per-resource buffer size in bytes to use when preserving network payloads (XHRs, etc).
    maxPostDataSize: Optional[int]
            Longest post body size (in bytes) that would be included in requestWillBeSent notification
    """
    return filter_unset_parameters(
        {
            "method": "Network.enable",
            "params": {
                "maxTotalBufferSize": maxTotalBufferSize,
                "maxResourceBufferSize": maxResourceBufferSize,
                "maxPostDataSize": maxPostDataSize,
            },
        }
    )


def get_all_cookies():
    """Returns all browser cookies. Depending on the backend support, will return detailed cookie
    information in the `cookies` field.

    Returns
    -------
    cookies: list[Cookie]
            Array of cookie objects.
    """
    return {"method": "Network.getAllCookies", "params": {}}


def get_certificate(origin: str):
    """Returns the DER-encoded certificate.

    **Experimental**

    Parameters
    ----------
    origin: str
            Origin to get certificate for.

    Returns
    -------
    tableNames: list[str]
    """
    return {"method": "Network.getCertificate", "params": {"origin": origin}}


def get_cookies(urls: Optional[list[str]] = None):
    """Returns all browser cookies for the current URL. Depending on the backend support, will return
    detailed cookie information in the `cookies` field.

    Parameters
    ----------
    urls: Optional[list[str]]
            The list of URLs for which applicable cookies will be fetched.
            If not specified, it's assumed to be set to the list containing
            the URLs of the page and all of its subframes.

    Returns
    -------
    cookies: list[Cookie]
            Array of cookie objects.
    """
    return filter_unset_parameters(
        {"method": "Network.getCookies", "params": {"urls": urls}}
    )


def get_response_body(requestId: RequestId):
    """Returns content served for the given request.

    Parameters
    ----------
    requestId: RequestId
            Identifier of the network request to get content for.

    Returns
    -------
    body: str
            Response body.
    base64Encoded: bool
            True, if content was sent as base64.
    """
    return {"method": "Network.getResponseBody", "params": {"requestId": requestId}}


def get_request_post_data(requestId: RequestId):
    """Returns post data sent with the request. Returns an error when no data was sent with the request.

    Parameters
    ----------
    requestId: RequestId
            Identifier of the network request to get content for.

    Returns
    -------
    postData: str
            Request body string, omitting files from multipart requests
    """
    return {"method": "Network.getRequestPostData", "params": {"requestId": requestId}}


def get_response_body_for_interception(interceptionId: InterceptionId):
    """Returns content served for the given currently intercepted request.

    **Experimental**

    Parameters
    ----------
    interceptionId: InterceptionId
            Identifier for the intercepted request to get body for.

    Returns
    -------
    body: str
            Response body.
    base64Encoded: bool
            True, if content was sent as base64.
    """
    return {
        "method": "Network.getResponseBodyForInterception",
        "params": {"interceptionId": interceptionId},
    }


def take_response_body_for_interception_as_stream(interceptionId: InterceptionId):
    """Returns a handle to the stream representing the response body. Note that after this command,
    the intercepted request can't be continued as is -- you either need to cancel it or to provide
    the response body. The stream only supports sequential read, IO.read will fail if the position
    is specified.

    **Experimental**

    Parameters
    ----------
    interceptionId: InterceptionId

    Returns
    -------
    stream: io.StreamHandle
    """
    return {
        "method": "Network.takeResponseBodyForInterceptionAsStream",
        "params": {"interceptionId": interceptionId},
    }


def replay_xhr(requestId: RequestId):
    """This method sends a new XMLHttpRequest which is identical to the original one. The following
    parameters should be identical: method, url, async, request body, extra headers, withCredentials
    attribute, user, password.

    **Experimental**

    Parameters
    ----------
    requestId: RequestId
            Identifier of XHR to replay.
    """
    return {"method": "Network.replayXHR", "params": {"requestId": requestId}}


def search_in_response_body(
    requestId: RequestId,
    query: str,
    caseSensitive: Optional[bool] = None,
    isRegex: Optional[bool] = None,
):
    """Searches for given string in response content.

    **Experimental**

    Parameters
    ----------
    requestId: RequestId
            Identifier of the network response to search.
    query: str
            String to search for.
    caseSensitive: Optional[bool]
            If true, search is case sensitive.
    isRegex: Optional[bool]
            If true, treats string parameter as regex.

    Returns
    -------
    result: list[debugger.SearchMatch]
            List of search matches.
    """
    return filter_unset_parameters(
        {
            "method": "Network.searchInResponseBody",
            "params": {
                "requestId": requestId,
                "query": query,
                "caseSensitive": caseSensitive,
                "isRegex": isRegex,
            },
        }
    )


def set_blocked_ur_ls(urls: list[str]):
    """Blocks URLs from loading.

    **Experimental**

    Parameters
    ----------
    urls: list[str]
            URL patterns to block. Wildcards ('*') are allowed.
    """
    return {"method": "Network.setBlockedURLs", "params": {"urls": urls}}


def set_bypass_service_worker(bypass: bool):
    """Toggles ignoring of service worker for each request.

    **Experimental**

    Parameters
    ----------
    bypass: bool
            Bypass service worker and load from network.
    """
    return {"method": "Network.setBypassServiceWorker", "params": {"bypass": bypass}}


def set_cache_disabled(cacheDisabled: bool):
    """Toggles ignoring cache for each request. If `true`, cache will not be used.

    Parameters
    ----------
    cacheDisabled: bool
            Cache disabled state.
    """
    return {
        "method": "Network.setCacheDisabled",
        "params": {"cacheDisabled": cacheDisabled},
    }


def set_cookie(
    name: str,
    value: str,
    url: Optional[str] = None,
    domain: Optional[str] = None,
    path: Optional[str] = None,
    secure: Optional[bool] = None,
    httpOnly: Optional[bool] = None,
    sameSite: Optional[CookieSameSite] = None,
    expires: Optional[TimeSinceEpoch] = None,
    priority: Optional[CookiePriority] = None,
):
    """Sets a cookie with the given cookie data; may overwrite equivalent cookies if they exist.

    Parameters
    ----------
    name: str
            Cookie name.
    value: str
            Cookie value.
    url: Optional[str]
            The request-URI to associate with the setting of the cookie. This value can affect the
            default domain and path values of the created cookie.
    domain: Optional[str]
            Cookie domain.
    path: Optional[str]
            Cookie path.
    secure: Optional[bool]
            True if cookie is secure.
    httpOnly: Optional[bool]
            True if cookie is http-only.
    sameSite: Optional[CookieSameSite]
            Cookie SameSite type.
    expires: Optional[TimeSinceEpoch]
            Cookie expiration date, session cookie if not set
    priority: Optional[CookiePriority]
            Cookie Priority type.

    Returns
    -------
    success: bool
            Always set to true. If an error occurs, the response indicates protocol error.
    """
    return filter_unset_parameters(
        {
            "method": "Network.setCookie",
            "params": {
                "name": name,
                "value": value,
                "url": url,
                "domain": domain,
                "path": path,
                "secure": secure,
                "httpOnly": httpOnly,
                "sameSite": sameSite,
                "expires": expires,
                "priority": priority,
            },
        }
    )


def set_cookies(cookies: list[CookieParam]):
    """Sets given cookies.

    Parameters
    ----------
    cookies: list[CookieParam]
            Cookies to be set.
    """
    return {"method": "Network.setCookies", "params": {"cookies": cookies}}


def set_data_size_limits_for_test(maxTotalSize: int, maxResourceSize: int):
    """For testing.

    **Experimental**

    Parameters
    ----------
    maxTotalSize: int
            Maximum total buffer size.
    maxResourceSize: int
            Maximum per-resource size.
    """
    return {
        "method": "Network.setDataSizeLimitsForTest",
        "params": {"maxTotalSize": maxTotalSize, "maxResourceSize": maxResourceSize},
    }


def set_extra_http_headers(headers: Headers):
    """Specifies whether to always send extra HTTP headers with the requests from this page.

    Parameters
    ----------
    headers: Headers
            Map with extra HTTP headers.
    """
    return {"method": "Network.setExtraHTTPHeaders", "params": {"headers": headers}}


def set_attach_debug_stack(enabled: bool):
    """Specifies whether to attach a page script stack id in requests

    **Experimental**

    Parameters
    ----------
    enabled: bool
            Whether to attach a page script stack for debugging purpose.
    """
    return {"method": "Network.setAttachDebugStack", "params": {"enabled": enabled}}


def set_request_interception(patterns: list[RequestPattern]):
    """Sets the requests to intercept that match the provided patterns and optionally resource types.
    Deprecated, please use Fetch.enable instead.

    **Experimental**

    **Deprectated**

    Parameters
    ----------
    patterns: list[RequestPattern]
            Requests matching any of these patterns will be forwarded and wait for the corresponding
            continueInterceptedRequest call.
    """
    return {
        "method": "Network.setRequestInterception",
        "params": {"patterns": patterns},
    }


def set_user_agent_override(
    userAgent: str,
    acceptLanguage: Optional[str] = None,
    platform: Optional[str] = None,
    userAgentMetadata: Optional[emulation.UserAgentMetadata] = None,
):
    """Allows overriding user agent with the given string.

    Parameters
    ----------
    userAgent: str
            User agent to use.
    acceptLanguage: Optional[str]
            Browser langugage to emulate.
    platform: Optional[str]
            The platform navigator.platform should return.
    userAgentMetadata: Optional[emulation.UserAgentMetadata]
            To be sent in Sec-CH-UA-* headers and returned in navigator.userAgentData
    """
    return filter_unset_parameters(
        {
            "method": "Network.setUserAgentOverride",
            "params": {
                "userAgent": userAgent,
                "acceptLanguage": acceptLanguage,
                "platform": platform,
                "userAgentMetadata": userAgentMetadata,
            },
        }
    )


def get_security_isolation_status(frameId: Optional[page.FrameId] = None):
    """Returns information about the COEP/COOP isolation status.

    **Experimental**

    Parameters
    ----------
    frameId: Optional[page.FrameId]
            If no frameId is provided, the status of the target is provided.

    Returns
    -------
    status: SecurityIsolationStatus
    """
    return filter_unset_parameters(
        {"method": "Network.getSecurityIsolationStatus", "params": {"frameId": frameId}}
    )


def load_network_resource(
    frameId: page.FrameId, url: str, options: LoadNetworkResourceOptions
):
    """Fetches the resource and returns the content.

    **Experimental**

    Parameters
    ----------
    frameId: page.FrameId
            Frame id to get the resource for.
    url: str
            URL of the resource to get content for.
    options: LoadNetworkResourceOptions
            Options for the request.

    Returns
    -------
    resource: LoadNetworkResourcePageResult
    """
    return {
        "method": "Network.loadNetworkResource",
        "params": {"frameId": frameId, "url": url, "options": options},
    }
