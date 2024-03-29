from typing import Optional

from sparrow_mlpipes.element import make_element
from sparrow_mlpipes.initialize import Gst


def make_sink_bin(output_path: str, bitrate_scale: Optional[float] = None) -> Gst.Bin:
    bin = Gst.Bin.new("sink")

    nvvideoconvert = make_element("nvvideoconvert")
    Gst.Bin.add(bin, nvvideoconvert)

    capsfilter = make_element(
        "capsfilter", caps=Gst.Caps.from_string("video/x-raw, format=I420")
    )
    Gst.Bin.add(bin, capsfilter)
    nvvideoconvert.link(capsfilter)

    bitrate_kwargs = {}
    if bitrate_scale is not None:
        assert 0 < bitrate_scale <= 1
        bitrate_kwargs["bitrate"] = round(bitrate_scale * 2147483647)
    avenc_mpeg4 = make_element("avenc_mpeg4", **bitrate_kwargs)
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

    bin.add_pad(Gst.GhostPad("sink", nvvideoconvert.get_static_pad("sink")))

    return bin
