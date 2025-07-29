# Remember Bot

A simple Telegram bot to remember and recall user messages, with support for both Persian and English, and persistent storage using PostgreSQL.

## Features
- Remembers any message you send (except questions ending with `?` or `؟`)
- Recalls your memories when you ask a question
- Supports both Persian and English
- Persistent storage using PostgreSQL
- Secure configuration using `.env` file

## Setup

1. **Clone the repository**

2. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   - Copy `.env.example` to `.env` (if provided) or create `.env` manually:
     ```env
     TELEGRAM_BOT_TOKEN=your-telegram-bot-token
     POSTGRES_DSN=your-postgres-dsn
     ```

4. **Run the bot**
   ```sh
   python3 bot.py
   ```

## Environment Variables
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `POSTGRES_DSN`: Your PostgreSQL connection string

## Database
The bot will automatically create a `memories` table in your PostgreSQL database if it does not exist.

## .gitignore
Sensitive files like `.env` and database files are ignored by git.

## License
MIT
