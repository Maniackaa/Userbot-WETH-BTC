from aiogram import Dispatcher, types, Router, Bot
from aiogram.filters import Command, CommandStart, Text
from aiogram.types import CallbackQuery, Message, URLInputFile

from aiogram.fsm.context import FSMContext

from database.db_func import lat_week_short_lonh_report, get_last_liquidations
from services.func import format_last_report

router: Router = Router()


@router.message(Command(commands=["start"]))
async def process_start_command(message: Message, state: FSMContext):
    await state.clear()
    text = (f'Привет! Это бот мониторинг групп:\n'
            f'https://t.me/BinanceFutures_Liquidations\n'
            f'https://t.me/BitMEXSniper\n'
            f'https://t.me/bybitliquidations20\n\n'
            f'Команды:\n'
            f'/report - Получить отчет\n'
            f'/last - Получить последние 10 ликивдаций\n'
            )
    await message.answer(text)


@router.message(Command(commands=["report"]))
async def process_report_command(message: Message):
    report = await lat_week_short_lonh_report()
    if report:
        # text = '\n'.join([str(row) for row in report])
        text = report
    else:
        text = 'Empty'
    await message.answer(text)


@router.message(Command(commands=["last"]))
async def process_last_command(message: Message):
    last = await get_last_liquidations()
    text = format_last_report(last)
    await message.answer(text)

