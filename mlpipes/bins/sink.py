from typing import Any, Callable, Optional, Tuple

from mlpipes.initialize import Gst
from mlpipes.element import make_element


def make_sink_bin(
    output_path: str,
    visualization: bool = False,
    osd_probe: Optional[
        Callable[[Gst.Pad, Gst.PadProbeInfo, Tuple[Any, ...]], Gst.PadProbeReturn]
    ] = None,
) -> Gst.Bin:
    bin = Gst.Bin.new("sink")

    if visualization:
        nvvideoconvert = make_element("nvvideoconvert")
        Gst.Bin.add(bin, nvvideoconvert)

        nvdsosd = make_element("nvdsosd")
        Gst.Bin.add(bin, nvdsosd)
        nvvideoconvert.link(nvdsosd)
        if osd_probe:
            nvdsosd.get_static_pad("sink").add_probe(
                Gst.PadProbeType.BUFFER, osd_probe, 0
            )

        queue = make_element("queue")
        Gst.Bin.add(bin, queue)
        nvdsosd.link(queue)

    nvvideoconvert2 = make_element("nvvideoconvert")
    Gst.Bin.add(bin, nvvideoconvert2)
    if visualization:
        queue.link(nvvideoconvert2)

    capsfilter = make_element(
        "capsfilter", caps=Gst.Caps.from_string("video/x-raw, format=I420")
    )
    Gst.Bin.add(bin, capsfilter)
    nvvideoconvert2.link(capsfilter)

    avenc_mpeg4 = make_element("avenc_mpeg4", bitrate=2000000)
    Gst.Bin.add(bin, avenc_mpeg4)
    capsfilter.link(avenc_mpeg4)

    mpeg4videoparse = make_element("mpeg4videoparse")
    Gst.Bin.add(bin, mpeg4videoparse)
    avenc_mpeg4.link(mpeg4videoparse)

    qtmux = make_element("qtmux")
    Gst.Bin.add(bin, qtmux)
    mpeg4videoparse.link(qtmux)

    sink = make_element("filesink", location=output_path, sync=0)
    sink.set_property("async", 0)
    Gst.Bin.add(bin, sink)
    qtmux.link(sink)

    if visualization:
        bin.add_pad(Gst.GhostPad("sink", nvvideoconvert.get_static_pad("sink")))
    else:
        bin.add_pad(Gst.GhostPad("sink", nvvideoconvert2.get_static_pad("sink")))

    return bin
