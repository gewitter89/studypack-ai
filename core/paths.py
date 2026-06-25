import os
import sys


def _is_frozen() -> bool:
    return getattr(sys, 'frozen', False)


def _resource_base() -> str:
    if _is_frozen():
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _user_base() -> str:
    if _is_frozen():
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _base_path() -> str:
    return _user_base()


def config_dir() -> str:
    return os.path.join(_resource_base(), "config")


def prompts_dir() -> str:
    return os.path.join(_resource_base(), "prompts")


def templates_dir() -> str:
    return os.path.join(_resource_base(), "templates_library")


def logo_path() -> str:
    return os.path.join(_resource_base(), "assets", "logo.png")


def output_dir() -> str:
    return os.path.join(_user_base(), "output")


def logs_dir() -> str:
    return os.path.join(_user_base(), "logs")


def env_file_path() -> str:
    return os.path.join(_user_base(), ".env")


def ensure_dirs():
    for d in [output_dir(), logs_dir()]:
        os.makedirs(d, exist_ok=True)

