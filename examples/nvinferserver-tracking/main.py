import time
from typing import no_type_check

import fire
import pyds
from labels import labels

import sparrow_mlpipes as mlp

WIDTH = 1920
HEIGHT = 1080
FPS = 20


@no_type_check
def visualization_callback(_, info, __) -> mlp.Gst.PadProbeReturn:
    """Add tracking boxes to image for visualization."""
    # Intiallizing object counter with 0.
    batch_meta = mlp.get_batch_meta(info)
    for frame in mlp.pyds_generator(batch_meta.frame_meta_list):
        frame_meta = mlp.get_frame_meta(frame)
        frame_number = frame_meta.frame_num
        for obj in mlp.pyds_generator(frame_meta.obj_meta_list):
            obj_meta = mlp.get_object_meta(obj)
            label = f"{labels[obj_meta.class_id]} {obj_meta.object_id}"
            obj_meta.text_params.display_text = label
            obj_meta.text_params.font_params.font_name = "Arial"
            obj_meta.rect_params.border_width = 3
            obj_meta.rect_params.border_color.set(0, 1, 1, 0)
            timestamp = time.strftime("%H:%M:%S", time.gmtime(frame_number / FPS))
            print("Track", timestamp, label)
    return mlp.Gst.PadProbeReturn.OK


@no_type_check
def detection_callback(_, info, __) -> mlp.Gst.PadProbeReturn:
    """Extract boxes from DeepStream metadata and track poles."""
    batch_meta = mlp.get_batch_meta(info)
    for frame in mlp.pyds_generator(batch_meta.frame_meta_list):
        frame_meta = mlp.get_frame_meta(frame)
        pyds.nvds_acquire_meta_lock(batch_meta)
        frame_number = frame_meta.frame_num
        # n_boxes = 0
        for user in mlp.pyds_generator(frame_meta.frame_user_meta_list):
            user_meta = mlp.get_user_meta(user)
            boxes = mlp.get_output_tensor(user_meta, 0)
            scores = mlp.get_output_tensor(user_meta, 1)
            class_indices = mlp.get_output_tensor(user_meta, 2)
            mask = scores > 0.5
            boxes = boxes[mask] / 512
            scores = scores[mask]
            class_indices = class_indices[mask]
            for box, score, class_idx in zip(boxes, scores, class_indices):
                x1, y1, x2, y2 = box
                obj_meta = pyds.nvds_acquire_obj_meta_from_pool(batch_meta)
                rect_params = obj_meta.rect_params
                rect_params.left = int(WIDTH * x1)
                rect_params.top = int(HEIGHT * y1)
                rect_params.width = int(WIDTH * (x2 - x1))
                rect_params.height = int(HEIGHT * (y2 - y1))

                obj_meta.confidence = score
                obj_meta.class_id = class_idx
                obj_meta.object_id = 0xFFFFFFFFFFFFFFFF
                pyds.nvds_add_obj_meta_to_frame(frame_meta, obj_meta, None)

            n_boxes = len(boxes)
        frame_meta.bInferDone = True
        pyds.nvds_release_meta_lock(batch_meta)
        timestamp = time.strftime("%H:%M:%S", time.gmtime(frame_number / FPS))
        print(f"Detection {timestamp} {n_boxes}")
    return mlp.Gst.PadProbeReturn.OK


def main(
    video_path: str,
    config_path: str = "./nvinferserver.pbtxt",
    output_path: str = "./out.mp4",
) -> None:
    pipeline = mlp.Gst.Pipeline()
    source_bin = mlp.make_source_bin(video_path)
    pipeline.add(source_bin)

    inference_bin = mlp.make_nvinferserver_bin(
        config_path,
        width=WIDTH,
        height=HEIGHT,
        fps=FPS,
        inference_probe=detection_callback,
    )
    pipeline.add(inference_bin)
    source_bin.link(inference_bin)

    tracking_bin = mlp.make_nvtracker_bin()
    pipeline.add(tracking_bin)
    inference_bin.link(tracking_bin)

    visualization_bin = mlp.make_visualization_bin(visualization_callback)
    pipeline.add(visualization_bin)
    tracking_bin.link(visualization_bin)

    sink_bin = mlp.make_sink_bin(output_path)
    pipeline.add(sink_bin)
    visualization_bin.link(sink_bin)

    mlp.run_pipeline(pipeline)


if __name__ == "__main__":
    fire.Fire(main)
