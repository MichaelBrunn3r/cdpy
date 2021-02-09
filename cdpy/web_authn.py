from __future__ import annotations

import dataclasses
import enum
from typing import Optional

from .common import filter_none


class AuthenticatorId(str):
    """"""

    def __repr__(self):
        return f"AuthenticatorId({super().__repr__()})"


class AuthenticatorProtocol(enum.Enum):
    """"""

    U2F = "u2f"
    CTAP2 = "ctap2"


class Ctap2Version(enum.Enum):
    """"""

    CTAP2_0 = "ctap2_0"
    CTAP2_1 = "ctap2_1"


class AuthenticatorTransport(enum.Enum):
    """"""

    USB = "usb"
    NFC = "nfc"
    BLE = "ble"
    CABLE = "cable"
    INTERNAL = "internal"


@dataclasses.dataclass
class VirtualAuthenticatorOptions:
    """
    Attributes
    ----------
    protocol: AuthenticatorProtocol
    transport: AuthenticatorTransport
    ctap2Version: Optional[Ctap2Version]
            Defaults to ctap2_0. Ignored if |protocol| == u2f.
    hasResidentKey: Optional[bool]
            Defaults to false.
    hasUserVerification: Optional[bool]
            Defaults to false.
    hasLargeBlob: Optional[bool]
            If set to true, the authenticator will support the largeBlob extension.
            https://w3c.github.io/webauthn#largeBlob
            Defaults to false.
    automaticPresenceSimulation: Optional[bool]
            If set to true, tests of user presence will succeed immediately.
            Otherwise, they will not be resolved. Defaults to true.
    isUserVerified: Optional[bool]
            Sets whether User Verification succeeds or fails for an authenticator.
            Defaults to false.
    """

    protocol: AuthenticatorProtocol
    transport: AuthenticatorTransport
    ctap2Version: Optional[Ctap2Version] = None
    hasResidentKey: Optional[bool] = None
    hasUserVerification: Optional[bool] = None
    hasLargeBlob: Optional[bool] = None
    automaticPresenceSimulation: Optional[bool] = None
    isUserVerified: Optional[bool] = None

    @classmethod
    def from_json(cls, json: dict) -> VirtualAuthenticatorOptions:
        return cls(
            AuthenticatorProtocol(json["protocol"]),
            AuthenticatorTransport(json["transport"]),
            Ctap2Version(json["ctap2Version"]) if "ctap2Version" in json else None,
            json.get("hasResidentKey"),
            json.get("hasUserVerification"),
            json.get("hasLargeBlob"),
            json.get("automaticPresenceSimulation"),
            json.get("isUserVerified"),
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "protocol": str(self.protocol),
                "transport": str(self.transport),
                "ctap2Version": str(self.ctap2Version) if self.ctap2Version else None,
                "hasResidentKey": self.hasResidentKey,
                "hasUserVerification": self.hasUserVerification,
                "hasLargeBlob": self.hasLargeBlob,
                "automaticPresenceSimulation": self.automaticPresenceSimulation,
                "isUserVerified": self.isUserVerified,
            }
        )


@dataclasses.dataclass
class Credential:
    """
    Attributes
    ----------
    credentialId: str
    isResidentCredential: bool
    privateKey: str
            The ECDSA P-256 private key in PKCS#8 format. (Encoded as a base64 string when passed over JSON)
    signCount: int
            Signature counter. This is incremented by one for each successful
            assertion.
            See https://w3c.github.io/webauthn/#signature-counter
    rpId: Optional[str]
            Relying Party ID the credential is scoped to. Must be set when adding a
            credential.
    userHandle: Optional[str]
            An opaque byte sequence with a maximum size of 64 bytes mapping the
            credential to a specific user. (Encoded as a base64 string when passed over JSON)
    largeBlob: Optional[str]
            The large blob associated with the credential.
            See https://w3c.github.io/webauthn/#sctn-large-blob-extension (Encoded as a base64 string when passed over JSON)
    """

    credentialId: str
    isResidentCredential: bool
    privateKey: str
    signCount: int
    rpId: Optional[str] = None
    userHandle: Optional[str] = None
    largeBlob: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict) -> Credential:
        return cls(
            json["credentialId"],
            json["isResidentCredential"],
            json["privateKey"],
            json["signCount"],
            json.get("rpId"),
            json.get("userHandle"),
            json.get("largeBlob"),
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "credentialId": self.credentialId,
                "isResidentCredential": self.isResidentCredential,
                "privateKey": self.privateKey,
                "signCount": self.signCount,
                "rpId": self.rpId,
                "userHandle": self.userHandle,
                "largeBlob": self.largeBlob,
            }
        )


def enable():
    """Enable the WebAuthn domain and start intercepting credential storage and
    retrieval with a virtual authenticator.
    """
    return {"method": "WebAuthn.enable", "params": {}}


def disable():
    """Disable the WebAuthn domain."""
    return {"method": "WebAuthn.disable", "params": {}}


def add_virtual_authenticator(options: VirtualAuthenticatorOptions):
    """Creates and adds a virtual authenticator.

    Parameters
    ----------
    options: VirtualAuthenticatorOptions

    Returns
    -------
    authenticatorId: AuthenticatorId
    """
    return {
        "method": "WebAuthn.addVirtualAuthenticator",
        "params": {"options": options},
    }


def remove_virtual_authenticator(authenticatorId: AuthenticatorId):
    """Removes the given authenticator.

    Parameters
    ----------
    authenticatorId: AuthenticatorId
    """
    return {
        "method": "WebAuthn.removeVirtualAuthenticator",
        "params": {"authenticatorId": authenticatorId},
    }


def add_credential(authenticatorId: AuthenticatorId, credential: Credential):
    """Adds the credential to the specified authenticator.

    Parameters
    ----------
    authenticatorId: AuthenticatorId
    credential: Credential
    """
    return {
        "method": "WebAuthn.addCredential",
        "params": {"authenticatorId": authenticatorId, "credential": credential},
    }


def get_credential(authenticatorId: AuthenticatorId, credentialId: str):
    """Returns a single credential stored in the given virtual authenticator that
    matches the credential ID.

    Parameters
    ----------
    authenticatorId: AuthenticatorId
    credentialId: str

    Returns
    -------
    credential: Credential
    """
    return {
        "method": "WebAuthn.getCredential",
        "params": {"authenticatorId": authenticatorId, "credentialId": credentialId},
    }


def get_credentials(authenticatorId: AuthenticatorId):
    """Returns all the credentials stored in the given virtual authenticator.

    Parameters
    ----------
    authenticatorId: AuthenticatorId

    Returns
    -------
    credentials: list[Credential]
    """
    return {
        "method": "WebAuthn.getCredentials",
        "params": {"authenticatorId": authenticatorId},
    }


def remove_credential(authenticatorId: AuthenticatorId, credentialId: str):
    """Removes a credential from the authenticator.

    Parameters
    ----------
    authenticatorId: AuthenticatorId
    credentialId: str
    """
    return {
        "method": "WebAuthn.removeCredential",
        "params": {"authenticatorId": authenticatorId, "credentialId": credentialId},
    }


def clear_credentials(authenticatorId: AuthenticatorId):
    """Clears all the credentials from the specified device.

    Parameters
    ----------
    authenticatorId: AuthenticatorId
    """
    return {
        "method": "WebAuthn.clearCredentials",
        "params": {"authenticatorId": authenticatorId},
    }


def set_user_verified(authenticatorId: AuthenticatorId, isUserVerified: bool):
    """Sets whether User Verification succeeds or fails for an authenticator.
    The default is true.

    Parameters
    ----------
    authenticatorId: AuthenticatorId
    isUserVerified: bool
    """
    return {
        "method": "WebAuthn.setUserVerified",
        "params": {
            "authenticatorId": authenticatorId,
            "isUserVerified": isUserVerified,
        },
    }


def set_automatic_presence_simulation(authenticatorId: AuthenticatorId, enabled: bool):
    """Sets whether tests of user presence will succeed immediately (if true) or fail to resolve (if false) for an authenticator.
    The default is true.

    Parameters
    ----------
    authenticatorId: AuthenticatorId
    enabled: bool
    """
    return {
        "method": "WebAuthn.setAutomaticPresenceSimulation",
        "params": {"authenticatorId": authenticatorId, "enabled": enabled},
    }
