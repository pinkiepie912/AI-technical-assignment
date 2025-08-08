import os
import glob
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from config.config import Config
from containers import Container


def load_controllers(base_path="src"):
    controllers = []
    pattern = os.path.join(base_path, "*", "controllers", "*.py")
    for controller_file in glob.glob(pattern):
        if os.path.basename(controller_file) == "__init__.py":
            continue
        module_path = (
            controller_file.replace(base_path + os.path.sep, "")
            .replace(".py", "")
            .replace(os.path.sep, ".")
        )
        controllers.append(module_path)
    return controllers


def create_app() -> FastAPI:
    config = Config()
    container = Container()

    container.config.from_pydantic(config)
    container.wire(modules=load_controllers())

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        print("FastAPI app Initialized")
        yield
        
        container.dispose()

    app = FastAPI(lifespan=lifespan)
    app.state.container = container

    print("FastAPI app started")
    return app


app = create_app()


class PingResponse(BaseModel):
    status: str


@app.get("/health", response_model=PingResponse)
async def ping() -> dict:
    return {"status": "success"}
