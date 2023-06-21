import asyncio
import datetime
import time
from pathlib import Path
import logging.config
import requests
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from config_data.config import config, LOGGING_CONFIG
from database.db import Token, engine
from database.db_func import read_bot_settings
from services.func import get_rug_check, get_honeypot_check, \
    get_honeypot_check_contract, find_holders

BASEDIR = Path(__file__).parent
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('checker-sender')
err_log = logging.getLogger('errors_logger3')


async def check_empty_score(async_session: async_sessionmaker[AsyncSession]):
    async with async_session() as session:
        result = await session.execute(select(Token).filter(
            Token.score == '').limit(1))
        token = result.scalars().first()
        logger.debug(token)
        if token:
            score = get_rug_check(token.token)
            logger.debug('score: {score}')
            token.score = score
        await session.commit()


async def check_empty_honey(async_session: async_sessionmaker[AsyncSession]):
    """
    Достает первый пустой is_honeypot
    Проверяет время и если время пришло заполняет is_honeypot и holders
    """
    async with async_session() as session:
        result = await session.execute(select(Token).filter(
            Token.is_honeypot == '').limit(1))
        token: Token = result.scalars().first()
        if token:
            HONEYPOT_DELAY = await read_bot_settings('HONEYPOT_DELAY')
            HONEYPOT_DELAY = int(HONEYPOT_DELAY)
            logger.debug(f'Проверяем token {token}')
            token_data = datetime.datetime.fromisoformat(token.date)
            logger.debug(f'token_data {token_data}')
            now_time = datetime.datetime.utcnow()
            logger.debug(f'now_time {now_time}')
            delta = (now_time - token_data).total_seconds()
            logger.debug(f'Дельта в секундах {delta}')
            logger.debug(f'{delta}/60 ({delta/60}) > {HONEYPOT_DELAY}: '
                         f'{delta / 60 > HONEYPOT_DELAY}')
            if delta / 60 > HONEYPOT_DELAY:
                honey = get_honeypot_check(token.token)
                holders = await find_holders(token.token)
                logger.debug(f'honey: {honey} holders: {holders}')
                token.is_honeypot = honey
                token.holders = holders
        await session.commit()


def token_is_ok(token_to_check: Token):
    # Проверка условий отправки сообщения
    logger.debug(f'Проверка на отправку сообщения')
    logger.debug(f'Nice in token_to_check.score and token_to_check.is_honeypot == 0 and int(token_to_check.weth) >= 0: {"Nice" in token_to_check.score and token_to_check.is_honeypot == "0" and int(token_to_check.weth) >= 0}')
    if 'Nice' in token_to_check.score and token_to_check.is_honeypot == '0' and int(token_to_check.weth) >= 0:
        honeypot_check_contract = get_honeypot_check_contract(token_to_check.token)
        logger.debug(f'honeypot_check_contract: {honeypot_check_contract} ({honeypot_check_contract is True})')
        if honeypot_check_contract is True:
            holders = token_to_check.holders
            logger.debug(f'holders: {holders}. > {config.logic.HOLDERS_LIMIT}: {token_to_check.holders > config.logic.HOLDERS_LIMIT}')
            if holders > config.logic.HOLDERS_LIMIT:
                logger.info(f'nice {token_to_check}')
                return 1
    logger.debug(f'Не отправляем {token_to_check}:')
    return 0


def format_message(token):
    logger.debug(f'Форматируем {token}')
    msg = (f'{token.token}\n'
           f'{token.token_url}\n'
           f'Weth: {token.weth}\n'
           f'Therugcheck: {token.score}\n'
           f'Is Honeypot: {token.is_honeypot}\n'
           )
    logger.debug(msg)
    return msg


def send_message_tg(message: str, chat_id: str,
                    sended_bot_token=config.tg_bot.token):
    """Отправка сообщения через чат-бот телеграмма"""
    url = (f'https://api.telegram.org/'
           f'bot{sended_bot_token}/'
           f'sendMessage?'
           f'chat_id={chat_id}&'
           f'text={message}')
    requests.get(url)


async def check_send(async_session: async_sessionmaker[AsyncSession]):
    """Отправка сообщения если удовлетворяют условия"""
    logger.debug('check_send')
    async with async_session() as session:
        # первое неотправленное и заполнены все поля
        result = await session.execute(select(Token).filter(
            Token.message_sended == '').filter(
            Token.score != '').filter(
            Token.is_honeypot != '').limit(1))
        token: Token = result.scalars().first()
        if token:
            logger.info(f'Есть не отправленные: {token.id}')
            # Надо отправлять?
            is_send = token_is_ok(token)
            logger.info(f'Результат проверки: {is_send}')
            token.message_sended = is_send
            if is_send:
                message = format_message(token)
                logger.info('Отправляем сообщение')
                send_message_tg(message, send_id, config.tg_bot.UNISWAP_TOKEN)
        await session.commit()


def read_group():
    with open(BASEDIR / 'myenv.env', 'r', encoding='UTF-8') as file:
        read_api_hash = config.tg_bot.API_HASH
        read_api_id = config.tg_bot.API_ID
        read_bot_token = config.tg_bot.UNISWAP_TOKEN
        read_send_id = config.tg_bot.admin_ids[0]
    return read_api_hash, read_api_id, read_bot_token, read_send_id


async def main():
    while True:
        try:
            await check_empty_score(async_sessionmaker(engine))
            await check_empty_honey(async_sessionmaker(engine))
            await check_send(async_sessionmaker(engine))
            logger.debug('Ждем')
            await asyncio.sleep(5)
        except Exception as err:
            err_log.error(f'Ошибка checker-sender', exc_info=True)
            await asyncio.sleep(5)
            continue

if __name__ == '__main__':

    api_hash, api_id, bot_token, send_id = read_group()
    asyncio.run(main())
