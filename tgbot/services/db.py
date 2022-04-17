from aiogram import types

from tgbot.misc.other import draw_hist
import firebase_admin
from firebase_admin import credentials, db


class Database:
    def __init__(self, firebase_key_path: str, firebase_url: str):
        cred = credentials.Certificate(firebase_key_path)
        self.app = firebase_admin.initialize_app(cred)
        self.url = firebase_url

    def add_city(self, data):
        country = "Беларусь" if data['country'] == "Белоруссия" else data['country']
        ref = db.reference("/cities/", self.app, self.url)
        cities = ref.get()
        key = str(data['id'])
        if cities and key in cities:
            value = cities.get(key)
            ref.child(key).update({'queries': value['queries'] + 1})
        else:
            ref.child(key).set({
                "city": data['city'],
                "region": data['region'],
                "country": country,
                "queries": 1
            })

    def clear_stats(self):
        ref = db.reference("/cities/", self.app, self.url)
        ref.set({})

    async def reply_cities_stats(self, message: types.Message):
        ref = db.reference("/cities/", self.app, self.url)
        data = ref.order_by_child("queries").limit_to_last(10).get()
        if not data:
            await message.reply("<b>Данные отсутствуют!</b>", disable_notification=True)
            return

        caption = f"<b>Топ {len(data)} самых запрашиваемых городов:</b>\n"
        cities = []
        queries = []
        for i, key in enumerate(reversed(data)):
            value = ref.child(key).get()
            queries.append(value['queries'])
            cities.append(f"{value['city']}\n{value['region']}\n{value['country']}")
            caption += f"{i + 1}) {value['city']}, {value['region']}, {value['country']} ({value['queries']})\n"

        img = draw_hist(cities, queries, data[0][4])
        await message.bot.send_photo(message.chat.id, photo=img, caption=caption,
                                     reply_to_message_id=message.message_id, disable_notification=True)
