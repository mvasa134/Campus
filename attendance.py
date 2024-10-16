from telebot import types
import csv
from datetime import datetime
from config import WHITE_LIST_FILE, ATTENDANCE_FILE, COLUMNS




def start_attendance_check(bot):
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    attendance_data = {}
    try:
        with open(WHITE_LIST_FILE, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    keyboard = types.InlineKeyboardMarkup()
                    to_attentedmenu_button = types.InlineKeyboardButton(text="Меню присутності", callback_data="attendance1")
                    keyboard.add(to_attentedmenu_button)
                    bot.send_message(row['id'], "Чи будете ви на парах?", reply_markup=keyboard)
                    attendance_data[row['id']] = {
                        "username": row['username'],
                        "name": row['name'],
                        "date": current_date,
                        "attendance": "Не відповів",
                        "report": ""
                    }
                except Exception as e:
                    print(f"Не вдалося відправити повідомлення користувачу з ID {row['id']}: {e}")
    except FileNotFoundError:
        print("Список білого списку порожній або відсутній.")
    return attendance_data



def im_save_attendance_to_csv(attendance_data):
    try:
        with open(ATTENDANCE_FILE, "w", newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=COLUMNS)
            writer.writeheader()
            for user_id, data in attendance_data.items():
                writer.writerow({
                    "id": user_id,
                    "username": data["username"],
                    "name": data["name"],
                    "date": data["date"],
                    "attendance": data["attendance"],
                    "report": data["report"]
                })
    except Exception as e:
        print('error')




def im_send_attendance_to_admin(bot, admin_id):
    import os
    if os.path.exists(ATTENDANCE_FILE):
        try:
            with open(ATTENDANCE_FILE, 'rb') as file:
                bot.send_document(admin_id, file)
            print(f"Файл успішно відправлено адміністратору {admin_id}")
        except Exception as e:
            print(f"Помилка при відправці файлу адміністратору {admin_id}: {e}")
            bot.send_message(admin_id, f"Виникла помилка при відправці файлу: {e}")
    else:
        error_message = f"Файл з відмітками не знайдено за шляхом: {ATTENDANCE_FILE}"
        print(error_message)
        bot.send_message(admin_id, error_message)