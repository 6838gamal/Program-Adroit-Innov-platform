from sqlalchemy.ext.asyncio import AsyncSession


class BaseAgent:
    def __init__(self, db: AsyncSession):
        self.db = db
