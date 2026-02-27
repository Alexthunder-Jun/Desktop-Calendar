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
    QSpinBox,
    QStackedWidget,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from daily_event.services.alarm_service import AlarmService

_ACTIVE_TAB = (
    "background:#0067c0; color:white; border:none; "
    "border-radius:4px; padding:6px 16px; font-weight:600;"
)
_INACTIVE_TAB = (
    "background:transparent; color:#666; border:1px solid #ddd; "
    "border-radius:4px; padding:6px 16px;"
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
        self.setMinimumSize(440, 400)
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
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(12)

        heading = QLabel("闹钟")
        heading.setStyleSheet("font-size:16px; font-weight:600; color:#1a1a1a;")
        root.addWidget(heading)

        tabs = QHBoxLayout()
        tabs.setSpacing(8)
        self._tab_countdown = QPushButton("倒计时")
        self._tab_countdown.clicked.connect(lambda: self._set_mode(0))
        tabs.addWidget(self._tab_countdown)
        self._tab_scheduled = QPushButton("定时提醒")
        self._tab_scheduled.clicked.connect(lambda: self._set_mode(1))
        tabs.addWidget(self._tab_scheduled)
        tabs.addStretch()
        root.addLayout(tabs)

        self._stack = QStackedWidget()

        # -- countdown --
        cd = QWidget()
        cdl = QHBoxLayout(cd)
        cdl.setContentsMargins(0, 0, 0, 0)
        cdl.setSpacing(8)
        self._min_spin = QSpinBox()
        self._min_spin.setRange(1, 999)
        self._min_spin.setValue(25)
        self._min_spin.setSuffix(" 分钟")
        cdl.addWidget(self._min_spin)
        self._cd_label = QLineEdit()
        self._cd_label.setPlaceholderText("标签（可选）")
        cdl.addWidget(self._cd_label, stretch=1)
        start_btn = QPushButton("开始")
        start_btn.setStyleSheet(
            "background:#0067c0; color:white; border:none;"
            "border-radius:4px; padding:6px 14px;"
        )
        start_btn.clicked.connect(self._start_countdown)
        cdl.addWidget(start_btn)
        self._stack.addWidget(cd)

        # -- scheduled --
        sc = QWidget()
        scl = QHBoxLayout(sc)
        scl.setContentsMargins(0, 0, 0, 0)
        scl.setSpacing(8)
        self._time_edit = QTimeEdit()
        self._time_edit.setDisplayFormat("HH:mm")
        self._time_edit.setTime(QTime(18, 30))
        scl.addWidget(self._time_edit)
        self._sc_label = QLineEdit()
        self._sc_label.setPlaceholderText("标签（可选）")
        scl.addWidget(self._sc_label, stretch=1)
        set_btn = QPushButton("设置")
        set_btn.setStyleSheet(
            "background:#0067c0; color:white; border:none;"
            "border-radius:4px; padding:6px 14px;"
        )
        set_btn.clicked.connect(self._set_scheduled)
        scl.addWidget(set_btn)
        self._stack.addWidget(sc)

        root.addWidget(self._stack)

        # -- list --
        sep = QLabel("闹钟列表")
        sep.setStyleSheet("font-size:13px; font-weight:600; color:#1a1a1a; margin-top:4px;")
        root.addWidget(sep)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._list_w = QWidget()
        self._list_w.setObjectName("scrollInner")
        self._list_lo = QVBoxLayout(self._list_w)
        self._list_lo.setContentsMargins(0, 0, 0, 0)
        self._list_lo.setSpacing(4)
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
        minutes = self._min_spin.value()
        label = self._cd_label.text().strip()
        self._service.create_countdown(label, minutes)
        self._cd_label.clear()
        self._refresh_list()

    def _set_scheduled(self) -> None:
        if not self._service:
            return
        t = self._time_edit.time()
        label = self._sc_label.text().strip()
        self._service.create_scheduled(label, t.hour(), t.minute())
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
            self._list_lo.addWidget(h)
        else:
            for a in alarms:
                self._list_lo.addWidget(self._build_item(a))
        self._list_lo.addStretch()

    def _build_item(self, alarm) -> QWidget:
        row = QWidget()
        lo = QHBoxLayout(row)
        lo.setContentsMargins(8, 4, 8, 4)
        lo.setSpacing(8)

        lbl = QLabel(alarm.label)
        lbl.setStyleSheet("font-size:12px; color:#1a1a1a;")
        lo.addWidget(lbl, stretch=1)

        time_str = alarm.target_time.strftime("%m-%d %H:%M") if alarm.target_time else ""
        time_lbl = QLabel(time_str)
        time_lbl.setStyleSheet("font-size:10px; color:#888;")
        lo.addWidget(time_lbl)

        status_text, status_color = _STATUS_LABELS.get(alarm.status, ("未知", "#888"))
        badge = QLabel(status_text)
        badge.setStyleSheet(
            f"font-size:10px; color:{status_color}; background:rgba(0,0,0,0.04);"
            "border-radius:3px; padding:1px 6px;"
        )
        lo.addWidget(badge)

        if alarm.status == "pending":
            cancel = QPushButton("取消")
            cancel.setFixedHeight(24)
            cancel.setStyleSheet("font-size:10px; color:#c42b1c; border:1px solid #ddd; border-radius:3px; padding:2px 8px;")
            cancel.clicked.connect(lambda checked=False, aid=alarm.id: self._cancel(aid))
            lo.addWidget(cancel)

        return row

    def _cancel(self, alarm_id: int) -> None:
        if self._service:
            self._service.cancel(alarm_id)
        self._refresh_list()
