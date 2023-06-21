import asyncio
import datetime
import sys

from sqlalchemy import create_engine, ForeignKey, Date, String, DateTime, \
    Float, UniqueConstraint, Integer
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from sqlalchemy.ext.asyncio import create_async_engine

from config_data.config import config

engine = create_async_engine(f"mysql+asyncmy://{config.db.db_user}:{config.db.db_password}@{config.db.db_host}:{config.db.db_port}/{config.db.database}", echo=False)


class Base(DeclarativeBase):
    pass


class Token(Base):
    __tablename__ = 'tokens'
    id: Mapped[int] = mapped_column(primary_key=True,
                                    autoincrement=True,
                                    comment='Первичный ключ')
    date: Mapped[str] = mapped_column(String(30), default=str(datetime.datetime.utcnow()))
    token: Mapped[str] = mapped_column(String(255))
    token_url: Mapped[str] = mapped_column(String(500))
    weth: Mapped[int] = mapped_column(String(255))
    score: Mapped[str] = mapped_column(String(500), nullable=True, default='')
    is_honeypot: Mapped[str] = mapped_column(String(255), nullable=True, default='')
    holders: Mapped[int] = mapped_column(Integer(), nullable=True)
    message_sended: Mapped[str] = mapped_column(String(30), default='')
    last_call: Mapped[str] = mapped_column(DateTime())

    def __repr__(self):
        return f'{self.id}. {self.token}'


class Liquidation(Base):
    __tablename__ = 'liquidates'
    id: Mapped[int] = mapped_column(primary_key=True,
                                    autoincrement=True,
                                    comment='Первичный ключ')
    source: Mapped[str] = mapped_column(String(100))
    text: Mapped[str] = mapped_column(String(255))
    addet_time: Mapped[str] = mapped_column(DateTime(), default=str(
        datetime.datetime.utcnow()))
    transaction: Mapped[str] = mapped_column(String(25), nullable=True)
    volume: Mapped[float] = mapped_column(Float(), nullable=True)
    price: Mapped[float] = mapped_column(Float(), nullable=True)
    # __table_args__ = (UniqueConstraint('date', 'text', name='tweet_row'),)

    def __repr__(self):
        return f'{self.id}. {self.addet_time}: {self.text}'


class BotSettings(Base):
    __tablename__ = 'bot_settings'
    id: Mapped[int] = mapped_column(primary_key=True,
                                    autoincrement=True,
                                    comment='Первичный ключ')
    name: Mapped[str] = mapped_column(String(50))
    value: Mapped[str] = mapped_column(String(50), nullable=True, default='')
    description: Mapped[str] = mapped_column(String(255),
                                             nullable=True,
                                             default='')


async def init_models():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


if __name__ == '__main__':
    if sys.version_info[:2] == (3, 7):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(init_models())
        loop.run_until_complete(asyncio.sleep(2.0))
    finally:
        loop.close()

