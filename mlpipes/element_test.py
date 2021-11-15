from .element import Element


def test_constructor__sets_name():
    element = Element("fakesink", name="foo bar")
    assert element.name == "foo bar"


def test_constructor__sets_properties():
    element = Element("videotestsrc", pattern=3)
    assert element.get_property("pattern").real == 3


def test_link__links_elements():
    a = Element("fakesrc")
    b = Element("fakesink")
    assert a.link(b)
