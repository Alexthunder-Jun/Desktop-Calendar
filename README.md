# 桌面日历 — Windows 悬浮窗日历 + 待办 + 闹钟

一个轻量级 Windows 桌面悬浮窗应用，包含月历视图、每日打卡（Daily Event）、工作事项（Work Event）和闹钟功能。采用 Fluent Design 风格，基于 PySide6 + SQLAlchemy + SQLite 构建。

## 功能概览

- **月历视图** — 自绘月历网格，Work Event 以彩色横线标示
- **Daily Event** — 每日打卡事项，自动计算连续/累计天数
- **Work Event** — 含起止日期的工作事项，在日历上以彩色横线贯穿显示
- **闹钟** — 倒计时与定时两种模式，到点通过 Windows 桌面通知提醒
- **悬浮窗** — 无边框、置顶、不占任务栏、支持拖动和贴边吸附

## 环境要求

- Python 3.9+
- Windows 10/11（开发阶段也可在 macOS/Linux 上运行）

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行
python main.py
# 或
python -m daily_event.app
```

## 打包为 .exe

```powershell
# Windows PowerShell
powershell -ExecutionPolicy Bypass -File build.ps1
```

或手动执行：

```bash
pip install -r requirements.txt
pyinstaller daily_event.spec --noconfirm --clean
```

生成的可执行文件位于 `dist/桌面日历.exe`。

## 运行测试

```bash
python -m pytest tests/ -v
```

## 目录结构

```
daily_event/
├── app/              # 启动与依赖注入
│   ├── bootstrap.py  # 初始化容器、启动 UI
│   └── container.py  # 简单 DI 容器
├── domain/           # 领域模型
│   ├── models.py     # SQLAlchemy ORM（DailyEvent, WorkEvent, Alarm...）
│   └── enums.py      # AlarmMode, AlarmStatus
├── services/         # 业务逻辑（不依赖 Qt）
│   ├── daily_event_service.py
│   ├── work_event_service.py
│   ├── alarm_service.py
│   ├── calendar_service.py  # 日期范围 → 日历线段拆分
│   └── config_service.py    # config.json 读写
├── infra/            # 基础设施
│   ├── database.py          # SQLAlchemy engine + 迁移
│   ├── color_allocator.py   # Work Event 颜色分配
│   ├── notification.py      # 桌面通知
│   └── sound.py             # 提示音
└── ui/               # PySide6 界面（不含业务逻辑）
    ├── main_window.py       # 主悬浮窗
    ├── calendar_widget.py   # 自绘月历
    ├── daily_panel.py       # Daily Event 面板
    ├── work_panel.py        # Work Event 面板
    ├── alarm_page.py        # 闹钟对话框
    ├── stats_page.py        # 累计统计对话框
    ├── dialogs.py           # 通用对话框
    ├── menu_panel.py        # 汉堡菜单
    └── styles.py            # Fluent QSS 主题
```

## 数据存储

- 数据库：`~/.daily_event/data.db`（SQLite）
- 配置：`~/.daily_event/config.json`

## 配置项

| 项 | 说明 | 默认值 |
|---|---|---|
| `window.x/y/width/height` | 窗口位置与尺寸 | 100, 100, 780, 520 |
| `snap_threshold` | 贴边吸附阈值（像素） | 20 |
| `sound_enabled` | 闹钟提示音开关 | true |
| `db_path` | 自定义数据库路径（留空=默认） | "" |

## 扩展指南

- **新增事项类型** — 在 `domain/models.py` 添加 ORM 模型，在 `services/` 添加对应 Service，在 `ui/` 添加面板
- **更换颜色方案** — 修改 `infra/color_allocator.py` 中的 `PALETTE`
- **主题切换** — 在 `ui/styles.py` 中添加暗色主题的 QSS
- **数据库迁移** — 在 `infra/database.py` 的 `MIGRATIONS` 字典中添加 SQL 语句

## FAQ

**Q: 窗口消失了怎么找回？**
删除 `~/.daily_event/config.json`，重启应用恢复默认位置。

**Q: 如何自定义应用图标？**
将 `.ico` 文件放到 `resources/icon.ico`，重新打包即可。

**Q: 数据如何备份？**
复制 `~/.daily_event/data.db` 即可。
