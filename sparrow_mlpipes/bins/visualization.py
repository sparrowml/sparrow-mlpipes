from typing import Any, Callable, Optional, Tuple

from sparrow_mlpipes.element import make_element
from sparrow_mlpipes.initialize import Gst


def make_visualization_bin(
    osd_probe: Optional[
        Callable[[Gst.Pad, Gst.PadProbeInfo, Tuple[Any, ...]], Gst.PadProbeReturn]
    ] = None,
) -> Gst.Bin:
    bin = Gst.Bin.new("visualization")

    nvvideoconvert = make_element("nvvideoconvert")
    Gst.Bin.add(bin, nvvideoconvert)

    nvdsosd = make_element("nvdsosd")
    Gst.Bin.add(bin, nvdsosd)
    nvvideoconvert.link(nvdsosd)
    if osd_probe:
        nvdsosd.get_static_pad("sink").add_probe(Gst.PadProbeType.BUFFER, osd_probe, 0)

    queue = make_element("queue")
    Gst.Bin.add(bin, queue)
    nvdsosd.link(queue)

    bin.add_pad(Gst.GhostPad("sink", nvvideoconvert.get_static_pad("sink")))
    bin.add_pad(Gst.GhostPad("src", queue.get_static_pad("src")))

    return bin
