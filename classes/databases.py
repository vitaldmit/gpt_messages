"""
В этом файле хранятся классы для работы с базами данных.
Пока только SQLite.
"""

import configparser
from abc import ABC, abstractmethod

from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")

database_name = config["DATABASE"]["DB_NAME"]


class Database(ABC):
    """
    Абстрактный класс для работы с базами данных.
    """

    @abstractmethod
    def get_from_db(self):
        """
        Получение из базы данных.
        """

    @abstractmethod
    def add_to_db(self):
        """
        Добавление в базу данных.
        """


class Base(DeclarativeBase):
    """
    Базовый класс для работы SQLAlchemy.
    """


class SqLite(Base):
    """
    Класс для работы с SQLite с помощью SQLAlchemy ORM.
    """

    __tablename__ = database_name
    id = Column(String, primary_key=True)
    text = Column(String)

    def __init__(self, text=None, _id=None):
        self.id = _id
        self.text = text
        self.engine = create_engine(f"sqlite:///{database_name}")
        self.session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def get_from_db(self):
        """
        Получение из базы данных.
        """
        session = self.session()
        try:
            db_entries_list = session.query(SqLite.text).all()
            return db_entries_list
        finally:
            session.close()

    def write_to_db(self, db_entry):
        """
        Запись в базу данных.
        """
        session = self.session()
        try:
            current_count = session.query(SqLite).count()
            new_db_entry = SqLite(_id=str(current_count + 1), text=db_entry)
            session.add(new_db_entry)
            session.commit()
        finally:
            session.close()
