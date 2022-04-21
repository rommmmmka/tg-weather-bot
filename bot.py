import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from tgbot.config import load_config
from tgbot.filters.admin import AdminFilter
from tgbot.filters.private_chat import PrivateChatFilter
from tgbot.filters.tiktaktoe_callback import TiktaktoeCallbackFilter
from tgbot.handlers.admin import register_admin
from tgbot.handlers.info import register_info
from tgbot.handlers.misc import register_misc
from tgbot.handlers.tiktaktoe import register_tiktaktoe
from tgbot.handlers.weather import register_weather
from tgbot.services.db import Database

logger = logging.getLogger(__name__)


def register_all_filters(dp: Dispatcher):
    dp.filters_factory.bind(AdminFilter)
    dp.filters_factory.bind(PrivateChatFilter)
    dp.filters_factory.bind(TiktaktoeCallbackFilter)


def register_all_handlers(dp: Dispatcher):
    register_admin(dp)
    register_info(dp)
    register_misc(dp)
    register_tiktaktoe(dp)
    register_weather(dp)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Запуск бота...")
    config = load_config(".env")

    storage = MemoryStorage()
    bot = Bot(token=config.bot_token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)
    db = Database(config.firebase_key_path, config.firebase_url)

    bot['config'] = config
    bot['db'] = db

    register_all_filters(dp)
    register_all_handlers(dp)

    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Бот остановлен!")
