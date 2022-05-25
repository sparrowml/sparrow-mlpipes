from typing import Any, Callable, Optional, Tuple

from sparrow_mlpipes.element import make_element
from sparrow_mlpipes.initialize import Gst


def make_nvinfer_bin(
    config_path: str,
    width: int,
    height: int,
    fps: Optional[int] = None,
    enable_padding: bool = True,
    inference_probe: Optional[
        Callable[[Gst.Pad, Gst.PadProbeInfo, Tuple[Any, ...]], Gst.PadProbeReturn]
    ] = None,
) -> Gst.Bin:
    bin = Gst.Bin.new("inference")
    caps = None
    if fps:
        videorate = make_element("videorate")
        Gst.Bin.add(bin, videorate)
        caps = make_element(
            "capsfilter",
            caps=Gst.Caps.from_string(f"video/x-raw(memory:NVMM), framerate={fps}/1"),
        )
        Gst.Bin.add(bin, caps)
        videorate.link(caps)

    nvstreammux = make_element(
        "nvstreammux",
        width=width,
        height=height,
        batch_size=1,
        enable_padding=enable_padding,
    )
    Gst.Bin.add(bin, nvstreammux)
    if caps:
        caps.get_static_pad("src").link(nvstreammux.get_request_pad("sink_0"))

    nvinfer = make_element("nvinfer", config_file_path=config_path)
    Gst.Bin.add(bin, nvinfer)
    nvstreammux.link(nvinfer)
    if inference_probe:
        nvinfer.get_static_pad("src").add_probe(
            Gst.PadProbeType.BUFFER, inference_probe, 0
        )

    if caps:
        bin.add_pad(Gst.GhostPad("sink", videorate.get_static_pad("sink")))
    else:
        bin.add_pad(Gst.GhostPad("sink", nvstreammux.get_request_pad("sink_0")))
    bin.add_pad(Gst.GhostPad("src", nvinfer.get_static_pad("src")))

    return bin
