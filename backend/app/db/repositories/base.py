"""Base repository class."""
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    """Base repository with common functionality."""
    
    def __init__(self, db: AsyncSession):
        """Initialize repository with database session."""
        self.db = db
