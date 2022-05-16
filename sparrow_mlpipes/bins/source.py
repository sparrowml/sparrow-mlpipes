import sys
from pathlib import Path
from typing import no_type_check

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
    uridecodebin = make_element(
        "uridecodebin", "uri-decode-bin", uri=f"file://{Path(input_uri).absolute()}"
    )
    Gst.Bin.add(bin, uridecodebin)
    uridecodebin.connect("pad-added", on_pad_added, bin)
    uridecodebin.connect("child-added", on_child_added, bin)
    bin.add_pad(Gst.GhostPad.new_no_target("src", Gst.PadDirection.SRC))
    return bin
