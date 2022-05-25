from typing import Optional

from .initialize import Gst


def make_element(
    factory_name: str, element_name: Optional[str] = None, **kwargs: str
) -> Gst.Element:
    """Create a GStreamer element."""
    element = Gst.ElementFactory.make(factory_name, element_name)
    for key, value in kwargs.items():
        element.set_property(key.replace("_", "-"), value)
    return element
