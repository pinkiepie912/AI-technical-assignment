from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Session, sessionmaker

__all__ = [
    "ReadSessionManager",
    "WriteSessionManager",
    "WriteSessionSyncManager",
]


class ReadSessionManager:
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]):
        self._session_maker = session_maker
        self._session: Optional[AsyncSession] = None

    async def __aenter__(self) -> AsyncSession:
        if self._session is None:
            self._session = self._session_maker()
        return self._session

    async def __aexit__(self, exc_type, exc_value, traceback):
        if not self._session:
            return

        try:
            if exc_type:
                return False
        finally:
            await self._session.close()
            self._session = None


class WriteSessionManager:
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]):
        self._session_maker = session_maker
        self._session: Optional[AsyncSession] = None

    async def __aenter__(self) -> AsyncSession:
        if self._session is None:
            self._session = self._session_maker()
        return self._session

    async def __aexit__(self, exc_type, exc_value, traceback):
        if not self._session:
            return

        try:
            if exc_type:
                await self._session.rollback()
                return False
            else:
                await self._session.commit()
        finally:
            await self._session.close()
            self._session = None


class WriteSessionSyncManager:
    def __init__(self, session_maker: sessionmaker[Session]):
        self._session_maker = session_maker
        self._session: Optional[Session] = None

    def __enter__(self) -> Session:
        if self._session is None:
            self._session = self._session_maker()
        return self._session

    def __exit__(self, exc_type, exc_value, traceback):
        if not self._session:
            return

        try:
            if exc_type:
                self._session.rollback()
                return False
            else:
                self._session.commit()
        finally:
            self._session.close()
            self._session = None
