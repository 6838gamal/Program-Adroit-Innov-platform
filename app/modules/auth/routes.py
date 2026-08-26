from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import CurrentUser
from app.core.exceptions import UnauthorizedError
from app.modules.auth.services import AuthService
from app.shared.schemas import MessageResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
async def google_login(request: Request, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    state = AuthService.generate_state()
    request.session["oauth_state"] = state
    auth_url = await service.get_login_redirect(state)
    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def google_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    if error:
        return RedirectResponse(url=f"{settings.APP_URL}/auth/error?error={error}")
    if not code or not state:
        raise UnauthorizedError("Missing code or state in OAuth callback")

    stored_state = request.session.get("oauth_state")
    if not stored_state or stored_state != state:
        raise UnauthorizedError("Invalid OAuth state")

    service = AuthService(db)
    user = await service.handle_callback(code)
    service.create_session(request, user)
    request.session.pop("oauth_state", None)
    return RedirectResponse(url=f"{settings.APP_URL}/dashboard")


@router.post("/logout")
async def logout(request: Request, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    service.destroy_session(request)
    return MessageResponse(message="Logged out successfully")


@router.get("/status")
async def auth_status(request: Request, user: CurrentUser):
    return {
        "authenticated": True,
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role.value,
        },
    }
