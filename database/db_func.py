import datetime
import logging.config

from sqlalchemy import select, delete, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from config_data.config import LOGGING_CONFIG
from database.db import engine, Liquidation


logging.config.dictConfig(LOGGING_CONFIG)
err_log = logging.getLogger('errors_logger')


async def add_liquidation(source, text, transaction, volume, price) -> None:
    """
    Добавляет распознанную Ликвидацию в базу
    :param source:
    :param text:
    :param transaction:
    :param volume:
    :param price:
    :return:
    """
    try:
        new_liquidation: Liquidation = Liquidation(
            source=source,
            text=text,
            addet_time=datetime.datetime.utcnow(),
            transaction=transaction,
            volume=volume,
            price=price
            )
        async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(engine)
        async with async_session() as session:
            session.add(new_liquidation)
            await session.commit()
        await engine.dispose()
    except Exception as err:
        err_log.error(f'Ошибка добаления токена: {source}, {text}, {transaction}, {volume}, {price}')


async def get_last_liquidations():
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        query = select(Liquidation).limit(100)
        result = await session.scalars(query)
        # result = result.scalars().all()
        # print(result.all())
        result = result.all()
        for row in result:
            print(row, type(row))
        return result