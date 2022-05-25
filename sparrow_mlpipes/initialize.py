import gi

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst  # pylint: disable=unused-import

Gst.init(None)
