from mlpipes import element
import pytest
from pytest_mock import MockerFixture

from mlpipes.initialize import Gst
from .source import rtsp_source_block, file_source_block, source_block

FAKE_RTSP_STREAM = "rtsp://foo-bar:554/hello"
FAKE_HTTP_VIDEO = "http://hello-world.com/video.mp4"
FAKE_FILE = "./test.mp4"


def test_rtsp_source_block__emits_h264():
    element = rtsp_source_block(FAKE_RTSP_STREAM)[-1]
    pad_template = element.gst_element.get_pad_template("src")
    assert "video/x-h264" in pad_template.caps.to_string()


def test_file_source_block__emits_h264():
    element = file_source_block(FAKE_FILE)[-1]
    pad_template = element.gst_element.get_pad_template("src")
    assert "video/x-h264" in pad_template.caps.to_string()


def test_source_block__calls_file_source_for_local_files(mocker: MockerFixture):
    file_source_block = mocker.patch("mlpipes.blocks.source.file_source_block")
    source_block(FAKE_FILE)
    file_source_block.assert_called_once_with(FAKE_FILE)


def test_source_block__calls_rtsp_source_for_rtsp_uris(mocker: MockerFixture):
    rtsp_source_block = mocker.patch("mlpipes.blocks.source.rtsp_source_block")
    source_block(FAKE_RTSP_STREAM)
    rtsp_source_block.assert_called_once_with(FAKE_RTSP_STREAM)


def test_source_block__raises_for_invalid_scheme():
    with pytest.raises(NotImplementedError):
        source_block(FAKE_HTTP_VIDEO)
