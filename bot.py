import asyncio
import logging

from aiogram import Bot, Dispatcher

from tgbot.config import load_config
from tgbot.filters.command import CommandFilter
from tgbot.filters.is_admin import IsAdminFilter
from tgbot.filters.is_chat_private import IsChatPrivateFilter
from tgbot.handlers.admin import register_admin
from tgbot.handlers.info import register_info
from tgbot.handlers.misc import register_misc
from tgbot.handlers.tiktaktoe import register_tiktaktoe
from tgbot.handlers.weather import register_weather
from tgbot.services.db import Database

logger = logging.getLogger(__name__)


def register_all_filters(dp: Dispatcher):
    dp.filters_factory.bind(CommandFilter)
    dp.filters_factory.bind(IsAdminFilter)
    dp.filters_factory.bind(IsChatPrivateFilter)


def register_all_handlers(dp: Dispatcher):
    register_admin(dp)
    register_info(dp)
    register_misc(dp)
    register_tiktaktoe(dp)
    register_weather(dp)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'[%(asctime)s] #%(levelname)s %(filename)s:%(lineno)d - %(name)s - %(message)s',
    )
    logger.info("Запуск бота...")
    config = load_config(".env")

    bot = Bot(token=config.bot_token, parse_mode='HTML')
    dp = Dispatcher(bot)
    db = Database(config.firebase_key_path, config.firebase_url)

    bot['config'] = config
    bot['db'] = db

    register_all_filters(dp)
    register_all_handlers(dp)

    try:
        await dp.start_polling()
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.warning("Бот остановлен!")
