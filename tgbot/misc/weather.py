import locale
from datetime import datetime

import requests
from aiogram import Bot

from tgbot.config import Config

EMOJI = {
    "Clear": "\u2600\uFE0F",
    "Clouds": "\u2601\uFE0F",
    "Rain": "\u2614\uFE0F",
    "Drizzle": "\u2614\uFE0F",
    "Thunderstorm": "\u26A1\uFE0F",
    "Snow": "\U0001F328\uFE0F",
    "Mist": "\U0001F32B\uFE0F",
}


def get_weather(bot: Bot, lat: float, lon: float, city_name: str = None):
    config: Config = bot.get("config")
    weather_data = requests.get(
        f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,alerts&appid={config.open_weather_token}&units=metric&lang=ru").json()
    locale.setlocale(locale.LC_ALL, ("ru_RU", "UTF-8"))

    weather_desc = weather_data['current']['weather'][0]['main']
    weather_desc = f"{EMOJI[weather_desc]} " if weather_desc in EMOJI else ""
    city_name = f"<b>{city_name}</b>\n\n" if city_name is not None else ""

    answer = f"{city_name}" \
             f"<b>Текущая погода:</b>\n" \
             f"{round(weather_data['current']['temp'])}°C (ощущается как {round(weather_data['current']['feels_like'])}°C)\n" \
             f"Влажность: {weather_data['current']['humidity']}%\nСкорость ветра: {weather_data['current']['wind_speed']} м/c\n" \
             f"{weather_desc}{weather_data['current']['weather'][0]['description'].capitalize()}\n"
    for i in range(3):
        weather_desc = weather_data['daily'][i]['weather'][0]['main']
        weather_desc = f"{EMOJI[weather_desc]} " if weather_desc in EMOJI else ""
        answer += f"<b>Прогноз на {datetime.utcfromtimestamp(weather_data['daily'][i]['dt']).strftime('%e %B %Y').strip()}:</b>\n" \
                  f"Утро: {round(weather_data['daily'][i]['temp']['morn'])}°C, день: {round(weather_data['daily'][i]['temp']['day'])}°C, вечер: {round(weather_data['daily'][i]['temp']['eve'])}°C, ночь: {round(weather_data['daily'][i]['temp']['night'])}°C\n" \
                  f"Влажность: {weather_data['daily'][i]['humidity']}%\nСкорость ветра: {weather_data['daily'][i]['wind_speed']} м/c\n" \
                  f"{weather_desc}{weather_data['daily'][i]['weather'][0]['description'].capitalize()}\n"

    return answer
