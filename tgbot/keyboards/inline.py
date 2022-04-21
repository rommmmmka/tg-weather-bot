from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.misc.tiktaktoe import TIKTAKTOE_EMOJI


def cities_kb(data: list):
    from tgbot.misc.other import get_full_city_name
    answer = "<b>Найдено несколько результатов:</b>"
    kb = InlineKeyboardMarkup()
    for i, el in enumerate(data):
        answer += f"\n<b>{i + 1})</b> {get_full_city_name(el)}"
        kb.add(InlineKeyboardButton(str(i + 1), callback_data=f"w_{el['id']}"))
    return answer, kb


def getid_kb():
    return InlineKeyboardMarkup().add(InlineKeyboardButton("Спасибо", callback_data="m_delete"))


def tiktaktoe_singleplayer_kb(player_id: int):
    kb = InlineKeyboardMarkup()
    for i in range(3):
        btns = [
            InlineKeyboardButton(TIKTAKTOE_EMOJI['Empty'], callback_data=f"t_sp_{player_id}_{i}_{j}")
                for j in range(3)
        ]
        kb = kb.row(*btns)
    return kb


def tiktaktoe_multiplayer_kb(player1_id: int, player2_id: int):
    kb = InlineKeyboardMarkup()
    for i in range(3):
        btns = [
            InlineKeyboardButton(TIKTAKTOE_EMOJI['Empty'], callback_data=f"t_mp_{player1_id}_{player2_id}_{i}_{j}_1")
            for j in range(3)
        ]
        kb = kb.row(*btns)
    return kb


def tiktaktoe_pick_enemy_kb(player_id: int):
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton("Против бота", callback_data=f"t_gmpick_{player_id}_1"),
        InlineKeyboardButton("Против человека", callback_data=f"t_gmpick_{player_id}_2")
    )


def tiktaktoe_join_kb(player_id: int):
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton("Вступить в игру", callback_data=f"t_mpjoin_{player_id}")
    )


def tiktaktoe_kill_callback_queries(kb: types.InlineKeyboardMarkup):
    for i in range(3):
        for j in range(3):
            kb.inline_keyboard[i][j].callback_data = "t_killed"
    return kb


def tiktaktoe_change_order(kb: types.InlineKeyboardMarkup, new_order: int):
    for i in range(3):
        for j in range(3):
            kb.inline_keyboard[i][j].callback_data = kb.inline_keyboard[i][j].callback_data[:-1] + str(new_order)
    return kb
