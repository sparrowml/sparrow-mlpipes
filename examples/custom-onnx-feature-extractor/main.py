import ctypes

import fire
import mlpipes as mlp
import numpy as np
import pyds

WIDTH = 1920
HEIGHT = 1080
FPS = 30


def print_objects_pad(_, info, __):
    frame_number = 0

    gst_buffer = info.get_buffer()
    if not gst_buffer:
        print("Unable to get GstBuffer ")
        return

    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
    for frame in mlp.pyds_generator(batch_meta.frame_meta_list):
        frame_meta = pyds.NvDsFrameMeta.cast(frame.data)
        frame_number = frame_meta.frame_num
        for user in mlp.pyds_generator(frame_meta.frame_user_meta_list):
            user_meta = pyds.NvDsUserMeta.cast(user.data)
            tensor_meta = pyds.NvDsInferTensorMeta.cast(user_meta.user_meta_data)
            layer = pyds.get_nvds_LayerInfo(tensor_meta, 0)
            ptr = ctypes.cast(
                pyds.get_ptr(layer.buffer), ctypes.POINTER(ctypes.c_float)
            )
            features = np.ctypeslib.as_array(ptr, shape=(256, 32, 32))
            print(frame_number, features.mean(), features.std())

    return mlp.Gst.PadProbeReturn.OK


def main(video_path: str, config_path: str = "./nvinferserver.pbtxt"):
    pipeline = mlp.Pipeline()
    pipeline.add_block(mlp.blocks.source_block(video_path))
    pipeline.add_block(
        mlp.blocks.inference_block(
            config_path,
            width=WIDTH,
            height=HEIGHT,
            fps=FPS,
            inference_probe=print_objects_pad,
        )
    )
    pipeline.add(mlp.Element("fakesink"))
    pipeline.run()


if __name__ == "__main__":
    fire.Fire(main)
