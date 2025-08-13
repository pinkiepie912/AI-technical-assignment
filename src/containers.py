from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from db.db import ReadSessionManager, WriteSessionManager, engine_with_pgvector
from enrichment.application.services.company_info_reader import CompanyInfoReader
from enrichment.application.services.company_info_writer import CompanyInfoWriter
from enrichment.application.services.news_reader import NewsReader
from enrichment.infrastructure.embeddings.openai import OpenAIEmbeddingClient
from enrichment.infrastructure.readers.forest_of_hyuksin_reader import (
    ForestOfHyuksinReader,
)
from enrichment.infrastructure.repositories.company_repository import CompanyRepository
from enrichment.infrastructure.repositories.news_repository import NewsRepository
from inference.application.services.talent_infer import TalentInference
from inference.infrastructure.adapters.company_search_adapter import (
    CompanyContextSearchAdapter,
)
from inference.infrastructure.adapters.news_search_adapter import NewsSearchAdapter
from inference.infrastructure.adapters.openai_adapter import OpenAIClient

__all__ = ["Container"]


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    # SqlAlchemy
    _write_db_engine = providers.Resource(
        engine_with_pgvector,
        url=providers.Callable(
            "{engine}://{user}:{password}@{url}:{port}/{name}".format,
            engine=config.DATABASE.WRITE_ENGINE,
            user=config.DATABASE.WRITE_USER,
            password=config.DATABASE.WRITE_PASSWORD,
            url=config.DATABASE.WRITE_URL,
            port=config.DATABASE.WRITE_PORT,
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

    _read_db_engine = providers.Resource(
        engine_with_pgvector,
        url=providers.Callable(
            "{engine}://{user}:{password}@{url}:{port}/{name}".format,
            engine=config.DATABASE.READ_ENGINE,
            user=config.DATABASE.READ_USER,
            password=config.DATABASE.READ_PASSWORD,
            url=config.DATABASE.READ_URL,
            port=config.DATABASE.READ_PORT,
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

    # Enrichment
    # # Repositories
    company_repository = providers.Factory(
        CompanyRepository,
        write_session_manager=write_session_manager,
        read_session_manager=read_session_manager,
    )
    news_respository = providers.Factory(
        NewsRepository,
        session_manager=read_session_manager,
    )

    # # Readers
    forest_hyucksin_reader = providers.Factory(
        ForestOfHyuksinReader,
    )

    # # Dynamic config for runtime values
    reader_source_key = providers.Dependency()

    # # Reader selector using config
    reader_selector = providers.Selector(
        reader_source_key,
        forestofhyucksin=forest_hyucksin_reader,
    )

    # # embedding clients
    openai_embedding_client = providers.Factory(
        OpenAIEmbeddingClient,
        api_key=config.OPENAI.API_KEY,
    )

    # # services
    company_info_writer = providers.Factory(
        CompanyInfoWriter,
        reader=reader_selector,
        repository=company_repository,
    )
    company_info_reader = providers.Factory(
        CompanyInfoReader,
        repository=company_repository,
    )

    news_reader = providers.Factory(
        NewsReader,
        embedding_client=openai_embedding_client,
        news_repository=news_respository,
    )

    # Inference
    # LLM Client
    openai_client = providers.Factory(
        OpenAIClient,
        api_key=config.OPENAI.API_KEY,
    )

    # adapters
    company_search_adapter = providers.Factory(
        CompanyContextSearchAdapter,
        company_search_service=company_info_reader,
    )
    news_search_adapter = providers.Factory(
        NewsSearchAdapter, news_search_service=news_reader
    )

    # services
    talent_inference_service = providers.Factory(
        TalentInference,
        company_search_adapter=company_search_adapter,
        news_search_adapter=news_search_adapter,
        llm_client=openai_client,
    )
