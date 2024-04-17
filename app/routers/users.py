from fastapi import APIRouter

router = APIRouter(tags=["Users"])


@router.get("/")
def read_users() -> dict[str, str]:
    """Get a user message."""
    return {"message": "Hello users"}
