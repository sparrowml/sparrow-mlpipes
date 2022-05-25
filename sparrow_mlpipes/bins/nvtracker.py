from sparrow_mlpipes.constants import DEEPSTREAM_DIRECTORY
from sparrow_mlpipes.element import make_element
from sparrow_mlpipes.initialize import Gst


def make_nvtracker_bin() -> Gst.Bin:
    """Create and configure nvtracker element."""
    ll_lib_file = DEEPSTREAM_DIRECTORY / "lib/libnvds_nvmultiobjecttracker.so"
    nvtracker = make_element("nvtracker", ll_lib_file=str(ll_lib_file))
    return nvtracker
