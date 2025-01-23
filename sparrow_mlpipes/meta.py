from dataclasses import dataclass
from pathlib import Path

from .initialize import Gst, GstPbutils


@dataclass
class Meta:
    fps: float
    duration: float
    width: int
    height: int


def get_meta(input_uri: str) -> Meta:
    """Get the metadata of the video file."""
    if "://" not in input_uri:
        input_uri = f"file://{Path(input_uri).absolute()}"
    discoverer = GstPbutils.Discoverer()
    info = discoverer.discover_uri(input_uri)
    duration = info.get_duration() / Gst.SECOND
    stream = info.get_video_streams()[0]
    fps = stream.get_framerate_num() / stream.get_framerate_denom()
    width = stream.get_width()
    height = stream.get_height()
    return Meta(fps, duration, width, height)
