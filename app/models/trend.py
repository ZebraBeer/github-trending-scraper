from sqlalchemy import Column, Integer, String, ForeignKey, Date
from app.database import Base

class Trend(Base):
    __tablename__ = 'trends'

    id = Column(Integer, primary_key=True, autoincrement=True)
    repository_id = Column(Integer, ForeignKey('repositories.id'), nullable=False)
    rank = Column(Integer, nullable=True)  # Rank can be NULL if not available
    date = Column(Date, nullable=False)

    def __repr__(self):
        return f"<Trend(repository_id={self.repository_id}, rank={self.rank}, date={self.date})>"