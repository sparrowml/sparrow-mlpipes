from typing import List
from urllib.parse import urlparse

from mlpipes.initialize import Gst
from mlpipes.element import Element


def rtsp_source_block(uri: str) -> List[Element]:
    """Create a block of elements for an RTSP source"""
    source = Element("rtspsrc", location=uri)
    depay = Element("rtph264depay")

    def rtspsrc_link(self: Element, _: Element) -> bool:
        def on_pad_added(source: Gst.Element, pad: Gst.Pad):
            print(f"Pad {pad.get_name()} from source {source.get_name()}")
            pad.link(depay.gst_element.get_static_pad("sink"))

        self.gst_element.connect("pad-added", on_pad_added)
        return True

    source.set_link(rtspsrc_link)
    return [source, depay]


def file_source_block(path: str) -> List[Element]:
    """Create a block of elements for a file source"""
    source = Element("filesrc", location=path)
    qtdemux = Element("qtdemux")
    h264parse = Element("h264parse")

    def qtdemux_link(self: Element, _: Element) -> bool:
        def on_pad_added(source: Gst.Element, pad: Gst.Pad):
            if "video" in pad.get_name():
                print(f"Pad {pad.get_name()} from source {source.get_name()}")
                pad.link(h264parse.gst_element.get_static_pad("sink"))

        self.gst_element.connect("pad-added", on_pad_added)
        return True

    qtdemux.set_link(qtdemux_link)
    return [source, qtdemux, h264parse]


def source_block(uri: str) -> List[Element]:
    """Create a block of elements from a single location"""
    parse_result = urlparse(uri)
    if parse_result.scheme == "rtsp":
        return rtsp_source_block(uri)
    elif parse_result.scheme in ("file", ""):
        return file_source_block(parse_result.path)
    raise NotImplementedError(f"{uri} not supported")
