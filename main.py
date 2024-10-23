import telebot
from bot_handlers import register_handlers
from scheduler import get_schedule_from_api, parse_schedule_data_from_api_response, save_schedule_to_csv
from config import BOT_TOKEN
from time1 import check_schedule
import schedule
import time
import threading

bot = telebot.TeleBot(BOT_TOKEN)


def main():
    register_handlers(bot)
    api_data = get_schedule_from_api()
    if api_data:
        schedule_data = parse_schedule_data_from_api_response(api_data)
        save_schedule_to_csv(schedule_data)
        print('Розклад оновлено')
    else:
        print("Не вдалося отримати розклад з API.")

    print("Бот запущено. Натисніть Ctrl+C для виходу.")

    # Запуск планувальника в окремому потоці
    scheduler_thread = threading.Thread(target=scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()

    # Запуск бота
    bot.polling(none_stop=True, interval=0)


def scheduler():
    # Запланувати виконання `check_schedule` кожну хвилину
    schedule.every(1).minutes.do(check_schedule, bot)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()