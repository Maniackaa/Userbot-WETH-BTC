import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from database.db import engine, init_models, BotSettings


async def add_column():
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        q = 'select(BotSettings)'


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(init_models())
        loop.run_until_complete(add_column())
    finally:
        loop.close()

