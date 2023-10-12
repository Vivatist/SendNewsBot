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
    last_time = Column(DateTime, comment="Дата и время последнего сообщения")
    moderator = Column(Boolean, default=False, comment="Является ли юзер модератором")
    active = Column(Boolean, default=True, comment="Активный ли юзер")


class MessageQueue(Base):
    __tablename__ = "message_queue"
    __tableargs__ = {"comment": "Очередь сообщений для публикации"}

    message_id = Column(
        Integer, nullable=False, unique=True, primary_key=True, autoincrement=True
    )
    text = Column(Text, comment="Текст сообщения")
    img = Column(String(256), comment="Путь к изображению")
    permission = Column(Boolean, comment="Допуск к публикации")


engine = create_engine("sqlite:///bot.db", echo=True)
Base.metadata.create_all(engine)


async def add_user(user_id):
    with Session(autoflush=False, bind=engine) as db:
        # проверяем наличие юзера в базе, если нет - добавляем
        row = db.query(Users).filter(Users.user_id == user_id).all()
        if len(row) == 0:
            user = Users(user_id=user_id)
            db.add(user)  # добавляем в бд
            db.commit()  # сохраняем изменения
