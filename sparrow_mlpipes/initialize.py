import gi

gi.require_version("Gst", "1.0")
gi.require_version('GstPbutils', '1.0')

# pylint: disable=unused-import
from gi.repository import GLib, Gst, GstPbutils

Gst.init(None)
