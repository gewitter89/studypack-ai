import os
import sys


def _is_frozen() -> bool:
    return getattr(sys, 'frozen', False)


def _base_path() -> str:
    if _is_frozen():
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def config_dir() -> str:
    return os.path.join(_base_path(), "config")


def prompts_dir() -> str:
    return os.path.join(_base_path(), "prompts")


def output_dir() -> str:
    return os.path.join(_base_path(), "output")


def logs_dir() -> str:
    return os.path.join(_base_path(), "logs")


def ensure_dirs():
    for d in [output_dir(), logs_dir()]:
        os.makedirs(d, exist_ok=True)
