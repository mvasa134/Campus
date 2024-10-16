import os

BOT_TOKEN = os.getenv('BOT_TOKEN', '1730365395:AAGo0vVk8efwHBSHMVhgN5fFf4wbAM5DNCI') #1730365395:AAGo0vVk8efwHBSHMVhgN5fFf4wbAM5DNCI  7932141583:AAGDR1FRwwYufB-MfoaUsHqugA8RRltV6IY

# File names
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
BACK_BUTTON_TEXT = "⬅️ Назад"
WHITE_LIST_COLUMNS = ["id", "username", "name", "is_admin", "lecture_notification","lab_notification"]