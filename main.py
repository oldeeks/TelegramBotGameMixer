import random
import json
from games import games_by_genre
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler


US_DATA_FILE = "user_data.json"


def load_user_data():
    """
    Данная функция загружает данные пользователей из JSON-файла.

    Returns:
        dict: Словарь с данными пользователей.
    """
    try:
        with open(US_DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_user_data(user_data):
    """
    Сохраняет данные пользователей в JSON-файл.

    Args:
        user_data (dict): Словарь с данными пользователей.
    """
    with open(US_DATA_FILE, "w") as file:
        json.dump(user_data, file)


def start(update, context):
    """
    Обработчик команды /start.

    Args:
        update (telegram.Update): Объект события Telegram.
        context (telegram.ext.CallbackContext): Контекст обработчика.

    """
    user_id = str(update.effective_user.id)
    user_data = load_user_data()

    if user_id not in user_data:
        user_data[user_id] = {
            "genre": None,
            "username": update.effective_user.username,
            "firstname":update.effective_user.first_name,
            "lastname": update.effective_user.last_name
        }
        save_user_data(user_data)

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Привет! Я бот, который поможет тебе выбрать игру. Напиши /genre, чтобы выбрать жанр.")


def genre(update, context):
    """
    Обработчик команды /genre.

    Args:
        update (telegram.Update): Объект события Telegram.
        context (telegram.ext.CallbackContext): Контекст обработчика.

    """
    user_id = str(update.effective_user.id)
    user_data = load_user_data()

    genre_keyboard = [[genre.capitalize()] for genre in games_by_genre.keys()]  # Клавиатура с доступными жанрами
    reply_markup = ReplyKeyboardMarkup(genre_keyboard, one_time_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Выбери интересующий тебя жанр:", reply_markup=reply_markup)

    user_data[user_id]["genre"] = None
    save_user_data(user_data)


def receive_genre(update, context):
    """Обработчик сообщений с жанром игры.

    Args:
        update (telegram.Update): Объект события Telegram.
        context (telegram.ext.CallbackContext): Контекст обработчика.

    """
    user_id = str(update.effective_user.id)
    user_data = load_user_data()

    genre = update.message.text.lower()
    if genre in games_by_genre:
        user_data[user_id]["genre"] = genre
        save_user_data(user_data)

        game = random.choice(games_by_genre[genre])
        title = game["title"]
        score = game["score"]
        description = game["description"]
        multiplayer = "Да" if game["multiplayer"] else "Нет"
        image_url = game["image_url"]
        stopgame_url = game["stopgame_url"]

        message = (
            f"<b>Я рекомендую игру:</b>\n\n"
            f"<b>Название:</b> {title}\n"
            f"<b>Жанр:</b> {genre.capitalize()}\n"
            f"<b>Оценка на Metacritic:</b> {score}/100\n"
            f"<b>Описание:</b> {description}\n"
            f"<b>Мультиплеер:</b> {multiplayer}\n"
            f"<a href='{image_url}'>&#8205;</a>"
        )

        inline_keyboard = [[InlineKeyboardButton("Ссылка на StopGame", url=stopgame_url)]]
        inline_markup = InlineKeyboardMarkup(inline_keyboard)

        context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_url, caption=message, parse_mode="HTML",
                               reply_markup=inline_markup)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Чтобы снова выбрать жанр напишите команду /genre")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Извини, я не знаю игры в таком жанре.")




def inline_button(update, context):
    """
    Обработчик инлайн запросов.

    Args:
        update (telegram.Update): Объект события Telegram.
        context (telegram.ext.CallbackContext): Контекст обработчика.

    """
    query = update.callback_query
    context.bot.answer_callback_query(query.id)


def main():
    """функция для запуска бота."""

    updater = Updater(token='6356101206:AAH7gfr3QcBFTCjqvLiqXU27jaDTJ7uvmpM', use_context=True)

    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    genre_handler = CommandHandler('genre', genre)
    dispatcher.add_handler(genre_handler)

    receive_genre_handler = MessageHandler(Filters.text, receive_genre)
    dispatcher.add_handler(receive_genre_handler)

    inline_button_handler = CallbackQueryHandler(inline_button)
    dispatcher.add_handler(inline_button_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
