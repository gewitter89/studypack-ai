# Licensing System Audit

This document reviews the licensing implementation, cryptographic security, and business relevance of the activation code in StudyPack AI.

---

## 1. Core Findings and Answers

### 1. Is licensing implemented?
Yes, the licensing system is fully implemented in the codebase. Both `app/gui.py` and `app/premium_ui.py` check activation on startup, and they will block program usage and redirect to a licensing window if a valid key is not found.

### 2. Is there a master key?
Yes. A universal master bypass key is hardcoded in the codebase.
> [!CAUTION]
> Found universal master key in file `core/licensing.py` (line 8). This is a critical security risk. If this key is exposed in code repositories, screenshots, build logs, or README files, any compiled copy of StudyPack AI can be instantly activated on any PC.

### 3. Is there a developer bypass?
Yes. Inside `core/licensing.py` (line 92), the function `is_activated()` returns `True` immediately if `sys.frozen` is `False`. This means developers running the application from source code do not see the activation screen.

### 4. Is there a key that activates on any PC?
Yes, the hardcoded master key acts as a universal activator for any hardware configuration.

### 5. Where is the secret salt stored?
The cryptographic salt `SECRET_SALT = "StudyPackAI_Premium_Secured_2026_Salt_#"` is hardcoded inside `core/licensing.py` (line 7). 

### 6. Can you generate keys from the project?
Yes. Running `scripts/keygen.py --hwid <HWID>` allows offline key generation for any machine.

### 7. Is this a safe or weak scheme?
It is **extremely weak**. Because the salt is hardcoded inside the executable and symmetric hashing is used:
*   Any reverse-engineer or automated tool (such as `pyinstxtractor` + `pycdc`) can extract the byte code of `core/licensing.py` in seconds.
*   Once the `SECRET_SALT` and hashing formula are extracted, any third party can build their own key generator.
*   A correct implementation would use **Asymmetric Signatures (RSA/ECDSA)**: the application should only contain a public key to verify license signatures, while the private key remains secure on the creator's machine.

### 8. Is this licensing needed now?
**No**. The project's immediate business model is selling **PDF worksheets directly to clients** (parents, tutors) on OLX or Telegram. The generator application itself is not being sold as an executable. Locking the door to the generator tool does not help sell PDF files and diverts focus from worksheet quality.

### 9. What files should be rolled back/deleted?
*   `core/licensing.py` (To be deleted, and all startup imports/calls removed from `app/gui.py` and `app/premium_ui.py`)
*   `scripts/keygen.py` (To be deleted)
*   `tests/test_licensing.py` (To be deleted)
