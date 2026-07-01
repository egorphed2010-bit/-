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

stats_file = BASE_DIR / "stats.json"

if stats_file.exists():
    with open(stats_file, "r", encoding="utf-8") as f:
        user_stats = json.load(f)
else:
    user_stats = {}

def save_stats():
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(user_stats, f, ensure_ascii=False, indent=4)

user_data = {}
user_stats = {}

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет, я бот для изучения немецкого языка по текстам :)\n Hi, I'm a bot for learning German by text :) "
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Команды:\n"
        "/new_lesson — начать новый урок\n"
        "/info — информация о боте\n"
        "/help — помощь\n"
        "/translate – перевод(доступно после 2х ошибок)\n"
        "/stop – завершить урок"
    )

last_text = None

async def command1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lesson = random.choice(LESSONS)

    user_id = str(update.effective_user.id)

    if user_id not in user_stats:
        user_stats[user_id] = {
        "lessons": 0,
        "correct_answers": 0,
        "wrong_answers": 0
    }

    selected_questions = random.sample(lesson["questions"], 2)

    user_data[user_id] = {
        "lesson": lesson,
        "questions": selected_questions,
        "question_index": 0,
        "mistakes": 0
    }

    await update.message.reply_text("📚 Начинаем новый урок!")

    await update.message.reply_text(lesson["text"])

    await update.message.reply_text(
        selected_questions[0]["question"]
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
    state["questions"][question_index]["answers"]
    )
    
    if answer.lower() in [a.lower().strip() for a in correct_answers]:
    
        user_stats[user_id]["correct_answers"] += 1
        save_stats()
        
        if question_index == 0:

            state["question_index"] = 1

            await update.message.reply_text(
                "✅ Ответ верный!"
            )

            await update.message.reply_text(
                state["questions"][1]["question"]
            )

        else:
            user_stats[user_id]["wrong_answers"] += 1
            save_stats()
            
            user_stats[user_id]["lessons"] += 1
            save_stats()

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
                "Теперь доступна команда /translate - перевод текста"
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

async def stat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in user_stats:
        await update.message.reply_text(
            "У вас пока нет статистики."
        )
        return

    stats = user_stats[user_id]

    total_answers = (
        stats["correct_answers"] +
        stats["wrong_answers"]
    )

    if total_answers == 0:
        accuracy = 0
    else:
        accuracy = round(
            stats["correct_answers"] / total_answers * 100
        )

    await update.message.reply_text(
        f"📊 Ваша статистика\n\n"
        f"📚 Пройдено уроков: {stats['lessons']}\n"
        f"✅ Правильных ответов: {stats['correct_answers']}\n"
        f"❌ Неправильных ответов: {stats['wrong_answers']}\n"
        f"📈 Точность: {accuracy}%"
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
    app.add_handler(CommandHandler("stat", stat))
    app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, check_answer)
)

    print("Бот запущен...")
    app.run_polling()



if __name__ == "__main__":
    main()