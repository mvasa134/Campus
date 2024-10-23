import os

BOT_TOKEN = os.getenv('BOT_TOKEN', '1730365395:AAGo0vVk8efwHBSHMVhgN5fFf4wbAM5DNCI') #1730365395:AAGo0vVk8efwHBSHMVhgN5fFf4wbAM5DNCI  7932141583:AAGDR1FRwwYufB-MfoaUsHqugA8RRltV6IY

# File names
BLACKLIST_FILE = "blacklist.csv"
WHITE_LIST_FILE = 'white_list.csv'
INVITES_FILE = 'invites.csv'
ATTENDANCE_FILE = 'attendance.csv'
SCHEDULE_FILE = 'schedule.csv'
# CSV columns
COLUMNS = ["id", "username", "name", "date", "attendance", "report"]
INVITE_COLUMNS = {
    'text': 0,
    'url': 1,
    'folder': 2
}
DAYS_MAP = {
    0: 'Пн',
    1: 'Вв',
    2: 'Ср',
    3: 'Чт',
    4: 'Пт',
    5: 'Сб',
    6: 'Нд'
}
BACK_BUTTON_TEXT: str = "⬅️Назад"
WHITE_LIST_COLUMNS = ["id", "username", "name", "is_admin", "lecture_notification","lab_notification"]