from aiogram import types
from firebase_admin import credentials, initialize_app, db

from tgbot.misc.other import draw_hist, get_full_city_name


class Database:
    def __init__(self, firebase_key_path: str, firebase_url: str):
        cred = credentials.Certificate(firebase_key_path)
        app = initialize_app(cred)
        self.ref = db.reference("/cities/", app, firebase_url)

    def add_city(self, data):
        country = "Беларусь" if data['country'] == "Белоруссия" else data['country']
        cities = self.ref.get()
        key = str(data['id'])
        if cities and key in cities:
            value = cities.get(key)
            self.ref.child(key).update({'queries': value['queries'] + 1})
        else:
            self.ref.child(key).set({
                "city": data['city'],
                "region": data['region'],
                "country": country,
                "queries": 1
            })

    def clear_stats(self):
        self.ref.set({})

    async def reply_cities_stats(self, message: types.Message):
        data = self.ref.order_by_child("queries").limit_to_last(10).get()
        if not data:
            await message.reply("<b>Данные отсутствуют!</b>", disable_notification=True)
            return

        caption = f"<b>Топ {len(data)} самых запрашиваемых городов:</b>\n"
        cities = []
        queries = []
        for i, key in enumerate(reversed(data)):
            value = self.ref.child(key).get()
            queries.append(value['queries'])
            cities.append(get_full_city_name(value, "\n"))
            caption += f"{i + 1}) {get_full_city_name(value)} ({value['queries']})\n"

        img = draw_hist(cities, queries, queries[0])
        await message.bot.send_photo(message.chat.id, photo=img, caption=caption,
                                     reply_to_message_id=message.message_id, disable_notification=True)
