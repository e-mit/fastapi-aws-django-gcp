from fastapi import APIRouter

router = APIRouter(tags=["Users"])


@router.get("/")
def read_users() -> dict[str, str]:
    """Get a user message."""
    return {"message": "Hello users"}


@router.get("/{user_id}")
def read_user_id(user_id: int) -> dict[str, str]:
    """Get a user ID."""
    return {"message": f"It is user {user_id}"}
