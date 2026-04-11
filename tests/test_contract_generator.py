import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

from app.services.contract_generator import _parse_response, _yaml_to_json


class TestParseResponse:
    def test_parses_valid_response(self):
        raw = """
<openapi>
openapi: "3.1.0"
info:
  title: Test API
  version: "1.0.0"
paths: {}
</openapi>

<markdown>
# Test API
Some documentation.
</markdown>
"""
        openapi_yaml, markdown = _parse_response(raw)
        assert "openapi" in openapi_yaml
        assert "Test API" in openapi_yaml
        assert "# Test API" in markdown

    def test_raises_when_openapi_block_missing(self):
        raw = "<markdown>Some docs</markdown>"
        with pytest.raises(ValueError, match="<openapi>"):
            _parse_response(raw)

    def test_raises_when_markdown_block_missing(self):
        raw = "<openapi>openapi: '3.1.0'\ninfo:\n  title: T\n  version: '1'\npaths: {}</openapi>"
        with pytest.raises(ValueError, match="<markdown>"):
            _parse_response(raw)

    def test_strips_whitespace_from_blocks(self):
        raw = "<openapi>\n  openapi: '3.1.0'\n  info:\n    title: T\n    version: '1'\n  paths: {}\n</openapi>\n<markdown>\n  # Docs\n</markdown>"
        openapi_yaml, markdown = _parse_response(raw)
        assert not openapi_yaml.startswith("\n")
        assert not markdown.startswith("\n")


class TestYamlToJson:
    def test_converts_valid_yaml(self):
        yaml_str = "openapi: '3.1.0'\ninfo:\n  title: My API\n  version: '1.0'\npaths: {}"
        result = _yaml_to_json(yaml_str)
        assert result["openapi"] == "3.1.0"
        assert result["info"]["title"] == "My API"

    def test_raises_on_invalid_yaml(self):
        with pytest.raises(ValueError, match="not valid"):
            _yaml_to_json("this: is: not: valid: yaml: :")
