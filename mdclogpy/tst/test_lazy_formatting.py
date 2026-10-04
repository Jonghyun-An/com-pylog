# SPDX-License-Identifier: Apache-2.0
import json
from collections import UserDict
from unittest.mock import Mock

import pytest
import mdclogpy
from mdclogpy import Logger, Level


@pytest.mark.parametrize("root", [False, True])
@pytest.mark.parametrize("method, level", [
    ("debug", Level.DEBUG), ("info", Level.INFO),
    ("warning", Level.WARNING), ("error", Level.ERROR), ("log", Level.INFO),
])
def test_percent_formatting(root, method, level, monkeypatch):
    logger = Logger(name="lazy", level=Level.DEBUG)
    output = Mock()
    monkeypatch.setattr(logger, "_output_log", output)
    if root:
        monkeypatch.setattr(mdclogpy, "_root_logger", logger)
    target = mdclogpy if root else logger
    fn = getattr(target, method)
    args = (level,) if method == "log" else ()
    fn(*args, "Pre-send: %s, Post-send: %s", "before", "after")
    entry = json.loads(output.call_args[0][0])
    assert entry["msg"] == "Pre-send: before, Post-send: after"
    assert entry["crit"] == level.name


@pytest.mark.parametrize("root", [False, True])
def test_filtered_message_is_not_formatted(root, monkeypatch):
    logger = Logger(level=Level.ERROR)
    argument = Mock()
    argument.__str__ = Mock(side_effect=AssertionError("filtered argument evaluated"))
    if root:
        monkeypatch.setattr(mdclogpy, "_root_logger", logger)
    (mdclogpy if root else logger).debug("%s", argument)
    argument.__str__.assert_not_called()


@pytest.mark.parametrize("mapping", [dict, UserDict])
def test_mapping_formatting(mapping, monkeypatch):
    logger = Logger(level=Level.INFO)
    output = Mock()
    monkeypatch.setattr(logger, "_output_log", output)
    logger.info("%(model)s v%(version)d", mapping(model="demo", version=2))
    assert json.loads(output.call_args[0][0])["msg"] == "demo v2"


@pytest.mark.parametrize("message", ["literal 100%", "literal %s", "한글"])
def test_existing_message_without_arguments(message, monkeypatch):
    logger = Logger(level=Level.INFO)
    output = Mock()
    monkeypatch.setattr(logger, "_output_log", output)
    logger.info(message)
    assert json.loads(output.call_args[0][0])["msg"] == message
