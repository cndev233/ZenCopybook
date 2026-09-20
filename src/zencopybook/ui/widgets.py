from PySide6.QtWidgets import QTextEdit


class PlainTextEdit(QTextEdit):
    """自定义文本框：强制过滤粘贴内容的富文本样式（颜色、背景色等）"""

    def insertFromMimeData(self, source):
        if source.hasText():
            self.insertPlainText(source.text())
        else:
            super().insertFromMimeData(source)