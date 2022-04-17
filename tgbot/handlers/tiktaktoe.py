from aiogram import Dispatcher, types

from tgbot.keyboards.inline import tiktaktoe_singleplayer_kb, tiktaktoe_pick_enemy_kb, tiktaktoe_kill_callback_queries, \
    tiktaktoe_join_kb, tiktaktoe_multiplayer_kb, tiktaktoe_change_order
from tgbot.misc.tiktaktoe import TIKTAKTOE_EMOJI, tiktaktoe_check_win, tiktaktoe_place_zero


async def callback_query_pick_gamemode(callback_query: types.CallbackQuery):
    player_id, gamemode = map(int, callback_query.data.split("_")[2:])
    if callback_query.from_user.id != player_id:
        await callback_query.bot.answer_callback_query(callback_query.id)
        return
    if gamemode == 1:
        await callback_query.bot.edit_message_text(
            f"<b>Крестики-нолики</b>\n@{callback_query.from_user.username} vs бот", callback_query.message.chat.id,
            callback_query.message.message_id,
            reply_markup=tiktaktoe_singleplayer_kb(callback_query.from_user.id))
    else:
        await callback_query.bot.edit_message_text(
            f"<b>Крестики-нолики</b>\n@{callback_query.from_user.username} vs ...\nПоиск противника",
            callback_query.message.chat.id, callback_query.message.message_id,
            reply_markup=tiktaktoe_join_kb(callback_query.from_user.id))
        await callback_query.bot.answer_callback_query(callback_query.id)


async def callback_query_join(callback_query: types.CallbackQuery):
    player1_id = int(callback_query.data.split("_")[2])
    if callback_query.from_user.id == player1_id:
        await callback_query.bot.answer_callback_query(callback_query.id)
        # return
    player2_id = callback_query.from_user.id
    message_split = callback_query.message.text[:-20].split("\n")
    message = f"<b>{message_split[0]}</b>\n{message_split[1]}@{callback_query.from_user.username}\nХод первого игрока"
    await callback_query.bot.edit_message_text(message, callback_query.message.chat.id,
                                               callback_query.message.message_id,
                                               reply_markup=tiktaktoe_multiplayer_kb(player1_id, player2_id))


async def callback_query_singleplayer(callback_query: types.CallbackQuery):
    try:
        player_id, i, j = map(int, callback_query.data.split("_")[2:])
        if player_id != callback_query.from_user.id:
            raise Exception
        kb = callback_query.message.reply_markup
        if kb.inline_keyboard[i][j].text != TIKTAKTOE_EMOJI['Empty']:
            raise Exception

        kb.inline_keyboard[i][j].text = TIKTAKTOE_EMOJI['Cross']
        winner = tiktaktoe_check_win(kb.inline_keyboard)
        if winner == 0 or winner == -1:
            kb.inline_keyboard = tiktaktoe_place_zero(kb.inline_keyboard)
            winner = tiktaktoe_check_win(kb.inline_keyboard)

        message_split = callback_query.message.text.split("\n")
        message = f"<b>{message_split[0]}</b>"
        if len(message_split) == 2:
            message += "\n" + message_split[1]
        match winner:
            case 0:
                await callback_query.bot.edit_message_text(message, callback_query.message.chat.id,
                                                           callback_query.message.message_id, reply_markup=kb)
            case -1:
                kb = tiktaktoe_kill_callback_queries(kb)
                await callback_query.bot.edit_message_text(message + "\nНичья!",
                                                           callback_query.message.chat.id,
                                                           callback_query.message.message_id, reply_markup=kb)
            case w:
                kb = tiktaktoe_kill_callback_queries(kb)
                await callback_query.bot.edit_message_text(
                    message + f"\nВы {'победили' if w == TIKTAKTOE_EMOJI['Cross'] else 'проиграли'}!",
                    callback_query.message.chat.id, callback_query.message.message_id, reply_markup=kb)
    except Exception:
        pass
    await callback_query.bot.answer_callback_query(callback_query.id)


async def callback_query_multiplayer(callback_query: types.CallbackQuery):
    player1_id, player2_id, i, j, order = map(int, callback_query.data.split("_")[2:])
    if order == 1:
        current_player_id = player1_id
        current_emoji = TIKTAKTOE_EMOJI['Cross']
    else:
        current_player_id = player2_id
        current_emoji = TIKTAKTOE_EMOJI['Zero']

    try:
        if current_player_id != callback_query.from_user.id:
            raise Exception
        kb = callback_query.message.reply_markup
        if kb.inline_keyboard[i][j].text != TIKTAKTOE_EMOJI['Empty']:
            raise Exception

        kb.inline_keyboard[i][j].text = current_emoji
        winner = tiktaktoe_check_win(kb.inline_keyboard)
        message_split = callback_query.message.text.split("\n")[:2]
        message = f"<b>{message_split[0]}</b>\n{message_split[1]}\n"

        match winner:
            case 0:
                new_order = 1 if order == 2 else 2
                message += "Ход первого игрока" if new_order == 1 else "Ход второго игрока"
                kb = tiktaktoe_change_order(kb, new_order)
                await callback_query.bot.edit_message_text(message, callback_query.message.chat.id,
                                                           callback_query.message.message_id, reply_markup=kb)
            case -1:
                kb = tiktaktoe_kill_callback_queries(kb)
                await callback_query.bot.edit_message_text(message + "Ничья!", callback_query.message.chat.id,
                                                           callback_query.message.message_id, reply_markup=kb)
            case w:
                message += f"Победил {'первый' if w == TIKTAKTOE_EMOJI['Cross'] else 'второй'} игрок"
                kb = tiktaktoe_kill_callback_queries(kb)
                await callback_query.bot.edit_message_text(message, callback_query.message.chat.id,
                                                           callback_query.message.message_id, reply_markup=kb)
    except Exception:
        pass
    await callback_query.bot.answer_callback_query(callback_query.id)


async def callback_query_killed_answer(callback_query: types.CallbackQuery):
    await callback_query.bot.answer_callback_query(callback_query.id)


async def tiktaktoe_start(message: types.Message):
    await message.reply("<b>Крестики-нолики</b>", reply_markup=tiktaktoe_singleplayer_kb(message.from_user.id),
                        disable_notification=True)


async def tiktaktoe_start_group(message: types.Message):
    await message.reply("<b>Крестики нолики</b>\nВыберите режим",
                        reply_markup=tiktaktoe_pick_enemy_kb(message.from_user.id),
                        disable_notification=True)


def register_tiktaktoe(dp: Dispatcher):
    dp.register_callback_query_handler(callback_query_pick_gamemode,
                                       lambda c: c.data[0] == "t" and c.data.split("_")[1] == "gmpick")
    dp.register_callback_query_handler(callback_query_join,
                                       lambda c: c.data[0] == "t" and c.data.split("_")[1] == "mpjoin")
    dp.register_callback_query_handler(callback_query_singleplayer,
                                       lambda c: c.data[0] == "t" and c.data.split("_")[1] == "sp")
    dp.register_callback_query_handler(callback_query_multiplayer,
                                       lambda c: c.data[0] == "t" and c.data.split("_")[1] == "mp")
    dp.register_callback_query_handler(callback_query_killed_answer,
                                       lambda c: c.data[0] == "t" and c.data.split("_")[1] == "killed")

    dp.register_message_handler(tiktaktoe_start, commands=["tiktaktoe", "ttt"], is_chat_private=True)
    dp.register_message_handler(tiktaktoe_start_group, commands=["tiktaktoe", "ttt"], is_chat_private=False)
