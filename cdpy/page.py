from __future__ import annotations

import dataclasses
import enum
from typing import Generator, Optional

from deprecated.sphinx import deprecated

from . import debugger, dom, emulation, io, network, runtime
from .common import filter_none


class FrameId(str):
    """Unique frame identifier."""

    def __repr__(self):
        return f"FrameId({super().__repr__()})"


class AdFrameType(enum.Enum):
    """Indicates whether a frame has been identified as an ad."""

    NONE = "none"
    CHILD = "child"
    ROOT = "root"


class SecureContextType(enum.Enum):
    """Indicates whether the frame is a secure context and why it is the case."""

    SECURE = "Secure"
    SECURE_LOCALHOST = "SecureLocalhost"
    INSECURE_SCHEME = "InsecureScheme"
    INSECURE_ANCESTOR = "InsecureAncestor"


class CrossOriginIsolatedContextType(enum.Enum):
    """Indicates whether the frame is cross-origin isolated and why it is the case."""

    ISOLATED = "Isolated"
    NOT_ISOLATED = "NotIsolated"
    NOT_ISOLATED_FEATURE_DISABLED = "NotIsolatedFeatureDisabled"


class GatedAPIFeatures(enum.Enum):
    """"""

    SHARED_ARRAY_BUFFERS = "SharedArrayBuffers"
    SHARED_ARRAY_BUFFERS_TRANSFER_ALLOWED = "SharedArrayBuffersTransferAllowed"
    PERFORMANCE_MEASURE_MEMORY = "PerformanceMeasureMemory"
    PERFORMANCE_PROFILE = "PerformanceProfile"


@dataclasses.dataclass
class Frame:
    """Information about the Frame on the page.

    Attributes
    ----------
    id: FrameId
            Frame unique identifier.
    loaderId: network.LoaderId
            Identifier of the loader associated with this frame.
    url: str
            Frame document's URL without fragment.
    domainAndRegistry: str
            Frame document's registered domain, taking the public suffixes list into account.
            Extracted from the Frame's url.
            Example URLs: http://www.google.com/file.html -> "google.com"
                          http://a.b.co.uk/file.html      -> "b.co.uk"
    securityOrigin: str
            Frame document's security origin.
    mimeType: str
            Frame document's mimeType as determined by the browser.
    secureContextType: SecureContextType
            Indicates whether the main document is a secure context and explains why that is the case.
    crossOriginIsolatedContextType: CrossOriginIsolatedContextType
            Indicates whether this is a cross origin isolated context.
    gatedAPIFeatures: list[GatedAPIFeatures]
            Indicated which gated APIs / features are available.
    parentId: Optional[str]
            Parent frame identifier.
    name: Optional[str]
            Frame's name as specified in the tag.
    urlFragment: Optional[str]
            Frame document's URL fragment including the '#'.
    unreachableUrl: Optional[str]
            If the frame failed to load, this contains the URL that could not be loaded. Note that unlike url above, this URL may contain a fragment.
    adFrameType: Optional[AdFrameType]
            Indicates whether this frame was tagged as an ad.
    """

    id: FrameId
    loaderId: network.LoaderId
    url: str
    domainAndRegistry: str
    securityOrigin: str
    mimeType: str
    secureContextType: SecureContextType
    crossOriginIsolatedContextType: CrossOriginIsolatedContextType
    gatedAPIFeatures: list[GatedAPIFeatures]
    parentId: Optional[str] = None
    name: Optional[str] = None
    urlFragment: Optional[str] = None
    unreachableUrl: Optional[str] = None
    adFrameType: Optional[AdFrameType] = None

    @classmethod
    def from_json(cls, json: dict) -> Frame:
        return cls(
            FrameId(json["id"]),
            network.LoaderId(json["loaderId"]),
            json["url"],
            json["domainAndRegistry"],
            json["securityOrigin"],
            json["mimeType"],
            SecureContextType(json["secureContextType"]),
            CrossOriginIsolatedContextType(json["crossOriginIsolatedContextType"]),
            [GatedAPIFeatures(g) for g in json["gatedAPIFeatures"]],
            json.get("parentId"),
            json.get("name"),
            json.get("urlFragment"),
            json.get("unreachableUrl"),
            AdFrameType(json["adFrameType"]) if "adFrameType" in json else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "id": str(self.id),
                "loaderId": str(self.loaderId),
                "url": self.url,
                "domainAndRegistry": self.domainAndRegistry,
                "securityOrigin": self.securityOrigin,
                "mimeType": self.mimeType,
                "secureContextType": self.secureContextType.value,
                "crossOriginIsolatedContextType": self.crossOriginIsolatedContextType.value,
                "gatedAPIFeatures": [g.value for g in self.gatedAPIFeatures],
                "parentId": self.parentId,
                "name": self.name,
                "urlFragment": self.urlFragment,
                "unreachableUrl": self.unreachableUrl,
                "adFrameType": self.adFrameType.value if self.adFrameType else None,
            }
        )


@dataclasses.dataclass
class FrameResource:
    """Information about the Resource on the page.

    Attributes
    ----------
    url: str
            Resource URL.
    type: network.ResourceType
            Type of this resource.
    mimeType: str
            Resource mimeType as determined by the browser.
    lastModified: Optional[network.TimeSinceEpoch]
            last-modified timestamp as reported by server.
    contentSize: Optional[float]
            Resource content size.
    failed: Optional[bool]
            True if the resource failed to load.
    canceled: Optional[bool]
            True if the resource was canceled during loading.
    """

    url: str
    type: network.ResourceType
    mimeType: str
    lastModified: Optional[network.TimeSinceEpoch] = None
    contentSize: Optional[float] = None
    failed: Optional[bool] = None
    canceled: Optional[bool] = None

    @classmethod
    def from_json(cls, json: dict) -> FrameResource:
        return cls(
            json["url"],
            network.ResourceType(json["type"]),
            json["mimeType"],
            network.TimeSinceEpoch(json["lastModified"])
            if "lastModified" in json
            else None,
            json.get("contentSize"),
            json.get("failed"),
            json.get("canceled"),
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "url": self.url,
                "type": self.type.value,
                "mimeType": self.mimeType,
                "lastModified": float(self.lastModified) if self.lastModified else None,
                "contentSize": self.contentSize,
                "failed": self.failed,
                "canceled": self.canceled,
            }
        )


@dataclasses.dataclass
class FrameResourceTree:
    """Information about the Frame hierarchy along with their cached resources.

    Attributes
    ----------
    frame: Frame
            Frame information for this tree item.
    resources: list[FrameResource]
            Information about frame resources.
    childFrames: Optional[list[FrameResourceTree]]
            Child frames.
    """

    frame: Frame
    resources: list[FrameResource]
    childFrames: Optional[list[FrameResourceTree]] = None

    @classmethod
    def from_json(cls, json: dict) -> FrameResourceTree:
        return cls(
            Frame.from_json(json["frame"]),
            [FrameResource.from_json(r) for r in json["resources"]],
            [FrameResourceTree.from_json(c) for c in json["childFrames"]]
            if "childFrames" in json
            else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "frame": self.frame.to_json(),
                "resources": [r.to_json() for r in self.resources],
                "childFrames": [c.to_json() for c in self.childFrames]
                if self.childFrames
                else None,
            }
        )


@dataclasses.dataclass
class FrameTree:
    """Information about the Frame hierarchy.

    Attributes
    ----------
    frame: Frame
            Frame information for this tree item.
    childFrames: Optional[list[FrameTree]]
            Child frames.
    """

    frame: Frame
    childFrames: Optional[list[FrameTree]] = None

    @classmethod
    def from_json(cls, json: dict) -> FrameTree:
        return cls(
            Frame.from_json(json["frame"]),
            [FrameTree.from_json(c) for c in json["childFrames"]]
            if "childFrames" in json
            else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "frame": self.frame.to_json(),
                "childFrames": [c.to_json() for c in self.childFrames]
                if self.childFrames
                else None,
            }
        )


class ScriptIdentifier(str):
    """Unique script identifier."""

    def __repr__(self):
        return f"ScriptIdentifier({super().__repr__()})"


class TransitionType(enum.Enum):
    """Transition type."""

    LINK = "link"
    TYPED = "typed"
    ADDRESS_BAR = "address_bar"
    AUTO_BOOKMARK = "auto_bookmark"
    AUTO_SUBFRAME = "auto_subframe"
    MANUAL_SUBFRAME = "manual_subframe"
    GENERATED = "generated"
    AUTO_TOPLEVEL = "auto_toplevel"
    FORM_SUBMIT = "form_submit"
    RELOAD = "reload"
    KEYWORD = "keyword"
    KEYWORD_GENERATED = "keyword_generated"
    OTHER = "other"


@dataclasses.dataclass
class NavigationEntry:
    """Navigation history entry.

    Attributes
    ----------
    id: int
            Unique id of the navigation history entry.
    url: str
            URL of the navigation history entry.
    userTypedURL: str
            URL that the user typed in the url bar.
    title: str
            Title of the navigation history entry.
    transitionType: TransitionType
            Transition type.
    """

    id: int
    url: str
    userTypedURL: str
    title: str
    transitionType: TransitionType

    @classmethod
    def from_json(cls, json: dict) -> NavigationEntry:
        return cls(
            json["id"],
            json["url"],
            json["userTypedURL"],
            json["title"],
            TransitionType(json["transitionType"]),
        )

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "url": self.url,
            "userTypedURL": self.userTypedURL,
            "title": self.title,
            "transitionType": self.transitionType.value,
        }


@dataclasses.dataclass
class ScreencastFrameMetadata:
    """Screencast frame metadata.

    Attributes
    ----------
    offsetTop: float
            Top offset in DIP.
    pageScaleFactor: float
            Page scale factor.
    deviceWidth: float
            Device screen width in DIP.
    deviceHeight: float
            Device screen height in DIP.
    scrollOffsetX: float
            Position of horizontal scroll in CSS pixels.
    scrollOffsetY: float
            Position of vertical scroll in CSS pixels.
    timestamp: Optional[network.TimeSinceEpoch]
            Frame swap timestamp.
    """

    offsetTop: float
    pageScaleFactor: float
    deviceWidth: float
    deviceHeight: float
    scrollOffsetX: float
    scrollOffsetY: float
    timestamp: Optional[network.TimeSinceEpoch] = None

    @classmethod
    def from_json(cls, json: dict) -> ScreencastFrameMetadata:
        return cls(
            json["offsetTop"],
            json["pageScaleFactor"],
            json["deviceWidth"],
            json["deviceHeight"],
            json["scrollOffsetX"],
            json["scrollOffsetY"],
            network.TimeSinceEpoch(json["timestamp"]) if "timestamp" in json else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "offsetTop": self.offsetTop,
                "pageScaleFactor": self.pageScaleFactor,
                "deviceWidth": self.deviceWidth,
                "deviceHeight": self.deviceHeight,
                "scrollOffsetX": self.scrollOffsetX,
                "scrollOffsetY": self.scrollOffsetY,
                "timestamp": float(self.timestamp) if self.timestamp else None,
            }
        )


class DialogType(enum.Enum):
    """Javascript dialog type."""

    ALERT = "alert"
    CONFIRM = "confirm"
    PROMPT = "prompt"
    BEFOREUNLOAD = "beforeunload"


@dataclasses.dataclass
class AppManifestError:
    """Error while paring app manifest.

    Attributes
    ----------
    message: str
            Error message.
    critical: int
            If criticial, this is a non-recoverable parse error.
    line: int
            Error line.
    column: int
            Error column.
    """

    message: str
    critical: int
    line: int
    column: int

    @classmethod
    def from_json(cls, json: dict) -> AppManifestError:
        return cls(json["message"], json["critical"], json["line"], json["column"])

    def to_json(self) -> dict:
        return {
            "message": self.message,
            "critical": self.critical,
            "line": self.line,
            "column": self.column,
        }


@dataclasses.dataclass
class AppManifestParsedProperties:
    """Parsed app manifest properties.

    Attributes
    ----------
    scope: str
            Computed scope value
    """

    scope: str

    @classmethod
    def from_json(cls, json: dict) -> AppManifestParsedProperties:
        return cls(json["scope"])

    def to_json(self) -> dict:
        return {"scope": self.scope}


@dataclasses.dataclass
class LayoutViewport:
    """Layout viewport position and dimensions.

    Attributes
    ----------
    pageX: int
            Horizontal offset relative to the document (CSS pixels).
    pageY: int
            Vertical offset relative to the document (CSS pixels).
    clientWidth: int
            Width (CSS pixels), excludes scrollbar if present.
    clientHeight: int
            Height (CSS pixels), excludes scrollbar if present.
    """

    pageX: int
    pageY: int
    clientWidth: int
    clientHeight: int

    @classmethod
    def from_json(cls, json: dict) -> LayoutViewport:
        return cls(
            json["pageX"], json["pageY"], json["clientWidth"], json["clientHeight"]
        )

    def to_json(self) -> dict:
        return {
            "pageX": self.pageX,
            "pageY": self.pageY,
            "clientWidth": self.clientWidth,
            "clientHeight": self.clientHeight,
        }


@dataclasses.dataclass
class VisualViewport:
    """Visual viewport position, dimensions, and scale.

    Attributes
    ----------
    offsetX: float
            Horizontal offset relative to the layout viewport (CSS pixels).
    offsetY: float
            Vertical offset relative to the layout viewport (CSS pixels).
    pageX: float
            Horizontal offset relative to the document (CSS pixels).
    pageY: float
            Vertical offset relative to the document (CSS pixels).
    clientWidth: float
            Width (CSS pixels), excludes scrollbar if present.
    clientHeight: float
            Height (CSS pixels), excludes scrollbar if present.
    scale: float
            Scale relative to the ideal viewport (size at width=device-width).
    zoom: Optional[float]
            Page zoom factor (CSS to device independent pixels ratio).
    """

    offsetX: float
    offsetY: float
    pageX: float
    pageY: float
    clientWidth: float
    clientHeight: float
    scale: float
    zoom: Optional[float] = None

    @classmethod
    def from_json(cls, json: dict) -> VisualViewport:
        return cls(
            json["offsetX"],
            json["offsetY"],
            json["pageX"],
            json["pageY"],
            json["clientWidth"],
            json["clientHeight"],
            json["scale"],
            json.get("zoom"),
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "offsetX": self.offsetX,
                "offsetY": self.offsetY,
                "pageX": self.pageX,
                "pageY": self.pageY,
                "clientWidth": self.clientWidth,
                "clientHeight": self.clientHeight,
                "scale": self.scale,
                "zoom": self.zoom,
            }
        )


@dataclasses.dataclass
class Viewport:
    """Viewport for capturing screenshot.

    Attributes
    ----------
    x: float
            X offset in device independent pixels (dip).
    y: float
            Y offset in device independent pixels (dip).
    width: float
            Rectangle width in device independent pixels (dip).
    height: float
            Rectangle height in device independent pixels (dip).
    scale: float
            Page scale factor.
    """

    x: float
    y: float
    width: float
    height: float
    scale: float

    @classmethod
    def from_json(cls, json: dict) -> Viewport:
        return cls(json["x"], json["y"], json["width"], json["height"], json["scale"])

    def to_json(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "scale": self.scale,
        }


@dataclasses.dataclass
class FontFamilies:
    """Generic font families collection.

    Attributes
    ----------
    standard: Optional[str]
            The standard font-family.
    fixed: Optional[str]
            The fixed font-family.
    serif: Optional[str]
            The serif font-family.
    sansSerif: Optional[str]
            The sansSerif font-family.
    cursive: Optional[str]
            The cursive font-family.
    fantasy: Optional[str]
            The fantasy font-family.
    pictograph: Optional[str]
            The pictograph font-family.
    """

    standard: Optional[str] = None
    fixed: Optional[str] = None
    serif: Optional[str] = None
    sansSerif: Optional[str] = None
    cursive: Optional[str] = None
    fantasy: Optional[str] = None
    pictograph: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> FontFamilies:
        return cls(
            json.get("standard"),
            json.get("fixed"),
            json.get("serif"),
            json.get("sansSerif"),
            json.get("cursive"),
            json.get("fantasy"),
            json.get("pictograph"),
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "standard": self.standard,
                "fixed": self.fixed,
                "serif": self.serif,
                "sansSerif": self.sansSerif,
                "cursive": self.cursive,
                "fantasy": self.fantasy,
                "pictograph": self.pictograph,
            }
        )


@dataclasses.dataclass
class FontSizes:
    """Default font sizes.

    Attributes
    ----------
    standard: Optional[int]
            Default standard font size.
    fixed: Optional[int]
            Default fixed font size.
    """

    standard: Optional[int] = None
    fixed: Optional[int] = None

    @classmethod
    def from_json(cls, json: dict) -> FontSizes:
        return cls(json.get("standard"), json.get("fixed"))

    def to_json(self) -> dict:
        return filter_none({"standard": self.standard, "fixed": self.fixed})


class ClientNavigationReason(enum.Enum):
    """"""

    FORM_SUBMISSION_GET = "formSubmissionGet"
    FORM_SUBMISSION_POST = "formSubmissionPost"
    HTTP_HEADER_REFRESH = "httpHeaderRefresh"
    SCRIPT_INITIATED = "scriptInitiated"
    META_TAG_REFRESH = "metaTagRefresh"
    PAGE_BLOCK_INTERSTITIAL = "pageBlockInterstitial"
    RELOAD = "reload"
    ANCHOR_CLICK = "anchorClick"


class ClientNavigationDisposition(enum.Enum):
    """"""

    CURRENT_TAB = "currentTab"
    NEW_TAB = "newTab"
    NEW_WINDOW = "newWindow"
    DOWNLOAD = "download"


@dataclasses.dataclass
class InstallabilityErrorArgument:
    """
    Attributes
    ----------
    name: str
            Argument name (e.g. name:'minimum-icon-size-in-pixels').
    value: str
            Argument value (e.g. value:'64').
    """

    name: str
    value: str

    @classmethod
    def from_json(cls, json: dict) -> InstallabilityErrorArgument:
        return cls(json["name"], json["value"])

    def to_json(self) -> dict:
        return {"name": self.name, "value": self.value}


@dataclasses.dataclass
class InstallabilityError:
    """The installability error

    Attributes
    ----------
    errorId: str
            The error id (e.g. 'manifest-missing-suitable-icon').
    errorArguments: list[InstallabilityErrorArgument]
            The list of error arguments (e.g. {name:'minimum-icon-size-in-pixels', value:'64'}).
    """

    errorId: str
    errorArguments: list[InstallabilityErrorArgument]

    @classmethod
    def from_json(cls, json: dict) -> InstallabilityError:
        return cls(
            json["errorId"],
            [InstallabilityErrorArgument.from_json(e) for e in json["errorArguments"]],
        )

    def to_json(self) -> dict:
        return {
            "errorId": self.errorId,
            "errorArguments": [e.to_json() for e in self.errorArguments],
        }


class ReferrerPolicy(enum.Enum):
    """The referring-policy used for the navigation."""

    NO_REFERRER = "noReferrer"
    NO_REFERRER_WHEN_DOWNGRADE = "noReferrerWhenDowngrade"
    ORIGIN = "origin"
    ORIGIN_WHEN_CROSS_ORIGIN = "originWhenCrossOrigin"
    SAME_ORIGIN = "sameOrigin"
    STRICT_ORIGIN = "strictOrigin"
    STRICT_ORIGIN_WHEN_CROSS_ORIGIN = "strictOriginWhenCrossOrigin"
    UNSAFE_URL = "unsafeUrl"


@deprecated(version=1.3)
def add_script_to_evaluate_on_load(
    scriptSource: str,
) -> Generator[dict, dict, ScriptIdentifier]:
    """Deprecated, please use addScriptToEvaluateOnNewDocument instead.

    Parameters
    ----------
    scriptSource: str

    Returns
    -------
    identifier: ScriptIdentifier
            Identifier of the added script.

    **Experimental**
    """
    response = yield {
        "method": "Page.addScriptToEvaluateOnLoad",
        "params": {"scriptSource": scriptSource},
    }
    return ScriptIdentifier(response["identifier"])


def add_script_to_evaluate_on_new_document(
    source: str, worldName: Optional[str] = None
) -> Generator[dict, dict, ScriptIdentifier]:
    """Evaluates given script in every frame upon creation (before loading frame's scripts).

    Parameters
    ----------
    source: str
    worldName: Optional[str]
            If specified, creates an isolated world with the given name and evaluates given script in it.
            This world name will be used as the ExecutionContextDescription::name when the corresponding
            event is emitted.

    Returns
    -------
    identifier: ScriptIdentifier
            Identifier of the added script.
    """
    response = yield {
        "method": "Page.addScriptToEvaluateOnNewDocument",
        "params": filter_none({"source": source, "worldName": worldName}),
    }
    return ScriptIdentifier(response["identifier"])


def bring_to_front() -> dict:
    """Brings page to front (activates tab)."""
    return {"method": "Page.bringToFront", "params": {}}


def capture_screenshot(
    format: Optional[str] = None,
    quality: Optional[int] = None,
    clip: Optional[Viewport] = None,
    fromSurface: Optional[bool] = None,
    captureBeyondViewport: Optional[bool] = None,
) -> Generator[dict, dict, str]:
    """Capture page screenshot.

    Parameters
    ----------
    format: Optional[str]
            Image compression format (defaults to png).
    quality: Optional[int]
            Compression quality from range [0..100] (jpeg only).
    clip: Optional[Viewport]
            Capture the screenshot of a given region only.
    fromSurface: Optional[bool]
            Capture the screenshot from the surface, rather than the view. Defaults to true.
    captureBeyondViewport: Optional[bool]
            Capture the screenshot beyond the viewport. Defaults to false.

    Returns
    -------
    data: str
            Base64-encoded image data. (Encoded as a base64 string when passed over JSON)
    """
    response = yield {
        "method": "Page.captureScreenshot",
        "params": filter_none(
            {
                "format": format,
                "quality": quality,
                "clip": clip.to_json() if clip else None,
                "fromSurface": fromSurface,
                "captureBeyondViewport": captureBeyondViewport,
            }
        ),
    }
    return response["data"]


def capture_snapshot(format: Optional[str] = None) -> Generator[dict, dict, str]:
    """Returns a snapshot of the page as a string. For MHTML format, the serialization includes
    iframes, shadow DOM, external resources, and element-inline styles.

    Parameters
    ----------
    format: Optional[str]
            Format (defaults to mhtml).

    Returns
    -------
    data: str
            Serialized page data.

    **Experimental**
    """
    response = yield {
        "method": "Page.captureSnapshot",
        "params": filter_none({"format": format}),
    }
    return response["data"]


@deprecated(version=1.3)
def clear_device_metrics_override() -> dict:
    """Clears the overriden device metrics.

    **Experimental**
    """
    return {"method": "Page.clearDeviceMetricsOverride", "params": {}}


@deprecated(version=1.3)
def clear_device_orientation_override() -> dict:
    """Clears the overridden Device Orientation.

    **Experimental**
    """
    return {"method": "Page.clearDeviceOrientationOverride", "params": {}}


@deprecated(version=1.3)
def clear_geolocation_override() -> dict:
    """Clears the overriden Geolocation Position and Error."""
    return {"method": "Page.clearGeolocationOverride", "params": {}}


def create_isolated_world(
    frameId: FrameId,
    worldName: Optional[str] = None,
    grantUniveralAccess: Optional[bool] = None,
) -> Generator[dict, dict, runtime.ExecutionContextId]:
    """Creates an isolated world for the given frame.

    Parameters
    ----------
    frameId: FrameId
            Id of the frame in which the isolated world should be created.
    worldName: Optional[str]
            An optional name which is reported in the Execution Context.
    grantUniveralAccess: Optional[bool]
            Whether or not universal access should be granted to the isolated world. This is a powerful
            option, use with caution.

    Returns
    -------
    executionContextId: runtime.ExecutionContextId
            Execution context of the isolated world.
    """
    response = yield {
        "method": "Page.createIsolatedWorld",
        "params": filter_none(
            {
                "frameId": str(frameId),
                "worldName": worldName,
                "grantUniveralAccess": grantUniveralAccess,
            }
        ),
    }
    return runtime.ExecutionContextId(response["executionContextId"])


@deprecated(version=1.3)
def delete_cookie(cookieName: str, url: str) -> dict:
    """Deletes browser cookie with given name, domain and path.

    Parameters
    ----------
    cookieName: str
            Name of the cookie to remove.
    url: str
            URL to match cooke domain and path.

    **Experimental**
    """
    return {
        "method": "Page.deleteCookie",
        "params": {"cookieName": cookieName, "url": url},
    }


def disable() -> dict:
    """Disables page domain notifications."""
    return {"method": "Page.disable", "params": {}}


def enable() -> dict:
    """Enables page domain notifications."""
    return {"method": "Page.enable", "params": {}}


def get_app_manifest() -> Generator[dict, dict, dict]:
    """
    Returns
    -------
    url: str
            Manifest location.
    errors: list[AppManifestError]
    data: Optional[str]
            Manifest content.
    parsed: Optional[AppManifestParsedProperties]
            Parsed manifest properties
    """
    response = yield {"method": "Page.getAppManifest", "params": {}}
    return {
        "url": response["url"],
        "errors": [AppManifestError.from_json(e) for e in response["errors"]],
        "data": response.get("data"),
        "parsed": AppManifestParsedProperties.from_json(response["parsed"])
        if "parsed" in response
        else None,
    }


def get_installability_errors() -> Generator[dict, dict, list[InstallabilityError]]:
    """
    Returns
    -------
    installabilityErrors: list[InstallabilityError]

    **Experimental**
    """
    response = yield {"method": "Page.getInstallabilityErrors", "params": {}}
    return [InstallabilityError.from_json(i) for i in response["installabilityErrors"]]


def get_manifest_icons() -> Generator[dict, dict, Optional[str]]:
    """
    Returns
    -------
    primaryIcon: Optional[str]

    **Experimental**
    """
    response = yield {"method": "Page.getManifestIcons", "params": {}}
    return response.get("primaryIcon")


@deprecated(version=1.3)
def get_cookies() -> Generator[dict, dict, list[network.Cookie]]:
    """Returns all browser cookies. Depending on the backend support, will return detailed cookie
    information in the `cookies` field.

    Returns
    -------
    cookies: list[network.Cookie]
            Array of cookie objects.

    **Experimental**
    """
    response = yield {"method": "Page.getCookies", "params": {}}
    return [network.Cookie.from_json(c) for c in response["cookies"]]


def get_frame_tree() -> Generator[dict, dict, FrameTree]:
    """Returns present frame tree structure.

    Returns
    -------
    frameTree: FrameTree
            Present frame tree structure.
    """
    response = yield {"method": "Page.getFrameTree", "params": {}}
    return FrameTree.from_json(response["frameTree"])


def get_layout_metrics() -> Generator[dict, dict, dict]:
    """Returns metrics relating to the layouting of the page, such as viewport bounds/scale.

    Returns
    -------
    layoutViewport: LayoutViewport
            Metrics relating to the layout viewport.
    visualViewport: VisualViewport
            Metrics relating to the visual viewport.
    contentSize: dom.Rect
            Size of scrollable area.
    """
    response = yield {"method": "Page.getLayoutMetrics", "params": {}}
    return {
        "layoutViewport": LayoutViewport.from_json(response["layoutViewport"]),
        "visualViewport": VisualViewport.from_json(response["visualViewport"]),
        "contentSize": dom.Rect.from_json(response["contentSize"]),
    }


def get_navigation_history() -> Generator[dict, dict, dict]:
    """Returns navigation history for the current page.

    Returns
    -------
    currentIndex: int
            Index of the current navigation history entry.
    entries: list[NavigationEntry]
            Array of navigation history entries.
    """
    response = yield {"method": "Page.getNavigationHistory", "params": {}}
    return {
        "currentIndex": response["currentIndex"],
        "entries": [NavigationEntry.from_json(e) for e in response["entries"]],
    }


def reset_navigation_history() -> dict:
    """Resets navigation history for the current page."""
    return {"method": "Page.resetNavigationHistory", "params": {}}


def get_resource_content(frameId: FrameId, url: str) -> Generator[dict, dict, dict]:
    """Returns content of the given resource.

    Parameters
    ----------
    frameId: FrameId
            Frame id to get resource for.
    url: str
            URL of the resource to get content for.

    Returns
    -------
    content: str
            Resource content.
    base64Encoded: bool
            True, if content was served as base64.

    **Experimental**
    """
    response = yield {
        "method": "Page.getResourceContent",
        "params": {"frameId": str(frameId), "url": url},
    }
    return {"content": response["content"], "base64Encoded": response["base64Encoded"]}


def get_resource_tree() -> Generator[dict, dict, FrameResourceTree]:
    """Returns present frame / resource tree structure.

    Returns
    -------
    frameTree: FrameResourceTree
            Present frame / resource tree structure.

    **Experimental**
    """
    response = yield {"method": "Page.getResourceTree", "params": {}}
    return FrameResourceTree.from_json(response["frameTree"])


def handle_java_script_dialog(accept: bool, promptText: Optional[str] = None) -> dict:
    """Accepts or dismisses a JavaScript initiated dialog (alert, confirm, prompt, or onbeforeunload).

    Parameters
    ----------
    accept: bool
            Whether to accept or dismiss the dialog.
    promptText: Optional[str]
            The text to enter into the dialog prompt before accepting. Used only if this is a prompt
            dialog.
    """
    return {
        "method": "Page.handleJavaScriptDialog",
        "params": filter_none({"accept": accept, "promptText": promptText}),
    }


def navigate(
    url: str,
    referrer: Optional[str] = None,
    transitionType: Optional[TransitionType] = None,
    frameId: Optional[FrameId] = None,
    referrerPolicy: Optional[ReferrerPolicy] = None,
) -> Generator[dict, dict, dict]:
    """Navigates current page to the given URL.

    Parameters
    ----------
    url: str
            URL to navigate the page to.
    referrer: Optional[str]
            Referrer URL.
    transitionType: Optional[TransitionType]
            Intended transition type.
    frameId: Optional[FrameId]
            Frame id to navigate, if not specified navigates the top frame.
    referrerPolicy: Optional[ReferrerPolicy]
            Referrer-policy used for the navigation.

    Returns
    -------
    frameId: FrameId
            Frame id that has navigated (or failed to navigate)
    loaderId: Optional[network.LoaderId]
            Loader identifier.
    errorText: Optional[str]
            User friendly error message, present if and only if navigation has failed.
    """
    response = yield {
        "method": "Page.navigate",
        "params": filter_none(
            {
                "url": url,
                "referrer": referrer,
                "transitionType": transitionType.value if transitionType else None,
                "frameId": str(frameId) if frameId else None,
                "referrerPolicy": referrerPolicy.value if referrerPolicy else None,
            }
        ),
    }
    return {
        "frameId": FrameId(response["frameId"]),
        "loaderId": network.LoaderId(response["loaderId"])
        if "loaderId" in response
        else None,
        "errorText": response.get("errorText"),
    }


def navigate_to_history_entry(entryId: int) -> dict:
    """Navigates current page to the given history entry.

    Parameters
    ----------
    entryId: int
            Unique id of the entry to navigate to.
    """
    return {"method": "Page.navigateToHistoryEntry", "params": {"entryId": entryId}}


def print_to_pdf(
    landscape: Optional[bool] = None,
    displayHeaderFooter: Optional[bool] = None,
    printBackground: Optional[bool] = None,
    scale: Optional[float] = None,
    paperWidth: Optional[float] = None,
    paperHeight: Optional[float] = None,
    marginTop: Optional[float] = None,
    marginBottom: Optional[float] = None,
    marginLeft: Optional[float] = None,
    marginRight: Optional[float] = None,
    pageRanges: Optional[str] = None,
    ignoreInvalidPageRanges: Optional[bool] = None,
    headerTemplate: Optional[str] = None,
    footerTemplate: Optional[str] = None,
    preferCSSPageSize: Optional[bool] = None,
    transferMode: Optional[str] = None,
) -> Generator[dict, dict, dict]:
    """Print page as PDF.

    Parameters
    ----------
    landscape: Optional[bool]
            Paper orientation. Defaults to false.
    displayHeaderFooter: Optional[bool]
            Display header and footer. Defaults to false.
    printBackground: Optional[bool]
            Print background graphics. Defaults to false.
    scale: Optional[float]
            Scale of the webpage rendering. Defaults to 1.
    paperWidth: Optional[float]
            Paper width in inches. Defaults to 8.5 inches.
    paperHeight: Optional[float]
            Paper height in inches. Defaults to 11 inches.
    marginTop: Optional[float]
            Top margin in inches. Defaults to 1cm (~0.4 inches).
    marginBottom: Optional[float]
            Bottom margin in inches. Defaults to 1cm (~0.4 inches).
    marginLeft: Optional[float]
            Left margin in inches. Defaults to 1cm (~0.4 inches).
    marginRight: Optional[float]
            Right margin in inches. Defaults to 1cm (~0.4 inches).
    pageRanges: Optional[str]
            Paper ranges to print, e.g., '1-5, 8, 11-13'. Defaults to the empty string, which means
            print all pages.
    ignoreInvalidPageRanges: Optional[bool]
            Whether to silently ignore invalid but successfully parsed page ranges, such as '3-2'.
            Defaults to false.
    headerTemplate: Optional[str]
            HTML template for the print header. Should be valid HTML markup with following
            classes used to inject printing values into them:
            - `date`: formatted print date
            - `title`: document title
            - `url`: document location
            - `pageNumber`: current page number
            - `totalPages`: total pages in the document

            For example, `<span class=title></span>` would generate span containing the title.
    footerTemplate: Optional[str]
            HTML template for the print footer. Should use the same format as the `headerTemplate`.
    preferCSSPageSize: Optional[bool]
            Whether or not to prefer page size as defined by css. Defaults to false,
            in which case the content will be scaled to fit the paper size.
    transferMode: Optional[str]
            return as stream

    Returns
    -------
    data: str
            Base64-encoded pdf data. Empty if |returnAsStream| is specified. (Encoded as a base64 string when passed over JSON)
    stream: Optional[io.StreamHandle]
            A handle of the stream that holds resulting PDF data.
    """
    response = yield {
        "method": "Page.printToPDF",
        "params": filter_none(
            {
                "landscape": landscape,
                "displayHeaderFooter": displayHeaderFooter,
                "printBackground": printBackground,
                "scale": scale,
                "paperWidth": paperWidth,
                "paperHeight": paperHeight,
                "marginTop": marginTop,
                "marginBottom": marginBottom,
                "marginLeft": marginLeft,
                "marginRight": marginRight,
                "pageRanges": pageRanges,
                "ignoreInvalidPageRanges": ignoreInvalidPageRanges,
                "headerTemplate": headerTemplate,
                "footerTemplate": footerTemplate,
                "preferCSSPageSize": preferCSSPageSize,
                "transferMode": transferMode,
            }
        ),
    }
    return {
        "data": response["data"],
        "stream": io.StreamHandle(response["stream"]) if "stream" in response else None,
    }


def reload(
    ignoreCache: Optional[bool] = None, scriptToEvaluateOnLoad: Optional[str] = None
) -> dict:
    """Reloads given page optionally ignoring the cache.

    Parameters
    ----------
    ignoreCache: Optional[bool]
            If true, browser cache is ignored (as if the user pressed Shift+refresh).
    scriptToEvaluateOnLoad: Optional[str]
            If set, the script will be injected into all frames of the inspected page after reload.
            Argument will be ignored if reloading dataURL origin.
    """
    return {
        "method": "Page.reload",
        "params": filter_none(
            {
                "ignoreCache": ignoreCache,
                "scriptToEvaluateOnLoad": scriptToEvaluateOnLoad,
            }
        ),
    }


@deprecated(version=1.3)
def remove_script_to_evaluate_on_load(identifier: ScriptIdentifier) -> dict:
    """Deprecated, please use removeScriptToEvaluateOnNewDocument instead.

    Parameters
    ----------
    identifier: ScriptIdentifier

    **Experimental**
    """
    return {
        "method": "Page.removeScriptToEvaluateOnLoad",
        "params": {"identifier": str(identifier)},
    }


def remove_script_to_evaluate_on_new_document(identifier: ScriptIdentifier) -> dict:
    """Removes given script from the list.

    Parameters
    ----------
    identifier: ScriptIdentifier
    """
    return {
        "method": "Page.removeScriptToEvaluateOnNewDocument",
        "params": {"identifier": str(identifier)},
    }


def screencast_frame_ack(sessionId: int) -> dict:
    """Acknowledges that a screencast frame has been received by the frontend.

    Parameters
    ----------
    sessionId: int
            Frame number.

    **Experimental**
    """
    return {"method": "Page.screencastFrameAck", "params": {"sessionId": sessionId}}


def search_in_resource(
    frameId: FrameId,
    url: str,
    query: str,
    caseSensitive: Optional[bool] = None,
    isRegex: Optional[bool] = None,
) -> Generator[dict, dict, list[debugger.SearchMatch]]:
    """Searches for given string in resource content.

    Parameters
    ----------
    frameId: FrameId
            Frame id for resource to search in.
    url: str
            URL of the resource to search in.
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

    **Experimental**
    """
    response = yield {
        "method": "Page.searchInResource",
        "params": filter_none(
            {
                "frameId": str(frameId),
                "url": url,
                "query": query,
                "caseSensitive": caseSensitive,
                "isRegex": isRegex,
            }
        ),
    }
    return [debugger.SearchMatch.from_json(r) for r in response["result"]]


def set_ad_blocking_enabled(enabled: bool) -> dict:
    """Enable Chrome's experimental ad filter on all sites.

    Parameters
    ----------
    enabled: bool
            Whether to block ads.

    **Experimental**
    """
    return {"method": "Page.setAdBlockingEnabled", "params": {"enabled": enabled}}


def set_bypass_csp(enabled: bool) -> dict:
    """Enable page Content Security Policy by-passing.

    Parameters
    ----------
    enabled: bool
            Whether to bypass page CSP.

    **Experimental**
    """
    return {"method": "Page.setBypassCSP", "params": {"enabled": enabled}}


@deprecated(version=1.3)
def set_device_metrics_override(
    width: int,
    height: int,
    deviceScaleFactor: float,
    mobile: bool,
    scale: Optional[float] = None,
    screenWidth: Optional[int] = None,
    screenHeight: Optional[int] = None,
    positionX: Optional[int] = None,
    positionY: Optional[int] = None,
    dontSetVisibleSize: Optional[bool] = None,
    screenOrientation: Optional[emulation.ScreenOrientation] = None,
    viewport: Optional[Viewport] = None,
) -> dict:
    """Overrides the values of device screen dimensions (window.screen.width, window.screen.height,
    window.innerWidth, window.innerHeight, and "device-width"/"device-height"-related CSS media
    query results).

    Parameters
    ----------
    width: int
            Overriding width value in pixels (minimum 0, maximum 10000000). 0 disables the override.
    height: int
            Overriding height value in pixels (minimum 0, maximum 10000000). 0 disables the override.
    deviceScaleFactor: float
            Overriding device scale factor value. 0 disables the override.
    mobile: bool
            Whether to emulate mobile device. This includes viewport meta tag, overlay scrollbars, text
            autosizing and more.
    scale: Optional[float]
            Scale to apply to resulting view image.
    screenWidth: Optional[int]
            Overriding screen width value in pixels (minimum 0, maximum 10000000).
    screenHeight: Optional[int]
            Overriding screen height value in pixels (minimum 0, maximum 10000000).
    positionX: Optional[int]
            Overriding view X position on screen in pixels (minimum 0, maximum 10000000).
    positionY: Optional[int]
            Overriding view Y position on screen in pixels (minimum 0, maximum 10000000).
    dontSetVisibleSize: Optional[bool]
            Do not set visible view size, rely upon explicit setVisibleSize call.
    screenOrientation: Optional[emulation.ScreenOrientation]
            Screen orientation override.
    viewport: Optional[Viewport]
            The viewport dimensions and scale. If not set, the override is cleared.

    **Experimental**
    """
    return {
        "method": "Page.setDeviceMetricsOverride",
        "params": filter_none(
            {
                "width": width,
                "height": height,
                "deviceScaleFactor": deviceScaleFactor,
                "mobile": mobile,
                "scale": scale,
                "screenWidth": screenWidth,
                "screenHeight": screenHeight,
                "positionX": positionX,
                "positionY": positionY,
                "dontSetVisibleSize": dontSetVisibleSize,
                "screenOrientation": screenOrientation.to_json()
                if screenOrientation
                else None,
                "viewport": viewport.to_json() if viewport else None,
            }
        ),
    }


@deprecated(version=1.3)
def set_device_orientation_override(alpha: float, beta: float, gamma: float) -> dict:
    """Overrides the Device Orientation.

    Parameters
    ----------
    alpha: float
            Mock alpha
    beta: float
            Mock beta
    gamma: float
            Mock gamma

    **Experimental**
    """
    return {
        "method": "Page.setDeviceOrientationOverride",
        "params": {"alpha": alpha, "beta": beta, "gamma": gamma},
    }


def set_font_families(fontFamilies: FontFamilies) -> dict:
    """Set generic font families.

    Parameters
    ----------
    fontFamilies: FontFamilies
            Specifies font families to set. If a font family is not specified, it won't be changed.

    **Experimental**
    """
    return {
        "method": "Page.setFontFamilies",
        "params": {"fontFamilies": fontFamilies.to_json()},
    }


def set_font_sizes(fontSizes: FontSizes) -> dict:
    """Set default font sizes.

    Parameters
    ----------
    fontSizes: FontSizes
            Specifies font sizes to set. If a font size is not specified, it won't be changed.

    **Experimental**
    """
    return {"method": "Page.setFontSizes", "params": {"fontSizes": fontSizes.to_json()}}


def set_document_content(frameId: FrameId, html: str) -> dict:
    """Sets given markup as the document's HTML.

    Parameters
    ----------
    frameId: FrameId
            Frame id to set HTML for.
    html: str
            HTML content to set.
    """
    return {
        "method": "Page.setDocumentContent",
        "params": {"frameId": str(frameId), "html": html},
    }


@deprecated(version=1.3)
def set_download_behavior(behavior: str, downloadPath: Optional[str] = None) -> dict:
    """Set the behavior when downloading a file.

    Parameters
    ----------
    behavior: str
            Whether to allow all or deny all download requests, or use default Chrome behavior if
            available (otherwise deny).
    downloadPath: Optional[str]
            The default path to save downloaded files to. This is requred if behavior is set to 'allow'

    **Experimental**
    """
    return {
        "method": "Page.setDownloadBehavior",
        "params": filter_none({"behavior": behavior, "downloadPath": downloadPath}),
    }


@deprecated(version=1.3)
def set_geolocation_override(
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    accuracy: Optional[float] = None,
) -> dict:
    """Overrides the Geolocation Position or Error. Omitting any of the parameters emulates position
    unavailable.

    Parameters
    ----------
    latitude: Optional[float]
            Mock latitude
    longitude: Optional[float]
            Mock longitude
    accuracy: Optional[float]
            Mock accuracy
    """
    return {
        "method": "Page.setGeolocationOverride",
        "params": filter_none(
            {"latitude": latitude, "longitude": longitude, "accuracy": accuracy}
        ),
    }


def set_lifecycle_events_enabled(enabled: bool) -> dict:
    """Controls whether page will emit lifecycle events.

    Parameters
    ----------
    enabled: bool
            If true, starts emitting lifecycle events.

    **Experimental**
    """
    return {"method": "Page.setLifecycleEventsEnabled", "params": {"enabled": enabled}}


@deprecated(version=1.3)
def set_touch_emulation_enabled(
    enabled: bool, configuration: Optional[str] = None
) -> dict:
    """Toggles mouse event-based touch event emulation.

    Parameters
    ----------
    enabled: bool
            Whether the touch event emulation should be enabled.
    configuration: Optional[str]
            Touch/gesture events configuration. Default: current platform.

    **Experimental**
    """
    return {
        "method": "Page.setTouchEmulationEnabled",
        "params": filter_none({"enabled": enabled, "configuration": configuration}),
    }


def start_screencast(
    format: Optional[str] = None,
    quality: Optional[int] = None,
    maxWidth: Optional[int] = None,
    maxHeight: Optional[int] = None,
    everyNthFrame: Optional[int] = None,
) -> dict:
    """Starts sending each frame using the `screencastFrame` event.

    Parameters
    ----------
    format: Optional[str]
            Image compression format.
    quality: Optional[int]
            Compression quality from range [0..100].
    maxWidth: Optional[int]
            Maximum screenshot width.
    maxHeight: Optional[int]
            Maximum screenshot height.
    everyNthFrame: Optional[int]
            Send every n-th frame.

    **Experimental**
    """
    return {
        "method": "Page.startScreencast",
        "params": filter_none(
            {
                "format": format,
                "quality": quality,
                "maxWidth": maxWidth,
                "maxHeight": maxHeight,
                "everyNthFrame": everyNthFrame,
            }
        ),
    }


def stop_loading() -> dict:
    """Force the page stop all navigations and pending resource fetches."""
    return {"method": "Page.stopLoading", "params": {}}


def crash() -> dict:
    """Crashes renderer on the IO thread, generates minidumps.

    **Experimental**
    """
    return {"method": "Page.crash", "params": {}}


def close() -> dict:
    """Tries to close page, running its beforeunload hooks, if any.

    **Experimental**
    """
    return {"method": "Page.close", "params": {}}


def set_web_lifecycle_state(state: str) -> dict:
    """Tries to update the web lifecycle state of the page.
    It will transition the page to the given state according to:
    https://github.com/WICG/web-lifecycle/

    Parameters
    ----------
    state: str
            Target lifecycle state

    **Experimental**
    """
    return {"method": "Page.setWebLifecycleState", "params": {"state": state}}


def stop_screencast() -> dict:
    """Stops sending each frame in the `screencastFrame`.

    **Experimental**
    """
    return {"method": "Page.stopScreencast", "params": {}}


def set_produce_compilation_cache(enabled: bool) -> dict:
    """Forces compilation cache to be generated for every subresource script.

    Parameters
    ----------
    enabled: bool

    **Experimental**
    """
    return {"method": "Page.setProduceCompilationCache", "params": {"enabled": enabled}}


def add_compilation_cache(url: str, data: str) -> dict:
    """Seeds compilation cache for given url. Compilation cache does not survive
    cross-process navigation.

    Parameters
    ----------
    url: str
    data: str
            Base64-encoded data (Encoded as a base64 string when passed over JSON)

    **Experimental**
    """
    return {"method": "Page.addCompilationCache", "params": {"url": url, "data": data}}


def clear_compilation_cache() -> dict:
    """Clears seeded compilation cache.

    **Experimental**
    """
    return {"method": "Page.clearCompilationCache", "params": {}}


def generate_test_report(message: str, group: Optional[str] = None) -> dict:
    """Generates a report for testing.

    Parameters
    ----------
    message: str
            Message to be displayed in the report.
    group: Optional[str]
            Specifies the endpoint group to deliver the report to.

    **Experimental**
    """
    return {
        "method": "Page.generateTestReport",
        "params": filter_none({"message": message, "group": group}),
    }


def wait_for_debugger() -> dict:
    """Pauses page execution. Can be resumed using generic Runtime.runIfWaitingForDebugger.

    **Experimental**
    """
    return {"method": "Page.waitForDebugger", "params": {}}


def set_intercept_file_chooser_dialog(enabled: bool) -> dict:
    """Intercept file chooser requests and transfer control to protocol clients.
    When file chooser interception is enabled, native file chooser dialog is not shown.
    Instead, a protocol event `Page.fileChooserOpened` is emitted.

    Parameters
    ----------
    enabled: bool

    **Experimental**
    """
    return {
        "method": "Page.setInterceptFileChooserDialog",
        "params": {"enabled": enabled},
    }


@dataclasses.dataclass
class DomContentEventFired:
    """
    Attributes
    ----------
    timestamp: network.MonotonicTime
    """

    timestamp: network.MonotonicTime

    @classmethod
    def from_json(cls, json: dict) -> DomContentEventFired:
        return cls(network.MonotonicTime(json["timestamp"]))


@dataclasses.dataclass
class FileChooserOpened:
    """Emitted only when `page.interceptFileChooser` is enabled.

    Attributes
    ----------
    frameId: FrameId
            Id of the frame containing input node.
    backendNodeId: dom.BackendNodeId
            Input node id.
    mode: str
            Input mode.
    """

    frameId: FrameId
    backendNodeId: dom.BackendNodeId
    mode: str

    @classmethod
    def from_json(cls, json: dict) -> FileChooserOpened:
        return cls(
            FrameId(json["frameId"]),
            dom.BackendNodeId(json["backendNodeId"]),
            json["mode"],
        )


@dataclasses.dataclass
class FrameAttached:
    """Fired when frame has been attached to its parent.

    Attributes
    ----------
    frameId: FrameId
            Id of the frame that has been attached.
    parentFrameId: FrameId
            Parent frame identifier.
    stack: Optional[runtime.StackTrace]
            JavaScript stack trace of when frame was attached, only set if frame initiated from script.
    """

    frameId: FrameId
    parentFrameId: FrameId
    stack: Optional[runtime.StackTrace] = None

    @classmethod
    def from_json(cls, json: dict) -> FrameAttached:
        return cls(
            FrameId(json["frameId"]),
            FrameId(json["parentFrameId"]),
            runtime.StackTrace.from_json(json["stack"]) if "stack" in json else None,
        )


@dataclasses.dataclass
class FrameClearedScheduledNavigation:
    """Fired when frame no longer has a scheduled navigation.

    Attributes
    ----------
    frameId: FrameId
            Id of the frame that has cleared its scheduled navigation.
    """

    frameId: FrameId

    @classmethod
    def from_json(cls, json: dict) -> FrameClearedScheduledNavigation:
        return cls(FrameId(json["frameId"]))


@dataclasses.dataclass
class FrameDetached:
    """Fired when frame has been detached from its parent.

    Attributes
    ----------
    frameId: FrameId
            Id of the frame that has been detached.
    reason: str
    """

    frameId: FrameId
    reason: str

    @classmethod
    def from_json(cls, json: dict) -> FrameDetached:
        return cls(FrameId(json["frameId"]), json["reason"])


@dataclasses.dataclass
class FrameNavigated:
    """Fired once navigation of the frame has completed. Frame is now associated with the new loader.

    Attributes
    ----------
    frame: Frame
            Frame object.
    """

    frame: Frame

    @classmethod
    def from_json(cls, json: dict) -> FrameNavigated:
        return cls(Frame.from_json(json["frame"]))


@dataclasses.dataclass
class DocumentOpened:
    """Fired when opening document to write to.

    Attributes
    ----------
    frame: Frame
            Frame object.
    """

    frame: Frame

    @classmethod
    def from_json(cls, json: dict) -> DocumentOpened:
        return cls(Frame.from_json(json["frame"]))


@dataclasses.dataclass
class FrameResized:
    """"""

    @classmethod
    def from_json(cls, json: dict) -> FrameResized:
        return cls()


@dataclasses.dataclass
class FrameRequestedNavigation:
    """Fired when a renderer-initiated navigation is requested.
    Navigation may still be cancelled after the event is issued.

    Attributes
    ----------
    frameId: FrameId
            Id of the frame that is being navigated.
    reason: ClientNavigationReason
            The reason for the navigation.
    url: str
            The destination URL for the requested navigation.
    disposition: ClientNavigationDisposition
            The disposition for the navigation.
    """

    frameId: FrameId
    reason: ClientNavigationReason
    url: str
    disposition: ClientNavigationDisposition

    @classmethod
    def from_json(cls, json: dict) -> FrameRequestedNavigation:
        return cls(
            FrameId(json["frameId"]),
            ClientNavigationReason(json["reason"]),
            json["url"],
            ClientNavigationDisposition(json["disposition"]),
        )


@dataclasses.dataclass
class FrameScheduledNavigation:
    """Fired when frame schedules a potential navigation.

    Attributes
    ----------
    frameId: FrameId
            Id of the frame that has scheduled a navigation.
    delay: float
            Delay (in seconds) until the navigation is scheduled to begin. The navigation is not
            guaranteed to start.
    reason: ClientNavigationReason
            The reason for the navigation.
    url: str
            The destination URL for the scheduled navigation.
    """

    frameId: FrameId
    delay: float
    reason: ClientNavigationReason
    url: str

    @classmethod
    def from_json(cls, json: dict) -> FrameScheduledNavigation:
        return cls(
            FrameId(json["frameId"]),
            json["delay"],
            ClientNavigationReason(json["reason"]),
            json["url"],
        )


@dataclasses.dataclass
class FrameStartedLoading:
    """Fired when frame has started loading.

    Attributes
    ----------
    frameId: FrameId
            Id of the frame that has started loading.
    """

    frameId: FrameId

    @classmethod
    def from_json(cls, json: dict) -> FrameStartedLoading:
        return cls(FrameId(json["frameId"]))


@dataclasses.dataclass
class FrameStoppedLoading:
    """Fired when frame has stopped loading.

    Attributes
    ----------
    frameId: FrameId
            Id of the frame that has stopped loading.
    """

    frameId: FrameId

    @classmethod
    def from_json(cls, json: dict) -> FrameStoppedLoading:
        return cls(FrameId(json["frameId"]))


@dataclasses.dataclass
class DownloadWillBegin:
    """Fired when page is about to start a download.

    Attributes
    ----------
    frameId: FrameId
            Id of the frame that caused download to begin.
    guid: str
            Global unique identifier of the download.
    url: str
            URL of the resource being downloaded.
    suggestedFilename: str
            Suggested file name of the resource (the actual name of the file saved on disk may differ).
    """

    frameId: FrameId
    guid: str
    url: str
    suggestedFilename: str

    @classmethod
    def from_json(cls, json: dict) -> DownloadWillBegin:
        return cls(
            FrameId(json["frameId"]),
            json["guid"],
            json["url"],
            json["suggestedFilename"],
        )


@dataclasses.dataclass
class DownloadProgress:
    """Fired when download makes progress. Last call has |done| == true.

    Attributes
    ----------
    guid: str
            Global unique identifier of the download.
    totalBytes: float
            Total expected bytes to download.
    receivedBytes: float
            Total bytes received.
    state: str
            Download status.
    """

    guid: str
    totalBytes: float
    receivedBytes: float
    state: str

    @classmethod
    def from_json(cls, json: dict) -> DownloadProgress:
        return cls(
            json["guid"], json["totalBytes"], json["receivedBytes"], json["state"]
        )


@dataclasses.dataclass
class InterstitialHidden:
    """Fired when interstitial page was hidden"""

    @classmethod
    def from_json(cls, json: dict) -> InterstitialHidden:
        return cls()


@dataclasses.dataclass
class InterstitialShown:
    """Fired when interstitial page was shown"""

    @classmethod
    def from_json(cls, json: dict) -> InterstitialShown:
        return cls()


@dataclasses.dataclass
class JavascriptDialogClosed:
    """Fired when a JavaScript initiated dialog (alert, confirm, prompt, or onbeforeunload) has been
    closed.

    Attributes
    ----------
    result: bool
            Whether dialog was confirmed.
    userInput: str
            User input in case of prompt.
    """

    result: bool
    userInput: str

    @classmethod
    def from_json(cls, json: dict) -> JavascriptDialogClosed:
        return cls(json["result"], json["userInput"])


@dataclasses.dataclass
class JavascriptDialogOpening:
    """Fired when a JavaScript initiated dialog (alert, confirm, prompt, or onbeforeunload) is about to
    open.

    Attributes
    ----------
    url: str
            Frame url.
    message: str
            Message that will be displayed by the dialog.
    type: DialogType
            Dialog type.
    hasBrowserHandler: bool
            True iff browser is capable showing or acting on the given dialog. When browser has no
            dialog handler for given target, calling alert while Page domain is engaged will stall
            the page execution. Execution can be resumed via calling Page.handleJavaScriptDialog.
    defaultPrompt: Optional[str]
            Default dialog prompt.
    """

    url: str
    message: str
    type: DialogType
    hasBrowserHandler: bool
    defaultPrompt: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> JavascriptDialogOpening:
        return cls(
            json["url"],
            json["message"],
            DialogType(json["type"]),
            json["hasBrowserHandler"],
            json.get("defaultPrompt"),
        )


@dataclasses.dataclass
class LifecycleEvent:
    """Fired for top level page lifecycle events such as navigation, load, paint, etc.

    Attributes
    ----------
    frameId: FrameId
            Id of the frame.
    loaderId: network.LoaderId
            Loader identifier. Empty string if the request is fetched from worker.
    name: str
    timestamp: network.MonotonicTime
    """

    frameId: FrameId
    loaderId: network.LoaderId
    name: str
    timestamp: network.MonotonicTime

    @classmethod
    def from_json(cls, json: dict) -> LifecycleEvent:
        return cls(
            FrameId(json["frameId"]),
            network.LoaderId(json["loaderId"]),
            json["name"],
            network.MonotonicTime(json["timestamp"]),
        )


@dataclasses.dataclass
class LoadEventFired:
    """
    Attributes
    ----------
    timestamp: network.MonotonicTime
    """

    timestamp: network.MonotonicTime

    @classmethod
    def from_json(cls, json: dict) -> LoadEventFired:
        return cls(network.MonotonicTime(json["timestamp"]))


@dataclasses.dataclass
class NavigatedWithinDocument:
    """Fired when same-document navigation happens, e.g. due to history API usage or anchor navigation.

    Attributes
    ----------
    frameId: FrameId
            Id of the frame.
    url: str
            Frame's new url.
    """

    frameId: FrameId
    url: str

    @classmethod
    def from_json(cls, json: dict) -> NavigatedWithinDocument:
        return cls(FrameId(json["frameId"]), json["url"])


@dataclasses.dataclass
class ScreencastFrame:
    """Compressed image data requested by the `startScreencast`.

    Attributes
    ----------
    data: str
            Base64-encoded compressed image. (Encoded as a base64 string when passed over JSON)
    metadata: ScreencastFrameMetadata
            Screencast frame metadata.
    sessionId: int
            Frame number.
    """

    data: str
    metadata: ScreencastFrameMetadata
    sessionId: int

    @classmethod
    def from_json(cls, json: dict) -> ScreencastFrame:
        return cls(
            json["data"],
            ScreencastFrameMetadata.from_json(json["metadata"]),
            json["sessionId"],
        )


@dataclasses.dataclass
class ScreencastVisibilityChanged:
    """Fired when the page with currently enabled screencast was shown or hidden `.

    Attributes
    ----------
    visible: bool
            True if the page is visible.
    """

    visible: bool

    @classmethod
    def from_json(cls, json: dict) -> ScreencastVisibilityChanged:
        return cls(json["visible"])


@dataclasses.dataclass
class WindowOpen:
    """Fired when a new window is going to be opened, via window.open(), link click, form submission,
    etc.

    Attributes
    ----------
    url: str
            The URL for the new window.
    windowName: str
            Window name.
    windowFeatures: list[str]
            An array of enabled window features.
    userGesture: bool
            Whether or not it was triggered by user gesture.
    """

    url: str
    windowName: str
    windowFeatures: list[str]
    userGesture: bool

    @classmethod
    def from_json(cls, json: dict) -> WindowOpen:
        return cls(
            json["url"], json["windowName"], json["windowFeatures"], json["userGesture"]
        )


@dataclasses.dataclass
class CompilationCacheProduced:
    """Issued for every compilation cache generated. Is only available
    if Page.setGenerateCompilationCache is enabled.

    Attributes
    ----------
    url: str
    data: str
            Base64-encoded data (Encoded as a base64 string when passed over JSON)
    """

    url: str
    data: str

    @classmethod
    def from_json(cls, json: dict) -> CompilationCacheProduced:
        return cls(json["url"], json["data"])
