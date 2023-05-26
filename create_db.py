import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from database.db import engine, init_models, BotSettings


async def settings_default():
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        q = select(BotSettings)
        result = await session.execute(q)
        settings = result.all()
        if not settings:
            print('Добавляем настройки по умолчанию')
            settings1 = BotSettings(
                name='HONEYPOT_DELAY',
                value='720',
                description='Задержка проверки HONEYPOT, мин.',
            )
            session.add_all([settings1])
            await session.commit()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(init_models())
        loop.run_until_complete(settings_default())
    finally:
        loop.close()



