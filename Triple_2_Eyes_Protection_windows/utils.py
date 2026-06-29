import sys
import os

def get_resource_path(relative_path):
    """
    获取资源的绝对路径，兼容开发环境和 PyInstaller 打包环境。
    确保在脚本同级目录下查找资源。
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的临时解压路径
        base_path = sys._MEIPASS
    else:
        # 获取当前文件 (utils.py) 所在的绝对路径目录
        # 而不是使用 ".." 指向父目录
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)
