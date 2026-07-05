import json
import os

class AppSettings:
    def __init__(self, config_path="eye_settings.json"):
        self.config_path = config_path
        # 默认值
        self.t1_mins = 20
        self.default_delay_mins = 10
        self.t2_secs = 20
        self.remind_mode = 0
        # 启动时加载配置
        self.load()

    def load(self):
        """从 JSON 文件加载配置。如果文件不存在或损坏，则使用默认值。"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    self.t1_mins = data.get("t1", self.t1_mins)
                    self.default_delay_mins = data.get("default_delay_mins", self.default_delay_mins)
                    self.t2_secs = data.get("t2", self.t2_secs)
                    self.remind_mode = data.get("mode", self.remind_mode)
            except (json.JSONDecodeError, IOError):
                # 如果文件解析失败或无法读取，则忽略并使用默认值
                pass

    def save(self):
        """将当前配置保存到 JSON 文件。"""
        with open(self.config_path, 'w') as f:
            settings_data = {
                "t1": self.t1_mins,
                "default_delay_mins": self.default_delay_mins,
                "t2": self.t2_secs,
                "mode": self.remind_mode
            }
            json.dump(settings_data, f, indent=4)
