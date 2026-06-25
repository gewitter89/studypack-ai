# Changed Files Summary

This document lists all changed and newly introduced files in the StudyPack AI project. It groups them by status and provides their purpose, category, and risk assessment.

## Summary Table

| File | Status | Purpose | Category | Risk / Warning |
| ---- | ------ | ------- | -------- | -------------- |
| `main.py` | [MODIFY] | Startup entry point, loads environment vars, runs CLI or Premium GUI | Application Core | Low. Added logging and `.env` loading, standard behavior. |
| `requirements.txt` | [MODIFY] | Added new dependencies like `customtkinter` and `pyinstaller` | Project Config | Low. Necessary for GUI and packaging. |
| `build.bat` | [MODIFY] | Automated PyInstaller compilation script | Build Scripts | Low. Standard compilation automation. |
| `StudyPack AI.spec` | [MODIFY] | PyInstaller spec file for standalone EXE bundle | Build Scripts | Low. Defines bundled assets and paths. |
| `config/settings.json` | [MODIFY] | Configures default model, temperature, retries, and UI preferences | App Configuration | Low. |
| `ai/__init__.py` | [MODIFY] | Import adjustments | AI Pipeline | Low. |
| `ai/openrouter_client.py` | [MODIFY] | AI client communication improvements | AI Pipeline | Low. |
| `ai/cascade_client.py` | **[NEW]** | Multi-provider client wrapper (OpenRouter/Groq/etc.) | AI Pipeline | Low. |
| `app/gui.py` | [MODIFY] | Standard TKinter GUI, integrated with licensing checks and auto-updates | User Interface | **Medium**. Blocks interface unless validated via `core/licensing`. |
| `app/premium_ui.py` | [MODIFY] | CustomTkinter-based premium user interface with dark/light themes | User Interface | **Medium**. Blocks interface unless validated via `core/licensing`. |
| `core/licensing.py` | **[NEW]** | Node/HWID check, verification formula, salt, and license verification | Licensing & Sales | **High**. Uses simple symmetric hashing with hardcoded salt. Contains universal master key. |
| `core/paths.py` | [MODIFY] | Single-EXE path resolver using `sys._MEIPASS` and user directories | Application Core | Low. Correctly separates read-only resources and writable configurations. |
| `core/updater.py` | **[NEW]** | Simple version checker for auto-updates | App Configuration | Low. Standard version checker. |
| `core/generator.py` | [MODIFY] | Generates worksheets page-by-page or in blocks, handles file output | PDF Generation | Low. Added support for commercial mode. |
| `core/card_text_gen.py` | [MODIFY] | Generates texts/questions/answers for child worksheets | PDF Generation | **Medium**. Uses Cyrillic 'о' instead of a symbol for circle tasks, leading to odd answers. |
| `core/templates.py` | [MODIFY] | Offline preset rendering layout rules and page selection | PDF Generation | **Medium**. Presets contain Russian grade labels ("Дошкольник") leaking to Ukrainian PDF. |
| `core/quality_gate.py` | [MODIFY] | Evaluates worksheet content for placeholders, brands, AI tone, lang mixing | PDF Generation | Low. Quality verification. |
| `core/postprocess.py` | [MODIFY] | Editorial pass and quality score calculator | PDF Generation | Low. |
| `core/topic_injector.py` | [MODIFY] | Injects vocabulary words based on chosen theme into worksheet tasks | PDF Generation | Low. |
| `core/topic_lexicon.py` | [MODIFY] | Contains dictionary of theme words in RU, UK, EN | PDF Generation | Low. |
| `core/math_checker.py` | [MODIFY] | Validates arithmetic task answers mathematically | PDF Generation | Low. |
| `pdf/renderer.py` | [MODIFY] | Custom ReportLab PDF generator, draws watermark, covers, page decorations | PDF Generation | **Medium**. Rotated text watermark blocks worksheet usage in demo mode. |
| `scripts/keygen.py` | **[NEW]** | Command-line activation key generator tool | Licensing & Sales | **High**. Exposes the universal master bypass key when run. |
| `scripts/tg_sales_bot.py` | **[NEW]** | Telegram sales assistant with receipt verification and HWID activation | Licensing & Sales | **Medium**. Standard bot but contains Alexander Kh. card numbers/name. |
| `tests/test_licensing.py` | **[NEW]** | Test suite for hardware ID check, master key, and key verification | Testing | Low. |
| `installer/setup.iss` | **[NEW]** | Inno Setup configuration script to create Windows installers | Packaging | Low. |
| `sales_pack_v2/` | **[NEW]** | Folder with OLX/TG promotional copy, pricing structure, outreach sheets | Licensing & Sales | Low. |
| `release/StudyPack AI.exe` | **[NEW]** | 76MB compiled PyInstaller binary | Executable | **Medium**. Executable requires a license key on startup. |
