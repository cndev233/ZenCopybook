from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPen


class CopybookDrawer:
    COLS = 10
    ROWS = 14
    CHARS_PER_PAGE = COLS * ROWS

    @staticmethod
    def draw_page(
        text_slice: str,
        grid_type: str,
        grid_color: QColor,
        text_color: QColor,
        font_family: str,
    ) -> QImage:
        width, height = 1240, 1754
        margin_x, margin_y = 70, 90

        image = QImage(width, height, QImage.Format_ARGB32)
        image.fill(Qt.white)

        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)

        cell_size = (width - 2 * margin_x) / CopybookDrawer.COLS

        pen_solid = QPen(grid_color, 2, Qt.SolidLine)
        pen_dashed = QPen(grid_color, 1, Qt.DashLine)

        font = QFont(font_family)
        font.setPixelSize(int(cell_size * 0.75))
        painter.setFont(font)

        text_idx = 0

        for r in range(CopybookDrawer.ROWS):
            for c in range(CopybookDrawer.COLS):
                x = margin_x + c * cell_size
                y = margin_y + r * cell_size

                painter.setPen(pen_solid)
                painter.drawRect(QRectF(x, y, cell_size, cell_size))

                if grid_type == "米字格":
                    painter.setPen(pen_dashed)
                    painter.drawLine(x + cell_size / 2, y, x + cell_size / 2, y + cell_size)
                    painter.drawLine(x, y + cell_size / 2, x + cell_size, y + cell_size / 2)
                    painter.drawLine(x, y, x + cell_size, y + cell_size)
                    painter.drawLine(x + cell_size, y, x, y + cell_size)
                elif grid_type == "田字格":
                    painter.setPen(pen_dashed)
                    painter.drawLine(x + cell_size / 2, y, x + cell_size / 2, y + cell_size)
                    painter.drawLine(x, y + cell_size / 2, x + cell_size, y + cell_size / 2)

                if text_idx < len(text_slice):
                    char = text_slice[text_idx]
                    painter.setPen(QPen(text_color))
                    rect = QRectF(x, y, cell_size, cell_size)
                    painter.drawText(rect, Qt.AlignCenter, char)
                    text_idx += 1

        painter.end()
        return image