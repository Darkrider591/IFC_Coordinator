"""Transformation parameters input widget."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QCheckBox, QPushButton, QGroupBox, QComboBox,
    QInputDialog, QMessageBox
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QDoubleValidator

from core.presets import (
    load_presets, save_presets, add_or_update_preset, delete_preset
)


class ParamsWidget(QWidget):
    """Widget for managing X, Y, Z translation and Ax, Ay, Az rotation parameters."""
    params_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.presets = []
        self._init_ui()
        self._load_and_populate_presets()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)

        # 1. Presets Header
        preset_box = QGroupBox("Пресеты координат и угла")
        preset_layout = QHBoxLayout(preset_box)
        preset_layout.setContentsMargins(8, 8, 8, 8)
        preset_layout.setSpacing(6)

        self.preset_combo = QComboBox()
        self.preset_combo.currentIndexChanged.connect(self._on_preset_selected)

        self.btn_save_preset = QPushButton("💾 Сохранить")
        self.btn_save_preset.setToolTip("Сохранить текущие параметры как именованный пресет")
        self.btn_save_preset.clicked.connect(self._save_current_preset)

        self.btn_del_preset = QPushButton("🗑")
        self.btn_del_preset.setToolTip("Удалить выбранный пресет")
        self.btn_del_preset.clicked.connect(self._delete_selected_preset)

        preset_layout.addWidget(QLabel("Пресет:"))
        preset_layout.addWidget(self.preset_combo, 1)
        preset_layout.addWidget(self.btn_save_preset)
        preset_layout.addWidget(self.btn_del_preset)

        main_layout.addWidget(preset_box)

        # 2. Coordinate Offsets
        trans_box = QGroupBox("Смещение (Offset)")
        trans_layout = QGridLayout(trans_box)
        trans_layout.setContentsMargins(10, 10, 10, 10)
        trans_layout.setHorizontalSpacing(10)
        trans_layout.setVerticalSpacing(8)

        # Validator allowing scientific notation and arbitrary decimals
        val = QDoubleValidator(self)
        val.setNotation(QDoubleValidator.Notation.StandardNotation)

        self.edit_x = QLineEdit("4151394")
        self.edit_x.setValidator(val)
        self.edit_x.textChanged.connect(self.params_changed)

        self.edit_y = QLineEdit("-4065338")
        self.edit_y.setValidator(val)
        self.edit_y.textChanged.connect(self.params_changed)

        self.edit_z = QLineEdit("184000")
        self.edit_z.setValidator(val)
        self.edit_z.textChanged.connect(self.params_changed)

        trans_layout.addWidget(QLabel("X:"), 0, 0)
        trans_layout.addWidget(self.edit_x, 0, 1)

        trans_layout.addWidget(QLabel("Y:"), 1, 0)
        trans_layout.addWidget(self.edit_y, 1, 1)

        trans_layout.addWidget(QLabel("Z:"), 2, 0)
        trans_layout.addWidget(self.edit_z, 2, 1)

        main_layout.addWidget(trans_box)

        # 3. Order Checkbox (Should Rotate First)
        order_box = QGroupBox("Порядок трансформации")
        order_layout = QVBoxLayout(order_box)
        order_layout.setContentsMargins(10, 8, 10, 8)

        self.check_rotate_first = QCheckBox("Should Rotate First (Сначала повернуть, затем сместить)")
        self.check_rotate_first.setChecked(True)
        self.check_rotate_first.setToolTip(
            "Если включено (как в BlenderBIM), модель сначала поворачивается вокруг исходного начала координат,\n"
            "а затем смещается на вектор (X, Y, Z).\n"
            "Если выключено, модель сначала смещается, а затем поворачивается."
        )
        self.check_rotate_first.toggled.connect(self.params_changed)
        order_layout.addWidget(self.check_rotate_first)

        main_layout.addWidget(order_box)

        # 4. Rotation Angles
        rot_box = QGroupBox("Поворот (Rotation Angles в градусах)")
        rot_layout = QGridLayout(rot_box)
        rot_layout.setContentsMargins(10, 10, 10, 10)
        rot_layout.setHorizontalSpacing(10)
        rot_layout.setVerticalSpacing(8)

        self.edit_ax = QLineEdit("0")
        self.edit_ax.setValidator(val)
        self.edit_ax.textChanged.connect(self.params_changed)

        self.edit_ay = QLineEdit("0")
        self.edit_ay.setValidator(val)
        self.edit_ay.textChanged.connect(self.params_changed)

        self.edit_az = QLineEdit("-48.55611111")
        self.edit_az.setValidator(val)
        self.edit_az.textChanged.connect(self.params_changed)

        rot_layout.addWidget(QLabel("Ax (вокруг X):"), 0, 0)
        rot_layout.addWidget(self.edit_ax, 0, 1)

        rot_layout.addWidget(QLabel("Ay (вокруг Y):"), 1, 0)
        rot_layout.addWidget(self.edit_ay, 1, 1)

        rot_layout.addWidget(QLabel("Az (вокруг Z - план):"), 2, 0)
        rot_layout.addWidget(self.edit_az, 2, 1)

        main_layout.addWidget(rot_box)

        # Reset button
        btn_reset = QPushButton("Сбросить в 0 (Без смещения/поворота)")
        btn_reset.clicked.connect(self.reset_to_zero)
        main_layout.addWidget(btn_reset)

        main_layout.addStretch()

    def _load_and_populate_presets(self):
        self.presets = load_presets()
        self.preset_combo.blockSignals(True)
        self.preset_combo.clear()
        for p in self.presets:
            self.preset_combo.addItem(p["name"])
        self.preset_combo.blockSignals(False)

        if self.presets:
            self._apply_preset_data(self.presets[0])

    def _on_preset_selected(self, index: int):
        if 0 <= index < len(self.presets):
            self._apply_preset_data(self.presets[index])

    def _apply_preset_data(self, p: dict):
        self.edit_x.setText(str(p.get("x", 0.0)))
        self.edit_y.setText(str(p.get("y", 0.0)))
        self.edit_z.setText(str(p.get("z", 0.0)))
        self.check_rotate_first.setChecked(bool(p.get("should_rotate_first", True)))
        self.edit_ax.setText(str(p.get("ax", 0.0)))
        self.edit_ay.setText(str(p.get("ay", 0.0)))
        self.edit_az.setText(str(p.get("az", 0.0)))
        self.params_changed.emit()

    def _save_current_preset(self):
        current_name = self.preset_combo.currentText() or "Новый пресет"
        name, ok = QInputDialog.getText(
            self, "Сохранение пресета", "Введите имя пресета:", text=current_name
        )
        if ok and name.strip():
            name = name.strip()
            params = self.get_parameters()
            preset_data = {
                "name": name,
                "x": params["x"],
                "y": params["y"],
                "z": params["z"],
                "should_rotate_first": params["should_rotate_first"],
                "ax": params["ax"],
                "ay": params["ay"],
                "az": params["az"],
            }
            self.presets = add_or_update_preset(preset_data)
            self._load_and_populate_presets()
            idx = self.preset_combo.findText(name)
            if idx >= 0:
                self.preset_combo.setCurrentIndex(idx)
            QMessageBox.information(self, "Успешно", f"Пресет '{name}' сохранен.")

    def _delete_selected_preset(self):
        current_name = self.preset_combo.currentText()
        if not current_name:
            return
        reply = QMessageBox.question(
            self, "Удаление", f"Удалить пресет '{current_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.presets = delete_preset(current_name)
            self._load_and_populate_presets()

    def reset_to_zero(self):
        self.edit_x.setText("0")
        self.edit_y.setText("0")
        self.edit_z.setText("0")
        self.edit_ax.setText("0")
        self.edit_ay.setText("0")
        self.edit_az.setText("0")
        self.check_rotate_first.setChecked(True)

    def get_parameters(self) -> dict:
        def parse_val(text: str, default: float = 0.0) -> float:
            try:
                # Support both comma and dot for Russian locale users
                cleaned = text.strip().replace(",", ".")
                return float(cleaned) if cleaned else default
            except ValueError:
                return default

        return {
            "x": parse_val(self.edit_x.text(), 0.0),
            "y": parse_val(self.edit_y.text(), 0.0),
            "z": parse_val(self.edit_z.text(), 0.0),
            "should_rotate_first": self.check_rotate_first.isChecked(),
            "ax": parse_val(self.edit_ax.text(), 0.0),
            "ay": parse_val(self.edit_ay.text(), 0.0),
            "az": parse_val(self.edit_az.text(), 0.0),
        }

    def set_parameters(self, params: dict):
        if "x" in params: self.edit_x.setText(str(params["x"]))
        if "y" in params: self.edit_y.setText(str(params["y"]))
        if "z" in params: self.edit_z.setText(str(params["z"]))
        if "should_rotate_first" in params:
            self.check_rotate_first.setChecked(bool(params["should_rotate_first"]))
        if "ax" in params: self.edit_ax.setText(str(params["ax"]))
        if "ay" in params: self.edit_ay.setText(str(params["ay"]))
        if "az" in params: self.edit_az.setText(str(params["az"]))
