from __future__ import annotations

import multiprocessing as mp
from operator import itemgetter
from typing import Any, Callable

import cv2
import fire
import numpy as np
import pyds
from labels import labels
from sparrow_datums import AugmentedBoxTracking, ChunkStreamWriter, PType

import sparrow_mlpipes as mlp

MODEL_IMAGE_SIZE = 512
DURATION = 4


def chunk_writer_thread(
    queue: mp.Queue[list[dict[str, float]] | None],
    writer: ChunkStreamWriter,
    image_width: float,
    image_height: float,
    fps: float,
) -> None:
    """Pull frames from the queue and write chunks."""
    frames: list[list[dict[str, float]]] = []
    start_time = 0
    while True:
        frame = queue.get()
        if frame is not None:
            frames.append(frame)
        if len(frames) / fps >= DURATION or frame is None:
            chunk = make_chunk(frames, image_width, image_height, fps, start_time)
            writer.add_chunk(chunk)
            start_time += chunk.duration
            frames = []
        if frame is None:
            break
    writer.close()


def make_chunk(
    frames: list[list[dict[str, float]]],
    image_width: float,
    image_height: float,
    fps: float,
    start_time: float,
) -> AugmentedBoxTracking:
    """Create a tracking chunk for a list of frames."""
    global START_TIME
    n_frames = len(frames)
    object_ids_set = set()
    for boxes in frames:
        object_ids_set |= set([b["object_id"] for b in boxes])
    object_ids = sorted(map(str, object_ids_set))
    data = np.zeros((n_frames, len(object_ids), 6)) * np.nan
    for i, boxes in enumerate(frames):
        for box in boxes:
            box_array = np.array(
                itemgetter("x", "y", "width", "height", "score", "label")(box)
            )
            j = object_ids.index(str(box["object_id"]))
            data[i, j] = box_array
    return AugmentedBoxTracking(
        data,
        ptype=PType.absolute_tlwh,
        image_width=image_width,
        image_height=image_height,
        fps=fps,
        object_ids=object_ids,
        start_time=start_time,
    )


def make_visualization_callback(
    queue: mp.Queue[list[dict[str, float]] | None]
) -> Callable[..., mlp.Gst.PadProbeReturn]:
    """Create visualization callback with video settings."""
    global FRAMES_QUEUE

    def visualization_callback(
        _: Any, info: mlp.Gst.PadProbeInfo, __: Any
    ) -> mlp.Gst.PadProbeReturn:
        """Add tracking boxes to image for visualization."""
        # Intiallizing object counter with 0.
        batch_meta = mlp.get_batch_meta(info)
        for frame in mlp.pyds_generator(batch_meta.frame_meta_list):
            frame_meta = mlp.get_frame_meta(frame)
            frame_number = frame_meta.frame_num
            boxes = []
            for obj in mlp.pyds_generator(frame_meta.obj_meta_list):
                obj_meta = mlp.get_object_meta(obj)
                rect = obj_meta.rect_params
                boxes.append(
                    {
                        "x": rect.left,
                        "y": rect.top,
                        "width": rect.width,
                        "height": rect.height,
                        "score": obj_meta.confidence,
                        "label": obj_meta.class_id,
                        "object_id": obj_meta.object_id,
                    }
                )
                label = f"{labels[obj_meta.class_id]} {obj_meta.object_id}"
                obj_meta.text_params.display_text = label
                obj_meta.text_params.font_params.font_name = "Arial"
                obj_meta.rect_params.border_width = 3
                obj_meta.rect_params.border_color.set(0, 1, 1, 0)
            queue.put(boxes)
            print(f"Frame {frame_number}, Objects {len(boxes)}")
        return mlp.Gst.PadProbeReturn.OK

    return visualization_callback


def make_detection_callback(
    image_width: int, image_height: int, fps: float
) -> Callable[..., mlp.Gst.PadProbeReturn]:
    """Create visualization callback with video settings."""

    def detection_callback(
        _: Any, info: mlp.Gst.PadProbeInfo, __: Any
    ) -> mlp.Gst.PadProbeReturn:
        """Extract boxes from DeepStream metadata and track poles."""
        batch_meta = mlp.get_batch_meta(info)
        for frame in mlp.pyds_generator(batch_meta.frame_meta_list):
            frame_meta = mlp.get_frame_meta(frame)
            pyds.nvds_acquire_meta_lock(batch_meta)
            for user in mlp.pyds_generator(frame_meta.frame_user_meta_list):
                user_meta = mlp.get_user_meta(user)
                boxes = mlp.get_output_tensor(user_meta, 0)
                scores = mlp.get_output_tensor(user_meta, 1)
                class_indices = mlp.get_output_tensor(user_meta, 2)
                mask = scores > 0.5
                boxes = boxes[mask] / MODEL_IMAGE_SIZE
                scores = scores[mask]
                class_indices = class_indices[mask]
                for box, score, class_idx in zip(boxes, scores, class_indices):
                    x1, y1, x2, y2 = box
                    obj_meta = pyds.nvds_acquire_obj_meta_from_pool(batch_meta)
                    rect_params = obj_meta.rect_params
                    rect_params.left = int(image_width * x1)
                    rect_params.top = int(image_height * y1)
                    rect_params.width = int(image_width * (x2 - x1))
                    rect_params.height = int(image_height * (y2 - y1))

                    obj_meta.confidence = score
                    obj_meta.class_id = int(class_idx)
                    obj_meta.object_id = 0xFFFFFFFFFFFFFFFF
                    pyds.nvds_add_obj_meta_to_frame(frame_meta, obj_meta, None)

            frame_meta.bInferDone = True
            pyds.nvds_release_meta_lock(batch_meta)
        return mlp.Gst.PadProbeReturn.OK

    return detection_callback


def main(
    video_path: str,
    config_path: str = "./nvinferserver.pbtxt",
    output_path: str = "./out.mp4",
) -> None:
    """Execute pipeline."""
    cap = cv2.VideoCapture(video_path)
    fps = round(cap.get(cv2.CAP_PROP_FPS))
    image_width = round(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    image_height = round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    queue: mp.Queue[list[dict[str, float]] | None] = mp.Queue()
    writer = ChunkStreamWriter("stream/manifest.jsonl", AugmentedBoxTracking)
    writer_proc = mp.Process(
        target=chunk_writer_thread, args=(queue, writer, image_width, image_height, fps)
    )

    pipeline = mlp.Gst.Pipeline()
    source_bin = mlp.make_source_bin(video_path)
    pipeline.add(source_bin)

    inference_bin = mlp.make_nvinferserver_bin(
        config_path,
        width=image_width,
        height=image_height,
        fps=fps,
        inference_probe=make_detection_callback(image_width, image_height, fps),
    )
    pipeline.add(inference_bin)
    source_bin.link(inference_bin)

    tracking_bin = mlp.make_nvtracker_bin()
    pipeline.add(tracking_bin)
    inference_bin.link(tracking_bin)

    visualization_bin = mlp.make_visualization_bin(make_visualization_callback(queue))
    pipeline.add(visualization_bin)
    tracking_bin.link(visualization_bin)

    sink_bin = mlp.make_sink_bin(output_path)
    pipeline.add(sink_bin)
    visualization_bin.link(sink_bin)

    writer_proc.start()
    mlp.run_pipeline(pipeline)
    queue.put(None)
    writer_proc.join()


if __name__ == "__main__":
    fire.Fire(main)
