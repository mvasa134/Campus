import pandas as pd
import datetime
import requests

API_URL = "https://api.campus.kpi.ua/time/current"


def get_current_time_data():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            current_time = datetime.datetime.now()
            return current_time
        else:
            print("Не вдалося отримати поточний час через API.")
            return None
    except Exception as e:
        print(f"Виникла помилка при отриманні поточного часу: {e}")
        return None


def send_reminder(subject, link, bot, users_df):
    message = f"Нагадування про пару: {subject}\nПосилання: {link} "

    for index, user in users_df.iterrows():
        try:
            if str(user['lecture_notification']).lower() == 'true' or str(user['lab_notification']).lower() == 'true':
                bot.send_message(chat_id=user['id'], text=message)
                print(f"Повідомлення відправлено до {user['username']} ({user['name']})")
        except Exception as e:
            print(f"Виникла помилка при відправці повідомлення до {user['username']} ({user['name']}): {e}")


# Ініціалізуємо словник для відстеження сповіщень
sent_notifications = {}
day_mapping = {
    "Mon": "Пн",
    "Tue": "Вв",
    "Wed": "Ср",
    "Thu": "Чт",
    "Fri": "Пт",
    "Sat": "Сб",
    "Sun": "Нд"
}

def is_week_numerator(current_date):
    """Функція для перевірки, чи поточний тиждень є чисельником."""
    week_number = current_date.isocalendar()[1]
    return week_number % 2 != 0


def check_schedule(bot):
    print("Запуск check_schedule...")
    current_time = datetime.datetime.now()
    english_day = current_time.strftime("%a")
    current_day = day_mapping.get(english_day, english_day)
    current_week_type = 'numerator' if is_week_numerator(current_time) else 'denominator'

    try:
        schedule_df = pd.read_csv('schedule.csv')
    except FileNotFoundError:
        print("Файл 'schedule.csv' не знайдено.")
        return
    except Exception as e:
        print(f"Виникла помилка при читанні файлу 'schedule.csv': {e}")
        return

    print("Файл розкладу зчитано успішно.")

    if 'day' not in schedule_df.columns or 'time' not in schedule_df.columns or \
            'subject' not in schedule_df.columns or 'link' not in schedule_df.columns or 'week' not in schedule_df.columns:
        print("Відсутні необхідні колонки в файлі 'schedule.csv'.")
        return

    # Фільтрація пар за поточним днем і типом тижня
    today_classes = schedule_df[(schedule_df['day'] == current_day) & (schedule_df['week'] == current_week_type)]

    try:
        users_df = pd.read_csv('white_list.csv')
    except FileNotFoundError:
        print("Файл 'white_list.csv' не знайдено.")
        return
    except Exception as e:
        print(f"Виникла помилка при читанні файлу 'white_list.csv': {e}")
        return

    print("Файл white_list зчитано успішно.")

    if 'id' not in users_df.columns or 'username' not in users_df.columns or 'name' not in users_df.columns or \
            'lecture_notification' not in users_df.columns or 'lab_notification' not in users_df.columns:
        print("Відсутні необхідні колонки в файлі 'white_list.csv'.")
        return

    for index, row in today_classes.iterrows():
        try:
            lesson_time = datetime.datetime.strptime(row['time'], '%H:%M').replace(year=current_time.year,
                                                                                   month=current_time.month,
                                                                                   day=current_time.day)
            reminder_time = lesson_time - datetime.timedelta(minutes=10)
            lesson_end_time = lesson_time + datetime.timedelta(hours=1.25)

            lesson_key = f"{current_day}_{lesson_time:%H:%M}_{row['subject']}"

            if reminder_time <= current_time <= lesson_end_time:
                if lesson_key not in sent_notifications or not sent_notifications[lesson_key]['start']:
                    send_reminder(f"Нагадування за 10 хвилин до початку пари: {row['subject']}", row['link'], bot,
                                  users_df)
                    sent_notifications[lesson_key] = {'reminder': True, 'start': False}
                    print(f"Сповіщення за 10 хвилин відправлено для пари: {row['subject']} в {row['time']}")

            if lesson_time <= current_time <= lesson_end_time:
                if not sent_notifications[lesson_key].get('start', False):
                    send_reminder(f"Нагадування про початок пари: {row['subject']}", row['link'], bot, users_df)
                    sent_notifications[lesson_key]['start'] = True
                    print(f"Сповіщення про початок відправлено для пари: {row['subject']} в {row['time']}")

            if lesson_end_time < current_time:
                sent_notifications.pop(lesson_key, None)
        except Exception as e:
            print(f"Виникла помилка при перевірці або відправленню нагадувань: {e}")