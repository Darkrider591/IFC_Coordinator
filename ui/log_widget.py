"""Logging and console output widget styled with corporate palette."""

import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QApplication
)
from PySide6.QtGui import QTextCursor

from ui.theme import COLOR_GREEN_PRIMARY, COLOR_YELLOW, COLOR_BERRY, COLOR_GREY


class LogWidget(QWidget):
    """Console widget for displaying execution logs with timestamps and color formatting."""

    COLOR_MAP = {
        "info": "#a3e6cd",
        "success": COLOR_GREEN_PRIMARY,
        "warning": COLOR_YELLOW,
        "error": "#f87171",
    }

    TAG_MAP = {
        "info": "[ИНФО]",
        "success": "[УСПЕХ]",
        "warning": "[ВНИМАНИЕ]",
        "error": "[ОШИБКА]",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Header bar
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Журнал операций:"))
        header_layout.addStretch()

        self.btn_copy = QPushButton("📋 Копировать")
        self.btn_copy.setToolTip("Скопировать текст журнала в буфер обмена")
        self.btn_copy.clicked.connect(self._copy_log)

        self.btn_clear = QPushButton("🧹 Очистить")
        self.btn_clear.setToolTip("Очистить журнал")
        self.btn_clear.clicked.connect(self.clear)

        header_layout.addWidget(self.btn_copy)
        header_layout.addWidget(self.btn_clear)
        layout.addLayout(header_layout)

        # Text edit
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setAcceptRichText(True)
        layout.addWidget(self.text_edit)

    def log(self, message: str, level: str = "info"):
        level = level.lower()
        color = self.COLOR_MAP.get(level, "#d4d4d4")
        tag = self.TAG_MAP.get(level, f"[{level.upper()}]")
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        html_line = (
            f"<span style='color: #88929b;'>[{timestamp}]</span> "
            f"<span style='color: {color}; font-weight: bold;'>{tag}</span> "
            f"<span style='color: {color};'>{message}</span><br>"
        )

        self.text_edit.moveCursor(QTextCursor.MoveOperation.End)
        self.text_edit.insertHtml(html_line)
        self.text_edit.moveCursor(QTextCursor.MoveOperation.End)

    def _copy_log(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_edit.toPlainText())

    def clear(self):
        self.text_edit.clear()
