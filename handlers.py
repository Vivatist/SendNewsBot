from datetime import timedelta
from aiogram import types, F, Router, Dispatcher
from aiogram.filters import Command, CommandStart
from db import add_new_user, add_message_to_queue, get_last_time, get_timeleft
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
import config


def get_start_keyboard():
    buttons = [
        [
            types.InlineKeyboardButton(text="Опубликовать", callback_data="start_post"),
            types.InlineKeyboardButton(text="Информация", callback_data="start_info"),
        ],
        [types.InlineKeyboardButton(text="Перейти в канал", callback_data="start_info")],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


class Form(StatesGroup):
    start_public = State()
    send_message = State()


router = Router()
dp = Dispatcher()


@router.message(CommandStart())
async def start_handler(
    msg: Message,
):
    await msg.answer(config.HELLO, reply_markup=get_start_keyboard())
    add_new_user(msg.from_user.id)


@router.callback_query(F.data.startswith("start_post"))
async def post_start_handler(msg: Message):
    await msg.answer(f"Время последней публикации: {get_last_time(msg.from_user.id)}")
    await msg.answer(
        (
            "Осталось времени до новой публикации:"
            f" {str(timedelta(seconds=get_timeleft(msg.from_user.id)))}"
        ),
    )
    


@router.message(Command("info"))
async def info_handler(msg: Message):
    await msg.answer(f"Время последней публикации: {get_last_time(msg.from_user.id)}")
    await msg.answer(
        (
            "Осталось времени до новой публикации:"
            f" {str(timedelta(seconds=get_timeleft(msg.from_user.id)))}"
        ),
    )


@router.message()
async def message_handler(msg: Message):
    await msg.answer(f"Публикация. юзер-ID: {msg.from_user.id}")
    add_message_to_queue(msg, publish=True)
