from typing import Any, Callable, List, Optional, Tuple

from mlpipes.initialize import Gst
from mlpipes.element import Element

BATCH_SIZE = 1


def inference_block(
    config_path: str,
    width: int,
    height: int,
    fps: int = 30,
    inference_probe: Optional[
        Callable[[Gst.Pad, Gst.PadProbeInfo, Tuple[Any, ...]], Gst.PadProbeReturn]
    ] = None,
) -> List[Element]:
    decoder = Element("nvv4l2decoder")
    videorate = Element("videorate")
    caps = Element(
        "capsfilter",
        caps=Gst.Caps.from_string(f"video/x-raw(memory:NVMM), framerate={fps}/1"),
    )

    def caps_link(self: Element, other: Element) -> bool:
        source_pad = self.gst_element.get_static_pad("src")
        sink_pad = other.gst_element.get_request_pad("sink_0")
        return source_pad.link(sink_pad)

    caps.set_link(caps_link)
    batcher = Element("nvstreammux", width=width, height=height, batch_size=BATCH_SIZE)
    if config_path.endswith(".config"):
        inference = Element("nvinfer", config_file_path=config_path)
    elif config_path.endswith(".pbtxt"):
        inference = Element("nvinferserver", config_file_path=config_path)
    else:
        raise ValueError(
            "config_path must end with .config for nvinfer or .pbtxt for nvinferserver"
        )
    if inference_probe:
        inference.add_source_probe(inference_probe)
    return [decoder, videorate, caps, batcher, inference]
