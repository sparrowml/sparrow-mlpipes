from typing import Any

from .exceptions import PipelineError
from .initialize import GLib, Gst


def bus_call(_: Any, message: Gst.Message, loop: GLib.MainLoop) -> None:
    """Handle bus messages."""
    if message.type == Gst.MessageType.EOS:
        loop.quit()
    elif message.type == Gst.MessageType.ERROR:
        error, debug = message.parse_error()
        loop.quit()
        raise PipelineError(f"{error} -- {debug}")


def run_pipeline(pipeline: Gst.Pipeline) -> None:
    """Run a GStreamer pipeline."""
    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, loop)

    print("Starting pipeline")
    pipeline.set_state(Gst.State.PLAYING)
    try:
        loop.run()
    except:
        loop.quit()
        pass

    # Clean up
    pipeline.set_state(Gst.State.NULL)
