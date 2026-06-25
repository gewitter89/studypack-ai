import os
import sys
import logging
import hashlib
import requests
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)

VERSION = "1.0.0"

def is_frozen() -> bool:
    return getattr(sys, 'frozen', False)

def get_current_exe_path() -> str:
    if is_frozen():
        return sys.executable
    return os.path.abspath(sys.argv[0])

def is_version_newer(current: str, latest: str) -> bool:
    try:
        c_parts = [int(x) for x in current.split(".")]
        l_parts = [int(x) for x in latest.split(".")]
        # Pad with zeros
        max_len = max(len(c_parts), len(l_parts))
        c_parts += [0] * (max_len - len(c_parts))
        l_parts += [0] * (max_len - len(l_parts))
        return l_parts > c_parts
    except Exception as e:
        logger.error(f"Failed to parse version: {e}")
        return False

def check_for_update(current_version: str) -> Optional[dict]:
    from config.settings_loader import load_settings
    settings = load_settings()
    url = settings.get("update_url")
    if not url:
        logger.info("Update URL not configured in settings")
        return None
    try:
        logger.info(f"Checking for updates at: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        latest_version = data.get("version")
        if latest_version and is_version_newer(current_version, latest_version):
            return {
                "version": latest_version,
                "download_url": data.get("download_url"),
                "sha256": data.get("sha256"),
                "changelog": data.get("changelog", "")
            }
    except Exception as e:
        logger.error(f"Error checking for updates: {e}")
    return None

def download_update(url: str, dest_path: str, progress_callback=None) -> bool:
    try:
        logger.info(f"Downloading update from {url} to {dest_path}")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        downloaded = 0
        
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback and total_size > 0:
                        progress_callback(downloaded / total_size)
        return True
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return False

def verify_sha256(file_path: str, expected_hash: str) -> bool:
    if not expected_hash:
        logger.warning("No expected SHA-256 hash provided, skipping verification")
        return True
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        calculated = sha256_hash.hexdigest().lower()
        match = calculated == expected_hash.lower()
        if not match:
            logger.error(f"Hash mismatch! Calculated: {calculated}, Expected: {expected_hash}")
        else:
            logger.info("SHA-256 hash successfully verified")
        return match
    except Exception as e:
        logger.error(f"Hash verification failed: {e}")
        return False

def apply_update(new_exe_path: str, current_exe_path: str) -> bool:
    if not is_frozen():
        logger.warning("Not running as frozen EXE, update swap skipped.")
        return False
        
    current_pid = os.getpid()
    temp_dir = os.path.dirname(new_exe_path)
    bat_path = os.path.join(temp_dir, "update.bat")
    
    # We must generate the bat script to swap the files
    # The batch script waits for PID to exit, copies the file, restarts the app, and deletes itself
    bat_content = f"""@echo off
chcp 65001 > nul
echo Ожидание завершения работы StudyPack AI...
timeout /t 2 /nobreak > nul

:wait_loop
tasklist /FI "PID eq {current_pid}" 2>NUL | find /I "{current_pid}" >NUL
if %ERRORLEVEL% equ 0 (
    timeout /t 1 /nobreak > nul
    goto wait_loop
)

echo Обновление файлов...
copy /y "{new_exe_path}" "{current_exe_path}"
if %ERRORLEVEL% equ 0 (
    echo Запуск обновлённой версии...
    start "" "{current_exe_path}"
) else (
    echo Ошибка при обновлении исполняемого файла! > "{os.path.join(temp_dir, "update_error.txt")}"
)

del "%~f0"
"""
    try:
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(bat_content)
        
        logger.info(f"Launching updater batch script: {bat_path}")
        subprocess.Popen([bat_path], shell=True)
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to apply update: {e}")
        return False
