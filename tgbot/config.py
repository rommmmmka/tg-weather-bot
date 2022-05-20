from dataclasses import dataclass

from environs import Env


@dataclass
class Config:
    bot_token: str
    open_weather_token: str
    geodb_token: str
    firebase_key_path: str
    firebase_url: str
    admin_ids: list[int]
    debug: bool


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        bot_token=env.str("BOT_TOKEN"),
        open_weather_token=env.str("OPEN_WEATHER_TOKEN"),
        geodb_token=env.str("GEODB_TOKEN"),
        firebase_key_path=env.str("FIREBASE_KEY_PATH"),
        firebase_url=env.str("FIREBASE_URL"),
        admin_ids=list(map(int, env.list("ADMINS"))),
        debug=env.bool("DEBUG"),
    )
