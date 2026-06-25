# Telegram Sales Bot Audit

This document reviews the Telegram Sales Bot implementation, active features, security risks, and business relevance.

---

## 1. Core Findings and Answers

### 1. Is the bot implemented or just a plan?
The bot is fully implemented and operational as a Python script in `scripts/tg_sales_bot.py`. It uses the `pyTelegramBotAPI` library.

### 2. What can the bot do?
*   **User Interface**: Greets users and displays a keyboard with menu options (🎁 Download demo, 💰 Buy generator, 🔑 Activate program, 💬 Support).
*   **Demo Ingestion**: Sends a sample PDF (`examples/6_uk_preschool_animals.pdf`) to users requesting free packs.
*   **Payment & Verification Flow**: Displays Monobank card payment details. It accepts screenshot uploads from users, forwards the receipts to the administrator's chat with inline verification buttons (`Approve` / `Reject`), and updates user status in `bot_data.json`.
*   **Key Generation**: Automatically generates activation keys for approved users who submit their Hardware ID.
*   **Admin Panel**: Provides command interfaces for the admin chat:
    *   `/keygen HWID` - Manual activation key generation.
    *   `/stats` - Shows user numbers, active sales, generated keys, and estimated revenues.
    *   `/broadcast <text>` - Broadcasts messages to all bot users.

### 3. Does it run without a token?
No. The script initializes the API using `telebot.TeleBot(BOT_TOKEN)`. If the default placeholder (`"YOUR_BOT_TOKEN_HERE"`) is kept and the environment variable `TELEGRAM_BOT_TOKEN` is missing, the script will crash or fail to connect.

### 4. Is there a data leak risk?
Yes. The bot writes user details, roles, purchase flags, and generated serial keys directly to a local JSON file (`bot_data.json`) in the project root directory. If this file is accidentally packaged into the release ZIP or committed to Git, buyer data (Telegram IDs, user names) will leak.

### 5. Are there real secrets in the code?
*   **API Tokens**: No. The bot safely relies on environment variables (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_ADMIN_CHAT_ID`) and defaults to placeholders.
*   **Personal Data**: Yes. Line 24 contains a real recipient name (`"Александр Х."`) and card placeholder text for payments, which could identify the developer.

### 6. Is the bot needed now?
**No**. Because we are not selling the generator software executable (and the PDF generation files are currently handled manually), a sales assistant bot is premature. It creates unnecessary support channels and database overhead.

### 7. Should we leave, delete, or postpone?
**Postpone and isolate**. The code is written and works, but it should be moved out of the active codebase to prevent it from being packaged or run. We should remove the `pyTelegramBotAPI` dependency from the main requirements file to keep the application lightweight.
