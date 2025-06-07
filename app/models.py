from sqlalchemy import Column, Integer, String

from .database import Base


class Test(Base):
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
