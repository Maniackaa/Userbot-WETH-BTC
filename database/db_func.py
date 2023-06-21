import datetime
import logging.config

from sqlalchemy import select, delete, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, \
    create_async_engine

from config_data.config import LOGGING_CONFIG, config
from database.db import engine, Liquidation, BotSettings
from services.func import find_start_period

logging.config.dictConfig(LOGGING_CONFIG)
err_log = logging.getLogger('errors_logger')
logger = logging.getLogger('bot-btc-reporter')


engine_uniswap = create_async_engine(f"mysql+asyncmy://{config.db.db_user}:{config.db.db_password}@{config.db.db_host}:{config.db.db_port}/uniswap_db", echo=False)


async def read_bot_settings(name: str) -> str:
    async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
        engine_uniswap, expire_on_commit=False)
    async with async_session() as session:
        q = select(BotSettings).where(BotSettings.name == name).limit(1)
        result = await session.execute(q)
        readed_setting: BotSettings = result.scalars().one_or_none()
    return readed_setting.value


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
        logger.debug(f'ПРобуем добавить {source, text, transaction, volume, price}')
        new_liquidation: Liquidation = Liquidation(
            source=source,
            text=text,
            addet_time=datetime.datetime.utcnow(),
            transaction=transaction,
            volume=volume,
            price=price
            )
        logger.debug(f'new_liquidation: {new_liquidation}')
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
        way_word = '🟢 Рынок вверх' if way < 0 else '🔴 Рынок вниз'
        report_message = (
            f'Отчет BTC-содержащих ликвидаций за период\n'
            f'с  {start_period}\n'
            f'по {str(datetime.datetime.utcnow())[:-7]}\n\n'
            f'Сумма Long: {long_sum:,.0f}\n'
            # f'{long_values}\n\n'
            f'Сумма Short: {short_sum:,.0f}\n\n'
            # f'{short_values}\n\n'
            f'{way_word}\n{way:,.0f}'
        )
        return report_message


async def get_last_volume(period, operation):
    """
    Раcчет объема последних операций за период в секундах.
    :param int period: Время в секундах.
    :param str operation: Поиск вхождения в text
    :return: объем за период
    :rtype: float
    """
    try:
        logger.debug(f'get_last_volume Секнуд назад:{period} Операция: {operation}')
        async_session = async_sessionmaker(engine)
        async with async_session() as session:
            result = await session.execute(select(Liquidation).filter(
                Liquidation.volume.is_not(None),
                Liquidation.text.icontains(operation),
                Liquidation.addet_time > datetime.datetime.utcnow() - datetime.timedelta(seconds=period)
                ).order_by(Liquidation.addet_time.desc()))
            tweets = result.scalars().all()
            volumes = []
            for row in tweets:
                volumes.append(row.volume)
            logger.debug(f'Объем {operation} за последние {period} секунд: {volumes}. Итого: {sum(volumes)}')
            await session.commit()
            await engine.dispose()
        logger.debug(f'Результат get_last_volume: {volumes}')
        return sum(volumes)
    except Exception:
        logger.error(f'Ошибка в функции get_last_volume', exc_info=True)

start_period = find_start_period(0)
report_message = (
    f'Отчет BTC-содержащих ликвидаций за период\n'
    f'с  {start_period}\n'
    f'по {str(datetime.datetime.utcnow())[:-7]}\n\n'

)
print(report_message)