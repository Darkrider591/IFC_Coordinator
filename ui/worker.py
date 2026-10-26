"""Background worker thread for executing IFC coordination tasks without freezing the GUI."""

import os
import time
from typing import List, Dict, Any, Optional
from PySide6.QtCore import QThread, Signal

from core.coordinator import coordinate_ifc, CoordinationError


class CoordinationWorker(QThread):
    """QThread worker executing single or batch IFC coordination."""

    sig_log = Signal(str, str)  # message, level
    sig_overall_progress = Signal(int, int, str)  # current, total, text
    sig_file_progress = Signal(int, int, str)  # file_index, percentage, status_text
    sig_file_finished = Signal(int, str, str, bool, str, float)  # idx, in_path, out_path, success, msg, elapsed
    sig_all_finished = Signal(int, int, int)  # total, success_count, error_count

    def __init__(
        self,
        tasks: List[Dict[str, Any]],
        params: Dict[str, Any],
        create_backup: bool = True,
        parent=None
    ):
        super().__init__(parent)
        self.tasks = tasks  # list of {'index': int, 'input_path': str, 'output_path': str}
        self.params = params
        self.create_backup = create_backup
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        total = len(self.tasks)
        success_count = 0
        error_count = 0

        self.sig_log.emit(f"Запуск координации {total} файл(ов)...", "info")
        self.sig_overall_progress.emit(0, total, f"0 / {total}")

        for i, task in enumerate(self.tasks):
            if self._is_cancelled:
                self.sig_log.emit("Процесс координации был прерван пользователем.", "warning")
                break

            idx = task.get("index", i)
            in_path = task["input_path"]
            out_path = task["output_path"]
            fname = os.path.basename(in_path)

            self.sig_overall_progress.emit(i, total, f"{i + 1} / {total}: {fname}")
            self.sig_file_progress.emit(idx, 0, "Запуск...")

            start_t = time.time()
            try:
                def on_log(msg: str, lvl: str):
                    self.sig_log.emit(f"[{fname}] {msg}", lvl)

                def on_progress(pct: int, txt: str):
                    self.sig_file_progress.emit(idx, pct, txt)

                def check_cancel() -> bool:
                    return self._is_cancelled

                res = coordinate_ifc(
                    input_path=in_path,
                    output_path=out_path,
                    x=self.params["x"],
                    y=self.params["y"],
                    z=self.params["z"],
                    ax=self.params.get("ax", 0.0),
                    ay=self.params.get("ay", 0.0),
                    az=self.params.get("az", 0.0),
                    should_rotate_first=self.params.get("should_rotate_first", True),
                    create_backup=self.create_backup,
                    log_callback=on_log,
                    progress_callback=on_progress,
                    cancel_check=check_cancel,
                )

                elapsed = res["elapsed_seconds"]
                success_count += 1
                self.sig_file_progress.emit(idx, 100, f"Готово ({elapsed:.1f}с)")
                self.sig_file_finished.emit(idx, in_path, out_path, True, "Успешно", elapsed)

            except InterruptedError:
                self.sig_file_progress.emit(idx, 0, "Отменено")
                self.sig_file_finished.emit(idx, in_path, out_path, False, "Отменено", 0.0)
                break

            except Exception as e:
                error_count += 1
                elapsed = time.time() - start_t
                err_msg = str(e)
                self.sig_log.emit(f"[{fname}] ОШИБКА: {err_msg}", "error")
                self.sig_file_progress.emit(idx, 0, "Ошибка")
                self.sig_file_finished.emit(idx, in_path, out_path, False, err_msg, elapsed)

            self.sig_overall_progress.emit(i + 1, total, f"{i + 1} / {total}")

        self.sig_all_finished.emit(total, success_count, error_count)
