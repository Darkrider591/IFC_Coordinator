"""Batch coordination tab for multi-file processing with Drag-and-Drop."""

import os
from typing import List, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QFileDialog, QGroupBox, QRadioButton, QLineEdit,
    QCheckBox, QLabel, QHeaderView, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QColor

from core.inspector import inspect_ifc_file
from ui.theme import COLOR_GREEN_PRIMARY, COLOR_GREEN_HOVER, COLOR_YELLOW, COLOR_BERRY


class BatchDropArea(QFrame):
    """Clickable and draggable drop zone for multiple files."""
    files_dropped = Signal(list)
    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("drop_zone")
        self.setAcceptDrops(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        lbl_text = QLabel("Перетащите сюда файлы .ifc или целые папки для пакетной координации")
        lbl_text.setStyleSheet("font-size: 13px; font-weight: 600;")

        layout.addWidget(lbl_text)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        paths = []
        for u in event.mimeData().urls():
            loc = u.toLocalFile()
            if os.path.isfile(loc) and loc.lower().endswith((".ifc", ".ifczip")):
                paths.append(loc)
            elif os.path.isdir(loc):
                for root, _, files in os.walk(loc):
                    for f in files:
                        if f.lower().endswith((".ifc", ".ifczip")):
                            paths.append(os.path.join(root, f))
        if paths:
            self.files_dropped.emit(paths)
            event.acceptProposedAction()


class BatchTab(QWidget):
    """Tab for batch processing of multiple IFC files."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_items: List[Dict[str, Any]] = []
        self.setAcceptDrops(True)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # 1. Drag & Drop Banner
        self.drop_area = BatchDropArea()
        self.drop_area.files_dropped.connect(self.add_files)
        self.drop_area.clicked.connect(self._add_files_dialog)
        layout.addWidget(self.drop_area)

        # 2. Top action buttons
        tools_layout = QHBoxLayout()
        tools_layout.setSpacing(6)

        self.btn_add_files = QPushButton("Добавить файлы...")
        self.btn_add_files.setToolTip("Выбрать один или несколько файлов .ifc")
        self.btn_add_files.clicked.connect(self._add_files_dialog)

        self.btn_add_folder = QPushButton("Добавить папку...")
        self.btn_add_folder.setToolTip("Добавить все файлы .ifc из выбранной папки")
        self.btn_add_folder.clicked.connect(self._add_folder_dialog)

        self.check_recursive = QCheckBox("Включая подпапки")
        self.check_recursive.setChecked(False)

        self.btn_select_all = QPushButton("Все")
        self.btn_select_all.clicked.connect(self._select_all)

        self.btn_deselect_all = QPushButton("Снять")
        self.btn_deselect_all.clicked.connect(self._deselect_all)

        self.btn_remove = QPushButton("Удалить")
        self.btn_remove.clicked.connect(self._remove_selected)

        self.btn_clear = QPushButton("Очистить")
        self.btn_clear.clicked.connect(self.clear)

        tools_layout.addWidget(self.btn_add_files)
        tools_layout.addWidget(self.btn_add_folder)
        tools_layout.addWidget(self.check_recursive)
        tools_layout.addSpacing(10)
        tools_layout.addWidget(self.btn_select_all)
        tools_layout.addWidget(self.btn_deselect_all)
        tools_layout.addWidget(self.btn_remove)
        tools_layout.addWidget(self.btn_clear)
        tools_layout.addStretch()

        layout.addLayout(tools_layout)

        # 3. Files table
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "", "Имя файла", "Путь к папке", "Размер (МБ)", "Схема", "Единицы", "Статус / Результат"
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(1, 240)
        self.table.setColumnWidth(6, 180)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)

        layout.addWidget(self.table)

        # 4. Output Configuration Group
        out_box = QGroupBox("Настройки сохранения пакета файлов")
        out_layout = QVBoxLayout(out_box)
        out_layout.setContentsMargins(10, 10, 10, 10)
        out_layout.setSpacing(8)

        # Radio 1: Suffix
        r1_layout = QHBoxLayout()
        self.radio_suffix = QRadioButton("Сохранять рядом с исходным файлом, добавив суффикс:")
        self.radio_suffix.setChecked(True)
        self.edit_suffix = QLineEdit("_coordination")
        self.edit_suffix.setMaximumWidth(150)
        r1_layout.addWidget(self.radio_suffix)
        r1_layout.addWidget(self.edit_suffix)
        r1_layout.addWidget(QLabel(".ifc"))
        r1_layout.addStretch()
        out_layout.addLayout(r1_layout)

        # Radio 2: Custom Folder
        r2_layout = QHBoxLayout()
        self.radio_folder = QRadioButton("Сохранять все файлы в отдельную папку:")
        self.edit_output_folder = QLineEdit()
        self.edit_output_folder.setPlaceholderText("Выберите папку назначения...")
        self.btn_browse_out_folder = QPushButton("Обзор...")
        self.btn_browse_out_folder.clicked.connect(self._browse_output_folder)
        r2_layout.addWidget(self.radio_folder)
        r2_layout.addWidget(self.edit_output_folder, 1)
        r2_layout.addWidget(self.btn_browse_out_folder)
        out_layout.addLayout(r2_layout)

        # Radio 3: Overwrite
        r3_layout = QHBoxLayout()
        self.radio_overwrite = QRadioButton("Перезаписать исходные файлы")
        self.check_backup = QCheckBox("Создавать резервную копию (.bak) перед перезаписью")
        self.check_backup.setChecked(True)
        r3_layout.addWidget(self.radio_overwrite)
        r3_layout.addSpacing(20)
        r3_layout.addWidget(self.check_backup)
        r3_layout.addStretch()
        out_layout.addLayout(r3_layout)

        layout.addWidget(out_box)

    def _add_files_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Выберите файлы IFC для пакетной обработки", "", "IFC Files (*.ifc *.ifczip);;All Files (*.*)"
        )
        if files:
            self.add_files(files)

    def _add_folder_dialog(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку с файлами IFC")
        if not folder:
            return
        recursive = self.check_recursive.isChecked()
        found_files = []
        if recursive:
            for root, _, files in os.walk(folder):
                for f in files:
                    if f.lower().endswith((".ifc", ".ifczip")):
                        found_files.append(os.path.join(root, f))
        else:
            for f in os.listdir(folder):
                if f.lower().endswith((".ifc", ".ifczip")):
                    found_files.append(os.path.join(folder, f))

        if found_files:
            self.add_files(found_files)
        else:
            QMessageBox.information(self, "Поиск файлов", "В указанной папке не найдено файлов .ifc.")

    def _browse_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения файлов")
        if folder:
            self.edit_output_folder.setText(folder)
            self.radio_folder.setChecked(True)

    def add_files(self, paths: List[str]):
        existing_paths = {item["path"] for item in self.file_items}
        for p in paths:
            abs_p = os.path.abspath(p)
            if abs_p in existing_paths or not os.path.isfile(abs_p):
                continue

            info = inspect_ifc_file(abs_p)
            item = {
                "path": abs_p,
                "name": os.path.basename(abs_p),
                "dir": os.path.dirname(abs_p),
                "size_mb": info["size_mb"],
                "schema": info["schema"],
                "unit": info["unit_name"],
                "status": "Ожидание",
            }
            self.file_items.append(item)
            existing_paths.add(abs_p)

            # Insert row into table
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Col 0: Checkbox
            check_item = QTableWidgetItem()
            check_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            check_item.setCheckState(Qt.CheckState.Checked)
            self.table.setItem(row, 0, check_item)

            # Col 1: Name
            self.table.setItem(row, 1, QTableWidgetItem(item["name"]))
            # Col 2: Dir
            self.table.setItem(row, 2, QTableWidgetItem(item["dir"]))
            # Col 3: Size
            self.table.setItem(row, 3, QTableWidgetItem(f"{item['size_mb']:.2f}"))
            # Col 4: Schema
            self.table.setItem(row, 4, QTableWidgetItem(item["schema"]))
            # Col 5: Unit
            self.table.setItem(row, 5, QTableWidgetItem(item["unit"]))
            # Col 6: Status
            status_item = QTableWidgetItem("Ожидание")
            status_item.setForeground(QColor("#888888"))
            self.table.setItem(row, 6, status_item)

    def _select_all(self):
        for r in range(self.table.rowCount()):
            item = self.table.item(r, 0)
            if item: item.setCheckState(Qt.CheckState.Checked)

    def _deselect_all(self):
        for r in range(self.table.rowCount()):
            item = self.table.item(r, 0)
            if item: item.setCheckState(Qt.CheckState.Unchecked)

    def _remove_selected(self):
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())

        if not selected_rows:
            for r in range(self.table.rowCount()):
                it = self.table.item(r, 0)
                if it and it.checkState() == Qt.CheckState.Checked:
                    selected_rows.add(r)

        for r in sorted(list(selected_rows), reverse=True):
            self.table.removeRow(r)
            if r < len(self.file_items):
                del self.file_items[r]

    def clear(self):
        self.table.setRowCount(0)
        self.file_items.clear()

    def update_file_progress(self, index: int, pct: int, status_text: str):
        if 0 <= index < self.table.rowCount():
            item = self.table.item(index, 6)
            if item:
                item.setText(f"{status_text} ({pct}%)")
                item.setForeground(QColor(COLOR_GREEN_PRIMARY))

    def update_file_finished(self, index: int, success: bool, msg: str, elapsed: float):
        if 0 <= index < self.table.rowCount():
            item = self.table.item(index, 6)
            if item:
                if success:
                    item.setText(f"Готово ({elapsed:.1f}с)")
                    item.setForeground(QColor(COLOR_GREEN_PRIMARY))
                else:
                    item.setText(f"Ошибка: {msg}")
                    item.setForeground(QColor("#ef4444"))

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        paths = []
        for u in event.mimeData().urls():
            loc = u.toLocalFile()
            if os.path.isfile(loc) and loc.lower().endswith((".ifc", ".ifczip")):
                paths.append(loc)
            elif os.path.isdir(loc):
                for f in os.listdir(loc):
                    if f.lower().endswith((".ifc", ".ifczip")):
                        paths.append(os.path.join(loc, f))
        if paths:
            self.add_files(paths)
            event.acceptProposedAction()

    def get_tasks(self) -> List[Dict[str, Any]]:
        tasks = []
        suffix = self.edit_suffix.text().strip() or "_coordination"
        out_folder = self.edit_output_folder.text().strip()

        if self.radio_folder.isChecked():
            if not out_folder:
                raise ValueError("Укажите папку назначения для сохранения результатов.")
            if not os.path.exists(out_folder):
                os.makedirs(out_folder, exist_ok=True)

        for r in range(self.table.rowCount()):
            check_item = self.table.item(r, 0)
            if not check_item or check_item.checkState() != Qt.CheckState.Checked:
                continue

            if r >= len(self.file_items):
                continue

            in_path = self.file_items[r]["path"]
            fname = os.path.basename(in_path)
            base_name, ext = os.path.splitext(fname)

            if self.radio_suffix.isChecked():
                out_path = os.path.join(os.path.dirname(in_path), f"{base_name}{suffix}{ext}")
            elif self.radio_folder.isChecked():
                out_path = os.path.join(out_folder, fname)
            elif self.radio_overwrite.isChecked():
                out_path = in_path
            else:
                out_path = os.path.join(os.path.dirname(in_path), f"{base_name}{suffix}{ext}")

            tasks.append({
                "index": r,
                "input_path": in_path,
                "output_path": out_path,
                "create_backup": self.check_backup.isChecked() if self.radio_overwrite.isChecked() else False,
            })

        if not tasks:
            raise ValueError("Не выбрано ни одного файла для обработки (отметьте галочками нужные файлы).")

        return tasks
