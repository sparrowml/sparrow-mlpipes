from pathlib import Path
from typing import Optional, Union

from sparrow_mlpipes.constants import DEEPSTREAM_DIRECTORY
from sparrow_mlpipes.element import make_element
from sparrow_mlpipes.initialize import Gst


def make_nvtracker_bin(
    tracker_config_path: Optional[Union[Path, str]] = None
) -> Gst.Bin:
    """Create and configure nvtracker element."""
    kwargs = dict(
        ll_lib_file=str(DEEPSTREAM_DIRECTORY / "lib/libnvds_nvmultiobjecttracker.so")
    )
    if tracker_config_path:
        kwargs["ll_config_file"] = str(tracker_config_path)
    nvtracker = make_element("nvtracker", **kwargs)
    return nvtracker
