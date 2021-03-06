import time

import fire
import pyds
from sparrow_datums import FrameAugmentedBoxes, PType, non_max_suppression

import sparrow_mlpipes as mlp

WIDTH = 1920
HEIGHT = 1080
FPS = 20


def print_objects_pad(_, info, __):
    # Intiallizing object counter with 0.
    batch_meta = mlp.get_batch_meta(info)
    pyds.nvds_acquire_meta_lock(batch_meta)
    for frame in mlp.pyds_generator(batch_meta.frame_meta_list):
        frame_meta = mlp.get_frame_meta(frame)
        for user in mlp.pyds_generator(frame_meta.frame_user_meta_list):
            user_meta = mlp.get_user_meta(user)
            augmented_boxes = mlp.get_output_tensor(user_meta, 0)
            boxes = non_max_suppression(
                FrameAugmentedBoxes(
                    augmented_boxes,
                    ptype=PType.relative_tlbr,
                    image_width=WIDTH,
                    image_height=HEIGHT,
                )
            )
            print(boxes.shape)
            for box in boxes:
                obj_meta = pyds.nvds_acquire_obj_meta_from_pool(batch_meta)
                obj_meta.rect_params.left = WIDTH * box.x1
                obj_meta.rect_params.top = HEIGHT * box.y1
                obj_meta.rect_params.width = WIDTH * box.w
                obj_meta.rect_params.height = HEIGHT * box.h
                obj_meta.rect_params.border_width = 3
                obj_meta.rect_params.border_color.set(0, box.label / 91, box.score, 0)
                pyds.nvds_add_obj_meta_to_frame(frame_meta, obj_meta, None)

    pyds.nvds_release_meta_lock(batch_meta)
    return mlp.Gst.PadProbeReturn.OK


def main(
    video_path: str,
    config_path: str = "./nvinfer.config",
    output_path: str = "./out.mp4",
) -> None:
    tic = time.time()
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
    toc = time.time() - tic
    print(toc)


if __name__ == "__main__":
    fire.Fire(main)
