from aiogram import Dispatcher, types

from tgbot.keyboards.inline import tiktaktoe_inline_kb
from tgbot.misc.tiktaktoe import TIKTAKTOE_EMOJI, tiktaktoe_kill_callback_queries, tiktaktoe_check_win, \
    tiktaktoe_place_zero


async def callback_query_tiktaktoe_button(callback_query: types.CallbackQuery):
    try:
        i = int(callback_query.data[1])
        j = int(callback_query.data[2])
        kb = callback_query['message']['reply_markup']
        if kb['inline_keyboard'][i][j]['text'] != TIKTAKTOE_EMOJI['Empty']:
            raise Exception
        else:
            kb['inline_keyboard'][i][j]['text'] = TIKTAKTOE_EMOJI['Cross']
            winner = tiktaktoe_check_win(kb['inline_keyboard'])
            if winner == 0 or winner == -1:
                kb['inline_keyboard'] = tiktaktoe_place_zero(kb['inline_keyboard'])
                winner = tiktaktoe_check_win(kb['inline_keyboard'])
            match winner:
                case 0:
                    await callback_query.bot.edit_message_text("<b>Крестики нолики</b>",
                                                               callback_query['message']['chat']['id'],
                                                               callback_query['message']['message_id'], reply_markup=kb)
                case -1:
                    kb = tiktaktoe_kill_callback_queries(kb)
                    await callback_query.bot.edit_message_text("<b>Крестики нолики</b>\nНичья!",
                                                               callback_query['message']['chat']['id'],
                                                               callback_query['message']['message_id'], reply_markup=kb)
                case w:
                    kb = tiktaktoe_kill_callback_queries(kb)
                    await callback_query.bot.edit_message_text(
                        f"<b>Крестики нолики</b>\nВы {'победили' if w == TIKTAKTOE_EMOJI['Cross'] else 'проиграли'}!",
                        callback_query['message']['chat']['id'],
                        callback_query['message']['message_id'], reply_markup=kb)

    except Exception:
        pass
    await callback_query.bot.answer_callback_query(callback_query.id)


async def callback_query_tiktaktoe_killed(callback_query: types.CallbackQuery):
    await callback_query.bot.answer_callback_query(callback_query.id)


async def tiktaktoe_command(message: types.Message):
    await message.reply("<b>Крестики нолики</b>", reply_markup=tiktaktoe_inline_kb(), disable_notification=True)


def register_tiktaktoe(dp: Dispatcher):
    dp.register_callback_query_handler(callback_query_tiktaktoe_button, lambda c: len(c.data) > 0 and c.data[0] == "t")
    dp.register_callback_query_handler(callback_query_tiktaktoe_killed, lambda c: c.data[0] == "killed_callback_query")
    dp.register_message_handler(tiktaktoe_command, commands=["tiktaktoe", "ttt"])
