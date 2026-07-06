import calendar
import json
import os
from datetime import datetime, timedelta

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import (QComboBox, QDateTimeEdit, QDoubleSpinBox,
                             QGroupBox, QHBoxLayout, QLabel, QPushButton,
                             QTableWidget, QTableWidgetItem, QVBoxLayout,
                             QWidget)


STATE_WORKING = "working"
STATE_REMINDED = "reminded"
STATE_RESTING = "resting"
STATE_UNRECORDED = "unrecorded"

STATE_KEYS = [STATE_WORKING, STATE_REMINDED, STATE_RESTING, STATE_UNRECORDED]

STATE_LABEL_MAP = {
    STATE_WORKING: "使用中",
    STATE_REMINDED: "提醒未休息",
    STATE_RESTING: "休息中",
    STATE_UNRECORDED: "未记录",
}

STATE_COLOR_MAP = {
    STATE_WORKING: QColor(220, 53, 69),
    STATE_REMINDED: QColor(245, 159, 0),
    STATE_RESTING: QColor(32, 201, 151),
    STATE_UNRECORDED: QColor(152, 160, 170),
}

DEFAULT_DISPLAY_Y = {
    STATE_WORKING: 1.0,
    STATE_REMINDED: 0.7,
    STATE_RESTING: 0.0,
    STATE_UNRECORDED: -0.1,
}

LEGACY_STATE_VALUE_MAP = [
    (1.0, STATE_WORKING),
    (0.3, STATE_REMINDED),
    (0.7, STATE_REMINDED),
    (0.0, STATE_RESTING),
    (-1.0, STATE_UNRECORDED),
]

FIXED_RANGE_PRESETS = [
    ("12h", "过去12h"),
    ("24h", "过去24h"),
    ("7d", "过去7天"),
    ("1m", "过去1个月"),
    ("6m", "过去6个月"),
    ("1y", "过去1年"),
]

DISPLAY_MODES = [
    ("timeline", "时间轴色块"),
    ("curve", "曲线图"),
]


def normalize_state_value(raw_state):
    try:
        value = float(raw_state)
    except (TypeError, ValueError):
        return None

    for legacy_value, state_key in LEGACY_STATE_VALUE_MAP:
        if abs(value - legacy_value) < 1e-9:
            return state_key
    return None


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
                            state_key = normalize_state_value(state_text)
                            if state_key is not None:
                                records.append((ts, state_key))
                        except ValueError:
                            continue
            except OSError:
                continue

        records.sort(key=lambda item: item[0])

        deduped = []
        for ts, state_key in records:
            if deduped and deduped[-1][0] == ts and deduped[-1][1] == state_key:
                continue
            deduped.append((ts, state_key))

        return deduped


def build_state_segments(records, start_time, end_time):
    if start_time >= end_time:
        return []

    current_state = STATE_UNRECORDED
    for ts, state_key in records:
        if ts <= start_time:
            current_state = state_key
        else:
            break

    segments = []
    cursor = start_time
    for ts, state_key in records:
        if ts <= start_time:
            continue
        if ts > end_time:
            break

        if ts > cursor:
            segments.append((cursor, ts, current_state))
        current_state = state_key
        cursor = max(cursor, ts)

    if end_time > cursor:
        segments.append((cursor, end_time, current_state))

    return segments


def compute_state_durations(records, start_time, end_time):
    totals = {state_key: 0.0 for state_key in STATE_KEYS}
    for seg_start, seg_end, state_key in build_state_segments(records, start_time, end_time):
        totals[state_key] += max(0.0, (seg_end - seg_start).total_seconds())
    return totals


def display_percentages(totals, total_seconds):
    if total_seconds <= 0:
        return {state_key: 0.0 for state_key in STATE_KEYS}

    percentages = {
        state_key: round((totals[state_key] / total_seconds) * 100.0, 1)
        for state_key in STATE_KEYS
    }
    diff = round(100.0 - sum(percentages.values()), 1)
    if abs(diff) >= 0.1:
        largest_key = max(STATE_KEYS, key=lambda key: totals[key])
        percentages[largest_key] = round(percentages[largest_key] + diff, 1)

    return {
        state_key: 0.0 if abs(value) < 0.05 else value
        for state_key, value in percentages.items()
    }


def format_duration_with_ratio(total_seconds, percent):
    return f"{format_seconds(total_seconds)} ({percent:.1f}%)"


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
        self.setMinimumHeight(340)
        self.range_start = None
        self.range_end = None
        self.records = []
        self.display_mode = "timeline"
        self.display_y = DEFAULT_DISPLAY_Y.copy()

    def set_config(self, display_mode, display_y):
        self.display_mode = display_mode
        self.display_y = display_y.copy()
        self.update()

    def set_data(self, records, range_start, range_end):
        self.records = records
        self.range_start = range_start
        self.range_end = range_end
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(250, 252, 255))

        if not self.range_start or not self.range_end:
            return

        if self.display_mode == "curve":
            self.draw_curve(painter)
        else:
            self.draw_timeline(painter)

    def draw_legend(self, painter, x, y):
        cursor_x = x
        for state_key in STATE_KEYS:
            color = STATE_COLOR_MAP[state_key]
            painter.setPen(QPen(color.darker(115), 1))
            painter.setBrush(color)
            painter.drawRoundedRect(cursor_x, y + 2, 12, 12, 3, 3)
            painter.setPen(QPen(QColor(55, 65, 75), 1))
            painter.drawText(cursor_x + 18, y + 14, STATE_LABEL_MAP[state_key])
            cursor_x += 18 + len(STATE_LABEL_MAP[state_key]) * 14 + 28

    def map_x(self, ts, left, width):
        total = (self.range_end - self.range_start).total_seconds()
        if total <= 0:
            return left
        delta = (ts - self.range_start).total_seconds()
        return int(left + (delta / total) * width)

    def draw_time_ticks(self, painter, left, y, width):
        painter.setPen(QPen(QColor(90, 102, 120), 1))
        tick_count = 6
        total_seconds = (self.range_end - self.range_start).total_seconds()
        for i in range(tick_count + 1):
            ratio = i / tick_count
            x = int(left + ratio * width)
            ts = self.range_start + timedelta(seconds=total_seconds * ratio)
            painter.drawLine(x, y, x, y + 4)

            if total_seconds <= 24 * 3600:
                text = ts.strftime("%m-%d %H:%M")
            elif total_seconds <= 31 * 24 * 3600:
                text = ts.strftime("%m-%d")
            else:
                text = ts.strftime("%Y-%m")
            painter.drawText(x - 30, y + 8, 86, 28, Qt.AlignmentFlag.AlignLeft, text)

    def draw_timeline(self, painter):
        left = 64
        right = 24
        top = 28
        bar_top = 92
        bar_height = 70
        width = max(1, self.width() - left - right)

        self.draw_legend(painter, left, top)

        painter.setPen(QPen(QColor(205, 213, 224), 1))
        painter.setBrush(QColor(244, 247, 250))
        painter.drawRoundedRect(left, bar_top, width, bar_height, 8, 8)

        segments = build_state_segments(self.records, self.range_start, self.range_end)
        for seg_start, seg_end, state_key in segments:
            x1 = self.map_x(seg_start, left, width)
            x2 = self.map_x(seg_end, left, width)
            seg_width = max(1, x2 - x1)
            color = STATE_COLOR_MAP[state_key]
            painter.fillRect(x1, bar_top + 1, seg_width, bar_height - 2, color.lighter(112))
            painter.setPen(QPen(color.darker(110), 1))
            painter.drawLine(x1, bar_top + 1, x1, bar_top + bar_height - 2)

        painter.setPen(QPen(QColor(180, 188, 200), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(left, bar_top, width, bar_height, 8, 8)

        painter.setPen(QPen(QColor(90, 102, 120), 1))
        painter.drawText(10, bar_top + 42, "状态")
        self.draw_time_ticks(painter, left, bar_top + bar_height + 10, width)

    def draw_curve(self, painter):
        label_samples = [
            f"{STATE_LABEL_MAP[state_key]} y={self.display_y[state_key]:g}"
            for state_key in STATE_KEYS
        ]
        metrics = self.fontMetrics()
        left = max(112, max(metrics.horizontalAdvance(label) for label in label_samples) + 18)
        right = 24
        top = 48
        bottom = 58
        width = max(1, self.width() - left - right)
        height = max(1, self.height() - top - bottom)

        y_values = list(self.display_y.values())
        y_min = min(y_values) - 0.05
        y_max = max(y_values) + 0.05
        if abs(y_max - y_min) < 1e-9:
            y_max = y_min + 1.0

        def map_y(state_key):
            value = self.display_y[state_key]
            ratio = (y_max - value) / (y_max - y_min)
            return int(top + ratio * height)

        self.draw_legend(painter, left, 14)

        painter.fillRect(left, top, width, height, QColor(255, 255, 255))
        painter.setPen(QPen(QColor(180, 188, 200), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(left, top, width, height)

        for state_key in STATE_KEYS:
            y = map_y(state_key)
            painter.setPen(QPen(QColor(220, 225, 235), 1, Qt.PenStyle.DashLine))
            painter.drawLine(left, y, left + width, y)
            painter.setPen(QPen(QColor(90, 102, 120), 1))
            label = f"{STATE_LABEL_MAP[state_key]} y={self.display_y[state_key]:g}"
            painter.drawText(4, y - 10, left - 12, 20, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, label)

        segments = build_state_segments(self.records, self.range_start, self.range_end)
        previous_y = None
        previous_x = None
        for seg_start, seg_end, state_key in segments:
            x1 = self.map_x(seg_start, left, width)
            x2 = self.map_x(seg_end, left, width)
            y = map_y(state_key)
            color = STATE_COLOR_MAP[state_key]

            if previous_y is not None and previous_x == x1 and previous_y != y:
                painter.setPen(QPen(QColor(150, 158, 168), 1))
                painter.drawLine(x1, previous_y, x1, y)

            pen_style = Qt.PenStyle.DashLine if state_key == STATE_UNRECORDED else Qt.PenStyle.SolidLine
            painter.setPen(QPen(color, 3, pen_style))
            painter.drawLine(x1, y, x2, y)
            painter.setBrush(color)
            painter.drawEllipse(x1 - 3, y - 3, 6, 6)

            previous_x = x2
            previous_y = y

        self.draw_time_ticks(painter, left, top + height + 10, width)


class UsageQueryWindow(QWidget):
    def __init__(self, usage_log_manager):
        super().__init__()
        self.usage_log_manager = usage_log_manager
        self.records = []
        self.settings_path = os.path.join(self.usage_log_manager.base_dir, "usage_query_settings.json")
        self.query_settings = self.load_query_settings()

        self.setWindowTitle("使用查询与统计")
        self.resize(1060, 760)

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

        self.btn_apply_range = QPushButton("应用")
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

        self.stat_table = QTableWidget(len(FIXED_RANGE_PRESETS), 1 + len(STATE_KEYS))
        self.stat_table.verticalHeader().setVisible(False)
        self.stat_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.stat_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.stat_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.update_stat_headers()
        stat_layout.addWidget(self.stat_table)
        root.addWidget(stat_group)

        chart_group = QGroupBox("状态曲线")
        chart_layout = QVBoxLayout(chart_group)

        chart_settings_row = QHBoxLayout()
        chart_settings_row.addWidget(QLabel("呈现方式:"))
        self.display_mode_combo = QComboBox()
        for mode_key, label in DISPLAY_MODES:
            self.display_mode_combo.addItem(label, mode_key)
        mode_index = self.display_mode_combo.findData(self.query_settings["display_mode"])
        self.display_mode_combo.setCurrentIndex(max(0, mode_index))
        self.display_mode_combo.currentIndexChanged.connect(self.on_chart_settings_changed)
        chart_settings_row.addWidget(self.display_mode_combo)

        self.y_inputs = {}
        for state_key in STATE_KEYS:
            chart_settings_row.addWidget(QLabel(f"{STATE_LABEL_MAP[state_key]} y:"))
            y_input = QDoubleSpinBox()
            y_input.setRange(-1.0, 1.5)
            y_input.setDecimals(2)
            y_input.setSingleStep(0.1)
            y_input.setValue(self.query_settings["display_y"][state_key])
            y_input.valueChanged.connect(self.on_chart_settings_changed)
            y_input.setFixedWidth(72)
            self.y_inputs[state_key] = y_input
            chart_settings_row.addWidget(y_input)

        self.btn_reset_chart = QPushButton("重置显示")
        self.btn_reset_chart.clicked.connect(self.reset_chart_settings)
        chart_settings_row.addWidget(self.btn_reset_chart)
        chart_settings_row.addStretch(1)
        chart_layout.addLayout(chart_settings_row)

        self.plot_widget = UsagePlotWidget()
        chart_layout.addWidget(self.plot_widget)
        root.addWidget(chart_group)

    def load_query_settings(self):
        defaults = {
            "display_mode": "timeline",
            "display_y": DEFAULT_DISPLAY_Y.copy(),
        }
        if not os.path.exists(self.settings_path):
            return defaults

        try:
            with open(self.settings_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return defaults

        display_mode = data.get("display_mode", defaults["display_mode"])
        if display_mode not in {mode_key for mode_key, _label in DISPLAY_MODES}:
            display_mode = defaults["display_mode"]

        display_y = defaults["display_y"].copy()
        raw_y = data.get("display_y", {})
        if isinstance(raw_y, dict):
            for state_key in STATE_KEYS:
                try:
                    display_y[state_key] = float(raw_y.get(state_key, display_y[state_key]))
                except (TypeError, ValueError):
                    pass

        return {
            "display_mode": display_mode,
            "display_y": display_y,
        }

    def save_query_settings(self):
        try:
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(self.query_settings, f, indent=4, ensure_ascii=False)
        except OSError:
            pass

    def current_display_y(self):
        return {
            state_key: self.y_inputs[state_key].value()
            for state_key in STATE_KEYS
        }

    def current_display_mode(self):
        return self.display_mode_combo.currentData() or "timeline"

    def on_chart_settings_changed(self):
        self.query_settings = {
            "display_mode": self.current_display_mode(),
            "display_y": self.current_display_y(),
        }
        self.save_query_settings()
        self.update_stat_headers()
        self.refresh_view()

    def reset_chart_settings(self):
        self.display_mode_combo.setCurrentIndex(self.display_mode_combo.findData("timeline"))
        for state_key, default_y in DEFAULT_DISPLAY_Y.items():
            self.y_inputs[state_key].setValue(default_y)
        self.on_chart_settings_changed()

    def update_stat_headers(self):
        display_y = self.query_settings["display_y"]
        headers = ["时间范围"]
        headers.extend(
            f"{STATE_LABEL_MAP[state_key]}(y={display_y[state_key]:g})"
            for state_key in STATE_KEYS
        )
        self.stat_table.setHorizontalHeaderLabels(headers)

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
        if not hasattr(self, "plot_widget"):
            return

        start_time = self.dt_start.dateTime().toPyDateTime()
        end_time = self.dt_end.dateTime().toPyDateTime()
        if start_time >= end_time:
            end_time = start_time + timedelta(minutes=1)
            self.dt_end.setDateTime(end_time)

        self._refresh_stats(datetime.now())
        self.plot_widget.set_config(self.current_display_mode(), self.current_display_y())
        self.plot_widget.set_data(self.records, start_time, end_time)

    def _refresh_stats(self, anchor_time):
        for row, (range_key, label) in enumerate(FIXED_RANGE_PRESETS):
            start_time, end_time = get_preset_range(range_key, anchor_time)
            totals = compute_state_durations(self.records, start_time, end_time)
            total_seconds = max(1.0, (end_time - start_time).total_seconds())
            percentages = display_percentages(totals, total_seconds)
            range_label = f"{label} ({start_time.strftime('%Y-%m-%d %H:%M')} ~ {end_time.strftime('%Y-%m-%d %H:%M')})"

            self.stat_table.setItem(row, 0, QTableWidgetItem(range_label))
            for col, state_key in enumerate(STATE_KEYS, start=1):
                text = format_duration_with_ratio(totals[state_key], percentages[state_key])
                self.stat_table.setItem(row, col, QTableWidgetItem(text))

        self.stat_table.resizeColumnsToContents()
