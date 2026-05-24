"""Umbrella test — passes when widget module is importable."""
from src.widget import format_widget
from src.types import Widget


def test_widget_format_basic():
    w = Widget(name="alpha", value=5)
    assert format_widget(w).startswith("alpha")
