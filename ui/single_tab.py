"""Single file coordination tab with Drag-and-Drop zone and flexible saving mask."""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QGroupBox, QRadioButton,
    QCheckBox, QFrame
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QMouseEvent

from core.inspector import inspect_ifc_file
from ui.theme import COLOR_GREEN_PRIMARY, COLOR_YELLOW, COLOR_BERRY


class DropArea(QFrame):
    """Clickable and draggable drop zone widget."""
    file_dropped = Signal(str)
    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("drop_zone")
        self.setAcceptDrops(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(6)

        self.lbl_icon = QLabel("📥")
        self.lbl_icon.setStyleSheet("font-size: 26px;")
        self.lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_text = QLabel("Перетащите сюда файл .ifc или нажмите для выбора")
        self.lbl_text.setStyleSheet("font-size: 14px; font-weight: 600;")
        self.lbl_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_subtext = QLabel("Поддерживаются форматы .ifc и .ifczip")
        self.lbl_subtext.setStyleSheet("font-size: 11px; opacity: 0.7;")
        self.lbl_subtext.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.lbl_icon)
        layout.addWidget(self.lbl_text)
        layout.addWidget(self.lbl_subtext)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            for u in event.mimeData().urls():
                if u.toLocalFile().lower().endswith((".ifc", ".ifczip")):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        for u in event.mimeData().urls():
            loc = u.toLocalFile()
            if loc.lower().endswith((".ifc", ".ifczip")):
                self.file_dropped.emit(loc)
                event.acceptProposedAction()
                break


class SingleTab(QWidget):
    """Tab for single IFC model coordination."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # 1. Visual Drag-and-Drop Zone
        self.drop_area = DropArea()
        self.drop_area.file_dropped.connect(self.set_input_path)
        self.drop_area.clicked.connect(self._browse_input)
        layout.addWidget(self.drop_area)

        # 2. Selected Input File
        input_box = QGroupBox("Исходная модель IFC")
        input_layout = QHBoxLayout(input_box)
        input_layout.setContentsMargins(10, 10, 10, 10)
        input_layout.setSpacing(8)

        self.edit_input = QLineEdit()
        self.edit_input.setPlaceholderText("Путь к исходному файлу .ifc...")
        self.edit_input.textChanged.connect(self._on_input_changed)

        self.btn_browse_input = QPushButton("📁 Обзор...")
        self.btn_browse_input.clicked.connect(self._browse_input)

        input_layout.addWidget(self.edit_input, 1)
        input_layout.addWidget(self.btn_browse_input)
        layout.addWidget(input_box)

        # 3. Save Configuration (Mask / Suffix / Custom)
        save_box = QGroupBox("Настройки сохранения выходного файла")
        save_layout = QVBoxLayout(save_box)
        save_layout.setContentsMargins(10, 10, 10, 10)
        save_layout.setSpacing(8)

        # Mode 1: Suffix in same folder (Default)
        r1_layout = QHBoxLayout()
        self.radio_suffix = QRadioButton("Добавить суффикс к имени файла (в исходной папке):")
        self.radio_suffix.setChecked(True)
        self.radio_suffix.toggled.connect(self._update_output_path)

        self.edit_suffix = QLineEdit("_coordination")
        self.edit_suffix.setMaximumWidth(150)
        self.edit_suffix.textChanged.connect(self._update_output_path)

        r1_layout.addWidget(self.radio_suffix)
        r1_layout.addWidget(self.edit_suffix)
        r1_layout.addWidget(QLabel(".ifc"))
        r1_layout.addStretch()
        save_layout.addLayout(r1_layout)

        # Mode 2: Custom file path
        r2_layout = QHBoxLayout()
        self.radio_custom = QRadioButton("Произвольный путь сохранения:")
        self.radio_custom.toggled.connect(self._update_output_path)

        self.edit_output = QLineEdit()
        self.edit_output.setPlaceholderText("Итоговый путь сохранения файла...")

        self.btn_browse_output = QPushButton("💾 Выбрать...")
        self.btn_browse_output.clicked.connect(self._browse_output)

        r2_layout.addWidget(self.radio_custom)
        r2_layout.addWidget(self.edit_output, 1)
        r2_layout.addWidget(self.btn_browse_output)
        save_layout.addLayout(r2_layout)

        # Mode 3: Overwrite
        r3_layout = QHBoxLayout()
        self.radio_overwrite = QRadioButton("Перезаписать исходный файл")
        self.radio_overwrite.toggled.connect(self._update_output_path)

        self.check_backup = QCheckBox("Создавать резервную копию (.bak)")
        self.check_backup.setChecked(True)

        r3_layout.addWidget(self.radio_overwrite)
        r3_layout.addSpacing(20)
        r3_layout.addWidget(self.check_backup)
        r3_layout.addStretch()
        save_layout.addLayout(r3_layout)

        # Active output preview label
        self.lbl_effective_output = QLabel("Итоговый файл: (файл не выбран)")
        self.lbl_effective_output.setStyleSheet(f"font-weight: 600; color: {COLOR_GREEN_PRIMARY};")
        save_layout.addWidget(self.lbl_effective_output)

        layout.addWidget(save_box)

        # 4. Model Information Card
        self.info_box = QGroupBox("Параметры модели")
        info_layout = QGridLayout(self.info_box)
        info_layout.setHorizontalSpacing(15)
        info_layout.setVerticalSpacing(6)

        self.lbl_schema = QLabel("Схема IFC: —")
        self.lbl_units = QLabel("Единицы измерения: —")
        self.lbl_size = QLabel("Размер файла: —")
        self.lbl_products = QLabel("Элементов / Размещений: —")
        self.lbl_origin = QLabel("Текущее начало: —")

        info_layout.addWidget(self.lbl_schema, 0, 0)
        info_layout.addWidget(self.lbl_units, 0, 1)
        info_layout.addWidget(self.lbl_size, 1, 0)
        info_layout.addWidget(self.lbl_products, 1, 1)
        info_layout.addWidget(self.lbl_origin, 2, 0, 1, 2)

        layout.addWidget(self.info_box)
        layout.addStretch()

    def _browse_input(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выберите исходный файл IFC", "", "IFC Files (*.ifc *.ifczip);;All Files (*.*)"
        )
        if path:
            self.set_input_path(path)

    def _browse_output(self):
        suggested = self.edit_output.text() or self._calculate_effective_path()
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить файл IFC как", suggested, "IFC Files (*.ifc);;All Files (*.*)"
        )
        if path:
            self.edit_output.setText(path)
            self.radio_custom.setChecked(True)
            self._update_output_path()

    def set_input_path(self, path: str):
        self.edit_input.setText(path)
        self._inspect_file(path)
        self._update_output_path()

    def _on_input_changed(self, text: str):
        path = text.strip()
        if os.path.isfile(path):
            self._inspect_file(path)
        self._update_output_path()

    def _calculate_effective_path(self) -> str:
        in_p = self.edit_input.text().strip()
        if not in_p:
            return ""

        directory = os.path.dirname(in_p)
        fname = os.path.basename(in_p)
        base, ext = os.path.splitext(fname)

        if self.radio_suffix.isChecked():
            suffix = self.edit_suffix.text().strip() or "_coordination"
            return os.path.join(directory, f"{base}{suffix}{ext}")
        elif self.radio_custom.isChecked():
            custom = self.edit_output.text().strip()
            if custom:
                return custom
            suffix = self.edit_suffix.text().strip() or "_coordination"
            return os.path.join(directory, f"{base}{suffix}{ext}")
        elif self.radio_overwrite.isChecked():
            return in_p

        return os.path.join(directory, f"{base}_coordination{ext}")

    def _update_output_path(self):
        eff_path = self._calculate_effective_path()
        if eff_path:
            self.lbl_effective_output.setText(f"Итоговый файл: {eff_path}")
            if not self.radio_custom.isChecked() or not self.edit_output.text():
                self.edit_output.setText(eff_path)
        else:
            self.lbl_effective_output.setText("Итоговый файл: (выберите исходный файл)")

    def _inspect_file(self, path: str):
        if not os.path.isfile(path):
            return
        info = inspect_ifc_file(path)
        if info.get("valid"):
            self.lbl_schema.setText(f"Схема IFC: <b style='color: {COLOR_GREEN_PRIMARY};'>{info['schema']}</b>")
            unit_str = f"{info['unit_name']} (масштаб: {info['unit_scale']})"
            self.lbl_units.setText(f"Единицы измерения: <b style='color: {COLOR_YELLOW};'>{unit_str}</b>")
            self.lbl_size.setText(f"Размер: <b>{info['size_mb']:.2f} МБ</b>")
            self.lbl_products.setText(
                f"Элементов: <b>{info['products_count']}</b> (размещений: {info['root_placements_count']})"
            )
            orig = info["current_origin"]
            self.lbl_origin.setText(
                f"Текущее начало: <b>X={orig[0]:.2f}, Y={orig[1]:.2f}, Z={orig[2]:.2f}</b>"
            )
        else:
            self.lbl_schema.setText("Схема IFC: Ошибка чтения")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            for u in event.mimeData().urls():
                if u.toLocalFile().lower().endswith((".ifc", ".ifczip")):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        for u in event.mimeData().urls():
            fpath = u.toLocalFile()
            if fpath.lower().endswith((".ifc", ".ifczip")):
                self.set_input_path(fpath)
                event.acceptProposedAction()
                break

    def get_task(self) -> dict:
        in_p = self.edit_input.text().strip()
        if not in_p:
            raise ValueError("Не выбран исходный файл IFC.")
        if not os.path.isfile(in_p):
            raise FileNotFoundError(f"Исходный файл не существует: {in_p}")

        out_p = self._calculate_effective_path()
        if not out_p:
            raise ValueError("Не указан путь сохранения для выходного файла IFC.")

        return {
            "index": 0,
            "input_path": in_p,
            "output_path": out_p,
            "create_backup": self.check_backup.isChecked() if self.radio_overwrite.isChecked() else False,
        }
