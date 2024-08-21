import contextlib

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from src.conf.config import config


class DatabaseSessionManager:
    def __init__(self, url: str):
        if not url:
            raise ValueError("Database URL cannot be empty")
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(autoflush=False, autocommit=False,
                                                                     bind=self._engine)

    @contextlib.asynccontextmanager
    async def session(self):
        if self._session_maker is None:
            raise Exception("Session is not initialized!")
        session = self._session_maker()
        try:
            yield session
        except Exception as error:
            print(error)
            await session.rollback()
        finally:
            await session.close()


# test_url = "postgresql+asyncpg://postgres:48368463@localhost:5432/hw_13"
# sessionmanager = DatabaseSessionManager(test_url)
sessionmanager = DatabaseSessionManager(config.DB_URL)


async def get_db():
    async with sessionmanager.session() as session:
        yield session


