import datetime

from database.db import Token, engine
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


async def add_token_to_base(eth_token, eth_url, weth) -> None:
    new_token: Token = Token(
        date=datetime.datetime.utcnow(),
        token=eth_token,
        token_url=eth_url,
        weth=weth,
        score='')
    async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
        engine)
    async with async_session() as session:
        session.add(new_token)
        await session.commit()
    await engine.dispose()
