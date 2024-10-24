import csv
from config import WHITE_LIST_FILE, WHITE_LIST_COLUMNS, BLACKLIST_FILE
import os
def is_user_in_whitelist(user_id):
    try:
        with open(WHITE_LIST_FILE, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return any(str(user_id) == row['id'] for row in reader)
    except FileNotFoundError:
        return False

def is_user_admin(user_id):
    try:
        with open(WHITE_LIST_FILE, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if str(user_id) == row['id']:
                    return row['is_admin'] == 'true'
    except FileNotFoundError:
        return False
    return False

def get_all_admins():
    admin_ids = []
    try:
        with open(WHITE_LIST_FILE, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['is_admin'] == 'true':
                    admin_ids.append(row['id'])
    except FileNotFoundError:
        print("White list file not found.")
    return admin_ids

def add_user_to_whitelist(user_data):
    with open(WHITE_LIST_FILE, "a", newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=WHITE_LIST_COLUMNS)
        if file.tell() == 0:
            writer.writeheader()
        writer.writerow(user_data)


def approve_user(bot, call):
    parts = call.data.split("_")
    if len(parts) < 3:
        bot.send_message(call.message.chat.id, "Error: Invalid data format")
        return

    user_id = parts[1]
    username = "_".join(parts[2:])  # Join all remaining parts as the username

    user_data = {
        "id": user_id,
        "username": username,
        "name": "N/A",
        "is_admin": "false",
        "lecture_notification": "true",
        "lab_notification": "true"
    }
    add_user_to_whitelist(user_data)
    bot.send_message(user_id, "Вам надано доступ до боту! Приємного користування! ")
    bot.send_message(user_id, "Для початку роботи введіть /start")
    bot.send_message(call.message.chat.id, f"Користувач {username} (ID: {user_id}) доданий в список.")


def toggle_notification(user_id, notification_type):
    users = []
    try:
        # Відкриваємо файл для читання
        with open(WHITE_LIST_FILE, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            users = list(reader)  # Читаємо всі дані у список

        # Оновлюємо статус сповіщення для конкретного користувача
        for user in users:
            if user['id'] == str(user_id):
                if notification_type == 'lecture':
                    # Перемикаємо сповіщення для пар
                    if user['lecture_notification'] == 'True':
                        user['lecture_notification'] = 'False'
                    else:
                        user['lecture_notification'] = 'True'
                elif notification_type == 'lab':
                    # Перемикаємо сповіщення для лабораторних/практичних
                    if user['lab_notification'] == 'True':
                        user['lab_notification'] = 'False'
                    else:
                        user['lab_notification'] = 'True'
                break

        # Пишемо оновлені дані назад у файл
        with open(WHITE_LIST_FILE, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = ['id', 'username', 'name', 'is_admin', 'lecture_notification', 'lab_notification']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(users)

    except Exception as e:
        print(f'Error: {e}')
def get_user_notifications(user_id):
    try:
        # Читаємо дані з CSV файлу
        with open(WHITE_LIST_FILE, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for user in reader:
                if user['id'] == str(user_id):
                    return user['lecture_notification'], user['lab_notification']
        return None, None
    except Exception as e:
        print(f'Error: {e}')
        return None, None
#BLACKLIST
if not os.path.exists(BLACKLIST_FILE):
    with open(BLACKLIST_FILE, 'w') as f:
        f.write("user_id,username\n")
def add_to_blacklist(user_id, username):
    with open(BLACKLIST_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([user_id, username])
def get_blacklist():
    with open(BLACKLIST_FILE, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        return list(reader)
def remove_from_blacklist(user_id):
    rows = get_blacklist()
    with open(BLACKLIST_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["user_id", "username"])  # Перезаписуємо заголовок
        for row in rows:
            if row[0] != user_id:  # Пропускаємо користувача, якого треба видалити
                writer.writerow(row)
if not os.path.exists(BLACKLIST_FILE):
    with open(BLACKLIST_FILE, 'w') as f:
        f.write("user_id,username\n")


def is_user_blacklisted(user_id):
    try:
        blacklist = get_blacklist()
        user_id_str = str(user_id)

        # Перевіряємо чи є user_id в першій колонці (індекс 0)
        # row[0] - user_id, row[1] - username
        for row in blacklist:
            if row and row[0] == user_id_str:
                return True
        return False
    except Exception as e:
        print(f"Помилка при перевірці чорного списку: {e}")
        return False