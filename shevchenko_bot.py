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
        with open(r'D:\bot\Нова папка\shevchenko_poems.txt', 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Помилка при зчитуванні файлу: {e}")
        return ""

# Функція для пошуку уривка з урахуванням мінімальної довжини
def find_poem_by_phrase(query, text):
    if not text.strip():
        logger.warning("Файл з віршами порожній або не завантажений.")
        return None, "Файл з віршами порожній або не завантажений."

    matches = []
    lines = text.split("\n")

    # Розбиваємо фразу на слова
    words = query.lower().split()
    logger.info(f"Шукаємо по фразі: {query}")

    # Пошук фрази у тексті
    for i, line in enumerate(lines):
        # Перевіряємо, чи містить рядок усі слова з фрази
        if all(word in line.lower() for word in words):
            logger.info(f"Знайдено збіг: {line}")
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
        # Обрізаємо перший рядок
        chosen_poem = "\n".join(chosen_poem.split("\n")[1:])
        return query, chosen_poem

    return None, "Не знайшов підходящих віршів."

# Функція для пошуку по слову (іменнику)
def find_poem_by_noun(query, text):
    if not text.strip():
        logger.warning("Файл з віршами порожній або не завантажений.")
        return None, "Файл з віршами порожній або не завантажений."

    matches = []
    lines = text.split("\n")

    logger.info(f"Шукаємо по слову: {query}")

    for i, line in enumerate(lines):
        if re.search(rf'\b{re.escape(query)}\b', line, re.IGNORECASE):
            logger.info(f"Знайдено збіг: {line}")
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
        # Обрізаємо перший рядок
        chosen_poem = "\n".join(chosen_poem.split("\n")[1:])
        return query, chosen_poem

    return None, "Не знайшов підходящих віршів."

# Команда /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Привіт! Напиши мені слово чи питання, і я підберу відповідь з віршів Шевченка.")

# Обробка повідомлень
async def reply_poem(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    text = read_poems()

    if not text.strip():
        await update.message.reply_text("Файл з віршами порожній або не завантажений.")
        return

    # Спочатку шукаємо фразу
    chosen_keyword, response = find_poem_by_phrase(user_message, text)

    if not chosen_keyword:  # Якщо фразу не знайшли, пробуємо шукати по іменнику
        chosen_keyword, response = find_poem_by_noun(user_message, text)

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

    application.run_polling()

if __name__ == '__main__':
    main()
