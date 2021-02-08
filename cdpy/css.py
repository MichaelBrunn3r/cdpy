from __future__ import annotations

import dataclasses
import enum
from typing import Optional

from . import dom, page
from .common import Type, filter_unset_parameters


class StyleSheetId(str):
    """"""

    def __repr__(self):
        return f"StyleSheetId({super().__repr__()})"


class StyleSheetOrigin(enum.Enum):
    """Stylesheet type: "injected" for stylesheets injected via extension, "user-agent" for user-agent
    stylesheets, "inspector" for stylesheets created by the inspector (i.e. those holding the "via
    inspector" rules), "regular" for regular stylesheets.
    """

    INJECTED = "injected"
    USER_AGENT = "user-agent"
    INSPECTOR = "inspector"
    REGULAR = "regular"


@dataclasses.dataclass
class PseudoElementMatches(Type):
    """CSS rule collection for a single pseudo style.

    Attributes
    ----------
    pseudoType: dom.PseudoType
            Pseudo element type.
    matches: list[RuleMatch]
            Matches of CSS rules applicable to the pseudo style.
    """

    pseudoType: dom.PseudoType
    matches: list[RuleMatch]

    @classmethod
    def from_json(cls, json: dict) -> PseudoElementMatches:
        return cls(
            dom.PseudoType(json["pseudoType"]),
            [RuleMatch.from_json(x) for x in json["matches"]],
        )


@dataclasses.dataclass
class InheritedStyleEntry(Type):
    """Inherited CSS rule collection from ancestor node.

    Attributes
    ----------
    matchedCSSRules: list[RuleMatch]
            Matches of CSS rules matching the ancestor node in the style inheritance chain.
    inlineStyle: Optional[CSSStyle] = None
            The ancestor node's inline style, if any, in the style inheritance chain.
    """

    matchedCSSRules: list[RuleMatch]
    inlineStyle: Optional[CSSStyle] = None

    @classmethod
    def from_json(cls, json: dict) -> InheritedStyleEntry:
        return cls(
            [RuleMatch.from_json(x) for x in json["matchedCSSRules"]],
            CSSStyle.from_json(json["inlineStyle"]) if "inlineStyle" in json else None,
        )


@dataclasses.dataclass
class RuleMatch(Type):
    """Match data for a CSS rule.

    Attributes
    ----------
    rule: CSSRule
            CSS rule in the match.
    matchingSelectors: list[int]
            Matching selector indices in the rule's selectorList selectors (0-based).
    """

    rule: CSSRule
    matchingSelectors: list[int]

    @classmethod
    def from_json(cls, json: dict) -> RuleMatch:
        return cls(CSSRule.from_json(json["rule"]), json["matchingSelectors"])


@dataclasses.dataclass
class Value(Type):
    """Data for a simple selector (these are delimited by commas in a selector list).

    Attributes
    ----------
    text: str
            Value text.
    range: Optional[SourceRange] = None
            Value range in the underlying resource (if available).
    """

    text: str
    range: Optional[SourceRange] = None

    @classmethod
    def from_json(cls, json: dict) -> Value:
        return cls(
            json["text"],
            SourceRange.from_json(json["range"]) if "range" in json else None,
        )


@dataclasses.dataclass
class SelectorList(Type):
    """Selector list data.

    Attributes
    ----------
    selectors: list[Value]
            Selectors in the list.
    text: str
            Rule selector text.
    """

    selectors: list[Value]
    text: str

    @classmethod
    def from_json(cls, json: dict) -> SelectorList:
        return cls([Value.from_json(x) for x in json["selectors"]], json["text"])


@dataclasses.dataclass
class CSSStyleSheetHeader(Type):
    """CSS stylesheet metainformation.

    Attributes
    ----------
    styleSheetId: StyleSheetId
            The stylesheet identifier.
    frameId: page.FrameId
            Owner frame identifier.
    sourceURL: str
            Stylesheet resource URL.
    origin: StyleSheetOrigin
            Stylesheet origin.
    title: str
            Stylesheet title.
    disabled: bool
            Denotes whether the stylesheet is disabled.
    isInline: bool
            Whether this stylesheet is created for STYLE tag by parser. This flag is not set for
            document.written STYLE tags.
    isMutable: bool
            Whether this stylesheet is mutable. Inline stylesheets become mutable
            after they have been modified via CSSOM API.
            <link> element's stylesheets become mutable only if DevTools modifies them.
            Constructed stylesheets (new CSSStyleSheet()) are mutable immediately after creation.
    isConstructed: bool
            Whether this stylesheet is a constructed stylesheet (created using new CSSStyleSheet()).
    startLine: float
            Line offset of the stylesheet within the resource (zero based).
    startColumn: float
            Column offset of the stylesheet within the resource (zero based).
    length: float
            Size of the content (in characters).
    endLine: float
            Line offset of the end of the stylesheet within the resource (zero based).
    endColumn: float
            Column offset of the end of the stylesheet within the resource (zero based).
    sourceMapURL: Optional[str] = None
            URL of source map associated with the stylesheet (if any).
    ownerNode: Optional[dom.BackendNodeId] = None
            The backend id for the owner node of the stylesheet.
    hasSourceURL: Optional[bool] = None
            Whether the sourceURL field value comes from the sourceURL comment.
    """

    styleSheetId: StyleSheetId
    frameId: page.FrameId
    sourceURL: str
    origin: StyleSheetOrigin
    title: str
    disabled: bool
    isInline: bool
    isMutable: bool
    isConstructed: bool
    startLine: float
    startColumn: float
    length: float
    endLine: float
    endColumn: float
    sourceMapURL: Optional[str] = None
    ownerNode: Optional[dom.BackendNodeId] = None
    hasSourceURL: Optional[bool] = None

    @classmethod
    def from_json(cls, json: dict) -> CSSStyleSheetHeader:
        return cls(
            StyleSheetId(json["styleSheetId"]),
            page.FrameId(json["frameId"]),
            json["sourceURL"],
            StyleSheetOrigin(json["origin"]),
            json["title"],
            json["disabled"],
            json["isInline"],
            json["isMutable"],
            json["isConstructed"],
            json["startLine"],
            json["startColumn"],
            json["length"],
            json["endLine"],
            json["endColumn"],
            json.get("sourceMapURL"),
            dom.BackendNodeId(json["ownerNode"]) if "ownerNode" in json else None,
            json.get("hasSourceURL"),
        )


@dataclasses.dataclass
class CSSRule(Type):
    """CSS rule representation.

    Attributes
    ----------
    selectorList: SelectorList
            Rule selector data.
    origin: StyleSheetOrigin
            Parent stylesheet's origin.
    style: CSSStyle
            Associated style declaration.
    styleSheetId: Optional[StyleSheetId] = None
            The css style sheet identifier (absent for user agent stylesheet and user-specified
            stylesheet rules) this rule came from.
    media: Optional[list[CSSMedia]] = None
            Media list array (for rules involving media queries). The array enumerates media queries
            starting with the innermost one, going outwards.
    """

    selectorList: SelectorList
    origin: StyleSheetOrigin
    style: CSSStyle
    styleSheetId: Optional[StyleSheetId] = None
    media: Optional[list[CSSMedia]] = None

    @classmethod
    def from_json(cls, json: dict) -> CSSRule:
        return cls(
            SelectorList.from_json(json["selectorList"]),
            StyleSheetOrigin(json["origin"]),
            CSSStyle.from_json(json["style"]),
            StyleSheetId(json["styleSheetId"]) if "styleSheetId" in json else None,
            [CSSMedia.from_json(x) for x in json["media"]] if "media" in json else None,
        )


@dataclasses.dataclass
class RuleUsage(Type):
    """CSS coverage information.

    Attributes
    ----------
    styleSheetId: StyleSheetId
            The css style sheet identifier (absent for user agent stylesheet and user-specified
            stylesheet rules) this rule came from.
    startOffset: float
            Offset of the start of the rule (including selector) from the beginning of the stylesheet.
    endOffset: float
            Offset of the end of the rule body from the beginning of the stylesheet.
    used: bool
            Indicates whether the rule was actually used by some element in the page.
    """

    styleSheetId: StyleSheetId
    startOffset: float
    endOffset: float
    used: bool

    @classmethod
    def from_json(cls, json: dict) -> RuleUsage:
        return cls(
            StyleSheetId(json["styleSheetId"]),
            json["startOffset"],
            json["endOffset"],
            json["used"],
        )


@dataclasses.dataclass
class SourceRange(Type):
    """Text range within a resource. All numbers are zero-based.

    Attributes
    ----------
    startLine: int
            Start line of range.
    startColumn: int
            Start column of range (inclusive).
    endLine: int
            End line of range
    endColumn: int
            End column of range (exclusive).
    """

    startLine: int
    startColumn: int
    endLine: int
    endColumn: int

    @classmethod
    def from_json(cls, json: dict) -> SourceRange:
        return cls(
            json["startLine"], json["startColumn"], json["endLine"], json["endColumn"]
        )


@dataclasses.dataclass
class ShorthandEntry(Type):
    """
    Attributes
    ----------
    name: str
            Shorthand name.
    value: str
            Shorthand value.
    important: Optional[bool] = None
            Whether the property has "!important" annotation (implies `false` if absent).
    """

    name: str
    value: str
    important: Optional[bool] = None

    @classmethod
    def from_json(cls, json: dict) -> ShorthandEntry:
        return cls(json["name"], json["value"], json.get("important"))


@dataclasses.dataclass
class CSSComputedStyleProperty(Type):
    """
    Attributes
    ----------
    name: str
            Computed style property name.
    value: str
            Computed style property value.
    """

    name: str
    value: str

    @classmethod
    def from_json(cls, json: dict) -> CSSComputedStyleProperty:
        return cls(json["name"], json["value"])


@dataclasses.dataclass
class CSSStyle(Type):
    """CSS style representation.

    Attributes
    ----------
    cssProperties: list[CSSProperty]
            CSS properties in the style.
    shorthandEntries: list[ShorthandEntry]
            Computed values for all shorthands found in the style.
    styleSheetId: Optional[StyleSheetId] = None
            The css style sheet identifier (absent for user agent stylesheet and user-specified
            stylesheet rules) this rule came from.
    cssText: Optional[str] = None
            Style declaration text (if available).
    range: Optional[SourceRange] = None
            Style declaration range in the enclosing stylesheet (if available).
    """

    cssProperties: list[CSSProperty]
    shorthandEntries: list[ShorthandEntry]
    styleSheetId: Optional[StyleSheetId] = None
    cssText: Optional[str] = None
    range: Optional[SourceRange] = None

    @classmethod
    def from_json(cls, json: dict) -> CSSStyle:
        return cls(
            [CSSProperty.from_json(x) for x in json["cssProperties"]],
            [ShorthandEntry.from_json(x) for x in json["shorthandEntries"]],
            StyleSheetId(json["styleSheetId"]) if "styleSheetId" in json else None,
            json.get("cssText"),
            SourceRange.from_json(json["range"]) if "range" in json else None,
        )


@dataclasses.dataclass
class CSSProperty(Type):
    """CSS property declaration data.

    Attributes
    ----------
    name: str
            The property name.
    value: str
            The property value.
    important: Optional[bool] = None
            Whether the property has "!important" annotation (implies `false` if absent).
    implicit: Optional[bool] = None
            Whether the property is implicit (implies `false` if absent).
    text: Optional[str] = None
            The full property text as specified in the style.
    parsedOk: Optional[bool] = None
            Whether the property is understood by the browser (implies `true` if absent).
    disabled: Optional[bool] = None
            Whether the property is disabled by the user (present for source-based properties only).
    range: Optional[SourceRange] = None
            The entire property range in the enclosing style declaration (if available).
    """

    name: str
    value: str
    important: Optional[bool] = None
    implicit: Optional[bool] = None
    text: Optional[str] = None
    parsedOk: Optional[bool] = None
    disabled: Optional[bool] = None
    range: Optional[SourceRange] = None

    @classmethod
    def from_json(cls, json: dict) -> CSSProperty:
        return cls(
            json["name"],
            json["value"],
            json.get("important"),
            json.get("implicit"),
            json.get("text"),
            json.get("parsedOk"),
            json.get("disabled"),
            SourceRange.from_json(json["range"]) if "range" in json else None,
        )


@dataclasses.dataclass
class CSSMedia(Type):
    """CSS media rule descriptor.

    Attributes
    ----------
    text: str
            Media query text.
    source: str
            Source of the media query: "mediaRule" if specified by a @media rule, "importRule" if
            specified by an @import rule, "linkedSheet" if specified by a "media" attribute in a linked
            stylesheet's LINK tag, "inlineSheet" if specified by a "media" attribute in an inline
            stylesheet's STYLE tag.
    sourceURL: Optional[str] = None
            URL of the document containing the media query description.
    range: Optional[SourceRange] = None
            The associated rule (@media or @import) header range in the enclosing stylesheet (if
            available).
    styleSheetId: Optional[StyleSheetId] = None
            Identifier of the stylesheet containing this object (if exists).
    mediaList: Optional[list[MediaQuery]] = None
            Array of media queries.
    """

    text: str
    source: str
    sourceURL: Optional[str] = None
    range: Optional[SourceRange] = None
    styleSheetId: Optional[StyleSheetId] = None
    mediaList: Optional[list[MediaQuery]] = None

    @classmethod
    def from_json(cls, json: dict) -> CSSMedia:
        return cls(
            json["text"],
            json.get("sourceURL"),
            SourceRange.from_json(json["range"]) if "range" in json else None,
            StyleSheetId(json["styleSheetId"]) if "styleSheetId" in json else None,
            [MediaQuery.from_json(x) for x in json["mediaList"]]
            if "mediaList" in json
            else None,
        )


@dataclasses.dataclass
class MediaQuery(Type):
    """Media query descriptor.

    Attributes
    ----------
    expressions: list[MediaQueryExpression]
            Array of media query expressions.
    active: bool
            Whether the media query condition is satisfied.
    """

    expressions: list[MediaQueryExpression]
    active: bool

    @classmethod
    def from_json(cls, json: dict) -> MediaQuery:
        return cls(
            [MediaQueryExpression.from_json(x) for x in json["expressions"]],
            json["active"],
        )


@dataclasses.dataclass
class MediaQueryExpression(Type):
    """Media query expression descriptor.

    Attributes
    ----------
    value: float
            Media query expression value.
    unit: str
            Media query expression units.
    feature: str
            Media query expression feature.
    valueRange: Optional[SourceRange] = None
            The associated range of the value text in the enclosing stylesheet (if available).
    computedLength: Optional[float] = None
            Computed length of media query expression (if applicable).
    """

    value: float
    unit: str
    feature: str
    valueRange: Optional[SourceRange] = None
    computedLength: Optional[float] = None

    @classmethod
    def from_json(cls, json: dict) -> MediaQueryExpression:
        return cls(
            json["value"],
            json["unit"],
            json["feature"],
            SourceRange.from_json(json["valueRange"]) if "valueRange" in json else None,
            json.get("computedLength"),
        )


@dataclasses.dataclass
class PlatformFontUsage(Type):
    """Information about amount of glyphs that were rendered with given font.

    Attributes
    ----------
    familyName: str
            Font's family name reported by platform.
    isCustomFont: bool
            Indicates if the font was downloaded or resolved locally.
    glyphCount: float
            Amount of glyphs that were rendered with this font.
    """

    familyName: str
    isCustomFont: bool
    glyphCount: float

    @classmethod
    def from_json(cls, json: dict) -> PlatformFontUsage:
        return cls(json["familyName"], json["isCustomFont"], json["glyphCount"])


@dataclasses.dataclass
class FontVariationAxis(Type):
    """Information about font variation axes for variable fonts

    Attributes
    ----------
    tag: str
            The font-variation-setting tag (a.k.a. "axis tag").
    name: str
            Human-readable variation name in the default language (normally, "en").
    minValue: float
            The minimum value (inclusive) the font supports for this tag.
    maxValue: float
            The maximum value (inclusive) the font supports for this tag.
    defaultValue: float
            The default value.
    """

    tag: str
    name: str
    minValue: float
    maxValue: float
    defaultValue: float

    @classmethod
    def from_json(cls, json: dict) -> FontVariationAxis:
        return cls(
            json["tag"],
            json["name"],
            json["minValue"],
            json["maxValue"],
            json["defaultValue"],
        )


@dataclasses.dataclass
class FontFace(Type):
    """Properties of a web font: https://www.w3.org/TR/2008/REC-CSS2-20080411/fonts.html#font-descriptions
    and additional information such as platformFontFamily and fontVariationAxes.

    Attributes
    ----------
    fontFamily: str
            The font-family.
    fontStyle: str
            The font-style.
    fontVariant: str
            The font-variant.
    fontWeight: str
            The font-weight.
    fontStretch: str
            The font-stretch.
    unicodeRange: str
            The unicode-range.
    src: str
            The src.
    platformFontFamily: str
            The resolved platform font family
    fontVariationAxes: Optional[list[FontVariationAxis]] = None
            Available variation settings (a.k.a. "axes").
    """

    fontFamily: str
    fontStyle: str
    fontVariant: str
    fontWeight: str
    fontStretch: str
    unicodeRange: str
    src: str
    platformFontFamily: str
    fontVariationAxes: Optional[list[FontVariationAxis]] = None

    @classmethod
    def from_json(cls, json: dict) -> FontFace:
        return cls(
            json["fontFamily"],
            json["fontStyle"],
            json["fontVariant"],
            json["fontWeight"],
            json["fontStretch"],
            json["unicodeRange"],
            json["src"],
            json["platformFontFamily"],
            [FontVariationAxis.from_json(x) for x in json["fontVariationAxes"]]
            if "fontVariationAxes" in json
            else None,
        )


@dataclasses.dataclass
class CSSKeyframesRule(Type):
    """CSS keyframes rule representation.

    Attributes
    ----------
    animationName: Value
            Animation name.
    keyframes: list[CSSKeyframeRule]
            List of keyframes.
    """

    animationName: Value
    keyframes: list[CSSKeyframeRule]

    @classmethod
    def from_json(cls, json: dict) -> CSSKeyframesRule:
        return cls(
            Value.from_json(json["animationName"]),
            [CSSKeyframeRule.from_json(x) for x in json["keyframes"]],
        )


@dataclasses.dataclass
class CSSKeyframeRule(Type):
    """CSS keyframe rule representation.

    Attributes
    ----------
    origin: StyleSheetOrigin
            Parent stylesheet's origin.
    keyText: Value
            Associated key text.
    style: CSSStyle
            Associated style declaration.
    styleSheetId: Optional[StyleSheetId] = None
            The css style sheet identifier (absent for user agent stylesheet and user-specified
            stylesheet rules) this rule came from.
    """

    origin: StyleSheetOrigin
    keyText: Value
    style: CSSStyle
    styleSheetId: Optional[StyleSheetId] = None

    @classmethod
    def from_json(cls, json: dict) -> CSSKeyframeRule:
        return cls(
            StyleSheetOrigin(json["origin"]),
            Value.from_json(json["keyText"]),
            CSSStyle.from_json(json["style"]),
            StyleSheetId(json["styleSheetId"]) if "styleSheetId" in json else None,
        )


@dataclasses.dataclass
class StyleDeclarationEdit(Type):
    """A descriptor of operation to mutate style declaration text.

    Attributes
    ----------
    styleSheetId: StyleSheetId
            The css style sheet identifier.
    range: SourceRange
            The range of the style text in the enclosing stylesheet.
    text: str
            New style text.
    """

    styleSheetId: StyleSheetId
    range: SourceRange
    text: str

    @classmethod
    def from_json(cls, json: dict) -> StyleDeclarationEdit:
        return cls(
            StyleSheetId(json["styleSheetId"]),
            SourceRange.from_json(json["range"]),
            json["text"],
        )


def add_rule(styleSheetId: StyleSheetId, ruleText: str, location: SourceRange):
    """Inserts a new rule with the given `ruleText` in a stylesheet with given `styleSheetId`, at the
    position specified by `location`.

    Parameters
    ----------
    styleSheetId: StyleSheetId
            The css style sheet identifier where a new rule should be inserted.
    ruleText: str
            The text of a new rule.
    location: SourceRange
            Text position of a new rule in the target style sheet.

    Returns
    -------
    rule: CSSRule
            The newly created rule.
    """
    return {
        "method": "CSS.addRule",
        "params": {
            "styleSheetId": styleSheetId,
            "ruleText": ruleText,
            "location": location,
        },
    }


def collect_class_names(styleSheetId: StyleSheetId):
    """Returns all class names from specified stylesheet.

    Parameters
    ----------
    styleSheetId: StyleSheetId

    Returns
    -------
    classNames: list[str]
            Class name list.
    """
    return {"method": "CSS.collectClassNames", "params": {"styleSheetId": styleSheetId}}


def create_style_sheet(frameId: page.FrameId):
    """Creates a new special "via-inspector" stylesheet in the frame with given `frameId`.

    Parameters
    ----------
    frameId: page.FrameId
            Identifier of the frame where "via-inspector" stylesheet should be created.

    Returns
    -------
    styleSheetId: StyleSheetId
            Identifier of the created "via-inspector" stylesheet.
    """
    return {"method": "CSS.createStyleSheet", "params": {"frameId": frameId}}


def disable():
    """Disables the CSS agent for the given page."""
    return {"method": "CSS.disable", "params": {}}


def enable():
    """Enables the CSS agent for the given page. Clients should not assume that the CSS agent has been
    enabled until the result of this command is received.
    """
    return {"method": "CSS.enable", "params": {}}


def force_pseudo_state(nodeId: dom.NodeId, forcedPseudoClasses: list[str]):
    """Ensures that the given node will have specified pseudo-classes whenever its style is computed by
    the browser.

    Parameters
    ----------
    nodeId: dom.NodeId
            The element id for which to force the pseudo state.
    forcedPseudoClasses: list[str]
            Element pseudo classes to force when computing the element's style.
    """
    return {
        "method": "CSS.forcePseudoState",
        "params": {"nodeId": nodeId, "forcedPseudoClasses": forcedPseudoClasses},
    }


def get_background_colors(nodeId: dom.NodeId):
    """
    Parameters
    ----------
    nodeId: dom.NodeId
            Id of the node to get background colors for.

    Returns
    -------
    backgroundColors: Optional[list[str]]
            The range of background colors behind this element, if it contains any visible text. If no
            visible text is present, this will be undefined. In the case of a flat background color,
            this will consist of simply that color. In the case of a gradient, this will consist of each
            of the color stops. For anything more complicated, this will be an empty array. Images will
            be ignored (as if the image had failed to load).
    computedFontSize: Optional[str]
            The computed font size for this node, as a CSS computed value string (e.g. '12px').
    computedFontWeight: Optional[str]
            The computed font weight for this node, as a CSS computed value string (e.g. 'normal' or
            '100').
    """
    return {"method": "CSS.getBackgroundColors", "params": {"nodeId": nodeId}}


def get_computed_style_for_node(nodeId: dom.NodeId):
    """Returns the computed style for a DOM node identified by `nodeId`.

    Parameters
    ----------
    nodeId: dom.NodeId

    Returns
    -------
    computedStyle: list[CSSComputedStyleProperty]
            Computed style for the specified DOM node.
    """
    return {"method": "CSS.getComputedStyleForNode", "params": {"nodeId": nodeId}}


def get_inline_styles_for_node(nodeId: dom.NodeId):
    """Returns the styles defined inline (explicitly in the "style" attribute and implicitly, using DOM
    attributes) for a DOM node identified by `nodeId`.

    Parameters
    ----------
    nodeId: dom.NodeId

    Returns
    -------
    inlineStyle: Optional[CSSStyle]
            Inline style for the specified DOM node.
    attributesStyle: Optional[CSSStyle]
            Attribute-defined element style (e.g. resulting from "width=20 height=100%").
    """
    return {"method": "CSS.getInlineStylesForNode", "params": {"nodeId": nodeId}}


def get_matched_styles_for_node(nodeId: dom.NodeId):
    """Returns requested styles for a DOM node identified by `nodeId`.

    Parameters
    ----------
    nodeId: dom.NodeId

    Returns
    -------
    inlineStyle: Optional[CSSStyle]
            Inline style for the specified DOM node.
    attributesStyle: Optional[CSSStyle]
            Attribute-defined element style (e.g. resulting from "width=20 height=100%").
    matchedCSSRules: Optional[list[RuleMatch]]
            CSS rules matching this node, from all applicable stylesheets.
    pseudoElements: Optional[list[PseudoElementMatches]]
            Pseudo style matches for this node.
    inherited: Optional[list[InheritedStyleEntry]]
            A chain of inherited styles (from the immediate node parent up to the DOM tree root).
    cssKeyframesRules: Optional[list[CSSKeyframesRule]]
            A list of CSS keyframed animations matching this node.
    """
    return {"method": "CSS.getMatchedStylesForNode", "params": {"nodeId": nodeId}}


def get_media_queries():
    """Returns all media queries parsed by the rendering engine.

    Returns
    -------
    medias: list[CSSMedia]
    """
    return {"method": "CSS.getMediaQueries", "params": {}}


def get_platform_fonts_for_node(nodeId: dom.NodeId):
    """Requests information about platform fonts which we used to render child TextNodes in the given
    node.

    Parameters
    ----------
    nodeId: dom.NodeId

    Returns
    -------
    fonts: list[PlatformFontUsage]
            Usage statistics for every employed platform font.
    """
    return {"method": "CSS.getPlatformFontsForNode", "params": {"nodeId": nodeId}}


def get_style_sheet_text(styleSheetId: StyleSheetId):
    """Returns the current textual content for a stylesheet.

    Parameters
    ----------
    styleSheetId: StyleSheetId

    Returns
    -------
    text: str
            The stylesheet text.
    """
    return {"method": "CSS.getStyleSheetText", "params": {"styleSheetId": styleSheetId}}


def track_computed_style_updates(propertiesToTrack: list[CSSComputedStyleProperty]):
    """Starts tracking the given computed styles for updates. The specified array of properties
    replaces the one previously specified. Pass empty array to disable tracking.
    Use takeComputedStyleUpdates to retrieve the list of nodes that had properties modified.
    The changes to computed style properties are only tracked for nodes pushed to the front-end
    by the DOM agent. If no changes to the tracked properties occur after the node has been pushed
    to the front-end, no updates will be issued for the node.

    **Experimental**

    Parameters
    ----------
    propertiesToTrack: list[CSSComputedStyleProperty]
    """
    return {
        "method": "CSS.trackComputedStyleUpdates",
        "params": {"propertiesToTrack": propertiesToTrack},
    }


def take_computed_style_updates():
    """Polls the next batch of computed style updates.

    **Experimental**

    Returns
    -------
    nodeIds: list[dom.NodeId]
            The list of node Ids that have their tracked computed styles updated
    """
    return {"method": "CSS.takeComputedStyleUpdates", "params": {}}


def set_effective_property_value_for_node(
    nodeId: dom.NodeId, propertyName: str, value: str
):
    """Find a rule with the given active property for the given node and set the new value for this
    property

    Parameters
    ----------
    nodeId: dom.NodeId
            The element id for which to set property.
    propertyName: str
    value: str
    """
    return {
        "method": "CSS.setEffectivePropertyValueForNode",
        "params": {"nodeId": nodeId, "propertyName": propertyName, "value": value},
    }


def set_keyframe_key(styleSheetId: StyleSheetId, range: SourceRange, keyText: str):
    """Modifies the keyframe rule key text.

    Parameters
    ----------
    styleSheetId: StyleSheetId
    range: SourceRange
    keyText: str

    Returns
    -------
    keyText: Value
            The resulting key text after modification.
    """
    return {
        "method": "CSS.setKeyframeKey",
        "params": {"styleSheetId": styleSheetId, "range": range, "keyText": keyText},
    }


def set_media_text(styleSheetId: StyleSheetId, range: SourceRange, text: str):
    """Modifies the rule selector.

    Parameters
    ----------
    styleSheetId: StyleSheetId
    range: SourceRange
    text: str

    Returns
    -------
    media: CSSMedia
            The resulting CSS media rule after modification.
    """
    return {
        "method": "CSS.setMediaText",
        "params": {"styleSheetId": styleSheetId, "range": range, "text": text},
    }


def set_rule_selector(styleSheetId: StyleSheetId, range: SourceRange, selector: str):
    """Modifies the rule selector.

    Parameters
    ----------
    styleSheetId: StyleSheetId
    range: SourceRange
    selector: str

    Returns
    -------
    selectorList: SelectorList
            The resulting selector list after modification.
    """
    return {
        "method": "CSS.setRuleSelector",
        "params": {"styleSheetId": styleSheetId, "range": range, "selector": selector},
    }


def set_style_sheet_text(styleSheetId: StyleSheetId, text: str):
    """Sets the new stylesheet text.

    Parameters
    ----------
    styleSheetId: StyleSheetId
    text: str

    Returns
    -------
    sourceMapURL: Optional[str]
            URL of source map associated with script (if any).
    """
    return {
        "method": "CSS.setStyleSheetText",
        "params": {"styleSheetId": styleSheetId, "text": text},
    }


def set_style_texts(edits: list[StyleDeclarationEdit]):
    """Applies specified style edits one after another in the given order.

    Parameters
    ----------
    edits: list[StyleDeclarationEdit]

    Returns
    -------
    styles: list[CSSStyle]
            The resulting styles after modification.
    """
    return {"method": "CSS.setStyleTexts", "params": {"edits": edits}}


def start_rule_usage_tracking():
    """Enables the selector recording."""
    return {"method": "CSS.startRuleUsageTracking", "params": {}}


def stop_rule_usage_tracking():
    """Stop tracking rule usage and return the list of rules that were used since last call to
    `takeCoverageDelta` (or since start of coverage instrumentation)

    Returns
    -------
    ruleUsage: list[RuleUsage]
    """
    return {"method": "CSS.stopRuleUsageTracking", "params": {}}


def take_coverage_delta():
    """Obtain list of rules that became used since last call to this method (or since start of coverage
    instrumentation)

    Returns
    -------
    coverage: list[RuleUsage]
    timestamp: float
            Monotonically increasing time, in seconds.
    """
    return {"method": "CSS.takeCoverageDelta", "params": {}}


def set_local_fonts_enabled(enabled: bool):
    """Enables/disables rendering of local CSS fonts (enabled by default).

    **Experimental**

    Parameters
    ----------
    enabled: bool
            Whether rendering of local fonts is enabled.
    """
    return {"method": "CSS.setLocalFontsEnabled", "params": {"enabled": enabled}}
