from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import difflib
import re
import asyncpg
import os
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! I'm your memory bot (testing mode).")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use /remember to store something. Use /recall to see it later.")

POSTGRES_DSN = os.getenv("POSTGRES_DSN")

# Database setup: create table if not exists
async def init_db():
    conn = await asyncpg.connect(POSTGRES_DSN)
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            user_id TEXT,
            memory TEXT
        )
    ''')
    await conn.close()

async def save_non_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.message.from_user.id)
    if not text.startswith("/") and not (text.strip().endswith("?") or text.strip().endswith("؟")):
        conn = await asyncpg.connect(POSTGRES_DSN)
        await conn.execute(
            "INSERT INTO memories (user_id, memory) VALUES ($1, $2)",
            user_id, text
        )
        await conn.close()
        if is_persian(text):
            await update.message.reply_text("به حافظه‌ات اضافه شد! 🧠")
        else:
            await update.message.reply_text("Added to your memory! 🧠")

def is_persian(text):
    # Checks for Persian characters or Persian question mark
    return bool(re.search(r'[\u0600-\u06FF]|؟', text))

async def reply_if_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.message.from_user.id)
    persian = is_persian(text)
    conn = await asyncpg.connect(POSTGRES_DSN)
    rows = await conn.fetch("SELECT memory FROM memories WHERE user_id = $1", user_id)
    memories = [row["memory"] for row in rows]
    await conn.close()
    if memories:
        match = difflib.get_close_matches(text, memories, n=1, cutoff=0.3)
        if match:
            if persian:
                await update.message.reply_text(f"پاسخ احتمالی: {match[0]}")
            else:
                await update.message.reply_text(f"Possible answer: {match[0]}")
        else:
            if persian:
                await update.message.reply_text("پاسخی ندارم، می‌تونی بهم یاد بدی!")
            else:
                await update.message.reply_text("I don’t know the answer yet, but you can teach me!")
    else:
        if persian:
            await update.message.reply_text("هنوز چیزی برایت ذخیره نکرده‌ام.")
        else:
            await update.message.reply_text("I don’t have anything saved for you yet.")

async def remember(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    message = " ".join(context.args)
    if message:
        conn = await asyncpg.connect(POSTGRES_DSN)
        await conn.execute(
            "INSERT INTO memories (user_id, memory) VALUES ($1, $2)",
            user_id, message
        )
        await conn.close()
        await update.message.reply_text("Got it! ✅ I’ll remember that.")
    else:
        await update.message.reply_text("What should I remember? 🤔")

async def recall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    conn = await asyncpg.connect(POSTGRES_DSN)
    rows = await conn.fetch("SELECT memory FROM memories WHERE user_id = $1", user_id)
    memories = [row["memory"] for row in rows]
    await conn.close()
    if memories:
        reply = "\n".join(f"- {m}" for m in memories)
        await update.message.reply_text(f"Here's what you asked me to remember:\n{reply}")
    else:
        await update.message.reply_text("I don’t have anything saved for you yet.")


async def run_bot():
    await init_db()
    from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("remember", remember))
    app.add_handler(CommandHandler("recall", recall))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex(r".*[\?|؟]$"), save_non_question))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r".*[\?|؟]$"), reply_if_question))
    await app.run_polling()


if __name__ == "__main__":
   import asyncio
   import nest_asyncio
   nest_asyncio.apply()
   asyncio.run(run_bot())
