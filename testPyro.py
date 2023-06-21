import time
from pathlib import Path


from pyrogram import Client

from config_data.config import LOGGING_CONFIG, config


BASEDIR = Path(__file__).parent
print(BASEDIR)


def read_group():
    with open(BASEDIR / 'myenv.env', 'r', encoding='UTF-8') as file:
        read_api_hash = config.tg_bot.API_HASH
        read_api_id = config.tg_bot.API_ID
        read_bot_token = config.tg_bot.token
        read_send_id = config.tg_bot.admin_ids[0]
    return read_api_hash, read_api_id, read_bot_token, read_send_id


try:
    api_hash, api_id, bot_token, send_id = read_group()
except Exception as err:
    time.sleep(5)
    raise err
delay = 1/20

client = Client(name="my_account", api_hash=api_hash, api_id=api_id)


print(f'Стартовые настройки:\n'
      f'api_hash: {api_hash}\n'
      f'api_id: {api_id}\n'
      f'bot_token: {bot_token}\n'
      )


try:
    client.run()

except Exception as err:
    print(err)
    input('Ошибка. Нажмите Enter')
    raise err
