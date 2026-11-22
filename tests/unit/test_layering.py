"""The business layers and the SQLite adapter must not import Flask."""

from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[2] / "src/online_shop"
INNER_LAYERS = ["domain", "application", "infrastructure"]


@pytest.mark.parametrize("layer", INNER_LAYERS)
def test_inner_layer_does_not_import_flask(layer: str) -> None:
    for path in (SRC / layer).rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "import flask" not in source, path
        assert "from flask" not in source, path
        assert "werkzeug" not in source, path
