from typing import Any, Callable, Optional

from .initialize import Gst


class Element:
    def __init__(self, factory_name: str, name: Optional[str] = None, **kwargs):
        self.gst_element: Gst.Element = Gst.ElementFactory.make(factory_name, name)
        self._link: Optional[Callable[["Element", "Element"], bool]] = None
        for key, value in kwargs.items():
            self.set_property(key.replace("_", "-"), value)

    def link(self, element: "Element") -> bool:
        if self._link:
            return self._link(self, element)
        return self.gst_element.link(element.gst_element)

    def set_link(self, link: Callable[["Element", "Element"], bool]):
        self._link = link

    @property
    def name(self) -> str:
        return self.gst_element.name

    def set_property(self, name: str, value: Any):
        self.gst_element.set_property(name, value)

    def get_property(self, name: str) -> Any:
        return self.gst_element.get_property(name)

    def add_source_probe(self, probe: Callable):
        self.gst_element.get_static_pad("src").add_probe(
            Gst.PadProbeType.BUFFER, probe, 0
        )
