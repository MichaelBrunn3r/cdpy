from __future__ import annotations

import dataclasses
import enum
from typing import Optional

from . import io, network
from .common import filter_unset_parameters


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


def disable():
    """Disables the fetch domain."""
    return {"method": "Fetch.disable", "params": {}}


def enable(
    patterns: Optional[list[RequestPattern]] = None,
    handleAuthRequests: Optional[bool] = None,
):
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


def fail_request(requestId: RequestId, errorReason: network.ErrorReason):
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
):
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
):
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
):
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


def get_response_body(requestId: RequestId):
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
    return {"method": "Fetch.getResponseBody", "params": {"requestId": requestId}}


def take_response_body_as_stream(requestId: RequestId):
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
    return {
        "method": "Fetch.takeResponseBodyAsStream",
        "params": {"requestId": requestId},
    }
