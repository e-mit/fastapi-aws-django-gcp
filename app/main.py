import pathlib

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from app.routers import users

VERSION = "0.1.0"

app = FastAPI(
    title="FastAPI demo",
    description="Description goes here (use *Markdown*).",
    summary="A simple FastAPI app.",
    version=VERSION,
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

app.include_router(
    users.router,
    prefix="/users"
)

app.mount("/static", StaticFiles(
    directory=pathlib.Path(__file__).parent / "static_files"))


@app.get("/", tags=["/"])
async def hello() -> dict[str, str]:
    """Get a simple message response."""
    return {"message": "Hello"}


@app.get("/favicon.ico", include_in_schema=False)
async def get_favicon() -> RedirectResponse:
    return RedirectResponse(url="/static/favicon.ico")
