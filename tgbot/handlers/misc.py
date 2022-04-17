from aiogram import types, Dispatcher

from tgbot.keyboards.inline import getchatid_kb


async def callback_query_delete(callback_query: types.CallbackQuery):
    await callback_query.bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    await callback_query.bot.answer_callback_query(callback_query.id)


async def getchatid_command(message: types.Message):
    await message.reply(message.chat.id, reply_markup=getchatid_kb(), disable_notification=True)


def register_misc(dp: Dispatcher):
    dp.register_callback_query_handler(callback_query_delete, lambda c: c.data == "m_delete")
    dp.register_message_handler(getchatid_command, commands=["getchatid", "gcid"])
