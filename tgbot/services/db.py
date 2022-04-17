import os
import sqlite3

from aiogram import types

from tgbot.misc.other import draw_hist


class Database:
    def __init__(self, database: str):
        if not os.path.exists(database):
            open(database, 'w')
        self.db = sqlite3.connect(database)
        cursor = self.db.cursor()
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS cities (
                    city_id INT PRIMARY KEY,
                    city TEXT,
                    region TEXT,
                    country TEXT,
                    queries INT
                );
            """)
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS countries (
                    country_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    country TEXT,
                    queries INT
                );
            """)
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INT PRIMARY KEY,
                    name TEXT,
                    login TEXT,
                    queries INT,
                    last_query_id INT
                );
            """)
        self.db.commit()
        cursor.close()

    def clear_stats(self):
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM cities;")
        cursor.execute("DELETE FROM countries;")
        cursor.execute("DELETE FROM users;")
        self.db.commit()
        cursor.close()

    def add_city(self, data):
        cursor = self.db.cursor()
        cursor.execute(f"SELECT city_id FROM cities WHERE city_id = {data['id']}")
        table_row = cursor.fetchall()
        if not table_row:
            country = "Беларусь" if data['country'] == "Белоруссия" else data['country']
            cursor.execute(
                f"INSERT INTO cities VALUES ({data['id']}, '{data['city']}', '{data['region']}', '{country}', 1)")
        else:
            cursor.execute(f"UPDATE cities SET queries = queries + 1 WHERE city_id = {data['id']}")
        self.db.commit()
        cursor.close()

    def add_country(self, data):
        cursor = self.db.cursor()
        country = "Беларусь" if data['country'] == "Белоруссия" else data['country']
        cursor.execute(f"SELECT country_id FROM countries WHERE country = '{country}'")
        table_row = cursor.fetchall()
        if not table_row:
            cursor.execute(f"INSERT INTO countries VALUES (NULL, '{country}', 1)")
        else:
            cursor.execute(f"UPDATE countries SET queries = queries + 1 WHERE country = '{country}'")
        self.db.commit()
        cursor.close()

    def add_user(self, user_data, city_data):
        cursor = self.db.cursor()
        cursor.execute(f"SELECT user_id FROM users WHERE user_id = {user_data['id']}")
        table_row = cursor.fetchall()
        if not table_row:
            cursor.execute(f"""
                INSERT INTO users
                VALUES ({user_data['id']}, '{user_data['first_name']}', '{user_data['username']}', 1, {city_data['id']})
            """)
        else:
            cursor.execute(f"""
                UPDATE users
                SET name = '{user_data['first_name']}',
                    login = '{user_data['username']}',
                    queries = queries + 1,
                    last_query_id = {city_data['id']}
                WHERE user_id = {user_data['id']}
            """)
        self.db.commit()
        cursor.close()

    def add(self, user_data, city_data):
        self.add_city(city_data)
        self.add_country(city_data)
        self.add_user(user_data, city_data)

    async def reply_cities_stats(self, message: types.Message):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM cities ORDER BY -queries LIMIT 10;")
        data = cursor.fetchall()
        if not data:
            await message.reply("<b>Данные отсутствуют!</b>", disable_notification=True)
            return

        caption = f"<b>Топ {len(data)} самых запрашиваемых городов:</b>\n"
        cities = []
        queries = []
        for i, el in enumerate(data):
            cities.append(f"{el[1]}\n{el[2]}\n{el[3]}")
            queries.append(el[4])
            caption += f"{i + 1}) {el[1]}, {el[2]}, {el[3]} ({el[4]})\n"

        img = draw_hist(cities, queries, data[0][4])
        await message.bot.send_photo(message.chat.id, photo=img, caption=caption,
                                     reply_to_message_id=message.message_id,
                                     disable_notification=True)

    async def reply_countries_stats(self, message: types.Message):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM countries ORDER BY -queries LIMIT 10;")
        data = cursor.fetchall()
        if not data:
            await message.reply("<b>Данные отсутствуют!</b>", disable_notification=True)
            return

        caption = f"<b>Топ {len(data)} самых запрашиваемых стран:</b>\n"
        countries = []
        queries = []
        for i in data:
            countries.append(i[1])
            queries.append(i[2])
            caption += f"{i[0]}) {i[1]} ({i[2]})\n"

        img = draw_hist(countries, queries, data[0][2])
        await message.bot.send_photo(message.chat.id, photo=img, caption=caption,
                                     reply_to_message_id=message.message_id, disable_notification=True)

    async def reply_users_stats(self, message: types.Message):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM users ORDER BY -queries LIMIT 50;")
        data = cursor.fetchall()
        if not data:
            await message.reply("<b>Данные отсутствуют!</b>", disable_notification=True)
            return

        caption = f"<b>Топ {len(data)} самых активных пользователей:</b>\n"
        users = []
        queries = []
        for i, el in enumerate(data):
            users.append(f"{el[1]}\n@{el[2]}")
            queries.append(el[3])
            cursor.execute(f"SELECT * FROM cities WHERE city_id = {el[4]};")
            last_query = cursor.fetchall()
            caption += f"{i + 1}) {el[1]}, @{el[2]}\n" \
                       f"    ID чата: {el[0]}\n" \
                       f"    Количество запросов: {el[3]}\n" \
                       f"    Последний запрос: {last_query[0][1]}, {last_query[0][2]}, {last_query[0][3]}\n"

        await message.reply(caption, disable_notification=True)
