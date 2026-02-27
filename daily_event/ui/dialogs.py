"""Shared dialogs — Work Event create / edit / detail."""

from __future__ import annotations

from datetime import date
from typing import Any, Optional

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QDateEdit,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class WorkEventDialog(QDialog):
    """Create or edit a Work Event. Set *event* to pre-fill for editing."""

    def __init__(
        self,
        parent: QWidget | None = None,
        event: Any = None,
    ) -> None:
        super().__init__(parent)
        self._event = event
        self._result: Optional[dict | str] = None

        editing = event is not None
        self.setWindowTitle("编辑工作事项" if editing else "创建工作事项")
        self.setMinimumWidth(380)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        lo = QVBoxLayout(self)
        lo.setSpacing(10)
        lo.setContentsMargins(20, 16, 20, 16)

        lo.addWidget(QLabel("标题"))
        self._title_edit = QLineEdit()
        self._title_edit.setPlaceholderText("事项标题...")
        if editing:
            self._title_edit.setText(event.title)
        lo.addWidget(self._title_edit)

        dates = QHBoxLayout()
        dates.setSpacing(12)

        start_box = QVBoxLayout()
        start_box.addWidget(QLabel("开始日期"))
        self._start_edit = QDateEdit()
        self._start_edit.setCalendarPopup(True)
        self._start_edit.setDisplayFormat("yyyy-MM-dd")
        self._start_edit.setDate(
            QDate(event.start_date.year, event.start_date.month, event.start_date.day)
            if editing
            else QDate.currentDate()
        )
        start_box.addWidget(self._start_edit)
        dates.addLayout(start_box)

        end_box = QVBoxLayout()
        end_box.addWidget(QLabel("截止日期"))
        self._end_edit = QDateEdit()
        self._end_edit.setCalendarPopup(True)
        self._end_edit.setDisplayFormat("yyyy-MM-dd")
        self._end_edit.setDate(
            QDate(event.end_date.year, event.end_date.month, event.end_date.day)
            if editing
            else QDate.currentDate()
        )
        end_box.addWidget(self._end_edit)
        dates.addLayout(end_box)
        lo.addLayout(dates)

        lo.addWidget(QLabel("备注（可选）"))
        self._note_edit = QTextEdit()
        self._note_edit.setMaximumHeight(80)
        self._note_edit.setPlaceholderText("添加备注...")
        if editing and event.note:
            self._note_edit.setPlainText(event.note)
        lo.addWidget(self._note_edit)

        btns = QHBoxLayout()
        if editing:
            del_btn = QPushButton("删除")
            del_btn.setStyleSheet("color: #c42b1c;")
            del_btn.clicked.connect(self._on_delete)
            btns.addWidget(del_btn)
        btns.addStretch()
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(cancel_btn)
        ok_btn = QPushButton("确定")
        ok_btn.setStyleSheet(
            "background: #0067c0; color: white; border: none;"
            "border-radius: 4px; padding: 6px 20px;"
        )
        ok_btn.clicked.connect(self._on_ok)
        btns.addWidget(ok_btn)
        lo.addLayout(btns)

    @property
    def result(self) -> Optional[dict | str]:
        return self._result

    def _on_ok(self) -> None:
        title = self._title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "提示", "标题不能为空")
            return
        start: date = self._start_edit.date().toPython()
        end: date = self._end_edit.date().toPython()
        if start > end:
            QMessageBox.warning(self, "提示", "开始日期不能晚于截止日期")
            return
        self._result = {
            "title": title,
            "start_date": start,
            "end_date": end,
            "note": self._note_edit.toPlainText().strip(),
        }
        self.accept()

    def _on_delete(self) -> None:
        reply = QMessageBox.question(
            self, "确认删除", "确定要删除这个事项吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._result = "DELETE"
            self.accept()
