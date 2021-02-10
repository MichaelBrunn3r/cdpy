from __future__ import annotations

import dataclasses
import enum
from typing import Generator, Optional

from . import io, network, page
from .common import filter_none, filter_unset_parameters


class RequestId(str):
    """Unique request identifier."""

    def __repr__(self):
        return f"RequestId({super().__repr__()})"


class RequestStage(enum.Enum):
    """Stages of the request to handle. Request will intercept before the request is
    sent. Response will intercept after the response is received (but before response
    body is received.
    """

    REQUEST = "Request"
    RESPONSE = "Response"


@dataclasses.dataclass
class RequestPattern:
    """
    Attributes
    ----------
    urlPattern: Optional[str]
            Wildcards ('*' -> zero or more, '?' -> exactly one) are allowed. Escape character is
            backslash. Omitting is equivalent to "*".
    resourceType: Optional[network.ResourceType]
            If set, only requests for matching resource types will be intercepted.
    requestStage: Optional[RequestStage]
            Stage at wich to begin intercepting requests. Default is Request.
    """

    urlPattern: Optional[str] = None
    resourceType: Optional[network.ResourceType] = None
    requestStage: Optional[RequestStage] = None

    @classmethod
    def from_json(cls, json: dict) -> RequestPattern:
        return cls(
            json.get("urlPattern"),
            network.ResourceType(json["resourceType"])
            if "resourceType" in json
            else None,
            RequestStage(json["requestStage"]) if "requestStage" in json else None,
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "urlPattern": self.urlPattern,
                "resourceType": self.resourceType.value if self.resourceType else None,
                "requestStage": self.requestStage.value if self.requestStage else None,
            }
        )


@dataclasses.dataclass
class HeaderEntry:
    """Response HTTP header entry

    Attributes
    ----------
    name: str
    value: str
    """

    name: str
    value: str

    @classmethod
    def from_json(cls, json: dict) -> HeaderEntry:
        return cls(json["name"], json["value"])

    def to_json(self) -> dict:
        return {"name": self.name, "value": self.value}


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


def disable() -> dict:
    """Disables the fetch domain."""
    return {"method": "Fetch.disable", "params": {}}


def enable(
    patterns: Optional[list[RequestPattern]] = None,
    handleAuthRequests: Optional[bool] = None,
) -> dict:
    """Enables issuing of requestPaused events. A request will be paused until client
    calls one of failRequest, fulfillRequest or continueRequest/continueWithAuth.

    Parameters
    ----------
    patterns: Optional[list[RequestPattern]]
            If specified, only requests matching any of these patterns will produce
            fetchRequested event and will be paused until clients response. If not set,
            all requests will be affected.
    handleAuthRequests: Optional[bool]
            If true, authRequired events will be issued and requests will be paused
            expecting a call to continueWithAuth.
    """
    return filter_unset_parameters(
        {
            "method": "Fetch.enable",
            "params": {"patterns": patterns, "handleAuthRequests": handleAuthRequests},
        }
    )


def fail_request(requestId: RequestId, errorReason: network.ErrorReason) -> dict:
    """Causes the request to fail with specified reason.

    Parameters
    ----------
    requestId: RequestId
            An id the client received in requestPaused event.
    errorReason: network.ErrorReason
            Causes the request to fail with the given reason.
    """
    return {
        "method": "Fetch.failRequest",
        "params": {"requestId": requestId, "errorReason": errorReason},
    }


def fulfill_request(
    requestId: RequestId,
    responseCode: int,
    responseHeaders: Optional[list[HeaderEntry]] = None,
    binaryResponseHeaders: Optional[str] = None,
    body: Optional[str] = None,
    responsePhrase: Optional[str] = None,
) -> dict:
    """Provides response to the request.

    Parameters
    ----------
    requestId: RequestId
            An id the client received in requestPaused event.
    responseCode: int
            An HTTP response code.
    responseHeaders: Optional[list[HeaderEntry]]
            Response headers.
    binaryResponseHeaders: Optional[str]
            Alternative way of specifying response headers as a \\0-separated
            series of name: value pairs. Prefer the above method unless you
            need to represent some non-UTF8 values that can't be transmitted
            over the protocol as text. (Encoded as a base64 string when passed over JSON)
    body: Optional[str]
            A response body. (Encoded as a base64 string when passed over JSON)
    responsePhrase: Optional[str]
            A textual representation of responseCode.
            If absent, a standard phrase matching responseCode is used.
    """
    return filter_unset_parameters(
        {
            "method": "Fetch.fulfillRequest",
            "params": {
                "requestId": requestId,
                "responseCode": responseCode,
                "responseHeaders": responseHeaders,
                "binaryResponseHeaders": binaryResponseHeaders,
                "body": body,
                "responsePhrase": responsePhrase,
            },
        }
    )


def continue_request(
    requestId: RequestId,
    url: Optional[str] = None,
    method: Optional[str] = None,
    postData: Optional[str] = None,
    headers: Optional[list[HeaderEntry]] = None,
) -> dict:
    """Continues the request, optionally modifying some of its parameters.

    Parameters
    ----------
    requestId: RequestId
            An id the client received in requestPaused event.
    url: Optional[str]
            If set, the request url will be modified in a way that's not observable by page.
    method: Optional[str]
            If set, the request method is overridden.
    postData: Optional[str]
            If set, overrides the post data in the request. (Encoded as a base64 string when passed over JSON)
    headers: Optional[list[HeaderEntry]]
            If set, overrides the request headers.
    """
    return filter_unset_parameters(
        {
            "method": "Fetch.continueRequest",
            "params": {
                "requestId": requestId,
                "url": url,
                "method": method,
                "postData": postData,
                "headers": headers,
            },
        }
    )


def continue_with_auth(
    requestId: RequestId, authChallengeResponse: AuthChallengeResponse
) -> dict:
    """Continues a request supplying authChallengeResponse following authRequired event.

    Parameters
    ----------
    requestId: RequestId
            An id the client received in authRequired event.
    authChallengeResponse: AuthChallengeResponse
            Response to  with an authChallenge.
    """
    return {
        "method": "Fetch.continueWithAuth",
        "params": {
            "requestId": requestId,
            "authChallengeResponse": authChallengeResponse,
        },
    }


def get_response_body(requestId: RequestId) -> Generator[dict, dict, dict]:
    """Causes the body of the response to be received from the server and
    returned as a single string. May only be issued for a request that
    is paused in the Response stage and is mutually exclusive with
    takeResponseBodyForInterceptionAsStream. Calling other methods that
    affect the request or disabling fetch domain before body is received
    results in an undefined behavior.

    Parameters
    ----------
    requestId: RequestId
            Identifier for the intercepted request to get body for.

    Returns
    -------
    body: str
            Response body.
    base64Encoded: bool
            True, if content was sent as base64.
    """
    response = yield {
        "method": "Fetch.getResponseBody",
        "params": {"requestId": requestId},
    }
    return {"body": response["body"], "base64Encoded": response["base64Encoded"]}


def take_response_body_as_stream(
    requestId: RequestId,
) -> Generator[dict, dict, io.StreamHandle]:
    """Returns a handle to the stream representing the response body.
    The request must be paused in the HeadersReceived stage.
    Note that after this command the request can't be continued
    as is -- client either needs to cancel it or to provide the
    response body.
    The stream only supports sequential read, IO.read will fail if the position
    is specified.
    This method is mutually exclusive with getResponseBody.
    Calling other methods that affect the request or disabling fetch
    domain before body is received results in an undefined behavior.

    Parameters
    ----------
    requestId: RequestId

    Returns
    -------
    stream: io.StreamHandle
    """
    response = yield {
        "method": "Fetch.takeResponseBodyAsStream",
        "params": {"requestId": requestId},
    }
    return io.StreamHandle(response)


@dataclasses.dataclass
class RequestPaused:
    """Issued when the domain is enabled and the request URL matches the
    specified filter. The request is paused until the client responds
    with one of continueRequest, failRequest or fulfillRequest.
    The stage of the request can be determined by presence of responseErrorReason
    and responseStatusCode -- the request is at the response stage if either
    of these fields is present and in the request stage otherwise.

    Attributes
    ----------
    requestId: RequestId
            Each request the page makes will have a unique id.
    request: network.Request
            The details of the request.
    frameId: page.FrameId
            The id of the frame that initiated the request.
    resourceType: network.ResourceType
            How the requested resource will be used.
    responseErrorReason: Optional[network.ErrorReason]
            Response error if intercepted at response stage.
    responseStatusCode: Optional[int]
            Response code if intercepted at response stage.
    responseHeaders: Optional[list[HeaderEntry]]
            Response headers if intercepted at the response stage.
    networkId: Optional[RequestId]
            If the intercepted request had a corresponding Network.requestWillBeSent event fired for it,
            then this networkId will be the same as the requestId present in the requestWillBeSent event.
    """

    requestId: RequestId
    request: network.Request
    frameId: page.FrameId
    resourceType: network.ResourceType
    responseErrorReason: Optional[network.ErrorReason] = None
    responseStatusCode: Optional[int] = None
    responseHeaders: Optional[list[HeaderEntry]] = None
    networkId: Optional[RequestId] = None

    @classmethod
    def from_json(cls, json: dict) -> RequestPaused:
        return cls(
            RequestId(json["requestId"]),
            network.Request.from_json(json["request"]),
            page.FrameId(json["frameId"]),
            network.ResourceType(json["resourceType"]),
            network.ErrorReason(json["responseErrorReason"])
            if "responseErrorReason" in json
            else None,
            json.get("responseStatusCode"),
            [HeaderEntry.from_json(r) for r in json["responseHeaders"]]
            if "responseHeaders" in json
            else None,
            RequestId(json["networkId"]) if "networkId" in json else None,
        )


@dataclasses.dataclass
class AuthRequired:
    """Issued when the domain is enabled with handleAuthRequests set to true.
    The request is paused until client responds with continueWithAuth.

    Attributes
    ----------
    requestId: RequestId
            Each request the page makes will have a unique id.
    request: network.Request
            The details of the request.
    frameId: page.FrameId
            The id of the frame that initiated the request.
    resourceType: network.ResourceType
            How the requested resource will be used.
    authChallenge: AuthChallenge
            Details of the Authorization Challenge encountered.
            If this is set, client should respond with continueRequest that
            contains AuthChallengeResponse.
    """

    requestId: RequestId
    request: network.Request
    frameId: page.FrameId
    resourceType: network.ResourceType
    authChallenge: AuthChallenge

    @classmethod
    def from_json(cls, json: dict) -> AuthRequired:
        return cls(
            RequestId(json["requestId"]),
            network.Request.from_json(json["request"]),
            page.FrameId(json["frameId"]),
            network.ResourceType(json["resourceType"]),
            AuthChallenge.from_json(json["authChallenge"]),
        )
