from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func
from database import Base

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key = True, index = True)
    title = Column(String(255), nullable = False)
    description = Column(Text, nullable = True)
    completed = Column(Boolean, default = False)
    created_at = Column(DateTime, server_default = func.now())

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, index = True)
    username = Column(String(50), unique=True, nullable = False)
    email = Column(String(100), unique=True, nullable = False)
    hashed_password = Column(String(255), nullable = False)
    created_at = Column(DateTime, server_default = func.now())
