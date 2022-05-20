from aiogram import types, Dispatcher

from tgbot.keyboards.reply import base_reply_kb

HELP_MESSAGE = """<b>Привет! Вот список моих команд:</b>
/start или /help – справка по командам
/about – история метеостанции
/weather [город] или /w [город] – информация о погоде
/tiktaktoe или /ttt – крестики-нолики
/getchatid или /gcid – получить идентификатор чата
/getmyid или /gmid – получить личный идентификатор
/admin или /a – панель администратора"""

ABOUT_MESSAGE = """<b>Метеостанция №13 г. Любань</b> является самой старой метеостанцией Беларуси. Её история начинается 29 ноября 1872 года, когда по указу императора Александра II в местечке Любань была открыта первая в Российской Империи метеостанция. 9 января 1936 года по приказу И.В. Сталина ей было присвоено имя выдающегося учёного-метеоролога Р.П. Багрия.\n
На протяжении полутора веков своей истории, наблюдения на станции оставались на высочайшем уровне. Здесь трудились и трудятся настоящие специалисты-профессионалы в своей области.\n
В последние годы, в рамках проекта по модернизации станции, было введено в эксплуатацию множество новых автоматизированных метеорологических средств, разработанных совместно с Белорусским Государственным Университетом Информатики и Радиоэлектроники."""


async def start_help_commands(message: types.Message):
    await message.reply(
        HELP_MESSAGE,
        reply_markup=base_reply_kb(message.chat.type),
        disable_notification=True,
    )


async def about_command(message: types.Message):
    await message.reply(ABOUT_MESSAGE, disable_notification=True)


def register_info(dp: Dispatcher):
    dp.register_message_handler(start_help_commands, commands=["start", "help"])
    dp.register_message_handler(about_command, commands=["about"])
