from aiogram.dispatcher.filters import BoundFilter


class CommandFilter(BoundFilter):
    key = "command"

    def __init__(self, command: list | None):
        self.command = command

    async def check(self, obj):
        return self.command and obj.data.split("_")[: len(self.command)] == self.command
