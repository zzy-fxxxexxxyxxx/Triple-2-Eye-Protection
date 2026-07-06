import os
import platform
import sys
import time
import traceback


APP_VERSION = "2.1.5"
main_window = None
single_instance_mutex = None
SINGLE_INSTANCE_MUTEX_NAME = "Local\\Triple2EyeProtectionSingleInstance"


def get_base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.realpath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def get_error_log_path():
    return os.path.join(get_base_dir(), "error.log")


def collect_app_state():
    win = globals().get("main_window")
    if win is None:
        return ["Main window: not initialized"]

    state_lines = ["Main window: initialized"]
    fields = [
        ("t1_mins", "t1_mins"),
        ("t2_secs", "t2_secs"),
        ("default_delay_mins", "default_delay_mins"),
        ("remind_mode", "remind_mode"),
        ("fade_secs", "fade_secs"),
        ("is_paused", "is_paused"),
        ("is_locked", "is_locked"),
        ("start_time", "start_time"),
        ("eye_session_start_time", "eye_session_start_time"),
        ("paused_remaining", "paused_remaining"),
    ]
    for label, attr in fields:
        try:
            state_lines.append(f"{label}: {getattr(win, attr)}")
        except Exception as exc:
            state_lines.append(f"{label}: <unavailable: {exc}>")

    try:
        state_lines.append(f"current_usage_state: {win.get_current_usage_state()}")
    except Exception as exc:
        state_lines.append(f"current_usage_state: <unavailable: {exc}>")

    try:
        reminder = win.get_visible_reminder_window()
        state_lines.append(f"reminder_visible: {reminder is not None}")
        if reminder is not None:
            state_lines.append(f"reminder_is_resting: {getattr(reminder, 'is_resting', None)}")
            state_lines.append(f"reminder_overtime_seconds: {getattr(reminder, 'overtime_seconds', None)}")
            state_lines.append(f"reminder_rest_seconds: {getattr(reminder, 'rest_seconds', None)}")
    except Exception as exc:
        state_lines.append(f"reminder_state: <unavailable: {exc}>")

    try:
        state_lines.append(f"config_path: {getattr(win, 'config_path', None)}")
        state_lines.append(f"usage_log_dir: {getattr(win.usage_log_manager, 'log_dir', None)}")
    except Exception as exc:
        state_lines.append(f"paths: <unavailable: {exc}>")

    return state_lines


def build_error_report(exctype, value, tb):
    traceback_details = "".join(traceback.format_exception(exctype, value, tb))
    lines = [
        f"--- {time.strftime('%Y-%m-%d %H:%M:%S')} ---",
        f"App version: {APP_VERSION}",
        f"Exception type: {getattr(exctype, '__name__', str(exctype))}",
        f"Exception message: {value}",
        f"Frozen: {getattr(sys, 'frozen', False)}",
        f"Executable: {sys.executable}",
        f"Base dir: {get_base_dir()}",
        f"Current working directory: {os.getcwd()}",
        f"Python: {sys.version.replace(os.linesep, ' ')}",
        f"Platform: {platform.platform()}",
        f"Architecture: {platform.architecture()}",
        f"argv: {sys.argv}",
        "",
        "[Application State]",
        *collect_app_state(),
        "",
        "[sys.path]",
        *[str(path) for path in sys.path],
        "",
        "[PATH]",
        os.environ.get("PATH", ""),
        "",
        "[Traceback]",
        traceback_details,
        "",
    ]
    return "\n".join(lines)


def write_error_log(report):
    log_path = get_error_log_path()
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(report)
    except OSError:
        fallback_path = os.path.join(os.path.expanduser("~"), "Triple2EyeProtection-error.log")
        with open(fallback_path, "a", encoding="utf-8") as f:
            f.write(report)


def show_error_dialog(report):
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox

        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Icon.Critical)
        error_box.setText("程序崩溃")
        error_box.setInformativeText(f"程序遇到一个意外错误，即将退出。\n\n错误详情:\n{report}")
        error_box.setWindowTitle("意外错误")
        error_box.exec()
    except Exception:
        # If Qt itself cannot be imported, the written log is the source of truth.
        pass


def global_except_hook(exctype, value, tb):
    report = build_error_report(exctype, value, tb)
    write_error_log(report)
    show_error_dialog(report)
    sys.exit(1)


def activate_existing_instance():
    try:
        import win32con
        import win32gui

        candidates = []

        def enum_windows(hwnd, _extra):
            title = win32gui.GetWindowText(hwnd)
            if "Triple 2 Eye" in title and "Protection" in title:
                candidates.append(hwnd)

        win32gui.EnumWindows(enum_windows, None)
        if not candidates:
            return False

        hwnd = candidates[0]
        win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        return True
    except Exception:
        return False


def ensure_single_instance():
    global single_instance_mutex
    try:
        import win32api
        import win32event
        import winerror

        single_instance_mutex = win32event.CreateMutex(None, True, SINGLE_INSTANCE_MUTEX_NAME)
        if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
            activate_existing_instance()
            sys.exit(0)
    except Exception:
        # Do not block startup if the Windows mutex API is unavailable.
        single_instance_mutex = None


sys.excepthook = global_except_hook
ensure_single_instance()

try:
    from PyQt6.QtWidgets import QApplication
    from main_app import EyeCarePro
except Exception as import_error:
    global_except_hook(type(import_error), import_error, import_error.__traceback__)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    try:
        main_window = EyeCarePro()
        main_window.show()
    except Exception as init_error:
        global_except_hook(type(init_error), init_error, init_error.__traceback__)

    sys.exit(app.exec())
