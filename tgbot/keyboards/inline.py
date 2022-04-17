from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def cities_inline_kb(data):
    from tgbot.misc.other import get_full_city_name
    answer = "<b>Найдено несколько результатов:</b>"
    kb = InlineKeyboardMarkup()
    for i, el in enumerate(data):
        answer += f"\n<b>{i + 1})</b> {get_full_city_name(el)}"
        kb.add(InlineKeyboardButton(str(i + 1), callback_data=f"w{el['id']}"))
    return answer, kb


def getchatid_inline_kb():
    return InlineKeyboardMarkup().add(InlineKeyboardButton("Спасибо", callback_data="delete"))


def tiktaktoe_inline_kb():
    from tgbot.misc.tiktaktoe import TIKTAKTOE_EMOJI
    kb = InlineKeyboardMarkup()
    for i in range(3):
        btns = [InlineKeyboardButton(TIKTAKTOE_EMOJI['Empty'], callback_data=f"t{i}{j}") for j in range(3)]
        kb = kb.row(btns[0], btns[1], btns[2])
    return kb
