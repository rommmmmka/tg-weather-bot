import requests
import locale
import matplotlib.pyplot as plt
import sqlite3
from io import BytesIO
from datetime import datetime
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardButton, \
    InlineKeyboardMarkup
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from tokens import BOT_TOKEN, OPEN_WEATHER_TOKEN, ADMIN_PASSWORD

EMOJI = {
    "Clear": "\u2600\uFE0F",
    "Clouds": "\u2601\uFE0F",
    "Rain": "\u2614\uFE0F",
    "Drizzle": "\u2614\uFE0F",
    "Thunderstorm": "\u26A1\uFE0F",
    "Snow": "\U0001F328\uFE0F",
    "Mist": "\U0001F32B\uFE0F",
}

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())
db = sqlite3.connect("db.sqlite")
cursor = db.cursor()


def init_db():
    cursor.execute("""CREATE TABLE IF NOT EXISTS cities (
       city_id INT PRIMARY KEY,
       city TEXT,
       state TEXT,
       country TEXT,
       queries INT);
    """)
    cursor.execute("""CREATE TABLE IF NOT EXISTS countries (
       city_id INT PRIMARY KEY,
       city TEXT,
       state TEXT,
       country TEXT,
       queries INT);
    """)
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
       user_id INT PRIMARY KEY,
       name TEXT,
       queries INT);
    """)
    db.commit()


def get_base_kb(chat_type):
    if chat_type == "private":
        return ReplyKeyboardMarkup(resize_keyboard=True).row(
            KeyboardButton("/help"), KeyboardButton("/about")
        ).add(KeyboardButton("Отправить местоположение", request_location=True))
    return ReplyKeyboardRemove()


def get_weather(chat_type, lat, lon, coords_data=None):
    request_weather = requests.get(
        f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,alerts&appid={OPEN_WEATHER_TOKEN}&units=metric&lang=ru")
    weather_data = request_weather.json()
    locale.setlocale(locale.LC_ALL, ("ru_RU", "UTF-8"))
    weather_desc = weather_data['current']['weather'][0]['main']
    if weather_desc in EMOJI:
        weather_desc = f"{EMOJI[weather_desc]} "
    else:
        weather_desc = ""
    city = coords_data['name']
    if "local_names" in coords_data and "ru" in coords_data['local_names']:
        city = coords_data['local_names']['ru']
    state = f"{coords_data['state']}, " if 'state' in coords_data else ""
    city_name = "" if coords_data is None else f"{city}, {state}{coords_data['country']}"
    answer = f"*{city_name}*\n\n" \
             f"*Текущая погода:*\n" \
             f"{round(weather_data['current']['temp'])}°C (ощущается как {round(weather_data['current']['feels_like'])}°C)\n" \
             f"Влажность: {weather_data['current']['humidity']}%\nСкорость ветра: {weather_data['current']['wind_speed']} м/c\n" \
             f"{weather_desc}{weather_data['current']['weather'][0]['description'].capitalize()}\n"
    for i in range(3):
        weather_desc = weather_data['daily'][i]['weather'][0]['main']
        if weather_desc in EMOJI:
            weather_desc = f"{EMOJI[weather_desc]} "
        else:
            weather_desc = ""
        answer += f"*Прогноз на {datetime.utcfromtimestamp(weather_data['daily'][i]['dt']).strftime('%e %B %Y')}:*\n" \
                  f"Утро: {round(weather_data['daily'][i]['temp']['morn'])}°C, день: {round(weather_data['daily'][i]['temp']['day'])}°C, вечер: {round(weather_data['daily'][i]['temp']['eve'])}°C, ночь: {round(weather_data['daily'][i]['temp']['night'])}°C\n" \
                  f"Влажность: {weather_data['daily'][i]['humidity']}%\nСкорость ветра: {weather_data['daily'][i]['wind_speed']} м/c\n" \
                  f"{weather_desc}{weather_data['daily'][i]['weather'][0]['description'].capitalize()}\n"
    kb = get_base_kb(chat_type)
    if chat_type == "private" and coords_data is not None:
        kb.add(KeyboardButton(f"/weather {city_name}"))
    return answer, kb


@dp.callback_query_handler(lambda c: c.data == "delete")
async def process_callback_button1(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query['message']['chat']['id'], callback_query['message']['message_id'])
    await bot.answer_callback_query(callback_query.id)


@dp.message_handler(commands=["start", "help"])
async def start_help_commands(message: types.Message):
    await message.reply(f"*Привет! Вот список моих команд:*\n/start\n/help\n/weather \[город]\n/w \[город]\n/about",
                        reply_markup=get_base_kb(message.chat.type) if message.get_command() == "/start" else None,
                        parse_mode=ParseMode.MARKDOWN, disable_notification=True)


@dp.message_handler(commands=["about"])
async def about_command(message: types.Message):
    await message.reply(
        "*Метеостанция №13 г. Любань* является самой старой метеостанцией Беларуси. Её история начинается 29 ноября "
        "1872 года, когда по указу императора Александра II в местечке Любань была открыта первая в Российской "
        "Империи метеостанция. 9 января 1936 года по приказу И.В. Сталина ей было присвоено имя выдающегося "
        "учёного-метеоролога Р.П. Багрия.\n\nНа протяжении полутора веков своей истории, наблюдения на станции "
        "оставались на высочайшем уровне. Здесь трудились и трудятся настоящие специалисты-профессионалы в своей "
        "области.\n\nВ последние годы, в рамках проекта по модернизации станции, было введено в эксплуатацию множество "
        "новых автоматизированных метеорологических средств, разработанных совместно с Белорусским Государственным "
        "Университетом Информатики и Радиоэлектроники.", parse_mode=ParseMode.MARKDOWN, disable_notification=True)


@dp.message_handler(commands=["weather", "w"])
async def weather_command(message: types.Message):
    if message.get_args() == "":
        print(f"{message['from']['username']} ({message['from']['id']}) не умеет вводить команду")
        await message.reply("*Ошибка! Введите команду в одном из форматов:*\n/weather \[город]\n/w \[город]",
                            parse_mode=ParseMode.MARKDOWN, disable_notification=True)
    else:
        try:
            print(f"{message['from']['username']} ({message['from']['id']}) интересуется погодой")
            city = message.get_args()
            request_coords = requests.get(
                f"https://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={OPEN_WEATHER_TOKEN}")
            coords_data = request_coords.json()
            lat = coords_data[0]["lat"]
            lon = coords_data[0]["lon"]
            answer, kb = get_weather(message.chat.type, lat, lon, coords_data[0])
            await message.reply(answer, parse_mode=ParseMode.MARKDOWN, reply_markup=kb, disable_notification=True)
        except Exception:
            await message.reply("*Ошибка!*\nПроверьте правильность ввода названия города!",
                                parse_mode=ParseMode.MARKDOWN, disable_notification=True)


@dp.message_handler(content_types=["location"])
async def handle_location(message: types.Message):
    lat = message.location.latitude
    lon = message.location.longitude
    answer, kb = get_weather(message.chat.type, lat, lon)
    await message.reply(answer, parse_mode=ParseMode.MARKDOWN, reply_markup=kb, disable_notification=True)


@dp.message_handler(commands=["getchatid", "gcid"])
async def getchatid_command(message: types.Message):
    btn = InlineKeyboardButton("Спасибо", callback_data="delete")
    kb = InlineKeyboardMarkup().add(btn)
    await message.reply(message.chat.id, reply_markup=kb, disable_notification=True)


# @dp.message_handler(commands=["about1"])
# async def getchatid_command(message: types.Message):
#     plt.plot([1, 3], [4, 6])
#     img = BytesIO()
#     plt.savefig(img, format="png")
#     img.seek(0)
#     await bot.send_photo(message.chat.id, img, reply_to_message_id=message.message_id)


@dp.message_handler(state="admin", commands=["admin", "a"])
async def admin_command(message: types.Message):
    if message.chat.type != "private":
        return
    match message.get_args().split(" "):
        case ["login" | "l", *_]:
            await message.reply("*Ошибка!* Вы уже вошли.",
                                parse_mode=ParseMode.MARKDOWN, disable_notification=True)
        case ["logout" | "lo"]:
            await dp.current_state(user=message.from_user.id).reset_state()
            await message.reply("*Вы успешно вышли!*",
                                parse_mode=ParseMode.MARKDOWN, isable_notification=True)
        case ["send" | "s", chat_id, *msg]:
            try:
                await bot.send_message(chat_id, " ".join(msg))
            except Exception:
                await message.reply(f"*Возникла ошибка при отправке!* Возможно, такого чата не существует.",
                                    parse_mode=ParseMode.MARKDOWN, disable_notification=True)
        case _:
            print(message.get_args().split(" "))
            await message.reply("*Ошибка!* Неизвестная команда.",
                                parse_mode=ParseMode.MARKDOWN, disable_notification=True)


@dp.message_handler(commands=["admin", "a"])
async def admin_command(message: types.Message):
    if message.chat.type != "private":
        return
    match message.get_args().split(" "):
        case ["login" | "l", password] if password == ADMIN_PASSWORD:
            await dp.current_state(user=message.from_user.id).set_state("admin")
            await message.delete()
            await bot.send_message(message.chat.id, "*Вы успешно вошли*", parse_mode=ParseMode.MARKDOWN,
                                   disable_notification=True)
        case _:
            await message.delete()
            await bot.send_message(message.chat.id, "*Ошибка входа!*", parse_mode=ParseMode.MARKDOWN,
                                   disable_notification=True)


if __name__ == "__main__":
    init_db()
    executor.start_polling(dp)
