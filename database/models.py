from sqlalchemy import Column, Integer, String
from db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    care_name = Column(String)
    phone = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # хешированный пароль
