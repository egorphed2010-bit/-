from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import random
from telegram.ext import MessageHandler, filters
import os
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent

with open(BASE_DIR / "lessons.json", "r", encoding="utf-8") as f:
    LESSONS = json.load(f)

user_data = {}

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет, я бот для изучения немецкого языка по текстам :)"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Команды:\n"
        "/command1 - новый урок\n"
        "/command2 - информация о боте\n"
        "/command3 - помощь"
    )

last_text = None

async def command1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lesson = random.choice(LESSONS)

    user_id = update.effective_user.id

    user_data[user_id] = {
        "lesson": lesson,
        "question_index": 0,
        "mistakes": 0
    }

    await update.message.reply_text("📚 Начинаем новый урок!")

    await update.message.reply_text(lesson["text"])

    await update.message.reply_text(
        lesson["questions"][0]["question"]
    )

async def command2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ Это бот, который помогает изучать немецкий язык с помощью текстов\n (This is a bot that helps you learn German using texts.)"
    )

async def command3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/new_lesson — начать новый урок\n"
        "/info — информация о боте\n"
        "/help — помощь\n"
        "/translate – перевод(доступно после 2х ошибок)\n"
        "/stop – завершить урок"
    )

async def command4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in user_data:
        await update.message.reply_text("Сначала начните урок.")
        return

    if user_data[user_id]["mistakes"] < 2:
        await update.message.reply_text(
            "Перевод станет доступен после 2 неверных ответов подряд."
        )
        return

    lesson = user_data[user_id]["lesson"]

    await update.message.reply_text(
        lesson["translation"]
    )

async def check_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in user_data:
        return

    state = user_data[user_id]

    answer = update.message.text.strip().lower()

    question_index = state["question_index"]

    correct_answers = (
        state["lesson"]["questions"][question_index]["answers"]
    )
    
    if answer.lower() in [a.lower().strip() for a in correct_answers]:

        if question_index == 0:

            state["question_index"] = 1

            await update.message.reply_text(
                "✅ Ответ верный!"
            )

            await update.message.reply_text(
                state["lesson"]["questions"][1]["question"]
            )

        else:

            await update.message.reply_text(
                "🎉 Ответ верный, поздравляю! Урок завершён."
            )

            del user_data[user_id]

    else:

        state["mistakes"] += 1

        await update.message.reply_text(
            "❌ Ответ неверный, попробуйте снова."
        )

        if state["mistakes"] >= 2:
            await update.message.reply_text(
                "Теперь доступна команда /command4 - перевод текста"
            )

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in user_data:
        del user_data[user_id]
        await update.message.reply_text(
            "🛑 Урок остановлен.\n"
            "Чтобы начать новый урок, используйте /newlesson."
        )
    else:
        await update.message.reply_text(
            "Сейчас у вас нет активного урока."
        )

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    app.add_handler(CommandHandler("new_lesson", command1))
    app.add_handler(CommandHandler("info", command2))
    app.add_handler(CommandHandler("help", command3))
    app.add_handler(CommandHandler("translate", command4))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, check_answer)
)

    print("Бот запущен...")
    app.run_polling()



if __name__ == "__main__":
    main()