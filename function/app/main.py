import pathlib

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from .routers import message

VERSION = "0.1.0"
MESSAGE_PREFIX = "message"

app = FastAPI(
    title="FastAPI demo",
    description="A simple API for message CRUD with a dynamoDB back end.",
    version=f"v{VERSION}",
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
    return RedirectResponse(url="/version")


@app.get("/version", tags=["Version"])
async def version() -> dict[str, str]:
    """The API version."""
    return {"api_version": VERSION}


@app.get("/favicon.ico", include_in_schema=False)
async def get_favicon() -> RedirectResponse:
    return RedirectResponse(url="/static/favicon.ico")


app.include_router(
    message.router,
    prefix=f"/{MESSAGE_PREFIX}"
)
