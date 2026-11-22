"""Tests of the entry point."""

from pathlib import Path

import pytest
from flask import Flask

from online_shop.main import main


def test_main_runs_the_app_without_debug(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    calls: list[dict[str, object]] = []

    def fake_run(self: Flask, **options: object) -> None:
        calls.append(options)

    monkeypatch.setattr(Flask, "run", fake_run)
    main("127.0.0.1", 5001, tmp_path / "shop.sqlite3")
    assert calls == [{"host": "127.0.0.1", "port": 5001, "debug": False}]
