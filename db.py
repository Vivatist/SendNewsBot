import logging
import config
import datetime
from sqlalchemy import Column, ForeignKey, create_engine
from sqlalchemy import Integer, String, Text, Date, DateTime, Boolean  # Типы данных
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from aiogram.types import Message
from sqlalchemy.sql import func


Base = declarative_base()


class Users(Base):
    __tablename__ = "users"
    __tableargs__ = {"comment": "Подписчики"}

    user_id = Column(
        String(32),
        primary_key=True,
        nullable=False,
        unique=True,
        comment="ID пользователя в Телеграме",
    )
    last_time = Column(
        DateTime(timezone=True), comment="Дата и время последнего сообщения"
    )
    moderator = Column(Boolean, default=False, comment="Является ли юзер модератором")
    active = Column(Boolean, default=True, comment="Активный ли юзер")


class MessageQueue(Base):
    __tablename__ = "message_queue"
    __tableargs__ = {"comment": "Очередь сообщений для публикации"}

    message_id = Column(
        Integer, nullable=False, unique=True, primary_key=True, autoincrement=True
    )
    user_id = Column(
        String(32),
        nullable=False,
        comment="ID автора сообщения",
    )
    text = Column(Text, comment="Текст сообщения")
    img = Column(String(256), comment="Путь к изображению")
    publish = Column(Boolean, comment="Допуск к публикации")


engine = create_engine("sqlite:///bot.sqlite", echo=True)
Base.metadata.create_all(engine)


def add_new_user(user_id):
    with Session(autoflush=False, bind=engine) as session:
        # проверяем наличие юзера в базе, если нет - добавляем
        row = session.query(Users).filter(Users.user_id == user_id).all()
        if len(row) == 0:
            user = Users(
                user_id=user_id,
                last_time=datetime.datetime.now()
                - datetime.timedelta(seconds=config.TIMEOUT),
            )
            session.add(user)  # добавляем в бд
            session.commit()  # сохраняем изменения
            logging.info("Новый пользователь добавлен: %s", user_id)


def add_message_to_queue(msg: Message, publish=False, img=""):
    with Session(autoflush=False, bind=engine) as session:
        message = MessageQueue(
            user_id=msg.from_user.id, text=msg.text, img=img, publish=publish
        )
        session.add(message)  # добавляем в бд
        user = session.query(Users).get(msg.from_user.id)
        user.last_time = datetime.datetime.now()
        session.commit()  # сохраняем изменения
        logging.info("Новое сообщение добавлено: %s", msg.text)


def get_last_time(user_id) -> DateTime:
    with Session(autoflush=False, bind=engine) as db:
        user = db.query(Users).filter(Users.user_id == user_id).first()
        logging.info(
            "У пользователя %s время последней публикации =  %s", user_id, user.last_time
        )
        return user.last_time


def get_timeleft(user_id):
    last_time: datetime = get_last_time(user_id)
    now = datetime.datetime.now()
    passed_time: datetime.timedelta = (
        now - last_time
    )  # прошло времени с прошлой публикации
    time_left_sec = int(config.TIMEOUT - passed_time.total_seconds())
    if time_left_sec < 0:
        time_left_sec = 0
    logging.info("Осталось времени: %s", int(time_left_sec))
    return time_left_sec
