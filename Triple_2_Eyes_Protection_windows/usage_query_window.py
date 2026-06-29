import calendar
import os
from datetime import datetime, timedelta

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QPen, QLinearGradient, QBrush
from PyQt6.QtWidgets import (QDateTimeEdit, QGroupBox, QHBoxLayout, QLabel,
                             QTableWidget, QTableWidgetItem, QVBoxLayout,
                             QWidget, QPushButton)


STATE_COLOR_MAP = {
    1.0: QColor(220, 53, 69),
    0.3: QColor(245, 159, 0),
    0.0: QColor(32, 201, 151),
}

STATE_LABEL_MAP = {
    1.0: "使用中",
    0.3: "提醒未开始休息",
    0.0: "休息中",
}

FIXED_RANGE_PRESETS = [
    ("12h", "过去12h"),
    ("24h", "过去24h"),
    ("7d", "过去7天"),
    ("1m", "过去1个月"),
    ("6m", "过去6个月"),
    ("1y", "过去1年"),
]


class UsageLogManager:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.log_dir = os.path.join(base_dir, "usage_logs")
        os.makedirs(self.log_dir, exist_ok=True)
        self.pending_entries = []
        self.last_state = None
        self.last_sample_time = None
        self.last_written_by_day = {}

    def _append_entry(self, ts, state_value):
        if self.pending_entries:
            last_ts, last_state = self.pending_entries[-1]
            if last_ts == ts and abs(last_state - state_value) < 1e-9:
                return
        self.pending_entries.append((ts, state_value))

    def record_state(self, state_value, at_time=None, force=False):
        state_value = float(state_value)
        ts = at_time or datetime.now()

        if self.last_sample_time is not None and ts < self.last_sample_time:
            ts = self.last_sample_time

        if self.last_state is None:
            self._append_entry(ts, state_value)
            self.last_state = state_value
            self.last_sample_time = ts
            if len(self.pending_entries) >= 200:
                self.flush()
            return

        state_changed = abs(self.last_state - state_value) >= 1e-9

        if state_changed:
            prev_ts = ts - timedelta(seconds=1)
            if self.last_sample_time is not None and prev_ts < self.last_sample_time:
                prev_ts = self.last_sample_time

            # 记录变化前后两个边界点，让图像呈现阶梯形。
            self._append_entry(prev_ts, self.last_state)
            self._append_entry(ts, state_value)
            self.last_state = state_value
        elif force:
            # 强制保存时不重复写同状态点，只更新时间游标。
            pass

        self.last_sample_time = ts

        if len(self.pending_entries) >= 200:
            self.flush()

    def flush(self):
        if not self.pending_entries:
            return

        grouped = {}
        for ts, state in self.pending_entries:
            day_key = ts.strftime("%Y-%m-%d")
            grouped.setdefault(day_key, []).append((ts, state))

        for day_key, entries in grouped.items():
            file_path = os.path.join(self.log_dir, f"usage_{day_key}.txt")
            entries.sort(key=lambda item: item[0])

            if day_key not in self.last_written_by_day:
                self.last_written_by_day[day_key] = self._read_last_row(file_path)

            last_written = self.last_written_by_day[day_key]
            with open(file_path, "a", encoding="utf-8") as f:
                for ts, state in entries:
                    row = (ts, float(state))
                    if last_written is not None:
                        if last_written[0] == row[0] and abs(last_written[1] - row[1]) < 1e-9:
                            continue
                    f.write(f"{ts.strftime('%Y-%m-%d %H:%M:%S')} {state:g}\n")
                    last_written = row

            self.last_written_by_day[day_key] = last_written

        self.pending_entries.clear()

    def _read_last_row(self, file_path):
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except OSError:
            return None

        for raw_line in reversed(lines):
            line = raw_line.strip()
            if not line:
                continue
            try:
                timestamp_text, state_text = line.rsplit(" ", 1)
                ts = datetime.strptime(timestamp_text, "%Y-%m-%d %H:%M:%S")
                return ts, float(state_text)
            except ValueError:
                continue

        return None

    def load_all_records(self):
        self.flush()

        records = []
        for file_name in sorted(os.listdir(self.log_dir)):
            if not (file_name.startswith("usage_") and file_name.endswith(".txt")):
                continue

            file_path = os.path.join(self.log_dir, file_name)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for raw_line in f:
                        line = raw_line.strip()
                        if not line:
                            continue
                        try:
                            timestamp_text, state_text = line.rsplit(" ", 1)
                            ts = datetime.strptime(timestamp_text, "%Y-%m-%d %H:%M:%S")
                            state = float(state_text)
                            if state in (1.0, 0.3, 0.0, -1.0):
                                records.append((ts, state))
                        except ValueError:
                            continue
            except OSError:
                continue

        records.sort(key=lambda item: item[0])

        deduped = []
        for ts, state in records:
            if deduped and deduped[-1][0] == ts and abs(deduped[-1][1] - state) < 1e-9:
                continue
            deduped.append((ts, state))

        return deduped


def compute_state_durations(records, start_time, end_time):
    totals = {1.0: 0.0, 0.3: 0.0, 0.0: 0.0}
    if start_time >= end_time or not records:
        return totals

    current_state = None
    for ts, state in records:
        if ts <= start_time:
            current_state = state
        else:
            break

    cursor = start_time
    for ts, state in records:
        if ts <= start_time:
            continue
        if ts > end_time:
            break

        if current_state in totals and ts > cursor:
            totals[current_state] += (ts - cursor).total_seconds()

        current_state = state
        cursor = ts

    if current_state in totals and end_time > cursor:
        totals[current_state] += (end_time - cursor).total_seconds()

    return totals


def format_seconds(total_seconds):
    total_seconds = int(max(0, total_seconds))
    hours, rem = divmod(total_seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def subtract_months(dt, months):
    month_index = dt.month - months - 1
    year = dt.year + month_index // 12
    month = month_index % 12 + 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)


def get_preset_range(range_key, end_time=None):
    end_time = end_time or datetime.now()
    if range_key == "12h":
        return end_time - timedelta(hours=12), end_time
    if range_key == "24h":
        return end_time - timedelta(hours=24), end_time
    if range_key == "7d":
        return end_time - timedelta(days=7), end_time
    if range_key == "1m":
        return subtract_months(end_time, 1), end_time
    if range_key == "6m":
        return subtract_months(end_time, 6), end_time
    if range_key == "1y":
        return subtract_months(end_time, 12), end_time
    return end_time - timedelta(hours=24), end_time


class UsagePlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(320)
        self.range_start = None
        self.range_end = None
        self.points = []

    def set_data(self, points, range_start, range_end):
        self.points = points
        self.range_start = range_start
        self.range_end = range_end
        self.update()

    def _gap_threshold_seconds(self):
        if not self.range_start or not self.range_end:
            return 3600
        span = (self.range_end - self.range_start).total_seconds()
        if span <= 12 * 3600:
            return 30 * 60
        if span <= 24 * 3600:
            return 60 * 60
        if span <= 7 * 24 * 3600:
            return 6 * 3600
        if span <= 31 * 24 * 3600:
            return 24 * 3600
        if span <= 183 * 24 * 3600:
            return 3 * 24 * 3600
        return 7 * 24 * 3600

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(250, 252, 255))

        if not self.range_start or not self.range_end:
            return

        left = 56
        right = 24
        top = 20
        bottom = 58
        w = max(1, self.width() - left - right)
        h = max(1, self.height() - top - bottom)

        painter.setPen(QPen(QColor(180, 188, 200), 1))
        painter.drawRect(left, top, w, h)

        def map_x(ts):
            total = (self.range_end - self.range_start).total_seconds()
            if total <= 0:
                return left
            delta = (ts - self.range_start).total_seconds()
            return int(left + (delta / total) * w)

        def map_y(state_value):
            # y=1 顶部，y=0 底部
            ratio = 1.0 - float(state_value)
            return int(top + ratio * h)

        for state_value in (1.0, 0.3, 0.0):
            y = map_y(state_value)
            painter.setPen(QPen(QColor(220, 225, 235), 1, Qt.PenStyle.DashLine))
            painter.drawLine(left, y, left + w, y)
            painter.setPen(QPen(QColor(90, 102, 120), 1))
            painter.drawText(8, y + 4, f"y={state_value:g}")

        gap_threshold = self._gap_threshold_seconds()
        points = [(ts, state) for ts, state in self.points if self.range_start <= ts <= self.range_end]

        for i in range(1, len(points)):
            t1, s1 = points[i - 1]
            t2, s2 = points[i]
            if (t2 - t1).total_seconds() > gap_threshold:
                continue
            if float(s1) == -1.0 or float(s2) == -1.0:
                # -1 表示离线/锁屏/休眠：该区段不绘制连线
                continue

            x1, y1 = map_x(t1), map_y(s1)
            x2, y2 = map_x(t2), map_y(s2)
            c1 = STATE_COLOR_MAP.get(float(s1), QColor(120, 120, 120))
            c2 = STATE_COLOR_MAP.get(float(s2), QColor(120, 120, 120))

            gradient = QLinearGradient(x1, y1, x2, y2)
            gradient.setColorAt(0.0, c1)
            gradient.setColorAt(1.0, c2)
            painter.setPen(QPen(QBrush(gradient), 2))
            painter.drawLine(x1, y1, x2, y1)
            painter.drawLine(x2, y1, x2, y2)

        for ts, state in points:
            if float(state) == -1.0:
                continue
            x = map_x(ts)
            y = map_y(state)
            color = STATE_COLOR_MAP.get(float(state), QColor(120, 120, 120))
            painter.setPen(QPen(color, 1))
            painter.setBrush(color)
            painter.drawEllipse(x - 3, y - 3, 6, 6)

        painter.setPen(QPen(QColor(90, 102, 120), 1))
        tick_count = 6
        total_seconds = (self.range_end - self.range_start).total_seconds()
        for i in range(tick_count + 1):
            ratio = i / tick_count
            x = int(left + ratio * w)
            ts = self.range_start + timedelta(seconds=total_seconds * ratio)
            painter.drawLine(x, top + h, x, top + h + 4)

            if total_seconds <= 24 * 3600:
                text = ts.strftime("%m-%d %H:%M")
            elif total_seconds <= 31 * 24 * 3600:
                text = ts.strftime("%m-%d")
            else:
                text = ts.strftime("%Y-%m")
            painter.drawText(x - 28, top + h + 20, 80, 28, Qt.AlignmentFlag.AlignLeft, text)


class UsageQueryWindow(QWidget):
    def __init__(self, usage_log_manager):
        super().__init__()
        self.usage_log_manager = usage_log_manager
        self.records = []

        self.setWindowTitle("使用查询与统计")
        self.resize(980, 720)

        root = QVBoxLayout(self)

        controls_group = QGroupBox("查询条件")
        controls_group_layout = QVBoxLayout(controls_group)

        custom_range_row = QHBoxLayout()

        custom_range_row.addWidget(QLabel("起始时间:"))
        self.dt_start = QDateTimeEdit()
        self.dt_start.setDisplayFormat("yyyy年MM月dd日 HH:mm")
        self.dt_start.setCalendarPopup(True)
        custom_range_row.addWidget(self.dt_start)

        custom_range_row.addWidget(QLabel("终止时间:"))
        self.dt_end = QDateTimeEdit()
        self.dt_end.setDisplayFormat("yyyy年MM月dd日 HH:mm")
        self.dt_end.setCalendarPopup(True)
        custom_range_row.addWidget(self.dt_end)

        self.btn_apply_range = QPushButton("Apply")
        self.btn_apply_range.clicked.connect(self.refresh_view)
        custom_range_row.addWidget(self.btn_apply_range)
        custom_range_row.addStretch(1)
        controls_group_layout.addLayout(custom_range_row)

        preset_range_row = QHBoxLayout()
        preset_range_row.addWidget(QLabel("快捷范围:"))
        self.preset_buttons = []
        for range_key, label in FIXED_RANGE_PRESETS:
            button = QPushButton(label)
            button.clicked.connect(lambda _checked=False, key=range_key: self.apply_preset_range(key))
            preset_range_row.addWidget(button)
            self.preset_buttons.append(button)
        preset_range_row.addStretch(1)
        controls_group_layout.addLayout(preset_range_row)

        root.addWidget(controls_group)

        stat_group = QGroupBox("信息统计")
        stat_layout = QVBoxLayout(stat_group)

        self.stat_table = QTableWidget(len(FIXED_RANGE_PRESETS), 4)
        self.stat_table.setHorizontalHeaderLabels(["时间范围", "使用中(y=1)", "提醒未休息(y=0.3)", "休息中(y=0)"])
        self.stat_table.verticalHeader().setVisible(False)
        self.stat_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.stat_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.stat_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        stat_layout.addWidget(self.stat_table)
        root.addWidget(stat_group)

        chart_group = QGroupBox("状态曲线")
        chart_layout = QVBoxLayout(chart_group)

        self.plot_widget = UsagePlotWidget()
        chart_layout.addWidget(self.plot_widget)
        root.addWidget(chart_group)

    def refresh(self):
        self.records = self.usage_log_manager.load_all_records()
        now = datetime.now()
        self.dt_end.setDateTime(now)
        self.dt_start.setDateTime(now - timedelta(hours=24))
        self.refresh_view()

    def apply_preset_range(self, range_key):
        start_time, end_time = get_preset_range(range_key, datetime.now())
        self.dt_start.setDateTime(start_time)
        self.dt_end.setDateTime(end_time)
        self.refresh_view()

    def refresh_view(self):
        start_time = self.dt_start.dateTime().toPyDateTime()
        end_time = self.dt_end.dateTime().toPyDateTime()
        if start_time >= end_time:
            end_time = start_time + timedelta(minutes=1)
            self.dt_end.setDateTime(end_time)

        self._refresh_stats(datetime.now())
        points = [(ts, state) for ts, state in self.records if start_time <= ts <= end_time]
        self.plot_widget.set_data(points, start_time, end_time)

    def _refresh_stats(self, anchor_time):
        for row, (range_key, label) in enumerate(FIXED_RANGE_PRESETS):
            start_time, end_time = get_preset_range(range_key, anchor_time)
            totals = compute_state_durations(self.records, start_time, end_time)
            range_label = f"{label} ({start_time.strftime('%Y-%m-%d %H:%M')} ~ {end_time.strftime('%Y-%m-%d %H:%M')})"

            self.stat_table.setItem(row, 0, QTableWidgetItem(range_label))
            self.stat_table.setItem(row, 1, QTableWidgetItem(format_seconds(totals[1.0])))
            self.stat_table.setItem(row, 2, QTableWidgetItem(format_seconds(totals[0.3])))
            self.stat_table.setItem(row, 3, QTableWidgetItem(format_seconds(totals[0.0])))

        self.stat_table.resizeColumnsToContents()
