import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from ..core.font_manager import FontManager
from ..core.generator import CopybookDrawer
from .widgets import PlainTextEdit


class CopybookGeneratorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("练字字帖生成器")
        self.resize(1280, 800)

        self.DEFAULT_LINE_COLOR = QColor("#D0D0D0")
        self.DEFAULT_TEXT_COLOR = QColor("#999999")

        self.grid_color = QColor(self.DEFAULT_LINE_COLOR)
        self.text_color = QColor(self.DEFAULT_TEXT_COLOR)

        # 动态获取当前包目录下的 fonts 路径
        package_dir = os.path.dirname(os.path.dirname(__file__))
        fonts_dir = os.path.join(package_dir, "fonts")
        
        self.font_manager = FontManager(fonts_dir)
        self.font_family = "SimSun"

        self.pages_data = []
        self.current_page_index = 0
        self.total_pages = 1
        self.current_qimage = None

        self.init_ui()

    def init_ui(self):
        main_splitter = QSplitter(Qt.Horizontal)

        # ================= 左侧控制面板 =================
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        control_layout.setContentsMargins(15, 15, 15, 15)
        control_layout.setSpacing(12)

        control_layout.addWidget(QLabel("<b>1. 选择字帖格型</b>"))
        self.grid_combo = QComboBox()
        self.grid_combo.addItems(["米字格", "田字格", "方格"])
        self.grid_combo.currentIndexChanged.connect(self.on_setting_changed)
        control_layout.addWidget(self.grid_combo)

        color_group = QGroupBox("2. 颜色设置")
        color_layout = QVBoxLayout()

        line_color_layout = QHBoxLayout()
        line_color_layout.addWidget(QLabel("线条颜色:"))
        self.line_color_btn = QPushButton()
        self.line_color_btn.setFixedHeight(24)
        self.line_color_btn.clicked.connect(self.choose_grid_color)
        self.update_color_preview(self.line_color_btn, self.grid_color)
        line_color_layout.addWidget(self.line_color_btn)

        line_reset_btn = QPushButton("重置")
        line_reset_btn.setFixedWidth(50)
        line_reset_btn.clicked.connect(self.reset_line_color)
        line_color_layout.addWidget(line_reset_btn)
        color_layout.addLayout(line_color_layout)

        text_color_layout = QHBoxLayout()
        text_color_layout.addWidget(QLabel("文字颜色:"))
        self.text_color_btn = QPushButton()
        self.text_color_btn.setFixedHeight(24)
        self.text_color_btn.clicked.connect(self.choose_text_color)
        self.update_color_preview(self.text_color_btn, self.text_color)
        text_color_layout.addWidget(self.text_color_btn)

        text_reset_btn = QPushButton("重置")
        text_reset_btn.setFixedWidth(50)
        text_reset_btn.clicked.connect(self.reset_text_color)
        text_color_layout.addWidget(text_reset_btn)

        color_layout.addLayout(text_color_layout)
        color_group.setLayout(color_layout)
        control_layout.addWidget(color_group)

        control_layout.addWidget(QLabel("<b>3. 字体设置</b>"))
        self.combo_font = QComboBox()
        self.combo_font.currentIndexChanged.connect(self.on_font_changed)
        control_layout.addWidget(self.combo_font)

        self.btn_load_font = QPushButton("导入新字体到 fonts 目录")
        self.btn_load_font.clicked.connect(self.import_custom_font)
        control_layout.addWidget(self.btn_load_font)

        self.reload_fonts_combo()

        control_layout.addWidget(QLabel("<b>4. 输入练字内容</b>"))
        self.text_input = PlainTextEdit()
        self.text_input.setPlaceholderText("在此输入文字...")
        self.text_input.setPlainText(
            "永和九年岁在癸丑暮春之初会于会稽山阴之兰亭修禊事也夫人之相与俯仰一世或取诸怀抱悟言一室之内或因寄所托放浪形骸之外"
        )
        control_layout.addWidget(self.text_input)

        self.btn_generate = QPushButton("生成预览")
        self.btn_generate.setStyleSheet(
            "background-color: #0078D4; color: white; font-weight: bold; padding: 8px;"
        )
        self.btn_generate.clicked.connect(self.generate_copybook)
        control_layout.addWidget(self.btn_generate)

        self.btn_export = QPushButton("导出 PNG 图片")
        self.btn_export.setStyleSheet(
            "background-color: #107C41; color: white; font-weight: bold; padding: 8px;"
        )
        self.btn_export.clicked.connect(self.export_png)
        control_layout.addWidget(self.btn_export)

        # ================= 右侧预览区 =================
        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(5)

        self.scroll_area = QScrollArea()
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.preview_label = QLabel("点击“生成预览”查看字帖")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.preview_label)
        self.scroll_area.setWidgetResizable(True)
        preview_layout.addWidget(self.scroll_area)

        page_control_panel = QWidget()
        page_control_panel.setFixedHeight(45)
        page_layout = QHBoxLayout(page_control_panel)
        page_layout.setContentsMargins(10, 5, 10, 5)

        self.btn_prev_page = QPushButton("上一页")
        self.btn_prev_page.setFixedWidth(80)
        self.btn_prev_page.clicked.connect(self.goto_prev_page)

        self.lbl_page_info = QLabel("页码: 1 / 1")
        self.lbl_page_info.setAlignment(Qt.AlignCenter)

        self.btn_next_page = QPushButton("下一页")
        self.btn_next_page.setFixedWidth(80)
        self.btn_next_page.clicked.connect(self.goto_next_page)

        page_layout.addStretch()
        page_layout.addWidget(self.btn_prev_page)
        page_layout.addWidget(self.lbl_page_info)
        page_layout.addWidget(self.btn_next_page)
        page_layout.addStretch()

        preview_layout.addWidget(page_control_panel)

        main_splitter.addWidget(control_panel)
        main_splitter.addWidget(preview_container)
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 3)

        self.setCentralWidget(main_splitter)
        self.generate_copybook()

    def update_color_preview(self, frame: QFrame, color: QColor):
        frame.setStyleSheet(
            f"background-color: {color.name()}; border: 1px solid #666; border-radius: 3px;"
        )

    def choose_grid_color(self):
        color = QColorDialog.getColor(self.grid_color, self, "选择线条颜色")
        if color.isValid():
            self.grid_color = color
            self.update_color_preview(self.line_color_btn, color)
            self.render_current_page()

    def choose_text_color(self):
        color = QColorDialog.getColor(self.text_color, self, "选择文字颜色")
        if color.isValid():
            self.text_color = color
            self.update_color_preview(self.text_color_btn, color)
            self.render_current_page()

    def reset_line_color(self):
        self.grid_color = QColor(self.DEFAULT_LINE_COLOR)
        self.update_color_preview(self.line_color_btn, self.grid_color)
        self.render_current_page()

    def reset_text_color(self):
        self.text_color = QColor(self.DEFAULT_TEXT_COLOR)
        self.update_color_preview(self.text_color_btn, self.text_color)
        self.render_current_page()

    def on_setting_changed(self):
        self.render_current_page()

    def reload_fonts_combo(self):
        self.combo_font.blockSignals(True)
        self.combo_font.clear()
        fonts_list = self.font_manager.scan_fonts()
        for display_name, font_name in fonts_list:
            self.combo_font.addItem(display_name, font_name)
        self.combo_font.blockSignals(False)
        self.combo_font.setCurrentIndex(0)

    def on_font_changed(self, index):
        if index >= 0:
            self.font_family = self.combo_font.itemData(index)
            self.render_current_page()

    def import_custom_font(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择字体文件", "", "Font Files (*.ttf *.otf)"
        )
        if not file_path:
            return

        file_name = os.path.basename(file_path)
        dest_path = os.path.join(self.font_manager.fonts_dir, file_name)

        if os.path.exists(dest_path):
            reply = QMessageBox.question(
                self,
                "提示",
                f"字体文件 '{file_name}' 已存在，是否覆盖？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.No:
                return

        success, result = self.font_manager.import_font(file_path)
        if success:
            self.reload_fonts_combo()
            for i in range(self.combo_font.count()):
                if file_name in self.combo_font.itemText(i):
                    self.combo_font.setCurrentIndex(i)
                    break
            QMessageBox.information(self, "成功", f"字体 '{file_name}' 已导入！")
            self.generate_copybook()
        else:
            QMessageBox.critical(self, "错误", f"复制字体文件失败:\n{result}")

    def generate_copybook(self):
        text_content = (
            self.text_input.toPlainText().replace("\n", "").replace(" ", "")
        )
        chunk_size = CopybookDrawer.CHARS_PER_PAGE

        if text_content:
            self.pages_data = [
                text_content[i : i + chunk_size]
                for i in range(0, len(text_content), chunk_size)
            ]
        else:
            self.pages_data = [""]

        self.total_pages = len(self.pages_data)
        self.current_page_index = 0
        self.render_current_page()

    def update_page_controls(self):
        self.lbl_page_info.setText(
            f"页码: {self.current_page_index + 1} / {self.total_pages}"
        )
        self.btn_prev_page.setEnabled(self.current_page_index > 0)
        self.btn_next_page.setEnabled(self.current_page_index < self.total_pages - 1)

    def goto_prev_page(self):
        if self.current_page_index > 0:
            self.current_page_index -= 1
            self.render_current_page()

    def goto_next_page(self):
        if self.current_page_index < self.total_pages - 1:
            self.current_page_index += 1
            self.render_current_page()

    def render_current_page(self):
        if not self.pages_data:
            return

        page_text = self.pages_data[self.current_page_index]
        image = CopybookDrawer.draw_page(
            page_text,
            self.grid_combo.currentText(),
            self.grid_color,
            self.text_color,
            self.font_family,
        )

        self.current_qimage = image
        pixmap = QPixmap.fromImage(image)
        scaled_pixmap = pixmap.scaledToHeight(720, Qt.SmoothTransformation)
        self.preview_label.setPixmap(scaled_pixmap)
        self.update_page_controls()

    def export_png(self):
        if not self.pages_data:
            QMessageBox.warning(self, "警告", "没有可导出的字帖内容！")
            return

        if self.total_pages == 1:
            self.export_single_page()
            return

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("导出字帖")
        msg_box.setText(f"检测到共有 {self.total_pages} 页字帖，请选择导出方式：")

        btn_current = msg_box.addButton("导出当前页", QMessageBox.AcceptRole)
        btn_all = msg_box.addButton("批量导出所有页", QMessageBox.AcceptRole)
        _ = msg_box.addButton("取消", QMessageBox.RejectRole)
        msg_box.exec()

        if msg_box.clickedButton() == btn_current:
            self.export_single_page()
        elif msg_box.clickedButton() == btn_all:
            self.export_all_pages()

    def export_single_page(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存当前页字帖",
            f"字帖_第{self.current_page_index + 1}页.png",
            "PNG Images (*.png)",
        )
        if file_path:
            if self.current_qimage.save(file_path, "PNG"):
                QMessageBox.information(
                    self, "成功", f"字帖已成功导出至:\n{file_path}"
                )
            else:
                QMessageBox.critical(self, "失败", "导出图片时发生错误！")

    def export_all_pages(self):
        dir_path = QFileDialog.getExistingDirectory(
            self, "选择保存所有页面的文件夹"
        )
        if not dir_path:
            return

        success_count = 0
        grid_type = self.grid_combo.currentText()

        for idx, page_text in enumerate(self.pages_data):
            img = CopybookDrawer.draw_page(
                page_text,
                grid_type,
                self.grid_color,
                self.text_color,
                self.font_family,
            )
            file_name = f"字帖_第{idx + 1}页.png"
            file_path = os.path.join(dir_path, file_name)
            if img.save(file_path, "PNG"):
                success_count += 1

        if success_count == self.total_pages:
            QMessageBox.information(
                self,
                "批量导出成功",
                f"已成功导出全部 {self.total_pages} 页字帖图片到目录:\n{dir_path}",
            )
        else:
            QMessageBox.warning(
                self,
                "导出提示",
                f"导出完成，成功 {success_count}/{self.total_pages} 页。",
            )