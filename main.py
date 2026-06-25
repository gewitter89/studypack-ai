#!/usr/bin/env python3
import os
import sys
import logging

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.cli import setup_argparser, run_cli
try:
    from app.premium_ui import PremiumStudyPackUI as GUI_CLASS
except ImportError:
    from app.gui import StudyPackGUI as GUI_CLASS


def setup_logging():
    from core.paths import logs_dir, ensure_dirs
    ensure_dirs()
    log_file = os.path.join(logs_dir(), "app.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("StudyPack AI started")

    parser = setup_argparser()
    args = parser.parse_args()

    if args.cli:
        run_cli(args)
    else:
        try:
            gui = GUI_CLASS()
            gui.run()
        except ImportError as e:
            print(f"Ошибка: не удалось запустить GUI. {e}")
            print("Убедитесь, что tkinter установлен.")
            print("Запустите с флагом --cli для командной строки.")
            sys.exit(1)


if __name__ == "__main__":
    main()
