"""Alarm management dialog — countdown and scheduled modes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QTime, Qt, QTimer
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from daily_event.ui.wheel_picker import WheelPicker

if TYPE_CHECKING:
    from daily_event.services.alarm_service import AlarmService

_ACTIVE_TAB = (
    "background:#0067c0; color:white; border:none; "
    "border-radius:16px; padding:6px 16px; font-weight:600;"
)
_INACTIVE_TAB = (
    "background:transparent; color:#666; border:1px solid #ddd; "
    "border-radius:16px; padding:6px 16px;"
)

_STATUS_LABELS = {
    "pending": ("等待中", "#0067c0"),
    "fired": ("已触发", "#888"),
    "cancelled": ("已取消", "#bbb"),
}


class AlarmPage(QDialog):
    def __init__(self, alarm_service: AlarmService | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._service = alarm_service
        self.setWindowTitle("闹钟")
        self.setMinimumSize(440, 450)
        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.WindowCloseButtonHint
        )

        self._mode = 0
        self._setup_ui()
        self._refresh_list()

        self._tick = QTimer(self)
        self._tick.timeout.connect(self._refresh_list)
        self._tick.start(2000)

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        # Header
        header_layout = QHBoxLayout()
        heading = QLabel("闹钟")
        heading.setStyleSheet("font-size:20px; font-weight:bold; color:#1a1a1a;")
        header_layout.addWidget(heading)
        header_layout.addStretch()
        root.addLayout(header_layout)

        # Tabs
        tabs = QHBoxLayout()
        tabs.setSpacing(12)
        self._tab_countdown = QPushButton("倒计时")
        self._tab_countdown.setCursor(Qt.CursorShape.PointingHandCursor)
        self._tab_countdown.clicked.connect(lambda: self._set_mode(0))
        tabs.addWidget(self._tab_countdown)
        
        self._tab_scheduled = QPushButton("定时提醒")
        self._tab_scheduled.setCursor(Qt.CursorShape.PointingHandCursor)
        self._tab_scheduled.clicked.connect(lambda: self._set_mode(1))
        tabs.addWidget(self._tab_scheduled)
        tabs.addStretch()
        root.addLayout(tabs)

        self._stack = QStackedWidget()

        # -- Countdown Page --
        cd_page = QWidget()
        cd_layout = QVBoxLayout(cd_page)
        cd_layout.setContentsMargins(0, 10, 0, 10)
        cd_layout.setSpacing(20)

        # Wheel Picker for minutes
        picker_container = QHBoxLayout()
        picker_container.addStretch()
        self._min_picker = WheelPicker(1, 120, 25, "{:d}")
        picker_container.addWidget(self._min_picker)
        unit_label = QLabel("分钟")
        unit_label.setStyleSheet("font-size: 16px; color: #666; margin-top: 10px;")
        picker_container.addWidget(unit_label)
        picker_container.addStretch()
        cd_layout.addLayout(picker_container)

        # Input and Button
        input_row = QHBoxLayout()
        self._cd_label = QLineEdit()
        self._cd_label.setPlaceholderText("标签（可选）")
        self._cd_label.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 8px 12px;
                background: #f9f9f9;
            }
            QLineEdit:focus {
                border: 1px solid #0067c0;
                background: #fff;
            }
        """)
        input_row.addWidget(self._cd_label)
        
        start_btn = QPushButton("开始")
        start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        start_btn.setStyleSheet("""
            QPushButton {
                background: #0067c0; 
                color: white; 
                border: none;
                border-radius: 8px; 
                padding: 8px 24px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #0056a0;
            }
        """)
        start_btn.clicked.connect(self._start_countdown)
        input_row.addWidget(start_btn)
        cd_layout.addLayout(input_row)
        
        self._stack.addWidget(cd_page)

        # -- Scheduled Page --
        sc_page = QWidget()
        sc_layout = QVBoxLayout(sc_page)
        sc_layout.setContentsMargins(0, 10, 0, 10)
        sc_layout.setSpacing(20)

        # Wheel Pickers for HH:MM
        time_picker_container = QHBoxLayout()
        time_picker_container.addStretch()
        
        self._hour_picker = WheelPicker(0, 23, 18, "{:02d}")
        time_picker_container.addWidget(self._hour_picker)
        
        colon = QLabel(":")
        colon.setStyleSheet("font-size: 32px; font-weight: bold; color: #0067c0; margin-bottom: 8px;")
        time_picker_container.addWidget(colon)
        
        self._minute_picker = WheelPicker(0, 59, 30, "{:02d}")
        time_picker_container.addWidget(self._minute_picker)
        
        time_picker_container.addStretch()
        sc_layout.addLayout(time_picker_container)

        # Input and Button
        sc_input_row = QHBoxLayout()
        self._sc_label = QLineEdit()
        self._sc_label.setPlaceholderText("标签（可选）")
        self._sc_label.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 8px 12px;
                background: #f9f9f9;
            }
            QLineEdit:focus {
                border: 1px solid #0067c0;
                background: #fff;
            }
        """)
        sc_input_row.addWidget(self._sc_label)
        
        set_btn = QPushButton("设置")
        set_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        set_btn.setStyleSheet("""
            QPushButton {
                background: #0067c0; 
                color: white; 
                border: none;
                border-radius: 8px; 
                padding: 8px 24px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #0056a0;
            }
        """)
        set_btn.clicked.connect(self._set_scheduled)
        sc_input_row.addWidget(set_btn)
        sc_layout.addLayout(sc_input_row)

        self._stack.addWidget(sc_page)

        root.addWidget(self._stack)

        # -- List --
        list_header = QLabel("闹钟列表")
        list_header.setStyleSheet("font-size:14px; font-weight:600; color:#444; margin-top:10px;")
        root.addWidget(list_header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self._list_w = QWidget()
        self._list_w.setObjectName("scrollInner")
        self._list_w.setStyleSheet("#scrollInner { background: transparent; }")
        self._list_lo = QVBoxLayout(self._list_w)
        self._list_lo.setContentsMargins(0, 0, 0, 0)
        self._list_lo.setSpacing(8)
        self._list_lo.addStretch()
        scroll.setWidget(self._list_w)
        root.addWidget(scroll, stretch=1)

        self._update_tab_styles()

    # -- mode switching --

    def _set_mode(self, idx: int) -> None:
        self._mode = idx
        self._stack.setCurrentIndex(idx)
        self._update_tab_styles()

    def _update_tab_styles(self) -> None:
        self._tab_countdown.setStyleSheet(_ACTIVE_TAB if self._mode == 0 else _INACTIVE_TAB)
        self._tab_scheduled.setStyleSheet(_INACTIVE_TAB if self._mode == 0 else _ACTIVE_TAB)

    # -- create alarms --

    def _start_countdown(self) -> None:
        if not self._service:
            return
        minutes = self._min_picker.value
        label = self._cd_label.text().strip()
        self._service.create_countdown(label, minutes)
        self._cd_label.clear()
        self._refresh_list()

    def _set_scheduled(self) -> None:
        if not self._service:
            return
        hour = self._hour_picker.value
        minute = self._minute_picker.value
        label = self._sc_label.text().strip()
        self._service.create_scheduled(label, hour, minute)
        self._sc_label.clear()
        self._refresh_list()

    # -- list --

    def _refresh_list(self) -> None:
        while self._list_lo.count() > 0:
            item = self._list_lo.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if not self._service:
            return
        alarms = self._service.get_all()
        if not alarms:
            h = QLabel("暂无闹钟")
            h.setObjectName("emptyHint")
            h.setAlignment(Qt.AlignmentFlag.AlignCenter)
            h.setStyleSheet("color: #aaa; font-style: italic; margin-top: 20px;")
            self._list_lo.addWidget(h)
        else:
            for a in alarms:
                self._list_lo.addWidget(self._build_item(a))
        self._list_lo.addStretch()

    def _build_item(self, alarm) -> QWidget:
        row = QWidget()
        row.setStyleSheet("""
            QWidget {
                background: #f5f5f5;
                border-radius: 8px;
            }
        """)
        lo = QHBoxLayout(row)
        lo.setContentsMargins(12, 8, 12, 8)
        lo.setSpacing(10)

        lbl = QLabel(alarm.label)
        lbl.setStyleSheet("font-size:13px; color:#1a1a1a; font-weight: 500;")
        lo.addWidget(lbl, stretch=1)

        time_str = alarm.target_time.strftime("%m-%d %H:%M") if alarm.target_time else ""
        time_lbl = QLabel(time_str)
        time_lbl.setStyleSheet("font-size:11px; color:#666;")
        lo.addWidget(time_lbl)

        status_text, status_color = _STATUS_LABELS.get(alarm.status, ("未知", "#888"))
        badge = QLabel(status_text)
        badge.setStyleSheet(
            f"font-size:10px; color:{status_color}; background:rgba(0,0,0,0.05);"
            "border-radius:4px; padding:2px 6px; font-weight: 600;"
        )
        lo.addWidget(badge)

        if alarm.status == "pending":
            cancel = QPushButton("取消")
            cancel.setCursor(Qt.CursorShape.PointingHandCursor)
            cancel.setFixedSize(40, 24)
            cancel.setStyleSheet("""
                QPushButton {
                    font-size:11px; 
                    color:#c42b1c; 
                    border:1px solid #e0b4b0; 
                    border-radius:4px; 
                    background: transparent;
                }
                QPushButton:hover {
                    background: #fce8e6;
                }
            """)
            cancel.clicked.connect(lambda checked=False, aid=alarm.id: self._cancel(aid))
            lo.addWidget(cancel)

        return row

    def _cancel(self, alarm_id: int) -> None:
        if self._service:
            self._service.cancel(alarm_id)
        self._refresh_list()
