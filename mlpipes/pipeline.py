from typing import List

from .initialize import Gst, GLib
from .element import Element
from .exceptions import PipelineError


def bus_call(_, message: Gst.Message, loop: GLib.MainLoop):
    if message.type == Gst.MessageType.EOS:
        loop.quit()
    elif message.type == Gst.MessageType.ERROR:
        error, debug = message.parse_error()
        loop.quit()
        raise PipelineError(f"{error} -- {debug}")


class Pipeline:
    def __init__(self):
        self._pipeline: Gst.Pipeline = Gst.Pipeline()
        self.elements: List[Element] = []

    def add(self, element: Element):
        self._pipeline.add(element.gst_element)
        if self.elements:
            self.elements[-1].link(element)
        self.elements.append(element)

    def add_block(self, elements: List[Element]):
        for element in elements:
            self.add(element)

    def run(self):
        loop = GLib.MainLoop()
        bus = self._pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", bus_call, loop)

        print("Starting pipeline")
        self._pipeline.set_state(Gst.State.PLAYING)
        try:
            loop.run()
        except:
            loop.quit()
            pass

        # Clean up
        self._pipeline.set_state(Gst.State.NULL)
