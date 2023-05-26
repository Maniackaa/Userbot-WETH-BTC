import datetime
import logging.config

from sqlalchemy import select, delete, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from config_data.config import LOGGING_CONFIG
from database.db import engine, Liquidation
from services.func import find_start_period

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
        query = select(Liquidation).order_by(
            Liquidation.addet_time.desc()).limit(10)
        result = await session.scalars(query)
        result = result.all()
        for row in result:
            print(row, type(row))
        return result


async def lat_week_short_lonh_report():
    async_session = async_sessionmaker(engine)
    async with async_session() as session:
        start_period = find_start_period(0)
        long_query = select(Liquidation.volume).filter(
            Liquidation.text.contains('Long'),
            Liquidation.volume.is_not(None),
            Liquidation.addet_time > start_period
            )
        long_rows = await session.execute(long_query)
        long = long_rows.scalars().all()
        print(long)
        long_values = [x for x in long]
        long_sum = sum(long_values)

        short_query = select(Liquidation.volume).filter(
            Liquidation.text.contains('Short'),
            Liquidation.volume.is_not(None),
            Liquidation.addet_time > start_period
            )
        short = await session.execute(short_query)
        short = short.scalars().all()
        short_values = [x for x in short]
        short_sum = sum(short_values)

        way = long_sum - short_sum
        way_word = '🔴 Рынок вверх' if way < 0 else '🟢 Рынок вниз'
        report_message = (
            f'Отчет BTC-содержащих ликвидаций за период\n'
            f'с  {start_period}\n'
            f'по {str(datetime.datetime.now())[:-7]}\n\n'
            f'Сумма Long: {long_sum:,.0f}\n'
            # f'{long_values}\n\n'
            f'Сумма Short: {short_sum:,.0f}\n\n'
            # f'{short_values}\n\n'
            f'{way_word}\n{way:,.0f}'
        )
        return report_message
