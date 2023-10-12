from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    create_engine,
    Boolean,
)
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
            user = Users(user_id=user_id)
            session.add(user)  # добавляем в бд
            session.commit()  # сохраняем изменения


def add_message_to_queue(msg: Message, publish=False, img=""):
    with Session(autoflush=False, bind=engine) as session:
        message = MessageQueue(
            user_id=msg.from_user.id, text=msg.text, img=img, publish=publish
        )
        session.add(message)  # добавляем в бд
        user = session.query(Users).get(msg.from_user.id)
        user.last_time = func.now()
        session.commit()  # сохраняем изменения


def get_time_last_post(user_id) -> DateTime:
    pass
