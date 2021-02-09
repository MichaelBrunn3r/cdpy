from __future__ import annotations

import dataclasses
import enum
from typing import Optional

from .common import filter_none


@dataclasses.dataclass
class GPUDevice:
    """Describes a single graphics processor (GPU).

    Attributes
    ----------
    vendorId: float
            PCI ID of the GPU vendor, if available; 0 otherwise.
    deviceId: float
            PCI ID of the GPU device, if available; 0 otherwise.
    vendorString: str
            String description of the GPU vendor, if the PCI ID is not available.
    deviceString: str
            String description of the GPU device, if the PCI ID is not available.
    driverVendor: str
            String description of the GPU driver vendor.
    driverVersion: str
            String description of the GPU driver version.
    subSysId: Optional[float]
            Sub sys ID of the GPU, only available on Windows.
    revision: Optional[float]
            Revision of the GPU, only available on Windows.
    """

    vendorId: float
    deviceId: float
    vendorString: str
    deviceString: str
    driverVendor: str
    driverVersion: str
    subSysId: Optional[float] = None
    revision: Optional[float] = None

    @classmethod
    def from_json(cls, json: dict) -> GPUDevice:
        return cls(
            json["vendorId"],
            json["deviceId"],
            json["vendorString"],
            json["deviceString"],
            json["driverVendor"],
            json["driverVersion"],
            json.get("subSysId"),
            json.get("revision"),
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "vendorId": self.vendorId,
                "deviceId": self.deviceId,
                "vendorString": self.vendorString,
                "deviceString": self.deviceString,
                "driverVendor": self.driverVendor,
                "driverVersion": self.driverVersion,
                "subSysId": self.subSysId,
                "revision": self.revision,
            }
        )


@dataclasses.dataclass
class Size:
    """Describes the width and height dimensions of an entity.

    Attributes
    ----------
    width: int
            Width in pixels.
    height: int
            Height in pixels.
    """

    width: int
    height: int

    @classmethod
    def from_json(cls, json: dict) -> Size:
        return cls(json["width"], json["height"])

    def to_json(self) -> dict:
        return {"width": self.width, "height": self.height}


@dataclasses.dataclass
class VideoDecodeAcceleratorCapability:
    """Describes a supported video decoding profile with its associated minimum and
    maximum resolutions.

    Attributes
    ----------
    profile: str
            Video codec profile that is supported, e.g. VP9 Profile 2.
    maxResolution: Size
            Maximum video dimensions in pixels supported for this |profile|.
    minResolution: Size
            Minimum video dimensions in pixels supported for this |profile|.
    """

    profile: str
    maxResolution: Size
    minResolution: Size

    @classmethod
    def from_json(cls, json: dict) -> VideoDecodeAcceleratorCapability:
        return cls(
            json["profile"],
            Size.from_json(json["maxResolution"]),
            Size.from_json(json["minResolution"]),
        )

    def to_json(self) -> dict:
        return {
            "profile": self.profile,
            "maxResolution": self.maxResolution.to_json(),
            "minResolution": self.minResolution.to_json(),
        }


@dataclasses.dataclass
class VideoEncodeAcceleratorCapability:
    """Describes a supported video encoding profile with its associated maximum
    resolution and maximum framerate.

    Attributes
    ----------
    profile: str
            Video codec profile that is supported, e.g H264 Main.
    maxResolution: Size
            Maximum video dimensions in pixels supported for this |profile|.
    maxFramerateNumerator: int
            Maximum encoding framerate in frames per second supported for this
            |profile|, as fraction's numerator and denominator, e.g. 24/1 fps,
            24000/1001 fps, etc.
    maxFramerateDenominator: int
    """

    profile: str
    maxResolution: Size
    maxFramerateNumerator: int
    maxFramerateDenominator: int

    @classmethod
    def from_json(cls, json: dict) -> VideoEncodeAcceleratorCapability:
        return cls(
            json["profile"],
            Size.from_json(json["maxResolution"]),
            json["maxFramerateNumerator"],
            json["maxFramerateDenominator"],
        )

    def to_json(self) -> dict:
        return {
            "profile": self.profile,
            "maxResolution": self.maxResolution.to_json(),
            "maxFramerateNumerator": self.maxFramerateNumerator,
            "maxFramerateDenominator": self.maxFramerateDenominator,
        }


class SubsamplingFormat(enum.Enum):
    """YUV subsampling type of the pixels of a given image."""

    YUV420 = "yuv420"
    YUV422 = "yuv422"
    YUV444 = "yuv444"


class ImageType(enum.Enum):
    """Image format of a given image."""

    JPEG = "jpeg"
    WEBP = "webp"
    UNKNOWN = "unknown"


@dataclasses.dataclass
class ImageDecodeAcceleratorCapability:
    """Describes a supported image decoding profile with its associated minimum and
    maximum resolutions and subsampling.

    Attributes
    ----------
    imageType: ImageType
            Image coded, e.g. Jpeg.
    maxDimensions: Size
            Maximum supported dimensions of the image in pixels.
    minDimensions: Size
            Minimum supported dimensions of the image in pixels.
    subsamplings: list[SubsamplingFormat]
            Optional array of supported subsampling formats, e.g. 4:2:0, if known.
    """

    imageType: ImageType
    maxDimensions: Size
    minDimensions: Size
    subsamplings: list[SubsamplingFormat]

    @classmethod
    def from_json(cls, json: dict) -> ImageDecodeAcceleratorCapability:
        return cls(
            ImageType(json["imageType"]),
            Size.from_json(json["maxDimensions"]),
            Size.from_json(json["minDimensions"]),
            [SubsamplingFormat(x) for x in json["subsamplings"]],
        )

    def to_json(self) -> dict:
        return {
            "imageType": str(self.imageType),
            "maxDimensions": self.maxDimensions.to_json(),
            "minDimensions": self.minDimensions.to_json(),
            "subsamplings": [str(s) for s in self.subsamplings],
        }


@dataclasses.dataclass
class GPUInfo:
    """Provides information about the GPU(s) on the system.

    Attributes
    ----------
    devices: list[GPUDevice]
            The graphics devices on the system. Element 0 is the primary GPU.
    driverBugWorkarounds: list[str]
            An optional array of GPU driver bug workarounds.
    videoDecoding: list[VideoDecodeAcceleratorCapability]
            Supported accelerated video decoding capabilities.
    videoEncoding: list[VideoEncodeAcceleratorCapability]
            Supported accelerated video encoding capabilities.
    imageDecoding: list[ImageDecodeAcceleratorCapability]
            Supported accelerated image decoding capabilities.
    auxAttributes: Optional[dict]
            An optional dictionary of additional GPU related attributes.
    featureStatus: Optional[dict]
            An optional dictionary of graphics features and their status.
    """

    devices: list[GPUDevice]
    driverBugWorkarounds: list[str]
    videoDecoding: list[VideoDecodeAcceleratorCapability]
    videoEncoding: list[VideoEncodeAcceleratorCapability]
    imageDecoding: list[ImageDecodeAcceleratorCapability]
    auxAttributes: Optional[dict] = None
    featureStatus: Optional[dict] = None

    @classmethod
    def from_json(cls, json: dict) -> GPUInfo:
        return cls(
            [GPUDevice.from_json(x) for x in json["devices"]],
            json["driverBugWorkarounds"],
            [
                VideoDecodeAcceleratorCapability.from_json(x)
                for x in json["videoDecoding"]
            ],
            [
                VideoEncodeAcceleratorCapability.from_json(x)
                for x in json["videoEncoding"]
            ],
            [
                ImageDecodeAcceleratorCapability.from_json(x)
                for x in json["imageDecoding"]
            ],
            json.get("auxAttributes"),
            json.get("featureStatus"),
        )

    def to_json(self) -> dict:
        return filter_none(
            {
                "devices": [d.to_json() for d in self.devices],
                "driverBugWorkarounds": self.driverBugWorkarounds,
                "videoDecoding": [v.to_json() for v in self.videoDecoding],
                "videoEncoding": [v.to_json() for v in self.videoEncoding],
                "imageDecoding": [i.to_json() for i in self.imageDecoding],
                "auxAttributes": self.auxAttributes,
                "featureStatus": self.featureStatus,
            }
        )


@dataclasses.dataclass
class ProcessInfo:
    """Represents process info.

    Attributes
    ----------
    type: str
            Specifies process type.
    id: int
            Specifies process id.
    cpuTime: float
            Specifies cumulative CPU usage in seconds across all threads of the
            process since the process start.
    """

    type: str
    id: int
    cpuTime: float

    @classmethod
    def from_json(cls, json: dict) -> ProcessInfo:
        return cls(json["type"], json["id"], json["cpuTime"])

    def to_json(self) -> dict:
        return {"type": self.type, "id": self.id, "cpuTime": self.cpuTime}


def get_info():
    """Returns information about the system.

    Returns
    -------
    gpu: GPUInfo
            Information about the GPUs on the system.
    modelName: str
            A platform-dependent description of the model of the machine. On Mac OS, this is, for
            example, 'MacBookPro'. Will be the empty string if not supported.
    modelVersion: str
            A platform-dependent description of the version of the machine. On Mac OS, this is, for
            example, '10.1'. Will be the empty string if not supported.
    commandLine: str
            The command line string used to launch the browser. Will be the empty string if not
            supported.
    """
    return {"method": "SystemInfo.getInfo", "params": {}}


def get_process_info():
    """Returns information about all running processes.

    Returns
    -------
    processInfo: list[ProcessInfo]
            An array of process info blocks.
    """
    return {"method": "SystemInfo.getProcessInfo", "params": {}}
