# src/zencopybook/consts/__init__.py
from PySide6.QtGui import QColor

DEFAULT_GRID_COLOR = QColor("#D0D0D0")
DEFAULT_TEXT_COLOR = QColor("#999999")
DEFAULT_FONT_FAMILY = "SimSun"
DEFAULT_GRID_TYPE = "米字格"

__all__ = [
    "DEFAULT_FONT_FAMILY",
    "DEFAULT_GRID_COLOR",
    "DEFAULT_GRID_TYPE",
    "DEFAULT_TEXT_COLOR",
]