from telebot import types
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from attendance import start_attendance_check, im_save_attendance_to_csv
from scheduler import save_schedule_to_csv, load_schedule_from_csv
from user_management import is_user_in_whitelist, is_user_admin, approve_user, add_user_to_whitelist, get_all_admins, is_user_blacklisted,toggle_notification, get_user_notifications, get_blacklist, remove_from_blacklist
from invites import add_invite_button_for_admin, get_available_folders, get_invites_by_folder
from utils import broadcast_message
from config import INVITE_COLUMNS, BACK_BUTTON_TEXT, ATTENDANCE_FILE, DAYS_MAP
from time1 import get_current_time_data


attendance_data = {}
user_data = {}
is_adding_id = {}
admin_schedule = {}
pending_requests = {}
def register_handlers(bot):
    @bot.message_handler(commands=['start'])
    def start_menu(message):
        user_id = message.from_user.id

        # Якщо користувач не в білому списку
        if not is_user_in_whitelist(user_id):
            request_access(user_id, message)
            return
        if user_id == is_user_blacklisted(user_id):
            bot.send_message(user_id,'Ви в чорному списку')
        # Формування головного меню
        keyboard = types.InlineKeyboardMarkup(row_width=2)

        # Кнопки доступні для всіх користувачів
        attendance_button = types.InlineKeyboardButton(text="Відмітитись на парі📍", callback_data="attendance")
        invites_button = types.InlineKeyboardButton(text="Записи/конспект❗", callback_data="invites")
        schedule_button = types.InlineKeyboardButton(text="Розклад📚", callback_data="view_schedule")
        form_button = types.InlineKeyboardButton(text="Відрахування🗿", callback_data='vidrh')
        settings_button = types.InlineKeyboardButton(text='Налаштування⚙️', callback_data='settings')

        # Додаємо загальні кнопки для користувачів
        keyboard.add(attendance_button, invites_button)
        keyboard.add(schedule_button, form_button)

        # Якщо користувач є адміністратором, додаємо додаткові кнопки
        if is_user_admin(str(user_id)):
            broadcast_button = types.InlineKeyboardButton(text='Розсилка📪', callback_data="broadcast")
            add_invite_button = types.InlineKeyboardButton(text="Додати посилання", callback_data="addinvite")
            blacklist_button = types.InlineKeyboardButton(text="Чорний список🕯", callback_data="blacklist")

            # Додаємо кнопки адміністратора
            keyboard.add(blacklist_button, add_invite_button)
            keyboard.add(broadcast_button, settings_button)
        else:
            # Якщо користувач не адміністратор, додаємо лише налаштування
            keyboard.add(settings_button)

        # Відправляємо меню
        bot.send_message(
            user_id,
            "Привіт! Я – бот ІК-44, створений спеціально для студентів, щоб полегшити ваше навчання та організацію групових справ!😉",
            reply_markup=keyboard
        )

        # --- Функція для запиту доступу ---

    def request_access(user_id, message):
        keyboard = types.InlineKeyboardMarkup()

        # Кнопки для схвалення та ігнорування запиту
        approve_button = types.InlineKeyboardButton(
            text="Схвалити✅", callback_data=f"approve_{user_id}_{message.from_user.username}"
        )
        ignore_button = types.InlineKeyboardButton(
            text="Ігнорувати❌", callback_data=f"ignore_{user_id}_{message.from_user.username}"
        )

        keyboard.add(approve_button, ignore_button)

        # Зберігаємо ID повідомлень для всіх адміністраторів
        pending_requests[user_id] = []

        # Надсилаємо повідомлення всім адміністраторам
        admin_id=407976503

        msg = bot.send_message(
            admin_id,
            f"Користувач {message.from_user.username} {message.from_user.first_name} (ID: {user_id}) запитує доступ.",
            reply_markup=keyboard
            )
        pending_requests[user_id].append((admin_id, msg.message_id))

        # Інформуємо користувача про очікування доступу
        bot.send_message(user_id, "У вас немає доступу! Очікуйте схвалення!")

    @bot.callback_query_handler(func=lambda call: call.data.startswith('approve_'))
    def whitelist_user(call):
        parts = call.data.split('_')
        user_id, username = parts[1], "_".join(parts[2:])

        user_data = {
            "id": user_id,
            "username": username,
            "name": "N/A",
            "is_admin": "false",
            "lecture_notification": "true",
            "lab_notification": "true"
        }
        add_user_to_whitelist(user_data)  # Add user to whitelist
        keyus = InlineKeyboardMarkup()
        keyus.add(InlineKeyboardButton(text='Перейти до головного меню', callback_data='back_to_start'))
        bot.send_message(user_id, "Вам надано доступ до боту! Приємного користування!",reply_markup=keyus)

        # Notify admin that the user has been approved
        bot.answer_callback_query(call.id, "Користувача додано до списку.")
        disabled_keyboard = types.InlineKeyboardMarkup()
        disabled_button = types.InlineKeyboardButton(
            text="Запит схвалено ✅",
            callback_data="disabled"
        )
        disabled_keyboard.add(disabled_button)

        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=disabled_keyboard)

        # Notify the user that they have been approved


    @bot.callback_query_handler(func=lambda call: call.data.startswith('ignore_'))
    def ignore_user(call):
        parts = call.data.split('_')
        user_id, username = parts[1], "_".join(parts[2:])

        # Notify admin that the user has been ignored
        bot.answer_callback_query(call.id, "Користувача проігноровано.")
        disabled_keyboard = types.InlineKeyboardMarkup()
        disabled_button = types.InlineKeyboardButton(
            text="Запит проігноровано ❌",
            callback_data="disabled"
        )
        disabled_keyboard.add(disabled_button)

        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=disabled_keyboard)

        # Notify the user that they have been ignored
        bot.send_message(user_id, "Вибачте, ваш запит на доступ до бота був проігнорований.")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("blacklist_"))
    def blacklist_user_callback(call):
        user_id = call.data.split("_")[1]
        username = call.data.split("_")[2]

        # Add user to the blacklist (your logic here)
        # After blacklisting, we need to disable the buttons
        disabled_keyboard = types.InlineKeyboardMarkup()
        disabled_button = types.InlineKeyboardButton(
            text="Користувача додано до чорного списку ❌",
            callback_data="disabled"
        )
        disabled_keyboard.add(disabled_button)

        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=disabled_keyboard)
        bot.answer_callback_query(call.id, "Користувача додано до чорного списку.")


    @bot.callback_query_handler(func=lambda call: call.data == "blacklist")
    def show_blacklist(call):
        blacklist = get_blacklist()
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text=BACK_BUTTON_TEXT,callback_data='back_to_start'))
        if not blacklist:
            bot.edit_message_text(chat_id= chat_id, message_id=message_id,
                                  text="список пустий:", reply_markup=keyboard)
            return


        for user_id, username in blacklist:
            button = types.InlineKeyboardButton(
                text=f"{username} (ID: {user_id})", callback_data=f"whitelist_{user_id}_{username}"
            )
            keyboard.add(button)

        bot.edit_message_text(chat_id, message_id=message_id,
                                  text="Проігноровані користувачі:", reply_markup=keyboard)

    # --- Обробник для переведення користувача з чорного в білий список ---
    @bot.callback_query_handler(func=lambda call: call.data.startswith('whitelist_'))
    def whitelist_user(call):
        parts = call.data.split('_')
        user_id, username = parts[1], "_".join(parts[2:])

        user_data = {
            "id": user_id,
            "username": username,
            "name": "N/A",
            "is_admin": "false",
            "lecture_notification": "true",
            "lab_notification":"true"
        }
        add_user_to_whitelist(user_data)
        remove_from_blacklist(user_id)

        bot.answer_callback_query(call.id, "Користувача додано до списку.")
        bot.send_message(call.message.chat.id, f"Користувач {username} (ID: {user_id}) доданий у список.")
        bot.send_message(user_id, "Вас додано до списку! Тепер у вас є доступ до боту! Приємного користування!")

    @bot.callback_query_handler(func=lambda call: call.data == "view_schedule")
    def view_schedule(call):
        chat_id = call.message.chat.id
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text="1 тиждень", callback_data="view_numerator"))
        keyboard.add(InlineKeyboardButton(text="2 тиждень", callback_data="view_denominator"))
        keyboard.add((InlineKeyboardButton(text="Я хз мені на сьогодні треба",callback_data="view_today")))
        keyboard.add(InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="back_to_start"))
        bot.edit_message_text("Оберіть тиждень:", chat_id, call.message.message_id,
                              reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: call.data == "view_today")
    def today(call):
        chat_id = call.message.chat.id
        try:
            api_data = get_current_time_data()
            current_day = DAYS_MAP[api_data['currentDay'] - 1]  # Convert 1-7 to 0-6 for indexing
            current_week = 'numerator' if api_data['currentWeek'] % 2 != 0 else 'denominator'
            schedule_data = load_schedule_from_csv()
            today_schedule = []
            for entry in schedule_data:
                if entry['day'] == current_day and entry['week'] == current_week:
                    today_schedule.append(entry)
            today_schedule.sort(key=lambda x: datetime.strptime(x['time'], '%H:%M'))
            if today_schedule:
                message_lines = [f"Розклад на сьогодні ({current_day}):"]
                for entry in today_schedule:
                    message_lines.append(f"⏰ {entry['time']} – {entry['subject']}")
                message = "\n".join(message_lines)
            else:
                message = f"На сьогодні ({current_day}) пар немає."
            bot.edit_message_text(chat_id=chat_id, text=message, message_id=call.message.message_id)
        except Exception as e:
            bot.send_message(chat_id, "Вибачте, сталася помилка при отриманні розкладу.")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("view_"))
    def select_week(call):
        chat_id = call.message.chat.id
        week_type = call.data.split("_")[1]
        keyboard = InlineKeyboardMarkup()
        days = ["Пн", "Вв", "Ср", "Чт", "Пт"]
        for day in days:
            keyboard.add(InlineKeyboardButton(text=day, callback_data=f"schedule_{week_type}_{day}"))
        keyboard.add(InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="back_to_start"))
        bot.edit_message_text("Оберіть день для перегляду розкладу:", chat_id, call.message.message_id,
                              reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("schedule_"))
    def show_schedule_for_day(call):
        chat_id = call.message.chat.id
        _, week_type, selected_day = call.data.split("_")
        schedule_data = load_schedule_from_csv()

        schedule_text = f"Розклад на {selected_day} ({'1 тиждень' if week_type == 'numerator' else '2 тиждень'}):\n"
        for entry in schedule_data:
            if entry['day'] == selected_day and entry['week'] == week_type:
                schedule_text += f"{entry['time']} - {entry['subject']}\n"

        if not schedule_text.strip():
            schedule_text = f"Розклад на {selected_day} не знайдено."

        bot.send_message(chat_id, schedule_text)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("set_day_") or call.data.startswith("set_time_"))
    def ask_day_to_schedule(message):
        keyboard = types.InlineKeyboardMarkup()
        days = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]

        for day in days:
            keyboard.add(types.InlineKeyboardButton(text=day, callback_data=f"set_day_{day}"))

        bot.send_message(message.chat.id, "Виберіть день тижня для запуску перевірки:", reply_markup=keyboard)

    def ask_time_to_schedule(call):
        keyboard = types.InlineKeyboardMarkup()

        times = ["09:00", "10:00", "12:00", "15:00", "18:00"]  # Приклади часу
        for time_option in times:
            keyboard.add(types.InlineKeyboardButton(text=time_option, callback_data=f"set_time_{time_option}"))

        bot.send_message(call.message.chat.id, "Виберіть час для запуску перевірки:", reply_markup=keyboard)

    def handle_schedule_settings(call):
        user_id = str(call.from_user.id)

        if is_user_admin(user_id):
            chat_id = call.message.chat.id


            if call.data.startswith("set_day_"):
                day = call.data.replace("set_day_", "")
                admin_schedule[user_id] = {"day": day}  # Зберігаємо вибір дня
                bot.answer_callback_query(call.id, f"Ви вибрали день: {day}")
                ask_time_to_schedule(call)  # Переходимо до вибору часу


            elif call.data.startswith("set_time_"):
                time_selected = call.data.replace("set_time_", "")
                if user_id in admin_schedule and "day" in admin_schedule[user_id]:
                    day = admin_schedule[user_id]["day"]

                    # Зберігаємо розклад у CSV
                    save_schedule_to_csv(chat_id, day, time_selected)
                    bot.answer_callback_query(call.id, f"Графік встановлено: {day} о {time_selected}")

                    # Оновлюємо планувальник


        else:
            bot.answer_callback_query(call.id, "Ви не маєте прав для налаштування графіку.")

    @bot.message_handler(commands=["set_schedule"])
    def set_schedule(message):
        user_id = str(message.from_user.id)

        if is_user_admin(user_id):
            ask_day_to_schedule(message)
        else:
            bot.send_message(message.chat.id, "Ви не маєте прав для налаштування.")

    @bot.callback_query_handler(func=lambda call: call.data == "settings")
    def settings_menu(call):
        user_id = call.from_user.id
        lecture_status, lab_status = get_user_notifications(user_id)

        lecture_icon = '✅' if lecture_status == 'True' else '❌'
        lab_icon = '✅' if lab_status == 'True' else '❌'

        keyboard = types.InlineKeyboardMarkup()

        lecture_button = types.InlineKeyboardButton(
            text=f'Сповіщення про пари {lecture_icon}',
            callback_data='toggle_lecture_notification'
        )
        lab_button = types.InlineKeyboardButton(
            text=f'Сповіщення про лабораторні/практичні {lab_icon}',
            callback_data='toggle_lab_notification'
        )
        keyboard.add(types.InlineKeyboardButton(text='Канал бота!', url='https://t.me/campushelper'))
        keyboard.add(lecture_button)
        keyboard.add(lab_button)
        keyboard.add(types.InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="back_to_start"))

        chat_id = call.message.chat.id
        message_id = call.message.message_id

        try:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="Налаштуйте сповіщення!",
                reply_markup=keyboard
            )
        except Exception as e:
            if "message is not modified" in str(e):
                # Якщо повідомлення не змінилося, просто ігноруємо помилку
                pass
            else:
                # Якщо виникла інша помилка, можна її обробити або залогувати
                print(f"Помилка при редагуванні повідомлення: {e}")

    @bot.callback_query_handler(
        func=lambda call: call.data in ['toggle_lecture_notification', 'toggle_lab_notification'])
    def callback_toggle_notification(call):
        user_id = call.from_user.id

        if call.data == 'toggle_lecture_notification':
            toggle_notification(user_id, 'lecture')
            bot.answer_callback_query(call.id, "Сповіщення про пари оновлено!")
        elif call.data == 'toggle_lab_notification':
            toggle_notification(user_id, 'lab')
            bot.answer_callback_query(call.id, "Сповіщення про лабораторні/практичні оновлено!")

        # Оновлюємо меню налаштувань
        settings_menu(call)

    @bot.callback_query_handler(func=lambda call: call.data == "vidrh")
    def vidrh_menu(call):
        user_id = call.from_user.id
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Форма для відрахування",
                                                url='https://docs.google.com/document/d/1O_UUbVFJrlt1u-TTTh65kIdSgRPAYRlL/edit?usp=sharing&ouid=102193641661235924869&rtpof=true&sd=true'))
        keyboard.add(types.InlineKeyboardButton(text="Надіслати форму", url="https://t.me/slovyan_k"))
        keyboard.add(types.InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="back_to_start"))

        chat_id = call.message.chat.id
        message_id = call.message.message_id

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text='Тут ти зможеш відрахуватися з нашого університету!',
            reply_markup=keyboard
        )

    @bot.callback_query_handler(func=lambda call: call.data == "broadcast")
    def broadcasting(call):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="back_to_start"))
        msg = bot.send_message(call.from_user.id, "Введіть текст!",reply_markup=keyboard)
        def broadcast_handler(message):
            broadcast_message(bot, message.chat.id, message.text)
        bot.register_next_step_handler(msg, lambda message: broadcast_handler(message))

    @bot.callback_query_handler(func=lambda call: call.data == ("addinvite"))
    def invite(call):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="back_to_start"))
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text= "Введіть назву файла ",reply_markup=keyboard)
        bot.register_next_step_handler(call.message, text_handler)
    @bot.callback_query_handler(func=lambda call: call.data == "attendance")
    def attendance_menu(call):
        keyboard = types.InlineKeyboardMarkup()
        user_id = str(call.from_user.id)
        if is_user_admin(user_id):

            start_attendance_button = types.InlineKeyboardButton(text="Відмітитися", callback_data="start_attendance")
            start_check_attendance_button = types.InlineKeyboardButton(text="Зібрати список присутніх/відсутніх📜", callback_data="start_check_attendance")
            send_attendance_button = types.InlineKeyboardButton(text="Отримати список присутніх/відсутніх📜", callback_data="send_attendance_to_admin")
            back_button = InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="back_to_start")
            keyboard.add(start_check_attendance_button)
            keyboard.add(start_attendance_button)
            keyboard.add(send_attendance_button)
            keyboard.add(back_button)
        else:
            start_attendance_button = types.InlineKeyboardButton(text="Відмітитися", callback_data="start_attendance")
            back_button = InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="back_to_start")
            keyboard.add(start_attendance_button)
            keyboard.add(back_button)
        bot.edit_message_text("Відмітитись на парі!😵‍💫", call.message.chat.id, call.message.message_id, reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: call.data == "start_attendance")
    def attendance(call):
        keyboard = types.InlineKeyboardMarkup()
        present_button = types.InlineKeyboardButton(text="Присутній✅", callback_data="present")
        absent_button = types.InlineKeyboardButton(text="Відсутній❌", callback_data="absent")
        report_button = types.InlineKeyboardButton(text="Причина відсутності📜", callback_data="report")
        back_button = InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="back_to_start")
        keyboard.add(present_button)
        keyboard.add(absent_button)
        keyboard.add(report_button)
        keyboard.add(back_button)
        bot.edit_message_text("Вкажіть вашу присутніть чи відсутність!🪦", call.message.chat.id, call.message.message_id, reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: call.data == "present")
    def present(call):
        user_id = str(call.from_user.id)
        chat_id = call.message.chat.id
        if user_id in attendance_data:
            attendance_data[user_id]['attendance'] = "Присутній✅"
            bot.send_message(chat_id,
                             "Ви підтвердили свою присутність! Дякую!")
        else:
            bot.send_message(chat_id, "Запит на відмітку не було відправлено або ви не в білому списку.")

    @bot.callback_query_handler(func=lambda call: call.data == "absent")
    def absent(call):
        user_id = str(call.from_user.id)
        chat_id = call.message.chat.id
        if user_id in attendance_data:
            attendance_data[user_id]['attendance'] = "Відсутній❌"
            bot.send_message(chat_id, "Ви підтвердили свою відсутність! Будь ласка, вкажіть причину вашої відсутності, використовуючи команду /report.")
        else:
            bot.send_message(chat_id, "Запит на відмітку не було відправлено або ви не в білому списку.")

    @bot.callback_query_handler(func=lambda call: call.data == "report")
    def report(call):
        user_id = str(call.from_user.id)

        if user_id in attendance_data:
            bot.send_message(user_id, "Введіть причину відсутності!")
            bot.register_next_step_handler(call.message, save_report)
        else:
            bot.send_message(call.id, "Почекайте адміни сплять та не запустили перевірку пристуності")

    @bot.callback_query_handler(func=lambda call: call.data == "start_check_attendance")
    def start_check_attendance(call):
        user_id = str(call.from_user.id)
        chat_id = call.message.chat.id
        global attendance_data
        if is_user_admin(user_id):
            attendance_data = start_attendance_check(bot)
            bot.answer_callback_query(call.id, "Запускаю...")
        else:
            bot.send_message(chat_id, "Ви лох без адмін прав")
    @bot.callback_query_handler(func=lambda call: call.data == "send_attendance_to_admin")
    def send_attendance_to_admin(call):
        if is_user_admin(call.from_user.id):
            im_save_attendance_to_csv(attendance_data)
            for admin_id in get_all_admins():
                try:
                    with open(ATTENDANCE_FILE, 'rb') as file:
                        bot.send_document(admin_id, file)
                except FileNotFoundError:
                    bot.send_message(admin_id, "Файл з відмітками не знайдено!")
                except Exception as e:
                    bot.send_message(admin_id, f"Помилка: {e}")
            bot.answer_callback_query(call.id, "Відмітки збережено і відправлено всім адміністраторам.")
        else:
            bot.answer_callback_query(call.id, "Тільки адміністратор може використовувати цю команду!")

    @bot.callback_query_handler(func=lambda call: call.data == "back_to_attendance")
    def back_to_attendance(call):
        attendance_menu(call)

    @bot.callback_query_handler(func=lambda call: call.data =="attendance1")
    def attendance1(call):
        attendance(call)

    @bot.callback_query_handler(func=lambda call: call.data == "back_to_start")
    def back_to_start(call):
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        message_id = call.message.message_id

        if not is_user_in_whitelist(user_id):
            request_access(user_id, call)
            return
        if user_id == is_user_blacklisted(user_id):
            bot.send_message(user_id, 'Ви в чорному списку')
            return

        # Формування головного меню
        keyboard = types.InlineKeyboardMarkup(row_width=2)

        # Кнопки доступні для всіх користувачів
        attendance_button = types.InlineKeyboardButton(text="Відмітитись на парі📍", callback_data="attendance")
        invites_button = types.InlineKeyboardButton(text="Записи/конспект❗", callback_data="invites")
        schedule_button = types.InlineKeyboardButton(text="Розклад📚", callback_data="view_schedule")
        form_button = types.InlineKeyboardButton(text="Відрахування🗿", callback_data='vidrh')
        settings_button = types.InlineKeyboardButton(text='Налаштування⚙️', callback_data='settings')

        # Додаємо загальні кнопки для користувачів
        keyboard.add(attendance_button, invites_button)
        keyboard.add(schedule_button, form_button)

        if is_user_admin(str(user_id)):
            broadcast_button = types.InlineKeyboardButton(text='Розсилка📪', callback_data="broadcast")
            add_invite_button = types.InlineKeyboardButton(text="Додати посилання", callback_data="addinvite")
            set_schedule_button = types.InlineKeyboardButton(text='Налаштування розсилки', callback_data="set_schedule")
            blacklist_button = types.InlineKeyboardButton(text="Чорний список🕯", callback_data="blacklist")

            # Додаємо кнопки адміністратора
            keyboard.add(set_schedule_button, add_invite_button)
            keyboard.add(broadcast_button, settings_button)
            keyboard.add(blacklist_button)
        else:
            # Якщо користувач не адміністратор, додаємо лише налаштування
            keyboard.add(settings_button)

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text='Головне меню',
            reply_markup=keyboard
        )

    @bot.callback_query_handler(func=lambda call: call.data == "invites")
    def show_folder_selection(call):
        folders = get_available_folders()
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        keyboard = InlineKeyboardMarkup()

        if not folders:
            keyboard.add(InlineKeyboardButton(BACK_BUTTON_TEXT, callback_data="back_to_start"))
            bot.edit_message_text(chat_id=chat_id,message_id=message_id,text=  "На жаль, доступних папок з інвайтами не знайдено.",reply_markup=keyboard)
            return


        for folder in folders:
            keyboard.add(InlineKeyboardButton(folder, callback_data=f"folder:{folder}"))
        keyboard.add(InlineKeyboardButton(BACK_BUTTON_TEXT, callback_data="back_to_start"))
        bot.edit_message_text(chat_id=chat_id,message_id=message_id,text= "Оберіть предмет📚", reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("folder:"))
    def folder_invites_handler(call):
        folder = call.data.split(":")[1]
        invite_keyboard = create_invite_keyboard_by_folder(folder)

        if invite_keyboard:
            invite_keyboard.add(InlineKeyboardButton(BACK_BUTTON_TEXT, callback_data="invites"))
            bot.edit_message_text(f"Корисні посилання в чаті '{folder}':", call.message.chat.id, call.message.message_id, reply_markup=invite_keyboard)
        else:
            bot.answer_callback_query(call.id, f"У папці '{folder}' не знайдено інвайтів.")
            show_folder_selection(call.message.chat.id)

    def create_invite_keyboard_by_folder(folder):
        keyboard = InlineKeyboardMarkup()
        invites = get_invites_by_folder(folder)
        for invite in invites:
            keyboard.add(InlineKeyboardButton(invite['text'], url=invite['url']))
        return keyboard



    @bot.message_handler(content_types=['text'])
    def get_text_messages(message):
        user_id = message.from_user.id
        if not is_user_in_whitelist(user_id):
            keyboard = types.InlineKeyboardMarkup()
            approve_button = types.InlineKeyboardButton(text="Схвалити", callback_data=f"approve_{user_id}_{message.from_user.username}")
            keyboard.add(approve_button)
            for admin_id in get_all_admins():
                bot.send_message(admin_id, f"Користувач {message.from_user.username} (ID: {user_id}) запитує доступ.", reply_markup=keyboard)
            bot.send_message(user_id, "У вас немає доступу! Очікуйте схвалення!")
            return

        if message.text == "/start":
            start_menu(message)
        elif message.text == "/help":
            bot.send_message(user_id, "Доступні команди:\n/start - головне меню далі кнопочки\n")
        elif message.text == '/reg_new_id' and is_user_admin(user_id):
            bot.send_message(user_id, "Введіть ID або /cancel для скасування:")
            is_adding_id[user_id] = True
            bot.register_next_step_handler(message, add_user_to_whitelist)
        elif message.text == "/cancel" and user_id in is_adding_id and is_adding_id[user_id]:
            bot.send_message(user_id, "Операція додавання ID скасована!")
            is_adding_id[user_id] = False
        elif message.text.startswith("/broadcast") and is_user_admin(user_id):
            broadcast_text = message.text[len("/broadcast "):].strip()
            if broadcast_text:
                bot.send_message(user_id, "Починаю розсилку...")
                broadcast_message(bot, message, broadcast_text)
            else:
                bot.send_message(user_id, "Текст для розсилки не вказаний.")
        elif message.text == "/add_invite" and is_user_admin(user_id):
            bot.send_message(user_id, "Введіть текст кнопки або /cancel для скасування:")
            bot.register_next_step_handler(message, text_handler)
        else:
            bot.send_message(user_id, "Я вас не розумію! Напишіть /help для отримання списку команд.")

    @bot.callback_query_handler(func=lambda call: call.data.startswith('approve_'))
    def approve_user_callback(call):
        approve_user(bot, call)
        user_id = call.data.split('_')[1]
        remove_pending_requests(user_id)
        bot.answer_callback_query(call.id, "Користувача схвалено.")


    def remove_pending_requests(user_id):
        if user_id in pending_requests:
            for admin_id, message_id in pending_requests[user_id]:
                try:
                    bot.delete_message(admin_id, message_id)
                except Exception as e:
                    print(f"Помилка при видаленні повідомлення: {e}")
            del pending_requests[user_id]




    def save_report(message):
        user_id = str(message.from_user.id)
        report = message.text

        if user_id in attendance_data:
            attendance_data[user_id]['report'] = report
            bot.send_message(user_id, "Ваш звіт збережено! Дякуємо за інформацію!")
            for admin_id in get_all_admins():
                bot.send_message(admin_id,
                                 f"Новий звіт від користувача {user_id} {message.from_user.username}:\nДата: {attendance_data[user_id]['date']}\nПричина: {report}")
        else:
            bot.send_message(user_id, "Не вдалося зберегти звіт! Спробуйте пізніше!")

    def text_handler(message):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="back_to_start"))
        INVITE_COLUMNS['text'] = message.text
        bot.send_message(message.from_user.id, "Вкажіть URL для кнопки ",reply_markup=keyboard)
        bot.register_next_step_handler(message, url_handler)

    def url_handler(message):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="back_to_start"))
        INVITE_COLUMNS['url'] = message.text
        bot.send_message(message.from_user.id, "Вкажіть назву кнопки (або залиште порожнім для 'default'):",reply_markup=keyboard)
        bot.register_next_step_handler(message, folder_handler)

    def folder_handler(message):
        folder = message.text.strip() if message.text.strip() else 'default'
        add_invite_button_for_admin(bot, message, INVITE_COLUMNS['text'], INVITE_COLUMNS['url'], folder)
        bot.send_message(message.from_user.id, f"Кнопка із запрошенням успішно додана в папку '{folder}'!")
