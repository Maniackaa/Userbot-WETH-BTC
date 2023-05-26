from dataclasses import dataclass


from environs import Env
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'default_formatter': {
            'format': "%(asctime)s - [%(levelname)8s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
        },
    },

    'handlers': {
        'stream_handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'default_formatter',
        },
        'rotating_file_handler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': f'{BASE_DIR / "logs" / "userbot"}.log',
            'backupCount': 2,
            'maxBytes': 1 * 1024 * 1024,
            'mode': 'a',
            'encoding': 'UTF-8',
            'formatter': 'default_formatter',
        },
        'rotating_file_handler2': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': f'{BASE_DIR / "logs" / "bot-btc-reporter"}.log',
            'backupCount': 2,
            'maxBytes': 1 * 1024 * 1024,
            'mode': 'a',
            'encoding': 'UTF-8',
            'formatter': 'default_formatter',
        },
        'rotating_file_handler3': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': f'{BASE_DIR / "logs" / "checker-sender"}.log',
            'backupCount': 2,
            'maxBytes': 1 * 1024 * 1024,
            'mode': 'a',
            'encoding': 'UTF-8',
            'formatter': 'default_formatter',
        },
        'errors_file_handler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': f'{BASE_DIR / "logs" / "errors_user_bot"}.log',
            'backupCount': 2,
            'maxBytes': 1 * 1024 * 1024,
            'mode': 'a',
            'encoding': 'UTF-8',
            'formatter': 'default_formatter',
        },
        'errors_file_handler2': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': f'{BASE_DIR / "logs" / "errors_bot_btc"}.log',
            'backupCount': 2,
            'maxBytes': 1 * 1024 * 1024,
            'mode': 'a',
            'encoding': 'UTF-8',
            'formatter': 'default_formatter',
        },
        'errors_file_handler3': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': f'{BASE_DIR / "logs" / "errors_checker-sender"}.log',
            'backupCount': 2,
            'maxBytes': 1 * 1024 * 1024,
            'mode': 'a',
            'encoding': 'UTF-8',
            'formatter': 'default_formatter',
        },
    },
    'loggers': {
        'userbot_logger': {
            'handlers': ['stream_handler', 'rotating_file_handler'],
            'level': 'DEBUG',
            'propagate': True
        },
        'bot-btc-reporter': {
            'handlers': ['stream_handler', 'rotating_file_handler2'],
            'level': 'DEBUG',
            'propagate': True
        },
        'checker-sender': {
            'handlers': ['stream_handler', 'rotating_file_handler3'],
            'level': 'DEBUG',
            'propagate': True
        },
        'errors_logger': {
            'handlers': ['stream_handler', 'errors_file_handler'],
            'level': 'DEBUG',
            'propagate': True
        },
        'errors_logger2': {
            'handlers': ['stream_handler', 'errors_file_handler2'],
            'level': 'DEBUG',
            'propagate': True
        },
        'errors_logger3': {
            'handlers': ['stream_handler', 'errors_file_handler3'],
            'level': 'DEBUG',
            'propagate': True
        },
    }
}


@dataclass
class DatabaseConfig:
    database: str  # Название базы данных
    db_host: str  # URL-адрес базы данных
    db_port: str  # URL-адрес базы данных
    db_user: str  # Username пользователя базы данных
    db_password: str  # Пароль к базе данных


@dataclass
class TgBot:
    token: str  # Токен для доступа к телеграм-боту
    admin_ids: list[int]  # Список id администраторов бота
    base_dir = BASE_DIR
    API_HASH: str
    API_ID: str


@dataclass
class Proxy:
    adress: str
    user: str
    password: str
    port: str


@dataclass
class Logic:
    HONEYPOT_DELAY: int


@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig
    proxy: Proxy
    logic: Logic


def load_config(path: str | None) -> Config:
    env: Env = Env()
    env.read_env(path)

    return Config(tg_bot=TgBot(token=env('BOT_TOKEN'),
                               API_HASH=env('API_HASH'),
                               API_ID=env('API_ID'),
                               admin_ids=list(map(int, env.list('ADMIN_IDS'))),
                               ),
                  db=DatabaseConfig(database=env('DB_NAME'),
                                    db_host=env('DB_HOST'),
                                    db_port=env('DB_PORT'),
                                    db_user=env('DB_USER'),
                                    db_password=env('DB_PASSWORD'),
                                    ),
                  proxy=Proxy(adress=env('PROXY_ADRESS'),
                              user=env('PROXY_USER'),
                              password=env('PROXY_PASSWORD'),
                              port=env('PROXY_PORT'),
                              ),
                  logic=Logic(HONEYPOT_DELAY=int(env('HONEYPOT_DELAY'))),
                  )


config = load_config('myenv.env')

# print('BOT_TOKEN:', config.tg_bot.token)
# print('ADMIN_IDS:', config.tg_bot.admin_ids)
# print()
# print('DATABASE:', config.db.database)
# print('DB_HOST:', config.db.db_host)
# print('DB_port:', config.db.db_port)
# print('DB_USER:', config.db.db_user)
# print('DB_PASSWORD:', config.db.db_password)
# print(config.tg_bot.admin_ids)
