import asyncio

import logging.config
import time

from bs4 import BeautifulSoup
import aiohttp
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from config_data.config import LOGGING_CONFIG
from database.db import engine, Token


logging.config.dictConfig(LOGGING_CONFIG)
err_log = logging.getLogger('errors_logger')
logger = logging.getLogger('bot-btc-reporter')


async def get_tokens(async_session: async_sessionmaker[AsyncSession]):
    """
    """
    async with async_session() as session:
        result = await session.execute(select(Token))
        return result.scalars().all()


async def find_holders(token_adress: str, delay: float = 0.5) -> int:
    """"
    Находит количество Holders по адресу токена
    """
    start = time.perf_counter()
    try:
        await asyncio.sleep(delay)
        headers = {
            'authority': 'etherscan.io',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',  # noqa: E501
            'accept-language': 'ru,en;q=0.9',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "YaBrowser";v="23"',  # noqa: E501
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 YaBrowser/23.3.4.603 Yowser/2.5 Safari/537.36',   # noqa: E501
        }
        url = f'https://etherscan.io/token/{token_adress}'

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                html = await response.text()
        soup = BeautifulSoup(html, features='html.parser')
        holders_div = soup.find(id='ContentPlaceHolder1_tr_tokenHolders')
        holders_text = holders_div.find('div').text.strip().replace(',', '').split(' ')
        print(f'{round(time.perf_counter() - start, 2)}. {url}: {holders_text[0]}')
        return int(holders_text[0])
    except Exception as err:
        print(response.status, response.json())
        pass


async def main():
    x = await get_tokens(async_sessionmaker(engine))
    # tasks_args = [asyncio.create_task(find_holders(token.token, delay / 1))
    #               for token, delay in zip(x, range(0, len(x)))]
    # result = asyncio.gather(*tasks_args)
    # await result
    for token in x:
        await find_holders(token.token)



if __name__ == '__main__':
    asyncio.run(main())