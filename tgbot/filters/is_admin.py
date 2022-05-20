from aiogram.dispatcher.filters import BoundFilter

from tgbot.config import Config


class IsAdminFilter(BoundFilter):
    key = 'is_admin'

    def __init__(self, is_admin: bool | None):
        self.is_admin = is_admin

    async def check(self, obj):
        if self.is_admin is None:
            return False
        config: Config = obj.bot.get('config')
        return (obj.from_user.id in config.admin_ids) == self.is_admin
