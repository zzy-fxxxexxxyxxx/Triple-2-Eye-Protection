import sys
import time
import json
import os
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import win32gui
import winsound
import winreg

from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, QWidget,
                             QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QSpinBox, QDoubleSpinBox,
                             QPushButton, QStyle, QFrame, QComboBox, QCheckBox,
                             QMessageBox, QDialog, QLineEdit, QProgressBar)
from PyQt6.QtCore import QTimer, Qt

# --- 假设这些类和函数在其他文件中 ---
from reminder_window import ReminderWindow
from utils import get_resource_path
from usage_query_window import UsageLogManager, UsageQueryWindow


WM_POWERBROADCAST = 0x0218
WM_WTSSESSION_CHANGE = 0x02B1
PBT_APMSUSPEND = 0x0004
PBT_APMRESUMEAUTOMATIC = 0x0012
PBT_APMRESUMESUSPEND = 0x0007
WTS_SESSION_LOCK = 0x7
WTS_SESSION_UNLOCK = 0x8
NOTIFY_FOR_THIS_SESSION = 0


class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt", wintypes.POINT),
    ]




# -----------------------------------------


class EyeCarePro(QWidget):
    def __init__(self):
        super().__init__()
        if getattr(sys, "frozen", False):
            self.base_dir = os.path.dirname(os.path.realpath(sys.executable))
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

        self.config_path = os.path.join(self.base_dir, "eye_settings.json")
        self.app_name = "Triple2EyeProtection"
        self.usage_log_manager = UsageLogManager(self.base_dir)
        self.query_window = None

        # <<< 改进 1: 将配置加载/保存的逻辑封装，而不是直接操作变量 >>>
        # 这样做让代码更清晰，将“数据”和“状态”分离。
        self.t1_mins, self.t2_secs, self.default_delay_mins, self.remind_mode, self.fade_secs = self.load_settings()

        # 核心状态变量
        self.start_time = time.time()
        self.eye_session_start_time = self.start_time
        self.is_locked = False
        self.lock_timestamp = 0
        self.remaining_at_lock = 0  # <<< 新增 >>>: 用于更精确地恢复计时
        self.lock_true_streak = 0
        self.unlock_true_streak = 0
        self.lock_confirm_seconds = 2
        self.is_paused = False
        self.paused_remaining = self.t1_mins * 60
        self.was_paused_at_lock = False
        self.session_notification_registered = False

        # <<< 新增代码 >>>
        # 添加一个标志位，用于区分是“隐藏”还是“真正退出”
        self.is_really_quitting = False
        self.remind_win = None

        self.init_ui()
        self.init_tray()
        self.register_windows_session_notifications()

        self.core_heartbeat = QTimer()
        self.core_heartbeat.timeout.connect(self.check_system_status)
        self.core_heartbeat.start(1000)

        self.daily_flush_timer = QTimer(self)
        self.daily_flush_timer.timeout.connect(self.save_usage_snapshot)
        self.daily_flush_timer.start(24 * 60 * 60 * 1000)

        app = QApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(self.unregister_windows_session_notifications)
            app.aboutToQuit.connect(lambda: self.save_usage_snapshot(mark_offline=True))

        self.update_usage_state(force=True)
        self.update_countdown_label()

    def load_settings(self):
        """加载配置，并增加对异常情况的处理。"""
        # <<< 改进 2: 捕获具体的异常，而不是宽泛的 except: pass >>>
        # 这样可以防止程序因为未知错误而静默失败，并且更容易调试。
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 使用 .get() 提供默认值，防止 JSON 文件中缺少某个键
                    return (
                        data.get("t1", 20),
                        data.get("t2", 20),
                        max(1, min(300, int(data.get("default_delay_mins", 10)))),
                        data.get("mode", 0),
                        float(data.get("fade_secs", 1.2)),
                    )
            except (json.JSONDecodeError, IOError, TypeError, ValueError) as e:
                # 如果文件损坏或无法读取，弹窗提示用户
                QMessageBox.warning(self, "加载配置失败",
                                    f"无法读取配置文件 '{self.config_path}'。\n将使用默认设置。\n错误: {e}")
        return 20, 20, 10, 0, 1.2  # 默认值

    def save_settings(self):
        """保存配置，并处理可能发生的异常。"""
        # <<< 改进 3: 保存操作也应该有异常处理 >>>
        # 防止因磁盘已满、权限问题等导致保存失败。
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                settings_data = {
                    "t1": self.t1_mins,
                    "t2": self.t2_secs,
                    "default_delay_mins": self.default_delay_mins,
                    "mode": self.remind_mode,
                    "fade_secs": self.fade_secs
                }
                json.dump(settings_data, f, indent=4)
        except IOError as e:
            QMessageBox.critical(self, "保存配置失败", f"无法写入配置文件 '{self.config_path}'。\n错误: {e}")

    def apply_main_window_style(self):
        self.setStyleSheet("""
            QWidget#MainWindow {
                background: #EEF4F8;
                color: #142033;
                font-family: "Microsoft YaHei UI", "Segoe UI", Arial;
                font-size: 14px;
            }
            QFrame#HeroCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #0F766E, stop:0.58 #14B8A6, stop:1 #7DD3FC);
                border: 1px solid #B7E7E3;
                border-radius: 18px;
            }
            QLabel#HeroTitle {
                color: #FFFFFF;
                font-size: 23px;
                font-weight: 700;
                letter-spacing: 0px;
            }
            QLabel#HeroSubtitle {
                color: #E7FFFB;
                font-size: 12px;
            }
            QFrame#Card {
                background: #FFFFFF;
                border: 1px solid #D8E3EA;
                border-radius: 14px;
            }
            QLabel#CardTitle {
                color: #172033;
                font-size: 16px;
                font-weight: 700;
            }
            QLabel#CardSubtitle, QLabel#FieldHint {
                color: #6B7A90;
                font-size: 12px;
            }
            QLabel#FieldLabel {
                color: #314155;
                font-weight: 600;
            }
            QLabel#StatusText {
                color: #0F766E;
                font-size: 14px;
                font-weight: 700;
            }
            QLabel#CountdownText {
                color: #102033;
                font-size: 26px;
                font-weight: 800;
            }
            QLabel#StateBadge {
                border-radius: 12px;
                padding: 5px 12px;
                font-weight: 700;
            }
            QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit {
                background: #F8FBFD;
                border: 1px solid #CBD8E2;
                border-radius: 10px;
                padding: 0 12px;
                min-height: 34px;
                color: #102033;
                selection-background-color: #99F6E4;
            }
            QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QLineEdit:focus {
                border: 1px solid #14B8A6;
                background: #FFFFFF;
            }
            QComboBox::drop-down {
                border: none;
                width: 34px;
            }
            QCheckBox {
                color: #243447;
                font-weight: 600;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 6px;
                border: 1px solid #9FB0C0;
                background: #FFFFFF;
            }
            QCheckBox::indicator:checked {
                background: #14B8A6;
                border: 1px solid #14B8A6;
            }
            QProgressBar {
                background: #DBE8EF;
                border: none;
                border-radius: 7px;
                min-height: 14px;
                max-height: 14px;
                text-align: center;
            }
            QProgressBar::chunk {
                border-radius: 7px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #14B8A6, stop:1 #38BDF8);
            }
            QPushButton {
                background: #F8FBFD;
                border: 1px solid #D4DEE8;
                border-radius: 11px;
                color: #132033;
                font-weight: 700;
                min-height: 34px;
            }
            QPushButton:hover {
                background: #EDF7FA;
                border-color: #A9D8D4;
            }
            QPushButton:pressed {
                background: #DDF3F0;
            }
            QPushButton#PrimaryButton {
                background: #0F766E;
                border: 1px solid #0F766E;
                color: #FFFFFF;
            }
            QPushButton#PrimaryButton:hover {
                background: #0D9488;
            }
            QPushButton#WarningButton {
                background: #FFF2D8;
                border: 1px solid #F6C76B;
                color: #9A5A00;
            }
            QPushButton#WarningButton:hover {
                background: #FFE7B3;
            }
            QPushButton#SoftButton {
                background: #EAF6F4;
                border: 1px solid #BDE4DE;
                color: #0F766E;
            }
            QPushButton#DangerButton {
                background: #FFF1F2;
                border: 1px solid #F3B3BA;
                color: #D11D36;
            }
            QPushButton#DangerButton:hover {
                background: #FFE4E7;
            }
        """)

    def create_card(self, title, subtitle=None):
        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 16, 18, 16)
        card_layout.setSpacing(12)

        title_label = QLabel(title)
        title_label.setObjectName("CardTitle")
        card_layout.addWidget(title_label)

        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setObjectName("CardSubtitle")
            card_layout.addWidget(subtitle_label)

        return card, card_layout

    def create_compact_field(self, text, widget):
        field = QWidget()
        field_layout = QVBoxLayout(field)
        field_layout.setContentsMargins(0, 0, 0, 0)
        field_layout.setSpacing(5)

        label = QLabel(text)
        label.setObjectName("FieldLabel")
        widget.setFixedHeight(36)
        field_layout.addWidget(label)
        field_layout.addWidget(widget)
        return field

    def get_standard_icon(self, name, fallback="SP_FileIcon"):
        pixmap = getattr(QStyle.StandardPixmap, name, getattr(QStyle.StandardPixmap, fallback))
        return self.style().standardIcon(pixmap)

    def create_action_button(self, text, object_name="SecondaryButton", height=40, icon_name=None):
        button = QPushButton(text)
        button.setObjectName(object_name)
        button.setFixedHeight(height)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        if icon_name:
            button.setIcon(self.get_standard_icon(icon_name))
            button.setIconSize(button.iconSize())
        return button

    def update_pause_button_visual(self):
        if not hasattr(self, "btn_pause_resume"):
            return
        self.btn_pause_resume.setText("继续" if self.is_paused else "暂停")
        icon_name = "SP_MediaPlay" if self.is_paused else "SP_MediaPause"
        self.btn_pause_resume.setIcon(self.get_standard_icon(icon_name))

    def set_status_visual_state(self, color):
        color_map = {
            "green": ("计时中", "#DDF7EF", "#0F766E"),
            "orange": ("注意", "#FFF2D8", "#A35B00"),
            "blue": ("暂停", "#E7F0FF", "#2563EB"),
            "red": ("警示", "#FFE4E7", "#D11D36"),
        }
        badge_text, badge_bg, badge_fg = color_map.get(color, color_map["green"])
        status_color = badge_fg
        if hasattr(self, "lbl_state_badge"):
            self.lbl_state_badge.setText(badge_text)
            self.lbl_state_badge.setStyleSheet(
                f"background: {badge_bg}; color: {badge_fg}; border-radius: 12px; padding: 5px 12px; font-weight: 700;"
            )
        if hasattr(self, "lbl_status"):
            self.lbl_status.setStyleSheet(f"color: {status_color}; font-size: 14px; font-weight: 700;")

    def restore_running_status(self):
        self.lbl_status.setText("状态: 正在计时...")
        self.set_status_visual_state("green")

    def update_countdown_display(self, remaining_seconds=None):
        if remaining_seconds is None:
            self.lbl_countdown.setText("剩余提醒时间: --:--")
            if hasattr(self, "countdown_progress"):
                self.countdown_progress.setValue(0)
            return

        rem = max(0, int(remaining_seconds))
        self.lbl_countdown.setText(f"剩余提醒时间: {self.format_countdown(rem)}")
        if hasattr(self, "countdown_progress"):
            total = max(1, int(self.t1_mins * 60))
            progress_value = int(max(0.0, min(1.0, rem / total)) * 1000)
            self.countdown_progress.setValue(progress_value)

    def init_ui(self):
        self.set_app_icon()
        self.setWindowTitle("Triple 2 Eye Protection - settings")
        self.setFixedSize(430, 740)
        self.setObjectName("MainWindow")
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.apply_main_window_style()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        hero = QFrame()
        hero.setObjectName("HeroCard")
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(18, 14, 18, 14)
        hero_layout.setSpacing(14)

        icon_label = QLabel()
        icon_label.setPixmap(self.app_icon.pixmap(42, 42))
        icon_label.setFixedSize(46, 46)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hero_layout.addWidget(icon_label)

        hero_text_layout = QVBoxLayout()
        hero_text_layout.setSpacing(3)
        hero_title = QLabel("Triple 2")
        hero_title.setObjectName("HeroTitle")
        hero_subtitle = QLabel("Eye Protection · 护眼计时控制台")
        hero_subtitle.setObjectName("HeroSubtitle")
        hero_text_layout.addWidget(hero_title)
        hero_text_layout.addWidget(hero_subtitle)
        hero_layout.addLayout(hero_text_layout, 1)
        layout.addWidget(hero)

        settings_card, settings_layout = self.create_card("参数配置")
        settings_layout.setSpacing(10)

        self.input_t1 = QSpinBox()
        self.input_t1.setRange(1, 300)
        self.input_t1.setValue(self.t1_mins)

        self.input_default_delay = QSpinBox()
        self.input_default_delay.setRange(1, 300)
        self.input_default_delay.setValue(self.default_delay_mins)
        self.input_default_delay.setToolTip("休息提醒弹窗中的默认延时时长；弹窗内临时修改不会影响这里。")

        self.input_t2 = QSpinBox()
        self.input_t2.setRange(5, 6000)
        self.input_t2.setValue(self.t2_secs)

        self.input_fade = QDoubleSpinBox()
        self.input_fade.setRange(0.0, 10.0)
        self.input_fade.setDecimals(3)
        self.input_fade.setSingleStep(0.1)
        self.input_fade.setValue(self.fade_secs)
        self.input_fade.setToolTip("休息提醒窗口从透明到完全显示的线性淡入时间，支持毫秒级小数。")

        settings_grid = QGridLayout()
        settings_grid.setContentsMargins(0, 0, 0, 0)
        settings_grid.setHorizontalSpacing(14)
        settings_grid.setVerticalSpacing(8)
        settings_grid.addWidget(self.create_compact_field("用眼时长 (min)", self.input_t1), 0, 0)
        settings_grid.addWidget(self.create_compact_field("默认延时 (min)", self.input_default_delay), 0, 1)
        settings_grid.addWidget(self.create_compact_field("远望时长 (sec)", self.input_t2), 1, 0)
        settings_grid.addWidget(self.create_compact_field("过渡时间 (s)", self.input_fade), 1, 1)
        settings_layout.addLayout(settings_grid)

        mode_row = QHBoxLayout()
        mode_row.setSpacing(12)
        mode_label = QLabel("提醒方式")
        mode_label.setObjectName("FieldLabel")
        mode_label.setMinimumWidth(78)
        self.combo_mode = QComboBox()
        self.combo_mode.addItems(["仅弹窗(静音)", "铃声+弹窗", "闪烁+弹窗（静音）", "铃声+闪烁+弹窗"])
        self.combo_mode.setCurrentIndex(self.remind_mode)
        self.combo_mode.setFixedHeight(36)
        mode_row.addWidget(mode_label)
        mode_row.addWidget(self.combo_mode, 1)
        settings_layout.addLayout(mode_row)

        self.check_autostart = QCheckBox("开机自动启动")
        self.check_autostart.setChecked(self.is_autostart_enabled())
        settings_layout.addWidget(self.check_autostart)
        layout.addWidget(settings_card)

        self.input_t1.editingFinished.connect(self.on_parameter_committed)
        self.input_default_delay.editingFinished.connect(self.on_parameter_committed)
        self.input_t2.editingFinished.connect(self.on_parameter_committed)
        self.input_fade.editingFinished.connect(self.on_parameter_committed)
        self.combo_mode.currentIndexChanged.connect(self.on_parameter_committed)
        self.check_autostart.stateChanged.connect(self.toggle_autostart)

        control_card, control_layout = self.create_card("当前状态")
        control_layout.setSpacing(10)
        status_header = QHBoxLayout()
        status_header.setSpacing(10)
        self.lbl_status = QLabel("状态: 正在计时...")
        self.lbl_status.setObjectName("StatusText")
        status_header.addWidget(self.lbl_status, 1)
        self.lbl_state_badge = QLabel("计时中")
        self.lbl_state_badge.setObjectName("StateBadge")
        self.lbl_state_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_header.addWidget(self.lbl_state_badge)
        control_layout.addLayout(status_header)

        self.lbl_countdown = QLabel("剩余提醒时间: --:--")
        self.lbl_countdown.setObjectName("CountdownText")
        self.lbl_countdown.setAlignment(Qt.AlignmentFlag.AlignCenter)
        control_layout.addWidget(self.lbl_countdown)

        self.countdown_progress = QProgressBar()
        self.countdown_progress.setRange(0, 1000)
        self.countdown_progress.setTextVisible(False)
        control_layout.addWidget(self.countdown_progress)
        self.set_status_visual_state("green")

        action_row_1 = QHBoxLayout()
        action_row_1.setSpacing(12)
        self.btn_pause_resume = self.create_action_button("暂停", height=38, icon_name="SP_MediaPause")
        self.btn_pause_resume.clicked.connect(self.toggle_pause_resume)
        action_row_1.addWidget(self.btn_pause_resume)

        btn_reset = self.create_action_button("重置", height=38, icon_name="SP_BrowserReload")
        btn_reset.clicked.connect(self.reset_countdown)
        action_row_1.addWidget(btn_reset)
        control_layout.addLayout(action_row_1)

        action_row_2 = QHBoxLayout()
        action_row_2.setSpacing(12)
        btn_start_rest_now = self.create_action_button("开始休息", "PrimaryButton", 38, "SP_DialogApplyButton")
        btn_start_rest_now.clicked.connect(self.start_rest_now)
        action_row_2.addWidget(btn_start_rest_now)

        btn_delay = self.create_action_button("延时", "WarningButton", 38, "SP_MessageBoxWarning")
        btn_delay.clicked.connect(self.show_delay_dialog)
        action_row_2.addWidget(btn_delay)
        control_layout.addLayout(action_row_2)

        action_row_3 = QHBoxLayout()
        action_row_3.setSpacing(12)
        btn_query = self.create_action_button("查询记录", height=38, icon_name="SP_FileDialogDetailedView")
        btn_query.clicked.connect(self.open_query_window)
        action_row_3.addWidget(btn_query)

        btn_hide = self.create_action_button("后台运行", "SoftButton", 38, "SP_TitleBarMinButton")
        btn_hide.clicked.connect(self.hide_to_tray)
        action_row_3.addWidget(btn_hide)
        control_layout.addLayout(action_row_3)

        btn_quit = self.create_action_button("彻底退出程序", "DangerButton", 38, "SP_DialogCloseButton")
        btn_quit.clicked.connect(self.confirm_quit)
        control_layout.addWidget(btn_quit)
        layout.addWidget(control_card)

        self.update_countdown_label()
    def set_app_icon(self):
        icon_path = get_resource_path("eye_icon.ico")
        if os.path.exists(icon_path):
            self.app_icon = QIcon(icon_path)
        else:
            # 如果图标不存在，使用系统内置的标准图标
            self.app_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.setWindowIcon(self.app_icon)

    def is_autostart_enabled(self):
        run_exists = False
        try:
            # 打开注册表键
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0,
                                 winreg.KEY_READ)
            # 查询值，如果存在则返回 True
            winreg.QueryValueEx(key, self.app_name)
            winreg.CloseKey(key)
            run_exists = True
        except FileNotFoundError:
            # <<< 改进 6: 明确捕获 FileNotFoundError >>>
            # 这是最常见的“不存在”异常，让逻辑更清晰。
            return False
        except Exception:
            # 其他异常也返回False，确保程序不会因此崩溃
            return False

        if not run_exists:
            return False

        approved_state = self.get_startup_approved_state()
        # 缺失时按启用处理（部分系统不会立即创建该值）
        if approved_state is None:
            return True

        # Windows StartupApproved 常见状态：
        # 02=启用；03/07=禁用（不同系统版本会有细微差异）。
        if approved_state in (0x02, 0x06):
            return True
        if approved_state in (0x03, 0x07):
            return False

        # 未知状态优先相信 Run 存在，避免 UI 与系统开关反复打架。
        return True

    def toggle_autostart(self, state):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE)
            # <<< 改进 7: 使用 Qt.CheckState.Checked.value，而不是硬编码的 `2` >>>
            # 这让代码更具可读性，并且不会因为Qt版本更新而失效。
            if state == Qt.CheckState.Checked.value:
                startup_cmd = self.build_autostart_command()
                winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, startup_cmd)
                self.set_startup_approved_enabled(True)
            else:
                try:
                    winreg.DeleteValue(key, self.app_name)
                except FileNotFoundError:
                    pass  # 如果值本就不存在，则忽略
                self.delete_startup_approved_value()
            winreg.CloseKey(key)
        except Exception as e:
            QMessageBox.critical(self, "操作失败", f"无法修改开机自启动项: \n{str(e)}")

    def refresh_autostart_checkbox(self):
        current_enabled = self.is_autostart_enabled()
        self.check_autostart.blockSignals(True)
        self.check_autostart.setChecked(current_enabled)
        self.check_autostart.blockSignals(False)

    def get_startup_approved_state(self):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, self.app_name)
            winreg.CloseKey(key)
            if isinstance(value, bytes) and len(value) > 0:
                return value[0]
        except FileNotFoundError:
            return None
        except Exception:
            return None
        return None

    def set_startup_approved_enabled(self, enabled):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
            # 12 字节结构：4字节状态码 + 8字节 FILETIME。
            state_code = 0x02 if enabled else 0x03
            payload = self.build_startup_approved_payload(state_code)
            winreg.SetValueEx(key, self.app_name, 0, winreg.REG_BINARY, payload)
            winreg.CloseKey(key)
        except Exception:
            # 启动批准状态写失败不应阻塞主流程
            pass

    def delete_startup_approved_value(self):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE)
            try:
                winreg.DeleteValue(key, self.app_name)
            except FileNotFoundError:
                pass
            winreg.CloseKey(key)
        except Exception:
            pass

    def build_startup_approved_payload(self, state_code):
        # FILETIME: since 1601-01-01 UTC, unit 100ns
        unix_ts = datetime.now(timezone.utc).timestamp()
        filetime = int((unix_ts + 11644473600) * 10_000_000)
        return bytes([state_code, 0, 0, 0]) + filetime.to_bytes(8, byteorder="little", signed=False)

    def build_autostart_command(self):
        """
        生成开机自启动命令：
        - 打包后运行：写入 exe 路径
        - 源码运行：写入 pythonw.exe + main.pyw 路径
        """
        # PyInstaller/Nuitka 等打包运行场景
        if getattr(sys, "frozen", False):
            exe_path = os.path.realpath(sys.executable)
            return f'"{exe_path}"'

        # 源码运行场景：优先使用 pythonw.exe，避免开机弹出终端窗口
        python_exe = os.path.realpath(sys.executable)
        python_dir = os.path.dirname(python_exe)
        pythonw_path = os.path.join(python_dir, "pythonw.exe")
        interpreter = pythonw_path if os.path.exists(pythonw_path) else python_exe

        project_dir = os.path.dirname(os.path.abspath(__file__))
        entry_script = os.path.join(project_dir, "main.pyw")
        if not os.path.exists(entry_script):
            # 兜底：如果 main.pyw 不存在则尝试 main.py
            entry_script = os.path.join(project_dir, "main.py")

        return f'"{interpreter}" "{entry_script}"'

    def on_parameter_committed(self):
        new_t1 = self.input_t1.value()
        new_default_delay = self.input_default_delay.value()
        new_t2 = self.input_t2.value()
        new_fade = round(self.input_fade.value(), 3)
        new_mode = self.combo_mode.currentIndex()

        has_changed = (
            new_t1 != self.t1_mins
            or new_default_delay != self.default_delay_mins
            or new_t2 != self.t2_secs
            or new_mode != self.remind_mode
            or new_fade != self.fade_secs
        )
        if has_changed:
            t1_was_changed = (new_t1 != self.t1_mins)

            self.t1_mins = new_t1
            self.default_delay_mins = new_default_delay
            self.t2_secs = new_t2
            self.fade_secs = new_fade
            self.remind_mode = new_mode
            self.save_settings()  # 调用封装好的保存方法

            if t1_was_changed:
                self.start_time = time.time()
                self.eye_session_start_time = self.start_time
                self.is_paused = False
                self.paused_remaining = self.t1_mins * 60
                self.update_pause_button_visual()
                self.set_status_message("用眼时长已改，重置计时", "orange", 3000)
            else:
                self.set_status_message("参数已更新", "green", 2000)

            self.update_countdown_label()

    def open_query_window(self):
        if self.query_window is None:
            self.query_window = UsageQueryWindow(self.usage_log_manager)
        self.query_window.refresh()
        self.query_window.show()
        self.query_window.raise_()
        self.query_window.activateWindow()

    def set_status_message(self, text, color, duration):
        """显示状态信息，并在需要时恢复到默认计时状态。"""
        self.lbl_status.setText(f"状态: {text}")
        self.set_status_visual_state(color)
        if duration and duration > 0:
            QTimer.singleShot(duration, self.restore_running_status)

    def register_windows_session_notifications(self):
        try:
            hwnd = int(self.winId())
            result = ctypes.windll.wtsapi32.WTSRegisterSessionNotification(hwnd, NOTIFY_FOR_THIS_SESSION)
            self.session_notification_registered = bool(result)
        except Exception:
            self.session_notification_registered = False

    def unregister_windows_session_notifications(self):
        if not self.session_notification_registered:
            return
        try:
            ctypes.windll.wtsapi32.WTSUnRegisterSessionNotification(int(self.winId()))
        except Exception:
            pass
        self.session_notification_registered = False

    def get_remaining_seconds(self):
        if self.is_paused:
            return max(0, int(self.paused_remaining))
        elapsed = time.time() - self.start_time
        return max(0, int(self.t1_mins * 60 - elapsed))

    def format_countdown(self, seconds):
        seconds = max(0, int(seconds))
        return f"{seconds // 60:02d}:{seconds % 60:02d}"

    def enter_inactive_period(self, reason):
        if self.is_locked:
            return

        self.is_locked = True
        self.lock_timestamp = time.time()
        self.was_paused_at_lock = self.is_paused
        self.remaining_at_lock = self.get_remaining_seconds()
        self.set_status_message(reason, "blue", 0)
        self.update_countdown_display(None)
        self.update_tray_status()
        self.update_usage_state(force=True)
        self.usage_log_manager.flush()

    def leave_inactive_period(self, reason):
        if not self.is_locked:
            return

        self.is_locked = False
        lock_duration = time.time() - self.lock_timestamp

        if lock_duration > self.t2_secs:
            self.start_time = time.time()
            self.eye_session_start_time = self.start_time
            self.is_paused = False
            self.paused_remaining = self.t1_mins * 60
            self.update_pause_button_visual()
            self.set_status_message(f"{reason}，休息达标({int(lock_duration)}s)，重置计时", "green", 3000)
        else:
            if self.was_paused_at_lock:
                self.is_paused = True
                self.paused_remaining = max(0, int(self.remaining_at_lock))
                self.update_pause_button_visual()
                self.set_status_message(f"{reason}，恢复暂停状态", "orange", 2000)
            else:
                self.is_paused = False
                self.start_time = time.time() - ((self.t1_mins * 60) - self.remaining_at_lock)
                self.update_pause_button_visual()
                self.set_status_message(f"{reason}，计时继续", "green", 2000)

        self.update_countdown_label()
        self.update_usage_state(force=True)

    def nativeEvent(self, event_type, message):
        try:
            msg = MSG.from_address(int(message))
        except Exception:
            return False, 0

        if msg.message == WM_WTSSESSION_CHANGE:
            if msg.wParam == WTS_SESSION_LOCK:
                self.enter_inactive_period("屏幕已锁定，暂停计时")
            elif msg.wParam == WTS_SESSION_UNLOCK:
                self.leave_inactive_period("屏幕已解锁")

        elif msg.message == WM_POWERBROADCAST:
            if msg.wParam == PBT_APMSUSPEND:
                self.enter_inactive_period("系统即将休眠，暂停计时")
            elif msg.wParam in (PBT_APMRESUMEAUTOMATIC, PBT_APMRESUMESUSPEND):
                self.leave_inactive_period("系统已唤醒")

        return False, 0

    def init_tray(self):
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.app_icon)
        self.tray.setToolTip("护眼程序正在后台运行")

        menu = QMenu()
        self.tray_status_action = QAction("用眼中: --:--", self)
        self.tray_status_action.setEnabled(False)
        menu.addAction(self.tray_status_action)
        menu.addSeparator()
        menu.addAction("显示设置").triggered.connect(self.show_main_window)
        self.tray_pause_action = menu.addAction("暂停")
        self.tray_pause_action.triggered.connect(self.toggle_pause_resume)
        self.tray_reset_action = menu.addAction("重置")
        self.tray_reset_action.triggered.connect(self.reset_countdown)
        self.tray_rest_action = menu.addAction("立即休息")
        self.tray_rest_action.triggered.connect(self.start_rest_now)
        menu.addSeparator()
        # <<< 改进 5 (对应): 菜单中的退出也调用带确认的方法 >>>
        menu.addAction("退出程序").triggered.connect(self.confirm_quit)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(
            lambda reason: self.show_main_window() if reason == QSystemTrayIcon.ActivationReason.DoubleClick else None)
        self.tray.show()
        self.update_tray_status()

    def show_main_window(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def update_tray_status(self):
        if not hasattr(self, "tray"):
            return

        reminder = self.get_visible_reminder_window()
        if reminder is not None:
            if getattr(reminder, "is_resting", False):
                status_text = f"休息中: {getattr(reminder, 'rest_seconds', 0)}秒"
            else:
                status_text = f"已提醒: {getattr(reminder, 'overtime_seconds', 0)}秒"
        elif self.is_locked:
            status_text = "屏幕锁定/休眠中"
        elif self.is_paused:
            status_text = f"暂停中: {self.format_countdown(self.get_remaining_seconds())}"
        else:
            status_text = f"用眼中: {self.format_countdown(self.get_remaining_seconds())}"

        self.tray.setToolTip(status_text)
        if hasattr(self, "tray_status_action"):
            self.tray_status_action.setText(status_text)
        if hasattr(self, "tray_pause_action"):
            self.tray_pause_action.setText("继续" if self.is_paused else "暂停")

    def trigger_alert(self):
        self.show_reminder_window(start_resting=False, with_alert=True)

    def get_eye_usage_seconds(self):
        return max(0, int(time.time() - self.eye_session_start_time))

    def get_visible_reminder_window(self):
        """Return the current visible reminder window, clearing stale Qt wrappers."""
        reminder = self.remind_win
        if reminder is None:
            return None

        try:
            if reminder.isVisible():
                return reminder
        except RuntimeError:
            # Qt may already have deleted the C++ object while Python still has
            # a wrapper reference.
            self.remind_win = None

        return None

    def show_reminder_window(self, start_resting=False, with_alert=True):
        reminder = self.get_visible_reminder_window()
        if reminder is not None:
            reminder.activateWindow()
            reminder.raise_()
            if start_resting and hasattr(reminder, "on_start_rest"):
                reminder.on_start_rest()
                self.update_usage_state(force=True)
            return

        self.is_paused = False
        self.update_pause_button_visual()

        if with_alert:
            if self.remind_mode in [1, 3]:  # 铃声
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            if self.remind_mode in [2, 3]:  # 闪烁
                QApplication.alert(self, 3000)

        reminder = ReminderWindow(
            self.t2_secs,
            self.fade_secs,
            self.get_eye_usage_seconds(),
            self.default_delay_mins,
        )
        reminder.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        reminder.rest_finished.connect(lambda win=reminder: self.restart_after_rest(win))
        reminder.destroyed.connect(lambda _obj=None, win=reminder: self.restart_after_rest(win))
        reminder.rest_started.connect(lambda: self.update_usage_state(force=True))
        reminder.delay_requested.connect(lambda delay_mins, win=reminder: self.delay_after_reminder(delay_mins, win))

        self.remind_win = reminder
        reminder.show()
        if start_resting and hasattr(reminder, "start_rest_immediately"):
            reminder.start_rest_immediately()
        self.update_usage_state(force=True)
        self.update_tray_status()

    def delay_after_reminder(self, delay_mins, reminder=None):
        if reminder is not None and self.remind_win is not reminder:
            return

        delay_mins = max(1, min(300, int(delay_mins)))
        delay_seconds = delay_mins * 60
        now = time.time()

        # Keep eye_session_start_time untouched so the next popup can show the
        # full eye-use duration since the last real rest/reset.
        self.start_time = now - ((self.t1_mins * 60) - delay_seconds)
        self.is_paused = False
        self.paused_remaining = delay_seconds
        self.update_pause_button_visual()
        self.remind_win = None
        self.update_countdown_label()
        self.set_status_message(f"已延时 {delay_mins} 分钟", "orange", 3000)
        self.update_usage_state(force=True)
        self.update_tray_status()

    def restart_after_rest(self, reminder=None):
        if reminder is not None and self.remind_win is not reminder:
            return

        self.start_time = time.time()
        self.eye_session_start_time = self.start_time
        self.is_paused = False
        self.paused_remaining = self.t1_mins * 60
        self.update_pause_button_visual()
        # 清理对窗口的引用
        self.remind_win = None
        self.update_tray_status()
        self.update_usage_state(force=True)

    def toggle_pause_resume(self):
        if self.get_visible_reminder_window() is not None:
            self.set_status_message("休息弹窗进行中，无法暂停", "orange", 2000)
            return

        if not self.is_paused:
            elapsed = time.time() - self.start_time
            self.paused_remaining = max(0, int(self.t1_mins * 60 - elapsed))
            self.is_paused = True
            self.update_pause_button_visual()
            self.update_countdown_display(self.paused_remaining)
            self.set_status_message("计时已暂停", "orange", 0)
        else:
            self.start_time = time.time() - ((self.t1_mins * 60) - self.paused_remaining)
            self.is_paused = False
            self.update_pause_button_visual()
            self.set_status_message("计时已继续", "green", 1500)
        self.update_tray_status()

    def reset_countdown(self):
        if self.get_visible_reminder_window() is not None:
            self.set_status_message("休息弹窗进行中，无法重置", "orange", 2000)
            return

        self.start_time = time.time()
        self.eye_session_start_time = self.start_time
        self.paused_remaining = self.t1_mins * 60
        self.is_paused = False
        self.update_pause_button_visual()
        self.update_countdown_label()
        self.set_status_message("倒计时已重置", "green", 2000)

    def start_rest_now(self):
        self.show_reminder_window(start_resting=True, with_alert=False)
        self.set_status_message("已手动开始休息", "blue", 2000)

    def show_delay_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("延时调整")
        dialog.setFixedSize(320, 160)

        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("请输入要调整的秒数（可正可负）:"))

        input_delay = QLineEdit(dialog)
        input_delay.setPlaceholderText("例如: 120 或 -60")
        layout.addWidget(input_delay)

        button_row = QHBoxLayout()
        btn_apply = QPushButton("Apply")
        btn_cancel = QPushButton("Cancel")
        button_row.addWidget(btn_apply)
        button_row.addWidget(btn_cancel)
        layout.addLayout(button_row)

        btn_cancel.clicked.connect(dialog.reject)

        def apply_delay():
            raw_text = input_delay.text().strip()
            if not raw_text:
                QMessageBox.warning(self, "输入无效", "请输入一个整数秒数。")
                return

            try:
                delta_seconds = int(raw_text)
            except ValueError:
                QMessageBox.warning(self, "输入无效", "请输入一个整数秒数，例如 120 或 -60。")
                return

            if delta_seconds == 0:
                dialog.accept()
                return

            if self.get_visible_reminder_window() is not None:
                QMessageBox.information(self, "当前不可调整", "休息弹窗进行中，不能调整用眼倒计时。")
                return

            if self.is_paused:
                self.paused_remaining += delta_seconds
                new_remaining = self.paused_remaining
            else:
                self.start_time += delta_seconds
                elapsed = time.time() - self.start_time
                new_remaining = int(self.t1_mins * 60 - elapsed)

            if new_remaining <= 0:
                dialog.accept()
                self.show_reminder_window(start_resting=True, with_alert=True)
                return

            if self.is_paused:
                self.paused_remaining = new_remaining

            self.update_countdown_label()
            change_text = f"已增加 {delta_seconds} 秒" if delta_seconds > 0 else f"已减少 {abs(delta_seconds)} 秒"
            self.set_status_message(change_text, "green", 2000)
            dialog.accept()

        btn_apply.clicked.connect(apply_delay)
        dialog.exec()

    def get_current_usage_state(self):
        reminder = self.get_visible_reminder_window()
        if reminder is not None:
            if getattr(reminder, "is_resting", False):
                return 0.0
            return 0.3
        if self.is_locked:
            return -1.0
        return 1.0

    def update_usage_state(self, force=False):
        state_value = self.get_current_usage_state()
        self.usage_log_manager.record_state(state_value, force=force)

    def save_usage_snapshot(self, mark_offline=False):
        if mark_offline:
            self.usage_log_manager.record_state(-1.0, force=True)
        else:
            self.update_usage_state(force=True)
        self.usage_log_manager.flush()

    def update_countdown_label(self):
        rem = self.get_remaining_seconds()
        self.update_countdown_display(rem)
        self.update_tray_status()
    def check_system_status(self):
        curr_locked = win32gui.GetForegroundWindow() == 0

        if curr_locked:
            self.lock_true_streak += 1
            self.unlock_true_streak = 0
        else:
            self.unlock_true_streak += 1
            self.lock_true_streak = 0

        if (not self.is_locked) and self.lock_true_streak >= self.lock_confirm_seconds:
            # 会话事件不可用时的兜底判断。
            self.enter_inactive_period("屏幕疑似锁定，暂停计时")

        elif self.is_locked and self.unlock_true_streak >= self.lock_confirm_seconds:
            self.leave_inactive_period("屏幕恢复")

        if self.get_visible_reminder_window() is not None:
            self.update_usage_state()
            self.update_tray_status()
            return

        if self.is_paused and not self.is_locked:
            self.update_countdown_label()
            self.update_usage_state()
            return

        # 只有在非锁屏状态下才更新倒计时
        if not self.is_locked:
            elapsed = time.time() - self.start_time
            rem = max(0, int(self.t1_mins * 60 - elapsed))
            self.update_countdown_display(rem)
            if elapsed >= (self.t1_mins * 60):
                self.trigger_alert()

        self.update_usage_state()
        self.update_tray_status()

    def mousePressEvent(self, event):
        # 点击窗口空白处时，让输入框失去焦点，以触发 editingFinished 信号
        focused_widget = QApplication.focusWidget()
        if isinstance(focused_widget, (QSpinBox, QComboBox)):
            focused_widget.clearFocus()
        super().mousePressEvent(event)

    def showEvent(self, event):
        self.refresh_autostart_checkbox()
        super().showEvent(event)

    # <<< 新增方法 >>>
    def hide_to_tray(self):
        """
        一个专门的方法，用于将窗口隐藏到系统托盘并显示提示消息。
        """
        self.hide()  # 隐藏窗口
        self.tray.showMessage(
            "程序已在后台运行",
            "我将继续守护您的双眼。",
            self.app_icon,
            2000  # 消息显示 2 秒
        )

    def confirm_quit(self):
        """弹出一个确认对话框，询问用户是否真的要退出。"""
        reply = QMessageBox.question(self, '确认退出',
                                     '您确定要彻底退出护眼程序吗？',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)  # 默认选中 "No"

        if reply == QMessageBox.StandardButton.Yes:
            # <<< 新增这行 >>>
            # 在真正退出前，设置标志位
            self.is_really_quitting = True
            QApplication.instance().quit()

    def closeEvent(self, event):
        """
        重写窗口关闭事件。
        根据 is_really_quitting 标志位来判断是真正退出还是隐藏到托盘。
        """
        # 如果标志位为True（意味着是点击了“彻底退出程序”）
        if self.is_really_quitting:
            self.unregister_windows_session_notifications()
            self.save_usage_snapshot(mark_offline=True)
            # 接受关闭事件，让程序正常退出
            event.accept()
        # 否则（意味着是点击了右上角的'X'）
        else:
            # 忽略关闭事件，防止程序退出
            event.ignore()
            # 调用我们封装好的“隐藏到托盘”方法
            self.hide_to_tray()
