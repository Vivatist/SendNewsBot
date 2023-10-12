from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command
from db import add_user


router = Router()


@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer(
        "Привет! Я помогу тебе узнать твой ID, просто отправь мне любое сообщение"
    )
    await add_user(msg.from_user.id)


@router.message()
async def message_handler(msg: Message):
    await msg.answer(f"Твой ID: {msg.from_user.id}")
