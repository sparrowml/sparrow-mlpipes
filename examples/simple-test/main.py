import fire

import sparrow_mlpipes as mlp


def main(path: str) -> None:
    """Get multifilesrc working."""
    pipeline = mlp.Gst.Pipeline()
    multifilesrc = mlp.make_element("multifilesrc", location=path, start_index=1)
    pipeline.add(multifilesrc)

    jpegparse = mlp.make_element("jpegparse")
    pipeline.add(jpegparse)
    multifilesrc.link(jpegparse)

    nvjpegdec = mlp.make_element("nvjpegdec")
    pipeline.add(nvjpegdec)
    jpegparse.link(nvjpegdec)

    nvstreammux = mlp.make_element(
        "nvstreammux",
        width=1920,
        height=1080,
        batch_size=1,
        enable_padding=True,
    )
    pipeline.add(nvstreammux)
    nvjpegdec.get_static_pad("src").link(nvstreammux.get_request_pad("sink_0"))

    fakesink = mlp.make_element("fakesink")
    pipeline.add(fakesink)
    nvstreammux.link(fakesink)

    print("Running pipeline...")
    mlp.run_pipeline(pipeline)


if __name__ == "__main__":
    fire.Fire(main)
