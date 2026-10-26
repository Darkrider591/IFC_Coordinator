"""IFC Coordinator - Main entry point.

Desktop application for translating and rotating IFC models (single & batch)
using the lossless OffsetObjectPlacements algorithm.
"""

import sys
import os
import argparse

# Pre-load shape to prevent circular import bug in ifcopenshell
try:
    import ifcopenshell.util.shape
except Exception:
    pass

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from ui.main_window import MainWindow
from ui.theme import DARK_THEME_QSS
from core.coordinator import coordinate_ifc


def run_cli(args):
    """Headless CLI execution mode."""
    print("=" * 60)
    print("IFC Coordinator (CLI Mode)")
    print("=" * 60)
    try:
        res = coordinate_ifc(
            input_path=args.input,
            output_path=args.output or args.input,
            x=args.x,
            y=args.y,
            z=args.z,
            ax=args.ax,
            ay=args.ay,
            az=args.az,
            should_rotate_first=not args.translate_first,
            create_backup=not args.no_backup,
            log_callback=lambda msg, lvl: print(f"[{lvl.upper()}] {msg}"),
            progress_callback=lambda pct, txt: print(f"[{pct}%] {txt}"),
        )
        print("=" * 60)
        print(f"Успешно скоординировано за {res['elapsed_seconds']:.2f} сек.")
        print(f"Выходной файл: {res['output_path']}")
        print("=" * 60)
        return 0
    except Exception as e:
        print(f"[ОШИБКА] {e}", file=sys.stderr)
        return 1


def run_gui():
    """GUI execution mode."""
    # Enable high-DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("IFC Coordinator")
    app.setApplicationVersion("1.1.0")
    app.setOrganizationName("BIM Tools")

    # Set application icon
    icon_path = os.path.join(os.path.dirname(__file__), "resources", "icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Apply Dark Theme
    app.setStyleSheet(DARK_THEME_QSS)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


def main():
    parser = argparse.ArgumentParser(
        description="IFC Coordinator - Смещение и поворот моделей IFC (OffsetObjectPlacements)"
    )
    parser.add_argument("--cli", action="store_true", help="Запуск в режиме командной строки без интерфейса")
    parser.add_argument("-i", "--input", help="Путь к исходному файлу .ifc")
    parser.add_argument("-o", "--output", help="Путь к выходному файлу .ifc")
    parser.add_argument("-x", type=float, default=0.0, help="Смещение по X в единицах проекта")
    parser.add_argument("-y", type=float, default=0.0, help="Смещение по Y в единицах проекта")
    parser.add_argument("-z", type=float, default=0.0, help="Смещение по Z в единицах проекта")
    parser.add_argument("--ax", type=float, default=0.0, help="Поворот вокруг X (градусы)")
    parser.add_argument("--ay", type=float, default=0.0, help="Поворот вокруг Y (градусы)")
    parser.add_argument("--az", type=float, default=0.0, help="Поворот вокруг Z (градусы в плане)")
    parser.add_argument("--translate-first", action="store_true", help="Сначала сместить, затем повернуть (по умолчанию наоборот)")
    parser.add_argument("--no-backup", action="store_true", help="Не создавать .bak при перезаписи")

    # If CLI flag is given or input is specified directly, run CLI
    args, unknown = parser.parse_known_args()
    if args.cli or args.input:
        if not args.input:
            parser.error("В режиме CLI параметр --input (-i) обязателен.")
        sys.exit(run_cli(args))
    else:
        run_gui()


if __name__ == "__main__":
    main()
