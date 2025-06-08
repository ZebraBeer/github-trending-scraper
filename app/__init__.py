# Import models to register them with SQLAlchemy
from .models.repository import Repository
from .models.trend import Trend

__all__ = ['Repository', 'Trend']