# Security Warnings and Vulnerabilities Log

This log lists security risks, vulnerabilities, and engineering concerns discovered during the technical audit of StudyPack AI.

---

## Active Risk Log

### Risk 1: Hardcoded Master Key
*   **Severity**: **CRITICAL**
*   **Target File**: `core/licensing.py` (Line 8)
*   **Vulnerability**: The master bypass key (`"STUDYPACK-DEV-MASTER-BYPASS-KEY"`) is stored in plain text.
*   **Impact**: Anyone who finds this key in the code, git logs, or decompiles the executable can bypass licensing checks on any computer.
*   **Resolution**: Delete the licensing check and remove the master key from the codebase completely.

---

### Risk 2: Hardcoded Cryptographic Salt (Symmetric Protection)
*   **Severity**: **HIGH**
*   **Target File**: `core/licensing.py` (Line 7)
*   **Vulnerability**: The salt (`"StudyPackAI_Premium_Secured_2026_Salt_#"`) used to generate serial keys from machine HWIDs is hardcoded in the source code.
*   **Impact**: Since the verification algorithm is stored inside the compiled executable, an attacker can extract the salt using Python decompilers and generate valid license serial keys for any hardware ID.
*   **Resolution**: If licensing is required in the future, transition to an asymmetric signature model (RSA/ECDSA) where the program only contains a public key to verify signatures, while the private signing key remains on the developer's server.

---

### Risk 3: Antivirus False-Positives (HWID Inspection & Packaging)
*   **Severity**: **MEDIUM**
*   **Target File**: `core/licensing.py` (Lines 17, 29) & `StudyPack AI.exe`
*   **Vulnerability**: The program runs shell subprocesses to fetch hardware data (`wmic csproduct get uuid` and `wmic bios get serialnumber`).
*   **Impact**: Antivirus software (such as Windows Defender) frequently flags PyInstaller single-executable files that run command-line tools or look up system serial numbers as malicious or Trojan-like. This blocks users from opening the tool.
*   **Resolution**: Avoid queries to Windows motherboard UUID or BIOS serials via command line. Use standard, non-intrusive APIs or a simple file-based configuration. Better yet, remove licensing entirely as we are not selling the generator executable.

---

### Risk 4: Bundled Selling Bot & Personal Data
*   **Severity**: **MEDIUM**
*   **Target File**: `scripts/tg_sales_bot.py` (Line 24)
*   **Vulnerability**: The Telegram selling bot contains card numbers and a real developer name (`"Александр Х."`).
*   **Impact**: This script is compiled into the main executable during PyInstaller builds, putting personal financial routes at risk of extraction.
*   **Resolution**: Exclude the `scripts/` directory from PyInstaller packaging by updating the spec file, or remove the sales bot script from the repository.

---

### Risk 5: Weak Developer Mode Bypass
*   **Severity**: **LOW**
*   **Target File**: `core/licensing.py` (Line 92)
*   **Vulnerability**: Developer mode checks for `sys.frozen == False`.
*   **Impact**: While acceptable for testing, anyone running the raw Python files can bypass licensing immediately.
*   **Resolution**: Use a local, git-ignored configuration flag (e.g. checking for a `.dev_mode` file) rather than checking the PyInstaller execution state.
