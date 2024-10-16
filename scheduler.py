import csv
import requests
import logging


# API URL
BASE_URL = "https://api.campus.kpi.ua/schedule/lessons"

# Group ID
GROUP_ID = "000011f1-0000-0000-0000-000000000000"

# File to store the schedule
SCHEDULE_FILE = "schedule.csv"

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

def parse_schedule_data_from_api_response(data):
    """Parses the schedule data from the KPI Campus API"""
    schedule_data = []
    seen_entries = set()  # Множина для відстеження унікальних записів
    if data and isinstance(data, dict) and 'data' in data and isinstance(data['data'], dict):
        for week in ['scheduleFirstWeek', 'scheduleSecondWeek']:
            week_type = 'numerator' if week == 'scheduleFirstWeek' else 'denominator'
            if week in data['data']:
                for day in data['data'][week]:
                    if 'pairs' in day:
                        for pair in day['pairs']:
                            entry = (
                                day['day'],
                                pair['time'],
                                pair['name'],
                                week_type
                            )
                            if entry not in seen_entries:
                                seen_entries.add(entry)  # Додаємо унікальний запис у множину
                                schedule_data.append({
                                    'day': day['day'],
                                    'time': pair['time'],
                                    'subject': pair['name'],
                                    'week': week_type,
                                    'link': ''  # доданий ключ для посилання на пару
                                })
        logging.info(f"Parsed {len(schedule_data)} lessons from the API data")
    else:
        logging.warning("Received empty or invalid data from API")
    return schedule_data

def save_schedule_to_csv(schedule_data):
    """Saves the schedule to a CSV file"""
    try:
        with open(SCHEDULE_FILE, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = ['day', 'time', 'subject', 'teacher', 'room', 'week', 'link']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for entry in schedule_data:
                writer.writerow(entry)
        logging.info(f"Successfully saved {len(schedule_data)} entries to {SCHEDULE_FILE}")
    except csv.Error as e:
        logging.error(f"Failed to save schedule to CSV: {e}")

def load_schedule_from_csv():
    """Loads the schedule from the CSV file"""
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

def get_class_info(day, time):
    """Gets the class information"""
    schedule_data = load_schedule_from_csv()
    for entry in schedule_data:
        if entry['day'] == day and entry['time'] == time:
            return entry['subject'], entry['teacher'], entry['room'], entry['link']
    logging.warning(f"No class found for {day} at {time}")
    return None, None, None, None