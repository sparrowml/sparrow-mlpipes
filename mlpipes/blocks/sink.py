from typing import List
from urllib.parse import urlparse

from mlpipes.element import Element


def rtsp_sink_block(uri: str) -> List[Element]:
    """Create an RTSP sink block"""
    return [Element("rtspclientsink", location=uri)]


def sink_block(uri: str) -> List[Element]:
    """Create a block of sink elements from a single location"""
    parse_result = urlparse(uri)
    if parse_result.scheme == "rtsp":
        return rtsp_sink_block(uri)
    raise NotImplementedError(f"{uri} not supported")
