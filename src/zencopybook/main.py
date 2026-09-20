import sys

from PySide6.QtWidgets import QApplication

from zencopybook.ui.main_window import CopybookGeneratorWindow


def main():
    app = QApplication(sys.argv)
    window = CopybookGeneratorWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()