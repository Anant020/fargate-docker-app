from sqlalchemy import Column, Integer, String
from database import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    role = Column(String)
    hashed_password = Column(String)
    is_active = Column(Integer, default=1)


class Books(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    author = Column(String)
    description = Column(String)
    year_published = Column(Integer)
    language = Column(String)