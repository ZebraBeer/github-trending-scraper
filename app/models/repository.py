from sqlalchemy import Column, Integer, String, Text
from app.database import Base

class Repository(Base):
    __tablename__ = 'repositories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    language = Column(String, nullable=True)
    stars = Column(Integer, nullable=False)
    forks = Column(Integer, nullable=False)
    url = Column(String, unique=True, nullable=False)

    def __repr__(self):
        return f"<Repository(name={self.name}, stars={self.stars})>"