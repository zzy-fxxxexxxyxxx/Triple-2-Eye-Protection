import sys
import os
import time

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QFrame, QSpinBox)
from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QTimer, Qt, pyqtSignal


class ReminderWindow(QWidget):
    rest_started = pyqtSignal()
    rest_finished = pyqtSignal()
    delay_requested = pyqtSignal(int)

    def __init__(self, t2_secs, fade_secs=1.2, eye_usage_seconds=0, default_delay_mins=10):
        super().__init__()
        # 计时变量
        self.overtime_seconds = 0
        self.rest_seconds = 0
        self.is_resting = False
        self.target_rest = t2_secs
        self.fade_secs = max(0.0, min(10.0, float(fade_secs)))
        self.fade_animation = None
        self.eye_usage_base_seconds = max(0, int(eye_usage_seconds))
        self.eye_usage_started_at = time.time()
        self.eye_usage_frozen_seconds = None
        self.default_delay_mins = max(1, min(300, int(default_delay_mins)))

        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(0.0 if self.fade_secs > 0 else 1.0)
        self.setFixedSize(430, 380)

        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

        container = QFrame(self)
        container.setObjectName("MainFrame")
        container.setFixedSize(430, 380)
        container.setStyleSheet("""
            #MainFrame {
                background-color: #F0FFF0;
                border: 3px solid #2D8A4E;
                border-radius: 10px;
            }
            QLabel {
                color: #2D4A3E;
                font-family: 'Microsoft YaHei';
            }
            QPushButton {
                background-color: #2D8A4E;
                color: white;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #1E5F35;
            }
            QPushButton:disabled {
                background-color: transparent;
                border: 2px dashed #2D8A4E;
                color: #2D8A4E;
            }
        """)
        layout = QVBoxLayout(container)
        # 1. 创建图标
        icon_label = QLabel("!")
        icon_label.setFixedSize(60, 60)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("""
            background-color: #2D8A4E;
            color: white;
            border-radius: 30px; /* 圆形 */
            font-weight: bold;
            font-size: 36px;
        """)
        # 2. 将其居中加入布局
        # 使用 alignment 参数确保它不靠左
        layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        # 3. 如果你的“放松时间到”标签也靠左，记得也加一个参数：
        # title_label = QLabel("放松时间到")
        # layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        # 2. 标题
        title = QLabel("放松时间到")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        # 3. 核心内容与倒计时
        self.content = QLabel(f"请离开屏幕，向 6 米外远眺\n建议休息时长：{t2_secs} 秒")
        self.content.setStyleSheet("font-size: 15px;")
        self.content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.content)
        # 新增：已超时计时显示
        self.lbl_overtime = QLabel("已提醒：0秒")
        self.lbl_overtime.setStyleSheet("color: #13A990; font-weight: bold;")
        self.lbl_overtime.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_overtime)
        self.lbl_eye_usage = QLabel(f"已用眼：{self.format_time(self.eye_usage_base_seconds)}")
        self.lbl_eye_usage.setStyleSheet("color: #C65F22; font-weight: bold;")
        self.lbl_eye_usage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_eye_usage)
        # 4. 按钮布局
        v_box = QVBoxLayout()
        v_box.setSpacing(10)
        self.input_delay_mins = QSpinBox()
        self.input_delay_mins.setRange(1, 300)
        self.input_delay_mins.setValue(self.default_delay_mins)
        self.input_delay_mins.setSuffix(" 分钟")
        self.input_delay_mins.setFixedSize(110, 36)
        self.input_delay_mins.valueChanged.connect(self.update_delay_button_text)

        self.btn_delay = QPushButton()
        self.btn_delay.setFixedSize(150, 40)
        self.btn_delay.clicked.connect(self.on_delay_requested)
        self.update_delay_button_text(self.default_delay_mins)

        delay_row = QHBoxLayout()
        delay_row.setSpacing(8)
        delay_row.addStretch()
        delay_row.addWidget(self.input_delay_mins)
        delay_row.addWidget(self.btn_delay)
        delay_row.addStretch()

        # 新增：开始休息按钮
        self.btn_start_rest = QPushButton("开始休息")
        self.btn_start_rest.setFixedSize(140, 40)
        self.btn_start_rest.clicked.connect(self.on_start_rest)
        # layout.addWidget(self.btn_start_rest)

        self.btn_done = QPushButton("休息好了")
        self.btn_done.setFixedSize(140, 40)
        self.btn_done.clicked.connect(self.on_rest_done)
        # layout.addWidget(self.btn_done)

        v_box.addStretch()
        v_box.addLayout(delay_row)
        v_box.addWidget(self.btn_start_rest, alignment=Qt.AlignmentFlag.AlignCenter)
        v_box.addWidget(self.btn_done, alignment=Qt.AlignmentFlag.AlignCenter)
        v_box.addStretch()
        layout.addLayout(v_box)
        # 启动定时器，每秒刷新
        self.display_timer = QTimer(self)
        self.display_timer.timeout.connect(self.tick)
        self.display_timer.start(1000)

    def showEvent(self, event):
        super().showEvent(event)
        if self.fade_secs <= 0:
            self.setWindowOpacity(1.0)
            return

        self.fade_animation = QPropertyAnimation(self, b"windowOpacity", self)
        self.fade_animation.setDuration(int(self.fade_secs * 1000))
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.Linear)
        self.fade_animation.start()

    def format_time(self, seconds):
        """将秒转换为分秒格式"""
        if seconds < 60:
            return f"{seconds}秒"
        else:
            m, s = divmod(seconds, 60)
            return f"{m}分{s}秒"

    def get_current_eye_usage_seconds(self):
        if self.eye_usage_frozen_seconds is not None:
            return self.eye_usage_frozen_seconds
        return self.eye_usage_base_seconds + max(0, int(time.time() - self.eye_usage_started_at))

    def update_eye_usage_label(self):
        self.lbl_eye_usage.setText(f"已用眼：{self.format_time(self.get_current_eye_usage_seconds())}")

    def update_delay_button_text(self, value):
        self.btn_delay.setText(f"延时：{int(value)}分钟")

    def tick(self):
        """每秒执行逻辑"""
        # 更新总超时时间
        self.overtime_seconds += 1
        self.lbl_overtime.setText(f"已提醒：{self.format_time(self.overtime_seconds)}")
        if not self.is_resting:
            self.update_eye_usage_label()
        # 如果点击了开始休息，更新按钮上的计时
        if self.is_resting:
            self.rest_seconds += 1
            self.btn_start_rest.setText(f"休息中:{self.format_time(self.rest_seconds)}")

    def on_start_rest(self):
        """点击开始休息"""
        if self.is_resting:
            return
        self.eye_usage_frozen_seconds = self.get_current_eye_usage_seconds()
        self.update_eye_usage_label()
        self.is_resting = True
        self.btn_start_rest.setEnabled(False)
        self.input_delay_mins.setEnabled(False)
        self.btn_delay.setEnabled(False)
        self.rest_started.emit()

    def on_delay_requested(self):
        """本次弹窗临时延时，不修改主界面的默认延时配置。"""
        self.delay_requested.emit(self.input_delay_mins.value())
        self.close()

    def start_rest_immediately(self):
        """供外部直接切换到“开始休息”状态。"""
        self.on_start_rest()

    def on_rest_done(self):
        """点击休息好了时，先通知主程序完成本轮，再关闭窗口。"""
        self.rest_finished.emit()
        self.close()

    def closeEvent(self, event):
        # 停止计时器防止内存泄漏
        self.display_timer.stop()
        super().closeEvent(event)
    # --- 让无边框窗口可以拖动 ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.m_drag = True
            # 记录鼠标按下时的相对位置
            self.m_DragPosition = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if hasattr(self, 'm_drag') and self.m_drag and event.buttons() & Qt.MouseButton.LeftButton:
            # 随鼠标移动窗口
            self.move(event.globalPosition().toPoint() - self.m_DragPosition)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.m_drag = False
