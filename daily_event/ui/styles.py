"""Fluent Design-inspired QSS stylesheet."""

from __future__ import annotations

ACCENT_BLUE = "#0067C0"
ACCENT_BLUE_HOVER = "rgba(0, 103, 192, 0.08)"


def get_stylesheet() -> str:
    return """
    * {
        font-family: "Segoe UI Variable", "Segoe UI", "Microsoft YaHei",
                     "PingFang SC", "Noto Sans SC", sans-serif;
        font-size: 13px;
    }

    #contentFrame {
        background-color: rgba(249, 249, 249, 0.82);
        border-radius: 10px;
        border: 1px solid rgba(0, 0, 0, 0.06);
    }

    #topBar {
        background: transparent;
    }

    QLabel#monthLabel {
        font-size: 15px;
        font-weight: 600;
        color: #1a1a1a;
        padding: 0 8px;
    }

    QPushButton#menuButton,
    QPushButton#navButton {
        background: transparent;
        border: none;
        border-radius: 6px;
        font-size: 14px;
        color: #444444;
    }

    QPushButton#menuButton:hover,
    QPushButton#navButton:hover {
        background-color: rgba(0, 0, 0, 0.05);
    }

    QPushButton#menuButton:pressed,
    QPushButton#navButton:pressed {
        background-color: rgba(0, 0, 0, 0.08);
    }

    QPushButton#closeButton {
        background: transparent;
        border: none;
        border-radius: 6px;
        font-size: 11px;
        color: #888888;
    }

    QPushButton#closeButton:hover {
        background-color: rgba(196, 43, 28, 0.12);
        color: #c42b1c;
    }

    QLabel#panelTitle {
        font-size: 13px;
        font-weight: 600;
        color: #1a1a1a;
    }

    QPushButton#addButton {
        background: transparent;
        border: none;
        border-radius: 4px;
        font-size: 18px;
        font-weight: 300;
        color: #0067c0;
    }

    QPushButton#addButton:hover {
        background-color: rgba(0, 103, 192, 0.08);
    }

    QLabel#emptyHint {
        color: #bbbbbb;
        font-size: 12px;
    }

    QScrollArea {
        border: none;
        background: transparent;
    }

    QWidget#scrollInner {
        background: transparent;
    }

    QScrollBar:vertical {
        background: transparent;
        width: 6px;
        margin: 0;
    }

    QScrollBar::handle:vertical {
        background: rgba(0, 0, 0, 0.12);
        border-radius: 3px;
        min-height: 30px;
    }

    QScrollBar::handle:vertical:hover {
        background: rgba(0, 0, 0, 0.22);
    }

    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {
        height: 0;
    }

    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {
        background: none;
    }

    QMenu {
        background-color: #ffffff;
        border: 1px solid rgba(0, 0, 0, 0.08);
        border-radius: 8px;
        padding: 4px 0;
    }

    QMenu::item {
        padding: 8px 32px 8px 16px;
        color: #1a1a1a;
        border-radius: 4px;
        margin: 2px 4px;
    }

    QMenu::item:selected {
        background-color: rgba(0, 0, 0, 0.04);
    }

    QLineEdit#inlineInput {
        border: 1px solid rgba(0, 0, 0, 0.1);
        border-radius: 4px;
        padding: 4px 8px;
        background: #ffffff;
        font-size: 12px;
    }

    QLineEdit#inlineInput:focus {
        border: 1px solid #0067c0;
    }

    QCheckBox {
        spacing: 6px;
    }

    QCheckBox::indicator {
        width: 16px;
        height: 16px;
        border-radius: 3px;
        border: 1.5px solid #999;
    }

    QCheckBox::indicator:checked {
        background-color: #0067c0;
        border-color: #0067c0;
    }
    """
