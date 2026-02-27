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
        color: #2c2c2c;
    }

    #contentFrame {
        background-color: rgba(255, 255, 255, 0.92);
        border-radius: 12px;
        border: 1px solid rgba(0, 0, 0, 0.08);
    }

    #topBar {
        background: transparent;
    }

    QLabel#monthLabel {
        font-size: 18px;
        font-weight: 700;
        color: #1a1a1a;
        padding: 0 10px;
        font-family: "Segoe UI Variable Display", "Segoe UI", sans-serif;
    }

    QPushButton#menuButton,
    QPushButton#navButton {
        background: transparent;
        border: none;
        border-radius: 6px;
        font-size: 14px;
        color: #555555;
        padding: 4px;
    }

    QPushButton#menuButton:hover,
    QPushButton#navButton:hover {
        background-color: rgba(0, 0, 0, 0.05);
        color: #000000;
    }

    QPushButton#menuButton:pressed,
    QPushButton#navButton:pressed {
        background-color: rgba(0, 0, 0, 0.08);
    }

    QPushButton#closeButton {
        background: transparent;
        border: none;
        border-radius: 6px;
        font-size: 12px;
        color: #666666;
        margin-right: 4px;
    }

    QPushButton#closeButton:hover {
        background-color: #c42b1c;
        color: #ffffff;
    }

    QLabel#panelTitle {
        font-size: 14px;
        font-weight: 600;
        color: #444444;
        margin-bottom: 6px;
        margin-left: 2px;
    }

    QPushButton#addButton {
        background: transparent;
        border: none;
        border-radius: 4px;
        font-size: 18px;
        font-weight: 400;
        color: #0067c0;
        padding-bottom: 2px;
    }

    QPushButton#addButton:hover {
        background-color: rgba(0, 103, 192, 0.08);
    }

    /* Item Cards */
    QWidget#itemCard {
        background-color: #ffffff;
        border: 1px solid rgba(0, 0, 0, 0.06);
        border-radius: 6px;
    }
    QWidget#itemCard:hover {
        background-color: #fdfdfd;
        border: 1px solid rgba(0, 0, 0, 0.12);
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    QLabel#emptyHint {
        color: #aaaaaa;
        font-size: 13px;
        font-style: italic;
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
        background: rgba(0, 0, 0, 0.15);
        border-radius: 3px;
        min-height: 30px;
    }

    QScrollBar::handle:vertical:hover {
        background: rgba(0, 0, 0, 0.25);
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
        border: 1px solid rgba(0, 0, 0, 0.1);
        border-radius: 8px;
        padding: 6px 0;
    }

    QMenu::item {
        padding: 8px 32px 8px 16px;
        color: #1a1a1a;
        border-radius: 4px;
        margin: 2px 6px;
    }

    QMenu::item:selected {
        background-color: rgba(0, 103, 192, 0.08);
        color: #0067c0;
    }

    QLineEdit#inlineInput {
        border: 1px solid rgba(0, 0, 0, 0.15);
        border-radius: 6px;
        padding: 6px 10px;
        background: #ffffff;
        font-size: 13px;
    }

    QLineEdit#inlineInput:focus {
        border: 1px solid #0067c0;
        background-color: #ffffff;
    }

    QCheckBox {
        spacing: 8px;
    }

    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 1px solid #bbbbbb;
        background: #ffffff;
    }

    QCheckBox::indicator:hover {
        border-color: #0067c0;
    }

    QCheckBox::indicator:checked {
        background-color: #0067c0;
        border-color: #0067c0;
    }
    """
