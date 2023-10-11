import logging

import constats

from telegram import ForceReply, Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from declarate_db import Users, MessageQueue, engine


async def add_user(user_id):
    with Session(autoflush=False, bind=engine) as db:
        # проверяем наличие юзера в базе, если нет - добавляем
        row = db.query(Users).filter(Users.user_id == user_id).all()
        if len(row) == 0:
            user = Users(user_id=user_id)
            db.add(user)  # добавляем в бд
            db.commit()  # сохраняем изменения


TOKEN = constats.TOKEN_BOT
CHAT_ID = constats.CHANNEL

bot = Bot(token=TOKEN)

# Старт логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.INFO)

logger = logging.getLogger(__name__)


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )
    await add_user(user.id)


# OTHER
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)
    await post_to_channel(CHAT_ID, update.message.text)


# Отправка текста  в канал от имени бота
async def post_to_channel(chat_id, text):
    print("Публикуем пост: ", text)
    await bot.send_message(chat_id=chat_id, text="_" + text + "_", parse_mode="Markdown")


def main() -> None:
    """Стартуем бота"""
    application = Application.builder().token(TOKEN).build()

    # Команды
    application.add_handler(CommandHandler("start", start))

    # Если не команда - значит сообщение
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Запускаем бота пока не Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
