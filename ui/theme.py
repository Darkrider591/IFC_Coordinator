"""Theme manager with Dark and Light themes styled with corporate CTIP palette.

Palette based on CTIP corporate brand identity:
- Emerald Green: #1faa79 (dark: #146a4b, light: #25c58d)
- Golden Amber:  #d8ce78 (dark: #c4b538, light: #e5db82)
- Berry / Pink:  #e3abce (dark: #953270, light: #f0c3df)
- Slate Grey:    #b1b1b0 (dark: #595959, light: #d0d0cf)
"""

COLOR_GREEN_PRIMARY = "#1faa79"
COLOR_GREEN_HOVER   = "#24c48c"
COLOR_GREEN_DARK    = "#146a4b"
COLOR_GREEN_BG      = "#13382c"

COLOR_YELLOW        = "#d8ce78"
COLOR_YELLOW_DARK   = "#c4b538"

COLOR_BERRY         = "#e3abce"
COLOR_BERRY_DARK    = "#953270"

COLOR_GREY          = "#b1b1b0"
COLOR_GREY_DARK     = "#595959"


DARK_THEME_QSS = f"""
QMainWindow, QDialog {{
    background-color: #1a1d20;
    color: #e6ebed;
}}

QWidget {{
    background-color: #1a1d20;
    color: #d8dee2;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
}}

/* Top Header & Labels */
QLabel#title_label {{
    font-size: 17px;
    font-weight: 700;
    color: {COLOR_GREEN_PRIMARY};
    letter-spacing: 0.5px;
}}

QLabel#brand_badge {{
    background-color: {COLOR_GREEN_DARK};
    color: #ffffff;
    font-weight: bold;
    font-size: 11px;
    padding: 3px 8px;
    border-radius: 4px;
}}

/* Tabs */
QTabWidget::pane {{
    border: 1px solid #2f363d;
    background-color: #212529;
    border-radius: 5px;
    top: -1px;
}}

QTabBar::tab {{
    background-color: #272c32;
    color: #a0abb4;
    padding: 9px 20px;
    margin-right: 3px;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    border: 1px solid #2f363d;
    border-bottom: none;
    font-weight: 600;
}}

QTabBar::tab:selected {{
    background-color: #212529;
    color: #ffffff;
    border-bottom: 3px solid {COLOR_GREEN_PRIMARY};
}}

QTabBar::tab:hover:!selected {{
    background-color: #31373e;
    color: #ffffff;
}}

/* Group Boxes */
QGroupBox {{
    background-color: #212529;
    border: 1px solid #323942;
    border-radius: 6px;
    margin-top: 18px;
    padding-top: 14px;
    padding-bottom: 10px;
    padding-left: 10px;
    padding-right: 10px;
    font-weight: bold;
    color: #e6ebed;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    padding: 0 8px;
    background-color: #212529;
    color: {COLOR_GREEN_PRIMARY};
}}

/* Drop Area Frame */
QFrame#drop_zone {{
    background-color: #1a2721;
    border: 2px dashed {COLOR_GREEN_PRIMARY};
    border-radius: 8px;
    padding: 12px;
}}

QFrame#drop_zone:hover {{
    background-color: #20352b;
    border: 2px dashed {COLOR_GREEN_HOVER};
}}

/* Input Fields */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background-color: #16181b;
    border: 1px solid #363e47;
    border-radius: 4px;
    padding: 6px 9px;
    color: #ffffff;
    selection-background-color: {COLOR_GREEN_DARK};
}}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
    border: 1px solid {COLOR_GREEN_PRIMARY};
    background-color: #121417;
}}

QLineEdit:disabled, QComboBox:disabled {{
    background-color: #23272c;
    color: #717d88;
    border: 1px solid #2f353c;
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 22px;
    border-left: 1px solid #363e47;
}}

QComboBox QAbstractItemView {{
    background-color: #212529;
    border: 1px solid #363e47;
    color: #e6ebed;
    selection-background-color: {COLOR_GREEN_DARK};
    outline: none;
}}

/* Buttons */
QPushButton {{
    background-color: #2a3038;
    color: #e6ebed;
    border: 1px solid #3a424d;
    border-radius: 4px;
    padding: 6px 14px;
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: #353d47;
    border-color: {COLOR_GREEN_PRIMARY};
    color: #ffffff;
}}

QPushButton:pressed {{
    background-color: #1d2126;
}}

QPushButton:disabled {{
    background-color: #23272c;
    color: #636d77;
    border-color: #2b3138;
}}

/* Theme Toggle Button */
QPushButton#theme_toggle {{
    background-color: #2a3038;
    color: {COLOR_YELLOW};
    border: 1px solid #3e4652;
    border-radius: 4px;
    padding: 5px 12px;
    font-weight: 600;
}}

QPushButton#theme_toggle:hover {{
    background-color: #38414c;
    border-color: {COLOR_YELLOW};
    color: #ffffff;
}}

/* Primary Action Execute Button (CTIP Emerald) */
QPushButton#execute_button {{
    background-color: {COLOR_GREEN_PRIMARY};
    color: #ffffff;
    border: 1px solid {COLOR_GREEN_HOVER};
    font-size: 14px;
    font-weight: bold;
    padding: 8px 24px;
    border-radius: 5px;
}}

QPushButton#execute_button:hover {{
    background-color: {COLOR_GREEN_HOVER};
    border-color: #38db9f;
}}

QPushButton#execute_button:pressed {{
    background-color: {COLOR_GREEN_DARK};
}}

QPushButton#cancel_button {{
    background-color: #a32d43;
    color: #ffffff;
    border: 1px solid #b8364e;
    font-size: 14px;
    font-weight: bold;
    padding: 8px 20px;
    border-radius: 5px;
}}

QPushButton#cancel_button:hover {{
    background-color: #be3552;
}}

QPushButton#cancel_button:pressed {{
    background-color: #872236;
}}

/* Checkboxes & Radio */
QCheckBox, QRadioButton {{
    color: #e6ebed;
    spacing: 7px;
}}

QCheckBox::indicator, QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid #4a5460;
    background-color: #16181b;
    border-radius: 3px;
}}

QRadioButton::indicator {{
    border-radius: 8px;
}}

QCheckBox::indicator:checked {{
    background-color: {COLOR_GREEN_PRIMARY};
    border: 1px solid {COLOR_GREEN_PRIMARY};
    image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12"><path fill="none" stroke="white" stroke-width="2" d="M2 6l3 3 5-5"/></svg>');
}}

QRadioButton::indicator:checked {{
    background-color: {COLOR_GREEN_PRIMARY};
    border: 1px solid {COLOR_GREEN_PRIMARY};
}}

/* Progress Bar */
QProgressBar {{
    background-color: #16181b;
    border: 1px solid #363e47;
    border-radius: 4px;
    text-align: center;
    color: #ffffff;
    font-weight: bold;
    height: 20px;
}}

QProgressBar::chunk {{
    background-color: {COLOR_GREEN_PRIMARY};
    border-radius: 3px;
}}

/* Table Widget */
QTableWidget {{
    background-color: #16181b;
    alternate-background-color: #1f2328;
    color: #e6ebed;
    border: 1px solid #2f363d;
    gridline-color: #272c32;
    border-radius: 4px;
    selection-background-color: {COLOR_GREEN_DARK};
    selection-color: #ffffff;
}}

QHeaderView::section {{
    background-color: #272c32;
    color: #d8dee2;
    padding: 7px;
    border: 1px solid #2f363d;
    font-weight: bold;
}}

/* Console Log */
QTextEdit {{
    background-color: #121417;
    color: #d8dee2;
    border: 1px solid #2f363d;
    border-radius: 4px;
    font-family: 'Consolas', 'Cascadia Code', monospace;
    font-size: 12px;
}}

/* ScrollBars */
QScrollBar:vertical {{
    background-color: #1a1d20;
    width: 12px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background-color: #363e47;
    min-height: 20px;
    border-radius: 6px;
    margin: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLOR_GREEN_PRIMARY};
}}

QScrollBar:horizontal {{
    background-color: #1a1d20;
    height: 12px;
    margin: 0px;
}}

QScrollBar::handle:horizontal {{
    background-color: #363e47;
    min-width: 20px;
    border-radius: 6px;
    margin: 2px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {COLOR_GREEN_PRIMARY};
}}

QScrollBar::add-line, QScrollBar::sub-line {{
    height: 0px;
    width: 0px;
}}

QStatusBar {{
    background-color: #212529;
    color: #a0abb4;
    border-top: 1px solid #2f363d;
    font-size: 12px;
}}
"""


LIGHT_THEME_QSS = f"""
QMainWindow, QDialog {{
    background-color: #f5f7f9;
    color: #1f2937;
}}

QWidget {{
    background-color: #f5f7f9;
    color: #1f2937;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
}}

/* Top Header & Labels */
QLabel#title_label {{
    font-size: 17px;
    font-weight: 700;
    color: {COLOR_GREEN_DARK};
    letter-spacing: 0.5px;
}}

QLabel#brand_badge {{
    background-color: {COLOR_GREEN_PRIMARY};
    color: #ffffff;
    font-weight: bold;
    font-size: 11px;
    padding: 3px 8px;
    border-radius: 4px;
}}

/* Tabs */
QTabWidget::pane {{
    border: 1px solid #d1d5db;
    background-color: #ffffff;
    border-radius: 5px;
    top: -1px;
}}

QTabBar::tab {{
    background-color: #e5e7eb;
    color: #4b5563;
    padding: 9px 20px;
    margin-right: 3px;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    border: 1px solid #d1d5db;
    border-bottom: none;
    font-weight: 600;
}}

QTabBar::tab:selected {{
    background-color: #ffffff;
    color: {COLOR_GREEN_DARK};
    border-bottom: 3px solid {COLOR_GREEN_PRIMARY};
}}

QTabBar::tab:hover:!selected {{
    background-color: #f3f4f6;
    color: #111827;
}}

/* Group Boxes */
QGroupBox {{
    background-color: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    margin-top: 18px;
    padding-top: 14px;
    padding-bottom: 10px;
    padding-left: 10px;
    padding-right: 10px;
    font-weight: bold;
    color: #111827;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    padding: 0 8px;
    background-color: #ffffff;
    color: {COLOR_GREEN_DARK};
}}

/* Drop Area Frame */
QFrame#drop_zone {{
    background-color: #edf8f3;
    border: 2px dashed {COLOR_GREEN_PRIMARY};
    border-radius: 8px;
    padding: 12px;
}}

QFrame#drop_zone:hover {{
    background-color: #ddf2e8;
    border: 2px dashed {COLOR_GREEN_HOVER};
}}

/* Input Fields */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    padding: 6px 9px;
    color: #0f172a;
    selection-background-color: {COLOR_GREEN_PRIMARY};
    selection-color: #ffffff;
}}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
    border: 1px solid {COLOR_GREEN_PRIMARY};
    background-color: #ffffff;
}}

QLineEdit:disabled, QComboBox:disabled {{
    background-color: #f1f5f9;
    color: #94a3b8;
    border: 1px solid #e2e8f0;
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 22px;
    border-left: 1px solid #cbd5e1;
}}

QComboBox QAbstractItemView {{
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    color: #0f172a;
    selection-background-color: {COLOR_GREEN_PRIMARY};
    selection-color: #ffffff;
    outline: none;
}}

/* Buttons */
QPushButton {{
    background-color: #ffffff;
    color: #1f2937;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    padding: 6px 14px;
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: #f8fafc;
    border-color: {COLOR_GREEN_PRIMARY};
    color: {COLOR_GREEN_DARK};
}}

QPushButton:pressed {{
    background-color: #e2e8f0;
}}

QPushButton:disabled {{
    background-color: #f1f5f9;
    color: #94a3b8;
    border-color: #e2e8f0;
}}

/* Theme Toggle Button */
QPushButton#theme_toggle {{
    background-color: #ffffff;
    color: {COLOR_GREEN_DARK};
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    padding: 5px 12px;
    font-weight: 600;
}}

QPushButton#theme_toggle:hover {{
    background-color: #f1f5f9;
    border-color: {COLOR_GREEN_PRIMARY};
}}

/* Primary Action Execute Button (CTIP Emerald) */
QPushButton#execute_button {{
    background-color: {COLOR_GREEN_PRIMARY};
    color: #ffffff;
    border: 1px solid {COLOR_GREEN_DARK};
    font-size: 14px;
    font-weight: bold;
    padding: 8px 24px;
    border-radius: 5px;
}}

QPushButton#execute_button:hover {{
    background-color: {COLOR_GREEN_HOVER};
}}

QPushButton#execute_button:pressed {{
    background-color: {COLOR_GREEN_DARK};
}}

QPushButton#cancel_button {{
    background-color: #dc2626;
    color: #ffffff;
    border: 1px solid #b91c1c;
    font-size: 14px;
    font-weight: bold;
    padding: 8px 20px;
    border-radius: 5px;
}}

QPushButton#cancel_button:hover {{
    background-color: #ef4444;
}}

QPushButton#cancel_button:pressed {{
    background-color: #991b1b;
}}

/* Checkboxes & Radio */
QCheckBox, QRadioButton {{
    color: #1f2937;
    spacing: 7px;
}}

QCheckBox::indicator, QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid #94a3b8;
    background-color: #ffffff;
    border-radius: 3px;
}}

QRadioButton::indicator {{
    border-radius: 8px;
}}

QCheckBox::indicator:checked {{
    background-color: {COLOR_GREEN_PRIMARY};
    border: 1px solid {COLOR_GREEN_PRIMARY};
    image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12"><path fill="none" stroke="white" stroke-width="2" d="M2 6l3 3 5-5"/></svg>');
}}

QRadioButton::indicator:checked {{
    background-color: {COLOR_GREEN_PRIMARY};
    border: 1px solid {COLOR_GREEN_PRIMARY};
}}

/* Progress Bar */
QProgressBar {{
    background-color: #e2e8f0;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    text-align: center;
    color: #0f172a;
    font-weight: bold;
    height: 20px;
}}

QProgressBar::chunk {{
    background-color: {COLOR_GREEN_PRIMARY};
    border-radius: 3px;
}}

/* Table Widget */
QTableWidget {{
    background-color: #ffffff;
    alternate-background-color: #f8fafc;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    gridline-color: #e2e8f0;
    border-radius: 4px;
    selection-background-color: #d1fae5;
    selection-color: #065f46;
}}

QHeaderView::section {{
    background-color: #f1f5f9;
    color: #334155;
    padding: 7px;
    border: 1px solid #cbd5e1;
    font-weight: bold;
}}

/* Console Log */
QTextEdit {{
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    font-family: 'Consolas', 'Cascadia Code', monospace;
    font-size: 12px;
}}

/* ScrollBars */
QScrollBar:vertical {{
    background-color: #f1f5f9;
    width: 12px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background-color: #cbd5e1;
    min-height: 20px;
    border-radius: 6px;
    margin: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLOR_GREEN_PRIMARY};
}}

QScrollBar:horizontal {{
    background-color: #f1f5f9;
    height: 12px;
    margin: 0px;
}}

QScrollBar::handle:horizontal {{
    background-color: #cbd5e1;
    min-width: 20px;
    border-radius: 6px;
    margin: 2px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {COLOR_GREEN_PRIMARY};
}}

QScrollBar::add-line, QScrollBar::sub-line {{
    height: 0px;
    width: 0px;
}}

QStatusBar {{
    background-color: #ffffff;
    color: #4b5563;
    border-top: 1px solid #e5e7eb;
    font-size: 12px;
}}
"""
