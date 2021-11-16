import fire
import mlpipes as mlp
import pyds

PGIE_CLASS_ID_VEHICLE = 0
PGIE_CLASS_ID_BICYCLE = 1
PGIE_CLASS_ID_PERSON = 2
PGIE_CLASS_ID_ROADSIGN = 3

WIDTH = 1920
HEIGHT = 1080
FPS = 30


def print_objects_pad(_, info, __):
    frame_number = 0
    # Intiallizing object counter with 0.
    obj_counter = {
        PGIE_CLASS_ID_VEHICLE: 0,
        PGIE_CLASS_ID_PERSON: 0,
        PGIE_CLASS_ID_BICYCLE: 0,
        PGIE_CLASS_ID_ROADSIGN: 0,
    }
    num_rects = 0

    gst_buffer = info.get_buffer()
    if not gst_buffer:
        print("Unable to get GstBuffer ")
        return

    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
    for frame in mlp.pyds_generator(batch_meta.frame_meta_list):
        frame_meta = pyds.NvDsFrameMeta.cast(frame.data)
        frame_number = frame_meta.frame_num
        num_rects = frame_meta.num_obj_meta
        for obj in mlp.pyds_generator(frame_meta.obj_meta_list):
            obj_meta = pyds.NvDsObjectMeta.cast(obj.data)
            obj_counter[obj_meta.class_id] += 1
            obj_meta.rect_params.border_color.set(0.0, 0.0, 1.0, 0.0)
        message = (
            f"Frame Number={frame_number} "
            f"Number of Objects={num_rects} "
            f"Vehicle Count={obj_counter[PGIE_CLASS_ID_VEHICLE]} "
            f"Person Count={obj_counter[PGIE_CLASS_ID_PERSON]}"
        )
        print(message)

    return mlp.Gst.PadProbeReturn.OK


def main(video_path: str, config_path: str = "./nvinfer.config"):
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
