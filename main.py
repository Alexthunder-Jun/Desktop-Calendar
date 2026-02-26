import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
from tkcalendar import Calendar
from datetime import date, datetime, timedelta
import threading
import time
import sys
import os

import database as db

try:
    from plyer import notification as plyer_notification
    HAS_PLYER = True
except ImportError:
    HAS_PLYER = False


class AlarmDialog(tk.Toplevel):
    """弹窗：设置闹钟时间"""

    def __init__(self, parent, todo_title, current_alarm=None):
        super().__init__(parent)
        self.title("设置闹钟")
        self.resizable(False, False)
        self.grab_set()
        self.result = None

        frame = ttk.Frame(self, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text=f"待办：{todo_title}").pack(anchor=tk.W)
        ttk.Label(frame, text="提醒时间（格式 YYYY-MM-DD HH:MM）：").pack(
            anchor=tk.W, pady=(10, 2)
        )

        self.entry = ttk.Entry(frame, width=25)
        self.entry.pack(anchor=tk.W)
        if current_alarm:
            self.entry.insert(0, current_alarm.strftime("%Y-%m-%d %H:%M"))
        else:
            tomorrow = datetime.now().replace(hour=9, minute=0, second=0) + timedelta(days=1)
            self.entry.insert(0, tomorrow.strftime("%Y-%m-%d %H:%M"))

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=(12, 0), fill=tk.X)
        ttk.Button(btn_frame, text="确定", command=self._on_ok).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_frame, text="清除闹钟", command=self._on_clear).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_frame, text="取消", command=self.destroy).pack(side=tk.LEFT)

        self.entry.focus_set()
        self.bind("<Return>", lambda e: self._on_ok())
        self.transient(parent)
        self.wait_window()

    def _on_ok(self):
        text = self.entry.get().strip()
        try:
            self.result = datetime.strptime(text, "%Y-%m-%d %H:%M")
            self.destroy()
        except ValueError:
            messagebox.showerror("格式错误", "请输入正确格式：YYYY-MM-DD HH:MM", parent=self)

    def _on_clear(self):
        self.result = "CLEAR"
        self.destroy()


class DeadlineDialog(tk.Toplevel):
    """弹窗：修改截止日期"""

    def __init__(self, parent, todo_title, current_deadline=None):
        super().__init__(parent)
        self.title("修改截止日期")
        self.resizable(False, False)
        self.grab_set()
        self.result = None

        frame = ttk.Frame(self, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text=f"待办：{todo_title}").pack(anchor=tk.W)
        ttk.Label(frame, text="选择新的截止日期：").pack(anchor=tk.W, pady=(10, 2))

        sel = current_deadline if current_deadline else date.today()
        self.cal = Calendar(
            frame,
            selectmode="day",
            year=sel.year,
            month=sel.month,
            day=sel.day,
            locale="zh_CN",
        )
        self.cal.pack()

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=(12, 0))
        ttk.Button(btn_frame, text="确定", command=self._on_ok).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_frame, text="取消", command=self.destroy).pack(side=tk.LEFT)

        self.transient(parent)
        self.wait_window()

    def _on_ok(self):
        self.result = self.cal.selection_get()
        self.destroy()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("桌面日历")
        self.geometry("700x520")
        self.minsize(600, 400)
        self._topmost = False

        db.init_db()
        self._build_ui()
        self._refresh_todo_list()
        self._highlight_dates()
        self._start_alarm_thread()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── UI 构建 ──────────────────────────────────────────────

    def _build_ui(self):
        style = ttk.Style(self)
        available = style.theme_names()
        for preferred in ("clam", "vista", "aqua", "default"):
            if preferred in available:
                style.theme_use(preferred)
                break

        main = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # ── 左侧：日历 + 置顶 ──
        left = ttk.Frame(main, padding=4)
        main.add(left, weight=1)

        self.calendar = Calendar(
            left,
            selectmode="day",
            date_pattern="yyyy-mm-dd",
            locale="zh_CN",
            font=("Microsoft YaHei", 10),
            showweeknumbers=False,
        )
        self.calendar.pack(fill=tk.BOTH, expand=True)
        self.calendar.bind("<<CalendarSelected>>", self._on_date_selected)

        bottom_bar = ttk.Frame(left)
        bottom_bar.pack(fill=tk.X, pady=(6, 0))

        self.pin_var = tk.BooleanVar(value=False)
        pin_cb = ttk.Checkbutton(
            bottom_bar, text="窗口置顶", variable=self.pin_var, command=self._toggle_topmost
        )
        pin_cb.pack(side=tk.LEFT)

        # ── 右侧：输入框 + 待办列表 ──
        right = ttk.Frame(main, padding=4)
        main.add(right, weight=2)

        ttk.Label(right, text="待办事项", font=("Microsoft YaHei", 12, "bold")).pack(
            anchor=tk.W, pady=(0, 4)
        )

        input_frame = ttk.Frame(right)
        input_frame.pack(fill=tk.X, pady=(0, 6))

        self.todo_entry = ttk.Entry(input_frame)
        self.todo_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        self.todo_entry.bind("<Return>", lambda e: self._add_todo())

        ttk.Button(input_frame, text="添加", width=6, command=self._add_todo).pack(side=tk.RIGHT)

        list_frame = ttk.Frame(right)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(
            list_frame,
            columns=("status", "title", "deadline", "alarm"),
            show="headings",
            selectmode="browse",
        )
        self.tree.heading("status", text="")
        self.tree.heading("title", text="标题")
        self.tree.heading("deadline", text="截止日期")
        self.tree.heading("alarm", text="闹钟")

        self.tree.column("status", width=36, anchor=tk.CENTER, stretch=False)
        self.tree.column("title", width=180, anchor=tk.W)
        self.tree.column("deadline", width=90, anchor=tk.CENTER, stretch=False)
        self.tree.column("alarm", width=120, anchor=tk.CENTER, stretch=False)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Button-3>", self._on_right_click)  # Windows 右键
        self.tree.bind("<Button-2>", self._on_right_click)  # macOS 右键

        self._setup_tags()

    def _setup_tags(self):
        completed_font = tkfont.Font(self, family="Microsoft YaHei", size=10, overstrike=True)
        self.tree.tag_configure("completed", foreground="gray")

    # ── 数据操作 ──────────────────────────────────────────────

    def _selected_date(self) -> date:
        return self.calendar.selection_get()

    def _add_todo(self):
        title = self.todo_entry.get().strip()
        if not title:
            return
        deadline = self._selected_date()
        db.add_todo(title, deadline)
        self.todo_entry.delete(0, tk.END)
        self._refresh_todo_list()
        self._highlight_dates()

    def _refresh_todo_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        target = self._selected_date()
        todos = db.get_todos_by_date(target)

        for t in todos:
            status = "\u2705" if t["completed"] else "\u2B1C"
            alarm_str = ""
            if t["alarm_time"]:
                a = t["alarm_time"]
                if isinstance(a, str):
                    a = datetime.strptime(a, "%Y-%m-%d %H:%M:%S")
                alarm_str = a.strftime("%m-%d %H:%M")
            deadline_str = ""
            if t["deadline"]:
                d = t["deadline"]
                if isinstance(d, str):
                    d = date.fromisoformat(d)
                deadline_str = d.strftime("%Y-%m-%d")

            tags = ("completed",) if t["completed"] else ()
            self.tree.insert(
                "",
                tk.END,
                iid=str(t["id"]),
                values=(status, t["title"], deadline_str, alarm_str),
                tags=tags,
            )

    def _highlight_dates(self):
        self.calendar.calevent_remove("all")
        dates = db.get_dates_with_todos()
        for d in dates:
            if isinstance(d, str):
                d = date.fromisoformat(d)
            self.calendar.calevent_create(d, "有待办", "has_todo")
        self.calendar.tag_config("has_todo", background="#FFD700", foreground="black")

    # ── 事件处理 ──────────────────────────────────────────────

    def _on_date_selected(self, event=None):
        self._refresh_todo_list()

    def _on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            db.toggle_completed(int(item))
            self._refresh_todo_list()
            self._highlight_dates()

    def _on_right_click(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return
        self.tree.selection_set(item)
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="设置闹钟", command=lambda: self._set_alarm(int(item)))
        menu.add_command(label="修改截止日期", command=lambda: self._change_deadline(int(item)))
        menu.add_separator()
        menu.add_command(label="删除", command=lambda: self._delete_todo(int(item)))
        menu.tk_popup(event.x_root, event.y_root)

    def _set_alarm(self, todo_id: int):
        todos = db.get_todos_by_date(self._selected_date())
        todo = next((t for t in todos if t["id"] == todo_id), None)
        if not todo:
            return
        current = todo["alarm_time"]
        if isinstance(current, str):
            current = datetime.strptime(current, "%Y-%m-%d %H:%M:%S")

        dlg = AlarmDialog(self, todo["title"], current)
        if dlg.result == "CLEAR":
            db.update_alarm(todo_id, None)
            self._refresh_todo_list()
        elif dlg.result is not None:
            db.update_alarm(todo_id, dlg.result)
            self._refresh_todo_list()

    def _change_deadline(self, todo_id: int):
        todos = db.get_todos_by_date(self._selected_date())
        todo = next((t for t in todos if t["id"] == todo_id), None)
        if not todo:
            return
        current = todo["deadline"]
        if isinstance(current, str):
            current = date.fromisoformat(current)

        dlg = DeadlineDialog(self, todo["title"], current)
        if dlg.result is not None:
            db.update_deadline(todo_id, dlg.result)
            self._refresh_todo_list()
            self._highlight_dates()

    def _delete_todo(self, todo_id: int):
        if messagebox.askyesno("确认删除", "确定要删除这条待办吗？"):
            db.delete_todo(todo_id)
            self._refresh_todo_list()
            self._highlight_dates()

    def _toggle_topmost(self):
        self._topmost = self.pin_var.get()
        self.attributes("-topmost", self._topmost)

    # ── 闹钟后台线程 ─────────────────────────────────────────

    def _start_alarm_thread(self):
        self._alarm_running = True
        t = threading.Thread(target=self._alarm_loop, daemon=True)
        t.start()

    def _alarm_loop(self):
        while self._alarm_running:
            try:
                pending = db.get_pending_alarms()
                for todo in pending:
                    self._fire_notification(todo)
                    db.mark_alarm_notified(todo["id"])
            except Exception:
                pass
            time.sleep(30)

    def _fire_notification(self, todo: dict):
        title = "待办提醒"
        message = f"「{todo['title']}」已到提醒时间！"

        if HAS_PLYER:
            try:
                plyer_notification.notify(
                    title=title,
                    message=message,
                    app_name="桌面日历",
                    timeout=10,
                )
                return
            except Exception:
                pass

        self.after(0, lambda: messagebox.showinfo(title, message))

    def _on_close(self):
        self._alarm_running = False
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
