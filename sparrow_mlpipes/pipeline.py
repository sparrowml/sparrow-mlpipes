from .initialize import Gst, GLib
from .exceptions import PipelineError


def bus_call(_, message: Gst.Message, loop: GLib.MainLoop):
    if message.type == Gst.MessageType.EOS:
        loop.quit()
    elif message.type == Gst.MessageType.ERROR:
        error, debug = message.parse_error()
        loop.quit()
        raise PipelineError(f"{error} -- {debug}")


def run_pipeline(pipeline: Gst.Pipeline) -> None:
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
