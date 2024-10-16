from config import WHITE_LIST_FILE
import csv

def broadcast_message(bot, message, text):
    try:
        with open(WHITE_LIST_FILE, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    bot.send_message(row['id'], text)
                except Exception as e:
                    print(f"Не вдалося відправити повідомлення користувачу з ID {row['id']}: {e}")
    except FileNotFoundError:
        bot.send_message(message.chat.id, "Список порожній або відсутній.")