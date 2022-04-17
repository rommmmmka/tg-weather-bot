import requests
from aiogram import types, Dispatcher

from tgbot.config import Config
from tgbot.keyboards.inline import cities_inline_kb
from tgbot.keyboards.reply import base_reply_kb
from tgbot.misc.other import get_full_city_name
from tgbot.misc.weather import get_weather
from tgbot.services.db import Database

WEATHER_WRONG_COMMAND = ("<b>Ошибка!</b> Введите команду в одном из форматов:\n"
                         "/weather [город]\n"
                         "/w [город]")
GEODB_URL = "https://wft-geo-db.p.rapidapi.com/v1/geo/cities/"


async def callback_query_weather(callback_query: types.CallbackQuery):
    config: Config = callback_query.bot.get('config')
    geodb_headers = {
        "X-RapidAPI-Host": "wft-geo-db.p.rapidapi.com",
        "X-RapidAPI-Key": config.geodb_token
    }
    query = {"languageCode": "ru"}

    city_id = callback_query.data[1:]
    coords_data = requests.request("GET", GEODB_URL + city_id, headers=geodb_headers, params=query).json()
    lat = coords_data['data']['latitude']
    lon = coords_data['data']['longitude']

    db: Database = callback_query.bot.get("db")
    db.add_city(coords_data['data'])
    db.add_country(coords_data['data'])
    db.add_user(callback_query['from'], coords_data['data'])

    answer = get_weather(callback_query.bot, lat, lon, get_full_city_name(coords_data['data']))
    try:
        await callback_query.bot.edit_message_text(answer, callback_query.message.chat.id,
                                                   callback_query.message.message_id, reply_markup=None)
    except Exception:
        pass
    await callback_query.bot.answer_callback_query(callback_query.id)


async def weather_command(message: types.Message):
    city_query = message.get_args()
    if city_query == "":
        await message.reply(WEATHER_WRONG_COMMAND, disable_notification=True)
        return

    config: Config = message.bot.get("config")
    geodb_headers = {
        "X-RapidAPI-Host": "wft-geo-db.p.rapidapi.com",
        "X-RapidAPI-Key": config.geodb_token
    }
    query = {
        "limit": "5",
        "namePrefix": city_query,
        "types": "CITY",
        "sort": "-population",
        "languageCode": "en" if city_query[0].lower() in "abcdefghijklmnopqrstuvwxyz" else "ru"
    }

    coords_data = requests.request("GET", GEODB_URL, headers=geodb_headers, params=query).json()
    match len(coords_data['data']):
        case 0:
            await message.reply("<b>Ошибка!</b> Город с таким названием не найден.", disable_notification=True)
        case 1:
            lat = coords_data['data'][0]['latitude']
            lon = coords_data['data'][0]['longitude']
            db: Database = message.bot.get("db")
            db.add_city(coords_data['data'][0])
            db.add_country(coords_data['data'][0])
            db.add_user(message['from'], coords_data['data'][0])
            answer = get_weather(message.bot, lat, lon, get_full_city_name(coords_data['data'][0]))
            await message.reply(answer, reply_markup=base_reply_kb(message.chat.type), disable_notification=True)
        case _:
            answer, kb = cities_inline_kb(coords_data['data'])
            await message.reply(answer, reply_markup=kb, disable_notification=True)


async def location(message: types.Message):
    lat = message.location.latitude
    lon = message.location.longitude
    answer = get_weather(message.bot, lat, lon)
    await message.reply(answer, reply_markup=base_reply_kb(message.chat.type), disable_notification=True)


def register_weather(dp: Dispatcher):
    dp.register_callback_query_handler(callback_query_weather, lambda c: len(c.data) > 0 and c.data[0] == "w")
    dp.register_message_handler(weather_command, commands=["weather", "w"])
    dp.register_message_handler(location, content_types=["location"])
