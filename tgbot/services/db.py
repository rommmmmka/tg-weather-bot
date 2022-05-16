from firebase_admin import credentials, initialize_app, db

from tgbot.misc.other import get_full_city_name


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

    def get_stats(self):
        data = self.ref.order_by_child("queries").get()
        queries = []
        cities_new_line = []
        cities_space = []
        for key in reversed(data):
            value = self.ref.child(key).get()
            queries.append(value['queries'])
            cities_new_line.append(get_full_city_name(value, "\n"))
            cities_space.append(get_full_city_name(value))

        return queries, cities_new_line, cities_space
