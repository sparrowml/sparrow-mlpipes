import ctypes
from typing import Generator, Union

import numpy as np
import numpy.typing as npt
import pyds

from .initialize import Gst


def get_batch_meta(info: Gst.PadProbeInfo) -> pyds.NvDsBatchMeta:
    """Get the NvDsBatchMeta object."""
    return pyds.gst_buffer_get_nvds_batch_meta(hash(info.get_buffer()))


def get_frame_meta(frame: pyds.GList) -> pyds.NvDsFrameMeta:
    """Get the NvDsFrameMeta object."""
    return pyds.NvDsFrameMeta.cast(frame.data)


def get_user_meta(user: pyds.GList) -> pyds.NvDsUserMeta:
    """Get the NvDsUserMeta object."""
    return pyds.NvDsUserMeta.cast(user.data)


def get_object_meta(obj: pyds.GList) -> pyds.NvDsObjectMeta:
    """Get the NvDsObjectMeta object."""
    return pyds.NvDsObjectMeta.cast(obj.data)


def get_output_tensor(
    user_meta: pyds.NvDsUserMeta,
    layer_index: int,
) -> npt.NDArray[np.float64]:
    """Convert an NvDsUserMeta object into a NumPy array."""
    tensor_meta = pyds.NvDsInferTensorMeta.cast(user_meta.user_meta_data)
    layer = pyds.get_nvds_LayerInfo(tensor_meta, layer_index)
    pointer = ctypes.cast(pyds.get_ptr(layer.buffer), ctypes.POINTER(ctypes.c_float))
    return np.ctypeslib.as_array(pointer, shape=layer.dims.d[: layer.dims.numDims])


def pyds_generator(
    pyds_list: pyds.GList,
) -> Generator[Union[pyds.NvDsFrameMeta, pyds.NvDsObjectMeta], None, None]:
    """Create a generator of frame/object meta instances."""
    if pyds_list is None:
        return
    yield pyds_list
    while pyds_list:
        pyds_list = pyds_list.next
        if pyds_list is None:
            return
        yield pyds_list
