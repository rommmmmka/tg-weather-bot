from aiogram import types, Dispatcher

from tgbot.misc.plots import get_plot
from tgbot.services.db import Database

ADMIN_HELP = """<b>Синтаксис команд администратора:</b>
/admin [команда] [аргументы]
/a [команда] [аргументы]\n
<b>Список команд:</b>
help (h) – справка по командам
send (s) [id чата] [сообщение] – отправить сообщение от имени бота
remove (rm) [ссылка на сообщение] – удалить сообщение
stats (st) [параметр] – статистика бота"""

ADMIN_STATS_SYNTAX = """<b>Синтаксис команды:</b>
/admin (a) stats (st) [параметр]
<b>Возможные параметры:</b>
hist (h) – гистограмма
circle (c) - круговая диаграмма
clear – очистить статистику"""


async def admin_command(message: types.Message):
    match message.get_args().split(" "):
        case ["help" | "h" | ""]:
            await message.reply(ADMIN_HELP, disable_notification=True)
        case ["send" | "s", chat_id, *msg]:
            try:
                await message.bot.send_message(chat_id, " ".join(msg))
            except Exception:
                await message.reply(
                    "<b>Возникла ошибка при отправке!</b> Возможно, такого чата не существует.",
                    disable_notification=True,
                )
        case ["remove" | "rm", link]:
            link = link.split("/")
            try:
                await message.bot.delete_message(
                    chat_id=f"-100{link[4]}", message_id=link[5]
                )
            except Exception:
                await message.reply(
                    f"<b>Ошибка!</b> Сообщение не найдено.", disable_notification=True
                )
        case ["stats" | "st", *args]:
            plot_type = args[0] if args else ""
            db: Database = message.bot.get("db")
            match plot_type:
                case "hist" | "circle" | "h" | "c":
                    queries, cities_new_line, cities_space = db.get_stats()
                    if len(queries) == 0:
                        await message.reply(
                            "<b>Данные отсутствуют!</b>", disable_notification=True
                        )
                        return
                    img = get_plot(plot_type, queries, cities_new_line)
                    caption = "<b>Самые запрашиваемые города:</b>"
                    for i, (city_name, queries_number) in enumerate(
                        zip(cities_space, queries)
                    ):
                        caption += f"\n{i + 1}) {city_name} ({queries_number})"
                    await message.bot.send_photo(
                        message.chat.id,
                        photo=img,
                        caption=caption,
                        reply_to_message_id=message.message_id,
                        disable_notification=True,
                    )
                case "clear":
                    db.clear_stats()
                    await message.reply(
                        "<b>Данные успешно удалены!</b>", disable_notification=True
                    )
                case _:
                    await message.reply(ADMIN_STATS_SYNTAX, disable_notification=True)
        case _:
            await message.reply(
                "<b>Ошибка!</b> Неизвестная команда.", disable_notification=True
            )


async def admin_command_no_access(message: types.Message):
    await message.reply(
        "<b>Ошибка доступа!</b> Вы не являетесь администратором!",
        disable_notification=True,
    )


async def admin_command_not_private_chat(message: types.Message):
    await message.reply(
        "<b>Ошибка!</b> Панель администратора доступна только в личной переписке с ботом!",
        disable_notification=True,
    )


def register_admin(dp: Dispatcher):
    dp.register_message_handler(
        admin_command, commands=["admin", "a"], is_chat_private=True, is_admin=True
    )
    dp.register_message_handler(
        admin_command_no_access,
        commands=["admin", "a"],
        is_chat_private=True,
        is_admin=False,
    )
    dp.register_message_handler(
        admin_command_not_private_chat, commands=["admin", "a"], is_chat_private=False
    )
