import csv
from telebot import types
from config import INVITES_FILE, INVITE_COLUMNS, WHITE_LIST_FILE


# Функція перевірки, чи є користувач адміністратором
def is_user_admin(user_id):
    try:
        with open(WHITE_LIST_FILE, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if str(user_id) == row['id']:
                    return row['is_admin'] == 'true'
    except FileNotFoundError:
        return False
    return False


# Додавання інвайту з кнопкою та папкою виключно для адміністраторів
def add_invite_button_for_admin(bot, message, text, url, folder="default"):
    user_id = message.from_user.id

    if is_user_admin(user_id):
        with open(INVITES_FILE, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([text, url, folder])
        bot.send_message(user_id, f"Кнопка з текстом '{text}' і URL '{url}' додана в папку '{folder}'")
    else:
        bot.send_message(user_id, "У вас немає прав на додавання інвайтів. Тільки адміністратор може це робити.")




# Перевірка, чи існує папка
def folder_exists(folder_name):
    with open(INVITES_FILE, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) > INVITE_COLUMNS['folder'] and row[INVITE_COLUMNS['folder']] == folder_name:
                return True
    return False


# Отримання інвайтів по папці
def get_invites_by_folder(folder):
    invites = []
    with open(INVITES_FILE, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) > INVITE_COLUMNS['folder'] and row[INVITE_COLUMNS['folder']] == folder:
                invites.append({
                    'text': row[INVITE_COLUMNS['text']],
                    'url': row[INVITE_COLUMNS['url']]
                })
    return invites


# Створення клавіатури з інвайтами для певної папки
def create_invite_keyboard_by_folder(folder):
    invites = get_invites_by_folder(folder)
    keyboard = types.InlineKeyboardMarkup()
    for invite in invites:
        button = types.InlineKeyboardButton(text=invite['text'], url=invite['url'])
        keyboard.add(button)
    return keyboard

def get_available_folders():
    folders = set()
    with open(INVITES_FILE, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 3:
                folders.add(row[2])  # Assuming folder is the third column
    return list(folders)