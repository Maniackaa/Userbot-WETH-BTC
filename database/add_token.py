import asyncio
import datetime
#
# from sqlalchemy.ext.asyncio import async_sessionmaker
# from sqlalchemy.orm import Session
# from database.db import Token, engine
# async_session = async_sessionmaker(engine)

from database.db import Token, engine
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


async def add_token_to_base(eth_token, eth_url, weth) -> None:
    new_token: Token = Token(
        date=datetime.datetime.now(),
        token=eth_token,
        token_url=eth_url,
        weth=weth,
        score='')
    async_session: AsyncSession = async_sessionmaker(engine)
    async with async_session() as session:
        session.add(new_token)
        await session.commit()
    await engine.dispose()


async def main():

    await add_token_to_base('1', '2', 3)
    await engine.dispose()

if __name__ == '__main__':
    print('xxxxxxxxxxxx')
    asyncio.run(main())
