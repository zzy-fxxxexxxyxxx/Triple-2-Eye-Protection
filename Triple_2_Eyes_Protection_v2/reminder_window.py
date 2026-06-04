import sys
import os
import time

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout,
                             QLabel, QPushButton, QFrame)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal


class ReminderWindow(QWidget):
    rest_started = pyqtSignal()

    def __init__(self, t2_secs):
        super().__init__()
        # 计时变量
        self.overtime_seconds = 0
        self.rest_seconds = 0
        self.is_resting = False
        self.target_rest = t2_secs

        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(400, 300)

        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

        container = QFrame(self)
        container.setObjectName("MainFrame")
        container.setFixedSize(400, 300)
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
        # 4. 按钮布局
        v_box = QVBoxLayout()
        v_box.setSpacing(10)
        # 新增：开始休息按钮
        self.btn_start_rest = QPushButton("开始休息")
        self.btn_start_rest.setFixedSize(120, 40)
        self.btn_start_rest.clicked.connect(self.on_start_rest)
        # layout.addWidget(self.btn_start_rest)

        self.btn_done = QPushButton("休息好了")
        self.btn_done.setFixedSize(120, 40)
        self.btn_done.clicked.connect(self.close)
        # layout.addWidget(self.btn_done)

        v_box.addStretch()
        v_box.addWidget(self.btn_start_rest, alignment=Qt.AlignmentFlag.AlignCenter)
        v_box.addWidget(self.btn_done, alignment=Qt.AlignmentFlag.AlignCenter)
        v_box.addStretch()
        layout.addLayout(v_box)
        # 启动定时器，每秒刷新
        self.display_timer = QTimer(self)
        self.display_timer.timeout.connect(self.tick)
        self.display_timer.start(1000)

    def format_time(self, seconds):
        """将秒转换为分秒格式"""
        if seconds < 60:
            return f"{seconds}秒"
        else:
            m, s = divmod(seconds, 60)
            return f"{m}分{s}秒"

    def tick(self):
        """每秒执行逻辑"""
        # 更新总超时时间
        self.overtime_seconds += 1
        self.lbl_overtime.setText(f"已提醒：{self.format_time(self.overtime_seconds)}")
        # 如果点击了开始休息，更新按钮上的计时
        if self.is_resting:
            self.rest_seconds += 1
            self.btn_start_rest.setText(f"休息中:{self.format_time(self.rest_seconds)}")

    def on_start_rest(self):
        """点击开始休息"""
        if self.is_resting:
            return
        self.is_resting = True
        self.btn_start_rest.setEnabled(False)
        self.rest_started.emit()

    def start_rest_immediately(self):
        """供外部直接切换到“开始休息”状态。"""
        self.on_start_rest()

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
