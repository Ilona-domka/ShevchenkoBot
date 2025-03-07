import logging
import random
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Встановлення логування
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


# Функція для зчитування віршів з файлу
def read_poems():
    try:
        with open(r'D:\bot\ShevchenkoBot\shevchenko_poems.txt', 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Помилка при зчитуванні файлу: {e}")
        return ""


# Функція для пошуку уривка з урахуванням мінімальної довжини
def find_random_poem_segment(query, text):
    if not text.strip():
        return None, "Файл з віршами порожній або не завантажений."

    # Перевірка на пошук по фразі (не по окремих словах)
    if len(query.split()) > 1:
        return find_poem_by_phrase(query, text)

    keywords = query.lower().split()
    matches = []

    # Розбиваємо текст на рядки
    lines = text.split("\n")

    for i, line in enumerate(lines):
        for keyword in keywords:
            if re.search(rf'\b{re.escape(keyword)}\b', line, re.IGNORECASE):
                # Починаємо з поточного рядка
                start_idx = i
                end_idx = i

                # Розширюємо вибір, щоб було хоча б 3 рядки
                while start_idx > 0 and (end_idx - start_idx) < 2:  # мінімум 3 рядки
                    start_idx -= 1
                while end_idx < len(lines) - 1 and (end_idx - start_idx) < 3:  # максимум 4 рядки
                    end_idx += 1

                # Прив'язка до розділових знаків кінця речення
                while start_idx > 0 and not re.search(r'[.!?;]', lines[start_idx]):
                    start_idx -= 1
                while end_idx < len(lines) - 1 and not re.search(r'[.!?;]', lines[end_idx]):
                    end_idx += 1

                matches.append("\n".join(lines[start_idx:end_idx + 1]))

    if matches:
        chosen_keyword = random.choice(keywords)  # Випадкове слово з запиту
        chosen_poem = random.choice(matches)  # Випадковий уривок
        chosen_poem = f"*{chosen_poem}...*"  # Курсив + три крапки

        return chosen_keyword, chosen_poem

    return None, "Не знайшов підходящих віршів."


# Функція для пошуку по фразі
def find_poem_by_phrase(query, text):
    if not text.strip():
        return None, "Файл з віршами порожній або не завантажений."

    matches = []

    # Розбиваємо текст на рядки
    lines = text.split("\n")

    # Розділяємо фразу на слова
    words = query.lower().split()

    # Пошук фрази у тексті
    for i, line in enumerate(lines):
        # Перевіряємо, чи містить рядок усі слова з фрази
        if all(word in line.lower() for word in words):
            # Починаємо з поточного рядка
            start_idx = i
            end_idx = i

            # Розширюємо вибір, щоб було хоча б 3 рядки
            while start_idx > 0 and (end_idx - start_idx) < 2:  # мінімум 3 рядки
                start_idx -= 1
            while end_idx < len(lines) - 1 and (end_idx - start_idx) < 3:  # максимум 4 рядки
                end_idx += 1

            # Прив'язка до розділових знаків кінця речення
            while start_idx > 0 and not re.search(r'[.!?;]', lines[start_idx]):
                start_idx -= 1
            while end_idx < len(lines) - 1 and not re.search(r'[.!?;]', lines[end_idx]):
                end_idx += 1

            matches.append("\n".join(lines[start_idx:end_idx + 1]))

    if matches:
        chosen_poem = random.choice(matches)  # Випадковий уривок
        chosen_poem = f"*{chosen_poem}...*"  # Курсив + три крапки

        return query, chosen_poem

    return None, "Не знайшов підходящих віршів."


# Команда /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Привіт! Напиши мені слово чи питання, і я підберу відповідь з віршів Шевченка.")


# Обробка повідомлень
async def reply_poem(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    text = read_poems()
    chosen_keyword, response = find_random_poem_segment(user_message, text)

    if chosen_keyword:
        await update.message.reply_text(f"То *{chosen_keyword}* тривожить твою душу...", parse_mode="Markdown")
        await update.message.reply_text(response, parse_mode="Markdown")  # Відправляємо вірш окремим повідомленням
        await update.message.reply_text("Із 'Кобзаря' Т. Шевченка", parse_mode="Markdown")  # Додаємо підпис
    else:
        await update.message.reply_text(response)


# Головна функція для запуску бота
def main():
    token = '8090719010:AAGwfy37bdnwsC5kUIDZxuIQZEKBScl9N4o'
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_poem))

    # Заміна polling на webhook
    application.run_webhook(
        listen="0.0.0.0",  # Це дозволяє отримувати запити з будь-якого IP
        port=5000,  # Вказуємо порт для веб-сервера
        url_path=token,  # шлях для запитів webhook
        webhook_url="https://shevchenkobot.onrender.com".format(token)  # URL для webhook (посилання на ваш сервер)
    )

if __name__ == '__main__':
    main()
