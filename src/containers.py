from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from db.db import ReadSessionManager, WriteSessionManager

__all__ = ["Container"]


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    # SqlAlchemy
    _write_db_engine = providers.Singleton(
        create_async_engine,
        url=providers.Callable(
            "{engine}://{user}:{password}@{url}:{port}/{name}".format,
            engine=config.DATABASE.WRITE_ENGINE,
            user=config.DATABASE.WRITE_USER,
            password=config.DATABASE.WRITE_PASSWORD,
            url=config.DATABASE.WRITE_URL,
            name=config.DATABASE.WRITE_NAME,
        ),
        pool_size=config.DATABASE.POOL_SIZE,
        max_overflow=config.DATABASE.MAX_OVERFLOW,
        pool_timeout=config.DATABASE.POOL_TIMEOUT,
        pool_recycle=config.DATABASE.POOL_RECYCLE,
    )
    _write_db_session_maker = providers.Singleton(
        async_sessionmaker, bind=_write_db_engine, class_=AsyncSession
    )

    _read_db_engine = providers.Singleton(
        create_async_engine,
        url=providers.Callable(
            "{engine}://{user}:{password}@{url}:{port}/{name}".format,
            engine=config.DATABASE.READ_ENGINE,
            user=config.DATABASE.READ_USER,
            password=config.DATABASE.READ_PASSWORD,
            url=config.DATABASE.READ_URL,
            name=config.DATABASE.READ_NAME,
        ),
        pool_size=config.DATABASE.POOL_SIZE,
        max_overflow=config.DATABASE.MAX_OVERFLOW,
        pool_timeout=config.DATABASE.POOL_TIMEOUT,
        pool_recycle=config.DATABASE.POOL_RECYCLE,
    )
    _read_db_session_maker = providers.Singleton(
        async_sessionmaker, bind=_read_db_engine, class_=AsyncSession
    )

    read_session_manager = providers.Factory(
        ReadSessionManager,
        session_maker=_read_db_session_maker,
    )

    write_session_manager = providers.Factory(
        WriteSessionManager,
        session_maker=_write_db_session_maker,
    )
