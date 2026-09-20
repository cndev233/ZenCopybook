import os
import shutil

from PySide6.QtGui import QFontDatabase


class FontManager:
    def __init__(self, fonts_dir: str):
        self.fonts_dir = fonts_dir
        self.init_font_dir()

    def init_font_dir(self):
        if not os.path.exists(self.fonts_dir):
            os.makedirs(self.fonts_dir)

    def scan_fonts(self) -> list[tuple[str, str]]:
        fonts_list = [
            ("楷体 (系统)", "KaiTi"),
            ("宋体 (系统)", "SimSun"),
            ("微软雅黑 (系统)", "Microsoft YaHei"),
        ]

        if os.path.exists(self.fonts_dir):
            for file_name in os.listdir(self.fonts_dir):
                if file_name.lower().endswith((".ttf", ".otf")):
                    file_path = os.path.join(self.fonts_dir, file_name)
                    font_id = QFontDatabase.addApplicationFont(file_path)
                    if font_id != -1:
                        families = QFontDatabase.applicationFontFamilies(font_id)
                        if families:
                            real_font_name = families[0]
                            display_name = f"{real_font_name} ({file_name})"
                            fonts_list.append((display_name, real_font_name))

        return fonts_list

    def import_font(self, src_file_path: str) -> tuple[bool, str]:
        file_name = os.path.basename(src_file_path)
        dest_path = os.path.join(self.fonts_dir, file_name)

        try:
            shutil.copy(src_file_path, dest_path)
            return True, file_name
        except OSError as e:
            return False, str(e)
