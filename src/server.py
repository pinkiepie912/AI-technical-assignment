import glob
import importlib
import logging
import os
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

from config.config import Config
from containers import Container

logger = logging.getLogger(__name__)


def load_controllers(base_path="src"):
    controllers = []
    pattern = os.path.join(base_path, "**", "controllers", "*.py")
    for controller_file in glob.glob(pattern, recursive=True):
        if os.path.basename(controller_file) == "__init__.py":
            continue
        module_path = (
            controller_file.replace(base_path + os.path.sep, "")
            .replace(".py", "")
            .replace(os.path.sep, ".")
        )
        controllers.append(module_path)
        logger.info(f"Found controller: {controller_file} -> {module_path}")
    return controllers


def register_routers(app: FastAPI, controller_modules: List[str]):
    registered_routers = []

    for module_path in controller_modules:
        try:
            module = importlib.import_module(module_path)

            if hasattr(module, "router"):
                router = getattr(module, "router")
                app.include_router(router)
                registered_routers.append(module_path)
                logger.info(f"Router registered: {module_path}")
            else:
                logger.warning(f"No router found in: {module_path}")

        except ImportError as e:
            logger.error(f"Failed to import controller: {module_path} - {e}")
        except Exception as e:
            logger.error(f"Error registering router from {module_path}: {e}")

    logger.info(f"Total routers registered: {len(registered_routers)}")
    return registered_routers


def create_app() -> FastAPI:
    config = Config()
    container = Container()

    controller_modules = load_controllers()

    container.config.from_pydantic(config)

    container.wire(modules=controller_modules)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("FastAPI app initialized")
        yield
        container.shutdown_resources()
        container.unwire()

        logger.info("FastAPI app shutdown complete")

    app = FastAPI(
        lifespan=lifespan,
        title="SearcHRight API",
        description="RAG-based talent enrichment system",
        version="1.0.0",
    )
    app.state.container = container

    register_routers(app, controller_modules)

    logger.info("FastAPI app startup complete")
    return app


app = create_app()


class PingResponse(BaseModel):
    status: str


@app.get("/health", response_model=PingResponse)
async def ping() -> dict:
    return {"status": "success"}
