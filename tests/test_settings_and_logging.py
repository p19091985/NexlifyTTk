import logging
import os
import sys


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from persistencia.logger import LogRedirector
from settings_manager import _deep_merge_defaults


class _ListHandler(logging.Handler):
    def __init__(self, bucket):
        super().__init__()
        self.bucket = bucket

    def emit(self, record):
        self.bucket.append(record.getMessage())


def test_deep_merge_defaults_clones_nested_defaults():
    source = {}
    defaults = {
        "custom_colors": {
            "primary": "#123456",
            "danger": "#ff0000",
        }
    }

    changed = _deep_merge_defaults(source, defaults)

    assert changed is True
    assert source["custom_colors"]["primary"] == "#123456"

    source["custom_colors"]["primary"] = "#abcdef"
    assert defaults["custom_colors"]["primary"] == "#123456"


def test_log_redirector_buffers_partial_lines_until_flush():
    logger = logging.getLogger("tests.log_redirector")
    logger.handlers.clear()
    logger.propagate = False

    messages = []
    handler = _ListHandler(messages)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    redirector = LogRedirector(logger, logging.INFO)

    redirector.write("primeira metade")
    assert messages == []

    redirector.write(" da linha\nsegunda metade")
    assert messages == ["primeira metade da linha"]

    redirector.flush()
    assert messages == ["primeira metade da linha", "segunda metade"]
