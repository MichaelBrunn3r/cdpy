from __future__ import annotations

import dataclasses
import enum
from typing import Optional

from . import runtime
from .common import Type, filter_unset_parameters


class StreamHandle(str):
    """This is either obtained from another method or specifed as `blob:&lt;uuid&gt;` where
    `&lt;uuid&gt` is an UUID of a Blob.
    """

    def __repr__(self):
        return f"StreamHandle({super().__repr__()})"


def close(handle: StreamHandle):
    """Close the stream, discard any temporary backing storage.

    Parameters
    ----------
    handle: StreamHandle
            Handle of the stream to close.
    """
    return {"method": "IO.close", "params": {"handle": handle}}


def read(
    handle: StreamHandle, offset: Optional[int] = None, size: Optional[int] = None
):
    """Read a chunk of the stream

    Parameters
    ----------
    handle: StreamHandle
            Handle of the stream to read.
    offset: Optional[int]
            Seek to the specified offset before reading (if not specificed, proceed with offset
            following the last read). Some types of streams may only support sequential reads.
    size: Optional[int]
            Maximum number of bytes to read (left upon the agent discretion if not specified).

    Returns
    -------
    base64Encoded: Optional[bool]
            Set if the data is base64-encoded
    data: str
            Data that were read.
    eof: bool
            Set if the end-of-file condition occured while reading.
    """
    return filter_unset_parameters(
        {
            "method": "IO.read",
            "params": {"handle": handle, "offset": offset, "size": size},
        }
    )


def resolve_blob(objectId: runtime.RemoteObjectId):
    """Return UUID of Blob object specified by a remote object id.

    Parameters
    ----------
    objectId: runtime.RemoteObjectId
            Object id of a Blob object wrapper.

    Returns
    -------
    uuid: str
            UUID of the specified Blob.
    """
    return {"method": "IO.resolveBlob", "params": {"objectId": objectId}}
