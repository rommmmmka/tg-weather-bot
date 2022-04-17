from dataclasses import dataclass

from environs import Env


@dataclass
class Config:
    bot_token: str
    open_weather_token: str
    geodb_token: str
    admin_ids: list[int]
    database: str


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        bot_token=env.str("BOT_TOKEN"),
        open_weather_token=env.str("OPEN_WEATHER_TOKEN"),
        geodb_token=env.str("GEODB_TOKEN"),
        admin_ids=list(map(int, env.list("ADMINS"))),
        database=env.str("DATABASE")
    )
