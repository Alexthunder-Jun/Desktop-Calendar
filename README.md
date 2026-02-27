# 桌面日历 — Windows 悬浮窗日历 + 待办 + 闹钟

一个轻量级 Windows 桌面悬浮窗应用，包含月历视图、每日打卡（Daily Event）、每日事项设置、工作事项（Work Event）、历史记录和闹钟功能。采用 Fluent Design 风格，基于 PySide6 + SQLAlchemy + SQLite 构建。

## 功能概览

- **月历视图** — 自绘月历网格，Work Event 以彩色横线跨日标示，支持跨周渲染
- **Daily Event** — 每日打卡事项，自动计算连续天数和累计天数；完成后当日隐藏、次日重现
- **每日事项设置** — 在汉堡菜单中统一管理 Daily Event，可配置间隔（工作日 / 周末 / 两天一次 / 三天一次 / 一周一次）与永久删除（带确认）
- **Work Event** — 含起止日期的工作事项，支持完成勾选；完成后自动归入历史
- **历史记录** — 已完成的 Work Event 归档查看，支持删除
- **累计统计** — 查看所有 Daily Event 的累计天数、连续天数、创建日期、最近完成日期；支持删除（需确认）
- **闹钟** — 倒计时与定时两种模式，支持滚轮式时间选择器（鼠标滚轮快速调节），到点通过 Windows 桌面通知 + 可选提示音提醒
- **系统托盘** — 最小化到系统托盘，不占任务栏；托盘菜单支持显示/隐藏/退出
- **悬浮窗** — 无边框半透明窗口，支持自由拖动和贴边吸附，首次启动自动定位至屏幕右侧
- **单实例运行** — 启动时自动加锁，防止重复启动导致多个托盘和多个独立窗口

## 下载 .exe

前往 [GitHub Actions](https://github.com/Alexthunder-Jun/Desktop-Calendar/actions) 页面，点击最新成功的构建，在 **Artifacts** 区域下载 `desktop-calendar-exe`。

或在 [Releases](https://github.com/Alexthunder-Jun/Desktop-Calendar/releases) 页面下载带版本号的发布包（需推送 `v*` 标签触发）。

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
# Windows PowerShell — 一键构建
powershell -ExecutionPolicy Bypass -File build.ps1
```

或手动执行：

```bash
pip install -r requirements.txt
pyinstaller daily_event.spec --noconfirm --clean
```

生成的可执行文件位于 `dist/桌面日历.exe`。

## 自动构建（CI/CD）

每次推送到 `main` 分支或推送 `v*` 标签时，GitHub Actions 会自动：

1. 安装依赖
2. 运行全部单元测试
3. 通过 PyInstaller 构建 `.exe`
4. 上传构建产物（Artifacts 保留 30 天）
5. 推送 `v*` 标签时自动创建 GitHub Release

## 运行测试

```bash
python -m pytest tests/ -v
```

测试覆盖：
- 连续打卡天数计算（8 个用例）
- Daily Event 可见性逻辑（6 个用例）
- Daily Event 间隔规则逻辑（3 个用例）
- 日历线段拆分与槽位分配（9 个用例）

## 目录结构

```
daily_event/
├── app/              # 启动与依赖注入
│   ├── bootstrap.py  # 初始化容器、启动 UI
│   ├── container.py  # 简单 DI 容器
│   └── __main__.py   # python -m daily_event.app 入口
├── domain/           # 领域模型
│   ├── models.py     # SQLAlchemy ORM（DailyEvent, WorkEvent, Alarm...）
│   └── enums.py      # AlarmMode, AlarmStatus
├── services/         # 业务逻辑（不依赖 Qt）
│   ├── daily_event_service.py   # Daily Event CRUD + 打卡 + 连续天数 + 间隔策略
│   ├── work_event_service.py    # Work Event CRUD + 完成 + 历史
│   ├── alarm_service.py         # 闹钟创建 + 触发 + 通知
│   ├── calendar_service.py      # 日期范围 → 日历线段拆分
│   └── config_service.py        # config.json 读写
├── infra/            # 基础设施
│   ├── database.py          # SQLAlchemy engine + 自动迁移
│   ├── color_allocator.py   # Work Event 颜色分配（12 色 Fluent 调色板）
│   ├── notification.py      # 桌面通知（plyer）
│   └── sound.py             # 提示音（winsound）
└── ui/               # PySide6 界面（不含业务逻辑）
    ├── main_window.py       # 主悬浮窗 + 系统托盘
    ├── calendar_widget.py   # 自绘月历
    ├── daily_panel.py       # Daily Event 面板
    ├── daily_settings_page.py # Daily Event 设置页（间隔/删除）
    ├── work_panel.py        # Work Event 面板（含完成勾选）
    ├── alarm_page.py        # 闹钟对话框（滚轮时间选择）
    ├── wheel_picker.py      # 时间滚轮选择器组件
    ├── stats_page.py        # 累计统计对话框（含删除确认）
    ├── history_page.py      # Work Event 历史对话框（含删除）
    ├── dialogs.py           # Work Event 创建/编辑对话框
    ├── menu_panel.py        # 汉堡菜单（累计/每日事项设置/闹钟/历史）
    └── styles.py            # Fluent QSS 主题
tests/
├── test_daily_streak.py     # 连续打卡算法测试
├── test_daily_visibility.py # Daily Event 可见性测试
├── test_daily_recurrence.py # Daily Event 间隔策略测试
└── test_calendar_segments.py # 日历线段拆分测试
```

## 数据存储

- 数据库：`~/.daily_event/data.db`（SQLite，自动创建与迁移）
- 配置：`~/.daily_event/config.json`（自动创建）

## 数据库迁移

应用启动时自动检测数据库版本并执行增量迁移，无需手动操作：

| 版本 | 变更 |
|------|------|
| v1 | 初始表结构 |
| v2 | `work_events` 增加 `is_completed` 字段 |
| v3 | `work_events` 增加 `completed_at` 字段 |
| v4 | `daily_events` 增加 `recurrence_rule` 字段 |

## 配置项

| 项 | 说明 | 默认值 |
|---|---|---|
| `window.x/y/width/height` | 窗口位置与尺寸 | 100, 100, 780, 520 |
| `window.initialized` | 是否已初始化位置（首次启动自动定位右侧） | false |
| `snap_threshold` | 贴边吸附阈值（像素） | 20 |
| `sound_enabled` | 闹钟提示音开关 | true |
| `db_path` | 自定义数据库路径（留空=默认） | "" |
| `theme` | 主题（预留） | "light" |

## 扩展指南

- **新增事项类型** — 在 `domain/models.py` 添加 ORM 模型，在 `services/` 添加对应 Service，在 `ui/` 添加面板
- **更换颜色方案** — 修改 `infra/color_allocator.py` 中的 `PALETTE`
- **主题切换** — 在 `ui/styles.py` 中添加暗色主题的 QSS
- **数据库迁移** — 在 `infra/database.py` 的 `MIGRATIONS` 字典中添加 SQL 语句，并递增 `CURRENT_SCHEMA_VERSION`

## FAQ

**Q: 窗口消失了怎么找回？**
右键系统托盘图标，点击"显示窗口"。或删除 `~/.daily_event/config.json`，重启应用恢复默认位置。

**Q: 关闭窗口后程序还在运行吗？**
是的，关闭按钮只是隐藏窗口，程序会最小化到系统托盘继续运行。如需完全退出，右键托盘图标选择"退出"。

**Q: 如何自定义应用图标？**
将 `.ico` 文件放到 `resources/icon.ico`，重新打包即可。

**Q: 数据如何备份？**
复制 `~/.daily_event/data.db` 即可。

**Q: 完成的 Work Event 去哪了？**
勾选完成后会从主列表和日历上消失，可通过菜单 → "历史" 查看所有已完成事项。

**Q: Daily Event 勾选后第二天还会出现吗？**
会。Daily Event 设计为循环事项，默认每天刷新；若在“每日事项设置”中改为工作日/周末/间隔模式，则按对应频率出现。

**Q: 想让某个 Daily Event 永久不再出现怎么办？**
打开菜单 → "每日事项设置"，找到该事项点击“删除”，确认后即永久移除，不会再刷新到主界面。

**Q: 为什么之前会出现多个托盘图标？现在如何避免？**
旧版本在重复启动应用时可能出现多个实例。当前版本已启用单实例锁（`app.lock`），重复启动会直接退出，确保系统托盘始终只有一个。

## License

MIT
