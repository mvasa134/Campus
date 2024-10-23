import csv
import requests
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone

#from user_management import get_all_users, get_user_notifications

# API URL
BASE_URL = "https://api.campus.kpi.ua/schedule/lessons"

# Group ID
GROUP_ID = "000011f1-0000-0000-0000-000000000000"

# Files to store the schedule and subject links
SCHEDULE_FILE = "schedule.csv"
SUBJECT_LINKS_FILE = "subject_links.csv"

# Kyiv timezone
KYIV_TZ = timezone('Europe/Kiev')


def get_schedule_from_api():
    """Fetches the schedule from the KPI Campus API"""
    try:
        params = {"groupId": GROUP_ID}
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        logging.info(f"Successfully fetched data from API. Response length: {len(data)}")
        return data
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch schedule: {e}")
        return None


def load_subject_links():
    """Loads subject links from CSV file with separate lecture and lab links"""
    subject_links = {}
    try:
        with open(SUBJECT_LINKS_FILE, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                subject_links[row['name']] = {
                    'lecture': row.get('lecture_link', ''),
                    'lab': row.get('lab_link', '')
                }
        logging.info(f"Loaded {len(subject_links)} subject links from {SUBJECT_LINKS_FILE}")
    except FileNotFoundError:
        logging.warning(f"Subject links file {SUBJECT_LINKS_FILE} not found.")
    except csv.Error as e:
        logging.error(f"Failed to load subject links from CSV: {e}")
    return subject_links


def parse_schedule_data_from_api_response(data):
    """Parses the schedule data from the KPI Campus API with separate lecture/lab links"""
    schedule_data = []
    seen_entries = set()
    subject_links = load_subject_links()

    if data and isinstance(data, dict) and 'data' in data and isinstance(data['data'], dict):
        for week in ['scheduleFirstWeek', 'scheduleSecondWeek']:
            week_type = 'numerator' if week == 'scheduleFirstWeek' else 'denominator'
            if week in data['data']:
                for day in data['data'][week]:
                    if 'pairs' in day:
                        for pair in day['pairs']:
                            lesson_type = 'lecture' if day['day'] in ['Пн', 'Вв'] else 'lab'
                            entry = (
                                day['day'],
                                pair['time'],
                                pair['name'],
                                week_type,
                                lesson_type
                            )

                            if entry not in seen_entries:
                                seen_entries.add(entry)

                                # Get the appropriate link based on lesson type
                                subject_link = ''
                                if pair['name'] in subject_links:
                                    subject_link = subject_links[pair['name']].get(lesson_type, '')

                                schedule_data.append({
                                    'day': day['day'],
                                    'time': pair['time'],
                                    'subject': pair['name'],
                                    'week': week_type,
                                    'link': subject_link,
                                    'type': lesson_type
                                })
        logging.info(f"Parsed {len(schedule_data)} lessons from the API data")
    else:
        logging.warning("Received empty or invalid data from API")
    return schedule_data


def save_schedule_to_csv(schedule_data):
    try:
        with open(SCHEDULE_FILE, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = ['day', 'time', 'subject', 'week', 'link', 'type']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for entry in schedule_data:
                writer.writerow(entry)
        logging.info(f"Successfully saved {len(schedule_data)} entries to {SCHEDULE_FILE}")
    except csv.Error as e:
        logging.error(f"Failed to save schedule to CSV: {e}")


def load_schedule_from_csv():
    schedule_data = []
    try:
        with open(SCHEDULE_FILE, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                schedule_data.append(row)
        logging.info(f"Loaded {len(schedule_data)} entries from {SCHEDULE_FILE}")
    except FileNotFoundError:
        logging.warning(f"Schedule file {SCHEDULE_FILE} not found. Fetching from API...")
        api_data = get_schedule_from_api()
        if api_data:
            schedule_data = parse_schedule_data_from_api_response(api_data)
            save_schedule_to_csv(schedule_data)
        else:
            logging.error("Failed to fetch data from API")
    except csv.Error as e:
        logging.error(f"Failed to load schedule from CSV: {e}")
    return schedule_data





def schedule_reminders(bot):
    """Schedules reminders for all classes"""
    schedule_data = load_schedule_from_csv()
    scheduler = BackgroundScheduler(timezone=KYIV_TZ)

    for class_info in schedule_data:
        day = class_info['day']
        time = class_info['time']

        # Convert day to number (0 = Monday, 6 = Sunday)
        day_number = ['Пн', 'Вт', 'Ср', 'Чт', "Пт", 'Сб', 'Нд'].index(day)

        # Parse time
        hour, minute = map(int, time.split(':'))

        # Schedule the job
        scheduler.add_job(
            #send_class_reminder(None,bot),
            'cron',
            day_of_week=day_number,
            hour=hour,
            minute=minute,
            args=[class_info]
        )

    scheduler.start()
    logging.info("Scheduled reminders for all classes")

