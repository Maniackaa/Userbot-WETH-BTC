from aiogram import Dispatcher, types, Router, Bot
from aiogram.filters import Command, CommandStart, Text
from aiogram.types import CallbackQuery, Message, URLInputFile

from aiogram.fsm.context import FSMContext

from database.db_func import get_last_liquidations

router: Router = Router()


@router.message(Command(commands=["start"]))
async def process_start_command(message: Message, state: FSMContext):
    await state.clear()
    text = (f'Привет! Это бот мониторинг групп:\n'
            f'https://t.me/BinanceFutures_Liquidations\n'
            f'https://t.me/BinanceLiquidations\n'
            f'https://t.me/BitMEXSniper\n'
            f'https://t.me/bybitliquidations20\n\n'
            f'Команды:\n'
            f'/report - Получить отчет\n'
            )
    await message.answer(text)


@router.message(Command(commands=["report"]))
async def process_start_command(message: Message):
    text = '🔴Пока не готово!🟢'
    report = await get_last_liquidations()
    text = '\n'.join([str(row) for row in report])
    await message.answer(text)


