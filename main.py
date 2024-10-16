import telebot
from bot_handlers import register_handlers
from scheduler import get_schedule_from_api, parse_schedule_data_from_api_response, save_schedule_to_csv
from config import BOT_TOKEN

def main():
    bot = telebot.TeleBot(BOT_TOKEN)
    register_handlers(bot)

    # Оновлюємо розклад при запуску
    api_data = get_schedule_from_api()
    if api_data:
        schedule_data = parse_schedule_data_from_api_response(api_data)
        save_schedule_to_csv(schedule_data)
    else:
        print("Не вдалося отримати розклад з API.")

    print("Бот запущено. Натисніть Ctrl+C для виходу.")

    # Запускаємо бота
    bot.polling(none_stop=True, interval=0)

if __name__ == "__main__":
    main()