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


def main(video_path: str, config_path: str = "./nvinfer.config", output_path: str = "./out.mp4"):
    pipeline = mlp.Gst.Pipeline()
    source_bin = mlp.make_source_bin(video_path)
    pipeline.add(source_bin)

    inference_bin = mlp.make_nvinfer_bin(
        config_path,
        width=WIDTH,
        height=HEIGHT,
        fps=FPS,
        inference_probe=print_objects_pad,
    )
    pipeline.add(inference_bin)
    source_bin.link(inference_bin)

    visualization_bin = mlp.make_visualization_bin()
    pipeline.add(visualization_bin)
    inference_bin.link(visualization_bin)

    sink_bin = mlp.make_sink_bin(output_path)
    pipeline.add(sink_bin)
    visualization_bin.link(sink_bin)

    mlp.run_pipeline(pipeline)


if __name__ == "__main__":
    fire.Fire(main)
