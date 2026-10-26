"""Main Window for the IFC Coordinator application with Dark/Light theme toggle."""

import os
import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTabWidget, QPushButton, QProgressBar, QLabel, QMessageBox,
    QStatusBar, QApplication
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon

from ui.single_tab import SingleTab
from ui.batch_tab import BatchTab
from ui.params_widget import ParamsWidget
from ui.log_widget import LogWidget
from ui.worker import CoordinationWorker
from ui.theme import DARK_THEME_QSS, LIGHT_THEME_QSS, COLOR_GREEN_PRIMARY


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.worker: CoordinationWorker = None
        self.is_dark_theme = True
        self._init_window()
        self._init_ui()

    def _init_window(self):
        self.setWindowTitle("IFC Coordinator v1.1 — Координация моделей IFC")
        self.resize(1120, 760)
        self.setMinimumSize(880, 600)

        # Set Icon
        icon_path = os.path.join(os.path.dirname(__file__), "..", "resources", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def _init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(12, 10, 12, 10)
        root_layout.setSpacing(10)

        # 1. Header Banner
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        # Title & Corporate Badge
        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(2)

        title_row = QHBoxLayout()
        title_row.setSpacing(8)

        lbl_title = QLabel("IFC COORDINATOR")
        lbl_title.setObjectName("title_label")
        title_row.addWidget(lbl_title)

        lbl_badge = QLabel("ЦТИП")
        lbl_badge.setObjectName("brand_badge")
        title_row.addWidget(lbl_badge)
        title_row.addStretch()

        lbl_sub = QLabel("Пакетное и одиночное смещение и поворот моделей IFC • 100% сохранность геометрии и атрибутов")
        lbl_sub.setStyleSheet("font-size: 11px; opacity: 0.8;")

        title_vbox.addLayout(title_row)
        title_vbox.addWidget(lbl_sub)
        header_layout.addLayout(title_vbox, 1)

        # Theme Switcher Button
        self.btn_theme_toggle = QPushButton("☀️ Светлая тема")
        self.btn_theme_toggle.setObjectName("theme_toggle")
        self.btn_theme_toggle.setToolTip("Переключить тему оформления (светлая / тёмная)")
        self.btn_theme_toggle.clicked.connect(self._toggle_theme)
        header_layout.addWidget(self.btn_theme_toggle)

        root_layout.addLayout(header_layout)

        # 2. Main content splitter (Left: Tabs, Right: Parameters)
        top_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Tabs for Batch and Single
        self.tabs = QTabWidget()
        self.single_tab = SingleTab()
        self.batch_tab = BatchTab()

        self.tabs.addTab(self.single_tab, "📄 Одиночный файл (Single)")
        self.tabs.addTab(self.batch_tab, "📁 Пакетная координация (Batch)")

        top_splitter.addWidget(self.tabs)

        # Right: Parameters Widget
        params_container = QWidget()
        params_layout = QVBoxLayout(params_container)
        params_layout.setContentsMargins(4, 0, 0, 0)

        self.params_widget = ParamsWidget()
        params_layout.addWidget(self.params_widget)

        top_splitter.addWidget(params_container)

        # Proportions
        top_splitter.setStretchFactor(0, 65)
        top_splitter.setStretchFactor(1, 35)

        # 3. Main vertical splitter (Top: Panels, Bottom: Console Log)
        main_v_splitter = QSplitter(Qt.Orientation.Vertical)
        main_v_splitter.addWidget(top_splitter)

        # Bottom: Log console
        self.log_widget = LogWidget()
        main_v_splitter.addWidget(self.log_widget)

        main_v_splitter.setStretchFactor(0, 72)
        main_v_splitter.setStretchFactor(1, 28)

        root_layout.addWidget(main_v_splitter, 1)

        # 4. Action bar & Progress bar
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v / %m (%p%)")

        self.btn_execute = QPushButton("🚀 Выполнить координацию")
        self.btn_execute.setObjectName("execute_button")
        self.btn_execute.setMinimumHeight(40)
        self.btn_execute.clicked.connect(self._start_coordination)

        self.btn_cancel = QPushButton("⏹ Отмена")
        self.btn_cancel.setObjectName("cancel_button")
        self.btn_cancel.setMinimumHeight(40)
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self._cancel_coordination)

        action_layout.addWidget(self.progress_bar, 1)
        action_layout.addWidget(self.btn_execute)
        action_layout.addWidget(self.btn_cancel)

        root_layout.addLayout(action_layout)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готово к работе.")

    def _toggle_theme(self):
        app = QApplication.instance()
        if not app:
            return

        if self.is_dark_theme:
            # Switch to Light
            app.setStyleSheet(LIGHT_THEME_QSS)
            self.btn_theme_toggle.setText("🌙 Тёмная тема")
            self.is_dark_theme = False
            self.status_bar.showMessage("Применена светлая тема оформления.")
        else:
            # Switch to Dark
            app.setStyleSheet(DARK_THEME_QSS)
            self.btn_theme_toggle.setText("☀️ Светлая тема")
            self.is_dark_theme = True
            self.status_bar.showMessage("Применена тёмная тема оформления (ЦТИП).")

    def _start_coordination(self):
        try:
            params = self.params_widget.get_parameters()

            # Check which tab is currently selected
            current_tab = self.tabs.currentWidget()
            if current_tab == self.single_tab:
                # Single file mode
                task = self.single_tab.get_task()
                tasks = [task]
                create_backup = task.get("create_backup", True)
            else:
                # Batch mode
                tasks = self.batch_tab.get_tasks()
                create_backup = self.batch_tab.check_backup.isChecked()

        except Exception as e:
            QMessageBox.warning(self, "Внимание", str(e))
            return

        self._set_ui_busy(True)
        self.progress_bar.setMaximum(len(tasks))
        self.progress_bar.setValue(0)
        self.log_widget.log(f"--- НАЧАЛО КООРДИНАЦИИ ({len(tasks)} ФАЙЛОВ) ---", "info")

        self.worker = CoordinationWorker(
            tasks=tasks,
            params=params,
            create_backup=create_backup,
            parent=self
        )

        self.worker.sig_log.connect(self.log_widget.log)
        self.worker.sig_overall_progress.connect(self._on_overall_progress)
        self.worker.sig_file_progress.connect(self._on_file_progress)
        self.worker.sig_file_finished.connect(self._on_file_finished)
        self.worker.sig_all_finished.connect(self._on_all_finished)

        self.worker.start()

    def _cancel_coordination(self):
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self, "Подтверждение отмены", "Прервать процесс координации?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.status_bar.showMessage("Остановка процесса...")
                self.worker.cancel()

    def _on_overall_progress(self, current: int, total: int, text: str):
        self.progress_bar.setValue(current)
        self.status_bar.showMessage(f"Обработка: {text}")

    def _on_file_progress(self, file_index: int, pct: int, status_text: str):
        if self.tabs.currentWidget() == self.batch_tab:
            self.batch_tab.update_file_progress(file_index, pct, status_text)

    def _on_file_finished(
        self, file_index: int, in_path: str, out_path: str, success: bool, msg: str, elapsed: float
    ):
        if self.tabs.currentWidget() == self.batch_tab:
            self.batch_tab.update_file_finished(file_index, success, msg, elapsed)

    def _on_all_finished(self, total: int, success_count: int, error_count: int):
        self._set_ui_busy(False)
        self.progress_bar.setValue(total)
        self.status_bar.showMessage(
            f"Завершено: успешно {success_count} из {total}" +
            (f" (ошибок: {error_count})" if error_count else "")
        )
        self.log_widget.log(
            f"--- ЗАВЕРШЕНО: Успешно: {success_count}, Ошибок: {error_count} ---",
            "success" if error_count == 0 else "warning"
        )

        if error_count == 0:
            QMessageBox.information(
                self, "Координация завершена",
                f"Все файлы ({success_count} шт.) успешно скоординированы!"
            )
        else:
            QMessageBox.warning(
                self, "Координация завершена с ошибками",
                f"Успешно обработано: {success_count}\nОшибок: {error_count}\nПодробности смотрите в журнале."
            )

    def _set_ui_busy(self, busy: bool):
        self.btn_execute.setEnabled(not busy)
        self.btn_cancel.setEnabled(busy)
        self.tabs.setEnabled(not busy)
        self.params_widget.setEnabled(not busy)

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self, "Выход из программы",
                "Выполняется координация файлов. Прервать и выйти?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.worker.cancel()
                self.worker.wait(3000)
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
