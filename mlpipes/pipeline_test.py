import pytest

from .element import Element
from .pipeline import Pipeline
from .exceptions import PipelineError


def test_add__links_elements():
    pipeline = Pipeline()
    a = Element("fakesrc")
    pipeline.add(a)
    b = Element("fakesink")
    pipeline.add(b)
    assert b.gst_element.get_static_pad("sink").is_linked()


def test_add_block__adds_multiple_elements():
    pipeline = Pipeline()
    pipeline.add_block(
        [
            Element("videotestsrc", name="a"),
            Element("x264enc", name="b"),
            Element("fakesink", name="c"),
        ]
    )
    assert tuple(element.name for element in pipeline.elements) == ("a", "b", "c")
