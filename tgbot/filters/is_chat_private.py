from aiogram.dispatcher.filters import BoundFilter


class IsChatPrivateFilter(BoundFilter):
    key = 'is_chat_private'

    def __init__(self, is_chat_private: bool | None):
        self.is_chat_private = is_chat_private

    async def check(self, obj):
        if self.is_chat_private is None:
            return False
        return (obj.chat.type == "private") == self.is_chat_private
