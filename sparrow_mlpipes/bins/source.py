import sys
from pathlib import Path
from typing import Optional, no_type_check

from fsutil import is_dir

from sparrow_mlpipes.element import make_element
from sparrow_mlpipes.initialize import Gst


@no_type_check
def on_pad_added(_, decoder_src_pad, data) -> None:
    caps = decoder_src_pad.get_current_caps()
    gst_struct = caps.get_structure(0)
    gst_name = gst_struct.get_name()
    source_bin = data
    features = caps.get_features(0)

    if gst_name.find("video") != -1:
        if features.contains("memory:NVMM"):
            bin_ghost_pad = source_bin.get_static_pad("src")
            if not bin_ghost_pad.set_target(decoder_src_pad):
                sys.stderr.write(
                    "Failed to link decoder src pad to source bin ghost pad\n"
                )
        else:
            sys.stderr.write(" Error: Decodebin did not pick nvidia decoder plugin.\n")


@no_type_check
def on_child_added(_, obj, name, user_data) -> None:
    print(f"Decodebin child added: {name}")
    if name.find("decodebin") != -1:
        obj.connect("child-added", on_child_added, user_data)


def make_source_bin(input_uri: str, index: int = 0) -> Gst.Bin:
    bin = Gst.Bin.new(f"source-{index:02d}")
    if Path(input_uri).is_file():
        uridecodebin = make_element(
            "uridecodebin", "uri-decode-bin", uri=f"file://{Path(input_uri).absolute()}"
        )
        Gst.Bin.add(bin, uridecodebin)
        uridecodebin.connect("pad-added", on_pad_added, bin)
        uridecodebin.connect("child-added", on_child_added, bin)
        bin.add_pad(Gst.GhostPad.new_no_target("src", Gst.PadDirection.SRC))
    elif Path(input_uri).is_dir():
        multifilesrc = make_element(
            "multifilesrc",
            location=Path(input_uri, "%d.jpeg"),
            start_index=0,
        )
        Gst.Bin.add(bin, multifilesrc)

        jpegparse = make_element("jpegparse")
        Gst.Bin.add(jpegparse)
        multifilesrc.link(jpegparse)

        nvjpegdec = make_element("nvjpegdec")
        Gst.Bin.add(nvjpegdec)
        jpegparse.link(nvjpegdec)
        bin.add_pad(Gst.GhostPad("src", nvjpegdec.get_static_pad("src")))

    return bin
