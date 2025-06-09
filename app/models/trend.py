from sqlalchemy import Column, Integer, String, ForeignKey, Date
from app.database import Base

class Trend(Base):
    __tablename__ = 'trends'

    id = Column(Integer, primary_key=True, autoincrement=True)
    repository_id = Column(Integer, ForeignKey('repositories.id'), nullable=False)
    stars = Column(Integer, nullable=False)  # Number of stars at the time of recording
    date = Column(Date, nullable=False)

    def __repr__(self):
        return f"<Trend(repository_id={self.repository_id}, stars={self.stars}, date={self.date})>"