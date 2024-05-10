"""Create and configure the FastAPI app."""

import pathlib

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from .routers import message

MESSAGE_URL_PREFIX = "message"


class APIVersion(BaseModel):
    api_version: str = "0.1.0"


app = FastAPI(
    title="FastAPI demo",
    description="A simple API for message CRUD with a DynamoDB back end.",
    version=f"v{APIVersion().api_version}",
    contact={
        "name": "e-mit.github.io",
        "url": "https://e-mit.github.io/"
    },
    license_info={
        "name": "AGPL-3.0 license",
        "url": "https://www.gnu.org/licenses/agpl-3.0.html#license-text",
    },
    redoc_url=None
)

app.mount("/static", StaticFiles(
    directory=pathlib.Path(__file__).parent / "static_files"))


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@app.get("/version", tags=["Version"])
async def version() -> APIVersion:
    """The API version."""
    return APIVersion()


@app.get("/favicon.ico", include_in_schema=False)
async def get_favicon() -> RedirectResponse:
    return RedirectResponse(url="/static/favicon.ico")


app.include_router(
    message.router,
    prefix=f"/{MESSAGE_URL_PREFIX}"
)
