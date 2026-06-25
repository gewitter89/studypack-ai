# Release Package Audit

This document reviews the compiled standalone executable package, bundled files, activation logic, and user readiness.

---

## 1. Core Findings and Answers

### 1. Is there a compiled EXE?
Yes. A standalone Windows executable is present.

### 2. Where does it lie?
It is located at `release/StudyPack AI.exe`. Its size is approximately 76.7 MB.

### 3. What is included in the `release/` folder?
The folder contains:
*   `StudyPack AI.exe` (the compiled program).
*   `README.txt` (User instructions).
*   `.env.example` (Environment variables template for API configuration).
*   `examples/` directory containing 12 sample files (6 JSON and 6 corresponding PDFs) demonstrating output worksheets.

### 4. Have any redundant or sensitive files leaked into the release?
*   **Outside the EXE (in folder)**: No. Writable configuration logs (`logs/app.log`), local memory states, and the active `.env` file containing real OpenRouter keys are excluded from the `release/` directory.
*   **Inside the EXE (compiled resources)**: Yes. PyInstaller bundles all Python files in the path. This means `core/licensing.py` (with the salt and master key), `scripts/keygen.py`, and `scripts/tg_sales_bot.py` are packaged inside the binary. Anyone who extracts the executable can access these scripts.

### 5. Does the EXE run?
Yes. The compiled program starts up and displays the Tkinter canvas.

### 6. Does the EXE require a license?
**Yes**. Because the executable is compiled (flagged as `sys.frozen == True`), the code bypasses developer mode. Upon launch, it runs the `is_activated()` check, which fails if `license.key` is missing. This pops up the activation prompt.

### 7. Can an ordinary user understand how to run it?
Yes, the `README.txt` file explains the setup clearly. However, users will be blocked immediately at startup by the activation lock. They cannot generate their own keys without the `keygen.py` tool or the Telegram bot.

### 8. Can this release package be distributed to clients?
**No**.
1.  **Software Lock**: Customers cannot run it unless you manually generate activation keys for them or they use the universal master key.
2.  **Weak Security**: Distributing this EXE gives away the compiled `core/licensing.py` file, exposing the hardcoded salt and master key to extraction.
3.  **Business Model**: Our target is selling high-quality PDF worksheets, not the generator program. Distributing the generator software is unnecessary for this phase.
