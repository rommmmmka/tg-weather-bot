from aiogram import types, Dispatcher

from tgbot.services.db import Database

ADMIN_HELP = """<b>Синтаксис команд администратора:</b>
/admin [команда] [аргументы]
/a [команда] [аргументы]\n
<b>Список команд:</b>
help (h) – справка по командам
send (s) [id чата] [сообщение] – отправить сообщение от имени бота
stats (st) [cities/countries/users] – статистика бота
stats (st) clear - очистить статистику бота"""

ADMIN_STATS_SYNTAX = """<b>Синтаксис команды:</b>
/admin (a) stats (st) [параметр]
<b>Возможные параметры:</b>
cities – статистика по городам
countries – статистика по странам
users – статистика по пользователям
clear - очистить статистику"""


async def admin_command(message: types.Message):
    print(1)
    match message.get_args().split(" "):
        case ["help" | "h" | ""]:
            await message.reply(ADMIN_HELP, disable_notification=True)
        case ["send" | "s", chat_id, *msg]:
            try:
                await message.answer(chat_id, " ".join(msg))
            except Exception:
                await message.reply("<b>Возникла ошибка при отправке!</b> Возможно, такого чата не существует.",
                                    disable_notification=True)
        case ["remove" | "rm", link]:
            link = link.split('/')
            try:
                await message.bot.delete_message(chat_id=f"-100{link[4]}", message_id=link[5])
            except Exception:
                await message.reply(f"<b>Ошибка!</b> Сообщение не найдено.", disable_notification=True)
        case ["stats" | "st", *args]:
            info = args[0] if args else ""
            db: Database = message.bot.get('db')
            match info:
                case "cities":
                    await db.reply_cities_stats(message)
                case "countries":
                    await db.reply_countries_stats(message)
                case "users":
                    await db.reply_users_stats(message)
                case "clear":
                    db.clear_stats()
                    await message.reply("<b>Данные успешно удалены!</b>", disable_notification=True)
                case _:
                    await message.reply(ADMIN_STATS_SYNTAX, disable_notification=True)
        case _:
            await message.reply("<b>Ошибка!</b> Неизвестная команда.", disable_notification=True)


async def admin_command_no_access(message: types.Message):
    print(2)
    await message.reply("<b>Ошибка доступа!</b> Вы не являетесь администратором!", disable_notification=True)


async def admin_command_not_private_chat(message: types.Message):
    print(3)
    await message.reply("<b>Ошибка!</b> Панель администратора доступна только в личной переписке с ботом!",
                        disable_notification=True)


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_command, commands=["admin", "a"], is_chat_private=True, is_admin=True)
    dp.register_message_handler(admin_command_no_access, commands=["admin", "a"], is_chat_private=True, is_admin=False)
    dp.register_message_handler(admin_command_not_private_chat, commands=["admin", "a"], is_chat_private=False)
