import typing

from aiogram.dispatcher.filters import BoundFilter


class TiktaktoeCallbackFilter(BoundFilter):
    key = 'is_tiktaktoe_callback'

    def __init__(self, is_tiktaktoe_callback: typing.Optional[bool] = None):
        self.is_tiktaktoe_callback = is_tiktaktoe_callback

    async def check(self, obj):
        if self.is_tiktaktoe_callback is None:
            return False
        return (len(obj.data) > 0 and obj.data[0] == "t") == self.is_tiktaktoe_callback
