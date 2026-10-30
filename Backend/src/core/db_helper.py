from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from src.core.config import settings


class DatabaseHelper:
    def __init__(self, url: str):
        self.engine = create_async_engine(
            url=url,
            connect_args={
                "prepared_statement_cache_size": 0,
                "statement_cache_size": 0,
            },
        )

        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def session_dependency(self) -> AsyncSession:
        async with self.session_factory() as session:
            yield session


db_helper = DatabaseHelper(settings.db_url)
