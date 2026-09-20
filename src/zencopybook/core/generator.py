from typing import Any

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPen

from zencopybook.consts import (
    DEFAULT_FONT_FAMILY,
    DEFAULT_GRID_COLOR,
    DEFAULT_GRID_TYPE,
    DEFAULT_TEXT_COLOR,
)


class CopybookDrawer:
    COLS = 10
    ROWS = 14
    CHARS_PER_PAGE = COLS * ROWS

    @staticmethod
    def parse_layout(
        text: str,
        grid_rows: int = ROWS,
        grid_cols: int = COLS,
        auto_indent: bool = False
    ) -> list[list[dict[str, Any]]]:
        """
        将文本按段落和米字格矩阵进行二维排版解析。
        
        :param text: 原始输入文本
        :param grid_rows: 页面行数
        :param grid_cols: 页面列数
        :param auto_indent: 是否在每个自然段首行自动缩进 2 格
        :return: 包含多页数据的列表，每页为字典列表 [{row, col, char}, ...]
        """
        pages = []
        current_page = []
        current_row = 0
        current_col = 0

        # 按换行符切分为自然段落
        paragraphs = text.splitlines()

        for p_idx, paragraph in enumerate(paragraphs):
            # 处理空行段落（连续换行）
            if not paragraph.strip():
                if current_row < grid_rows - 1:
                    current_row += 1
                    current_col = 0
                else:
                    # 当前页已满，换页
                    pages.append(current_page)
                    current_page = []
                    current_row = 0
                    current_col = 0
                continue

            # 段首自动缩进 2 格
            if auto_indent:
                current_col += 2
                if current_col >= grid_cols:
                    current_row += 1
                    current_col = current_col % grid_cols
                    if current_row >= grid_rows:
                        pages.append(current_page)
                        current_page = []
                        current_row = 0

            # 排版段落中的每个字符
            for char in paragraph:
                current_page.append({
                    "row": current_row,
                    "col": current_col,
                    "char": char
                })

                current_col += 1
                # 满列自动折行
                if current_col >= grid_cols:
                    current_col = 0
                    current_row += 1
                    # 满行自动换页
                    if current_row >= grid_rows:
                        pages.append(current_page)
                        current_page = []
                        current_row = 0

            # 段落结束：强制换行（下一段从新的一行行首开始）
            if current_col > 0:
                current_col = 0
                current_row += 1
                if current_row >= grid_rows:
                    pages.append(current_page)
                    current_page = []
                    current_row = 0

        if current_page:
            pages.append(current_page)

        return pages if pages else [[]]

    @staticmethod
    def draw_page(
        page_chars: list[dict[str, Any]],
        grid_type: str = DEFAULT_GRID_TYPE,
        grid_color: QColor = DEFAULT_GRID_COLOR,
        text_color: QColor = DEFAULT_TEXT_COLOR,
        font_family: str = DEFAULT_FONT_FAMILY,
        grid_rows: int = ROWS,
        grid_cols: int = COLS,
    ) -> QImage:
        width, height = 1240, 1754
        margin_x, margin_y = 70, 90

        image = QImage(width, height, QImage.Format_ARGB32)
        image.fill(Qt.white)

        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)

        # 1. 使用入参 grid_cols 计算格子大小
        cell_size = (width - 2 * margin_x) / grid_cols

        pen_solid = QPen(grid_color, 2, Qt.SolidLine)
        pen_dashed = QPen(grid_color, 1, Qt.DashLine)

        font = QFont(font_family)
        font.setPixelSize(int(cell_size * 0.75))
        painter.setFont(font)

        # 2. 将传入的 [{row, col, char}, ...] 转换为 (row, col) 到 char 的快速查找映射
        char_map = {(item["row"], item["col"]): item["char"] for item in page_chars}

        # 3. 使用入参 grid_rows 和 grid_cols 进行网格遍历
        for r in range(grid_rows):
            for c in range(grid_cols):
                x = margin_x + c * cell_size
                y = margin_y + r * cell_size

                # 绘制外框
                painter.setPen(pen_solid)
                painter.drawRect(QRectF(x, y, cell_size, cell_size))

                # 绘制内部辅助虚线
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

                # 4. 根据当前 (r, c) 坐标判断是否有字符需要绘制
                char = char_map.get((r, c))
                if char:
                    painter.setPen(QPen(text_color))
                    rect = QRectF(x, y, cell_size, cell_size)
                    painter.drawText(rect, Qt.AlignCenter, char)

        painter.end()
        return image