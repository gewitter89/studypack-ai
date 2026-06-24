#!/usr/bin/env python3
import os
import sys
import logging

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.cli import setup_argparser, run_cli
from app.gui import StudyPackGUI


def setup_logging():
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, "app.log")

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
            gui = StudyPackGUI()
            gui.run()
        except ImportError as e:
            print(f"Ошибка: не удалось запустить GUI. {e}")
            print("Убедитесь, что tkinter установлен.")
            print("Запустите с флагом --cli для командной строки.")
            sys.exit(1)


if __name__ == "__main__":
    main()
