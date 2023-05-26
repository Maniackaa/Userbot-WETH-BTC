import time
from pathlib import Path
import logging.config

from pyrogram import Client, filters
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message

from config_data.config import LOGGING_CONFIG, config
from database.add_token import add_token_to_base
from database.db_func import add_liquidation
from services.func import find_weth, send_message_tg
from services.response_func import response_liquidation, \
    response_bitmex_liquidation

BASEDIR = Path(__file__).parent
print(BASEDIR)


logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('userbot_logger')
err_log = logging.getLogger('errors_logger')


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
bot = Client(name='bot',
             api_id=api_id,
             api_hash=api_hash,
             bot_token=bot_token)


print(f'Стартовые настройки:\n'
      f'api_hash: {api_hash}\n'
      f'api_id: {api_id}\n'
      f'bot_token: {bot_token}\n'
      )


def filter_to_channel(data):
    async def func(flt, client, message):
        logger.debug(f'Фильтр на message:\n{message.text}')
        try:
            logger.debug(f'filter_to_channel. data: {data}')
            chat_title = message.chat.title
            logger.debug(f'chat_title: {message.chat.title}')
            logger.debug(f'chat_title in data: {chat_title in data}')
            print('chat_title:', chat_title)
            return chat_title in data
        except TypeError:
            err_log.warning(f'Ошибка в фильтре сообщения:{message}')
            return False
    return filters.create(func, data=data)


@client.on_message(filters.text & filters.channel &
                   filter_to_channel(['BitMEX Sniper']))
async def bitmex(client: Client, message: Message):
    """
    Достает из сообщения группы 'BitMEX Sniper' значения
     ликвидаций и добавляет в базу.
    :param client:
    :param message:
    :return:
    """
    logger.debug(f'BitMEX Sniper: {message.text}')
    try:
        text = message.text
        transaction, volume, price = response_bitmex_liquidation(text)
        await add_liquidation('Binance Futures Liquidations',
                                  text, transaction, volume, price)
    except Exception as err:
        err_log.warning(f'Ошибка при обработке сообщения:\n {message}')
        send_message_tg(f'Не распознал сообщение {message.chat.title}:\n'
                        f'{message.text}',
                        config.tg_bot.admin_ids[0])


@client.on_message(filters.text & filters.channel &
                   filter_to_channel(['Binance Futures Liquidations',
                                      'Bybit Liquidations 2.0 (Futures)',
                                      'BinanceLiquidations']))
async def binance_futures_liquidations(client: Client, message: Message):
    """
    Достает из сообщений групп
     'BinanceFutures_Liquidations', 'Bybit Liquidations 2.0 (Futures)'
      значения ликвидаций добавляет в базу.
    :param client:
    :param message:
    :return:
    """
    logger.debug(f'Binance Futures Liquidations: {message.text}')
    try:
        text = message.text
        source = message.chat.title
        coin, transaction, volume, price = response_liquidation(text)
        logger.debug(f'Распознано из {text}:\n'
                     f'{(coin, transaction, volume, price)}')
        if coin == 'BTC':
            await add_liquidation(source,
                                  text, transaction, volume, price)
        else:
            logger.debug(f'Не BTC: {text}')
    except Exception as err:
        err_log.warning(f'Ошибка при обработке сообщения:\n {message}')
        send_message_tg(f'Не распознал сообщение {message.chat.title}:\n'
                        f'{message.text}',
                        config.tg_bot.admin_ids[0])


@client.on_message(filters.channel & filter_to_channel(['Uniswap INSTANT Listings']))
async def send_message(client: Client, message: Message):
    """
    Достает из сообщения группы Uniswap INSTANT Listings значение WETH
     и адрес Etherscan и добавляет в базу.
    :param client:
    :param message:
    :return:
    """
    try:
        print('Uniswap INSTANT Listings')
        if 'WETH liquidity:' in message.text:
            weth = int(find_weth(message.text))
        else:
            weth = 0
        for entity in message.entities:
            if entity.type == MessageEntityType.TEXT_LINK:
                if 'https://etherscan.io/token/' in entity.url:
                    eth_url = entity.url
                    eth_token = entity.url.split('https://etherscan.io/token/')[1]
                    await add_token_to_base(eth_token, eth_url, weth)
    except Exception as err:
        print('Ошибка при обработке сообщения:')
        print(err)


@client.on_message()
async def last_filter(client: Client, message: Message):
    print('Мимо')
    # await add_token_to_base(message.text, '2', 3)

try:
    # bot.start()
    # bot.send_message(send_id, 'Monitoring start')
    client.run()

except Exception as err:
    # bot.stop()
    print(err)
    input('Ошибка. Нажмите Enter')
    raise err
