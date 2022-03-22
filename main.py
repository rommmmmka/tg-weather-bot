import requests
import locale
from datetime import datetime
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from aiogram.utils import executor
from tokens import BOT_TOKEN, OPEN_WEATHER_TOKEN

EMOJI = {
    "Clear": "\u2600\uFE0F",
    "Clouds": "\u2601\uFE0F",
    "Rain": "\u2614\uFE0F",
    "Drizzle": "\u2614\uFE0F",
    "Thunderstorm": "\u26A1\uFE0F",
    "Snow": "\U0001F328\uFE0F",
    "Mist": "\U0001F32B\uFE0F",
}


def get_base_kb(chat_type):
    if chat_type == "private":
        return ReplyKeyboardMarkup(resize_keyboard=True).row(
            KeyboardButton("/help"), KeyboardButton("/about")
        ).add(KeyboardButton("Отправить местоположение", request_location=True))
    return ReplyKeyboardRemove()


def get_weather(city, chat_type, lat=None, lon=None):
    try:
        if lat is None and lon is None:
            request_coords = requests.get(
                f"https://api.openweathermap.org/geo/1.0/direct?q={city}, BY&limit=1&appid={OPEN_WEATHER_TOKEN}")
            coords_data = request_coords.json()
            if not coords_data:
                request_coords = requests.get(
                    f"https://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={OPEN_WEATHER_TOKEN}")
                coords_data = request_coords.json()
            lat = coords_data[0]["lat"]
            lon = coords_data[0]["lon"]
        request_weather = requests.get(
            f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,alerts&appid={OPEN_WEATHER_TOKEN}&units=metric&lang=ru")
        weather_data = request_weather.json()
        locale.setlocale(locale.LC_ALL, ('ru_RU', 'UTF-8'))
        weather_desc = weather_data['current']['weather'][0]['main']
        if weather_desc in EMOJI:
            weather_desc = f"{EMOJI[weather_desc]} "
        else:
            weather_desc = ""
        answer = f"*Текущая погода:*\n" \
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
        if chat_type == "private" and city != "":
            kb.add(KeyboardButton(f"/weather {city}"))
        return answer, kb
    except Exception:
        return "*Ошибка!*\nПроверьте правильность ввода названия города!", None


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


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
        await message.reply("*Ошибка! Введите команду в одном из форматов:*\n/weather \[город]\n/w \[город]",
                            parse_mode=ParseMode.MARKDOWN, disable_notification=True)
    else:
        answer, kb = get_weather(message.get_args(), message.chat.type)
        await message.reply(answer, parse_mode=ParseMode.MARKDOWN, reply_markup=kb, disable_notification=True)


@dp.message_handler(commands=["getchatid"])
async def getchatid_command(message: types.Message):
    await message.reply(message.chat.id, disable_notification=True)


@dp.message_handler(commands=["sendtochat", "s"])
async def sendtochat_command(message: types.Message):
    try:
        arg = message.get_args().split(" ")
        member = await bot.get_chat_member(int(arg[0]), message['from'].id)
        if member['can_manage_chat']:
            msg = ""
            for i in range(1, len(arg)):
                msg += arg[i] + ' '
            await bot.send_message(int(arg[0]), msg)
        else:
            raise Exception
    except Exception:
        await message.reply("*Ошибка: чат не существует или у вас в нём отсутствуют права администратора*",
                            parse_mode=ParseMode.MARKDOWN, disable_notification=True)


@dp.message_handler(content_types=['location'])
async def handle_location(message: types.Message):
    lat = message.location.latitude
    lon = message.location.longitude
    answer, kb = get_weather("", message.chat.type, lat, lon)
    await message.reply(answer, parse_mode=ParseMode.MARKDOWN, reply_markup=kb, disable_notification=True)


if __name__ == '__main__':
    executor.start_polling(dp)
