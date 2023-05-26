import asyncio
import datetime
from sqlalchemy import create_engine, ForeignKey, Date, String, DateTime, \
    Float, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from sqlalchemy.ext.asyncio import create_async_engine

from config_data.config import config

engine = create_async_engine(f"mysql+asyncmy://{config.db.db_user}:{config.db.db_password}@{config.db.db_host}:{config.db.db_port}/{config.db.database}", echo=False)
connection = engine.connect()


class Base(DeclarativeBase):
    pass


class Token(Base):
    __tablename__ = 'tokens'
    id: Mapped[int] = mapped_column(primary_key=True,
                                    autoincrement=True,
                                    comment='Первичный ключ')
    date: Mapped[str] = mapped_column(String(30), default=str(datetime.datetime.now()))
    token: Mapped[str] = mapped_column(String(255))
    token_url: Mapped[str] = mapped_column(String(500))
    weth: Mapped[int] = mapped_column(String(255))
    score: Mapped[str] = mapped_column(String(500), nullable=True, default='')
    is_honeypot: Mapped[str] = mapped_column(String(255), nullable=True, default='')
    message_sended: Mapped[str] = mapped_column(String(30), default='')

    def __repr__(self):
        return f'{self.id}. {self.token} {self.score}'


class Liquidation(Base):
    __tablename__ = 'liquidates'
    id: Mapped[int] = mapped_column(primary_key=True,
                                    autoincrement=True,
                                    comment='Первичный ключ')
    source: Mapped[str] = mapped_column(String(100))
    text: Mapped[str] = mapped_column(String(255))
    addet_time: Mapped[str] = mapped_column(DateTime(), default=str(
        datetime.datetime.now()))
    transaction: Mapped[str] = mapped_column(String(25), nullable=True)
    volume: Mapped[float] = mapped_column(Float(), nullable=True)
    price: Mapped[float] = mapped_column(Float(), nullable=True)
    # __table_args__ = (UniqueConstraint('date', 'text', name='tweet_row'),)

    def __repr__(self):
        return f'{self.id}. {self.addet_time}: {self.text}'


# Base.metadata.create_all(engine)


async def init_models():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()

# asyncio.run(init_models())

