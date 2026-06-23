from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import random
from telegram.ext import MessageHandler, filters
import os

LESSONS = [
    {
        "text": """Hallo!

Mein Name ist Anna.
Ich komme aus Berlin.
Ich lerne Deutsch.""",

        "translation": """Привет!

Меня зовут Анна.
Я из Берлина.
Я учу немецкий.""",

        "questions": [
            {
                "question": "Wie heißt die Person aus dem Text?",
                "answer": "анна"
            },
            {
                "question": "Woher kommt sie?",
                "answer": "из берлина"
            }
        ]
    }
]

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
        "ℹ️ Этот бот помогает изучать немецкий язык."
    )

async def command3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/command1 — начать новый урок\n"
        "/command2 — информация о боте\n"
        "/command3 — помощь"
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

    correct_answer = (
        state["lesson"]["questions"][question_index]["answer"]
    )

    if answer == correct_answer:

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

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    app.add_handler(CommandHandler("command1", command1))
    app.add_handler(CommandHandler("command2", command2))
    app.add_handler(CommandHandler("command3", command3))
    app.add_handler(CommandHandler("command4", command4))
    app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, check_answer)
)

    print("Бот запущен...")
    app.run_polling()



if __name__ == "__main__":
    main()