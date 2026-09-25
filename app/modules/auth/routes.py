# app/modules/auth/routes.py
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


# ------------------------------------------------------------------
# 0) صفحة تسجيل الدخول (HTML)
# ------------------------------------------------------------------
@router.get("/login")
async def login_page(
    request: Request,
    next: str | None = None,
    error: str | None = None,
):
    """
    صفحة تسجيل الدخول.
    - لا تبدأ OAuth تلقائياً (حتى لا يعود المستخدم مسجّلاً بعد logout)
    - تعرض زر "الدخول بحساب Google"
    - تحفظ `next` لإعادة المستخدم للمسار المطلوب بعد الدخول
    """
    # امسح أي state قديم لتجنب تسريب الجلسة السابقة
    request.session.pop("oauth_state", None)

    # احفظ المسار المطلوب للعودة إليه لاحقاً
    if next:
        request.session["next_url"] = next

    # إذا كان المستخدم مسجّلاً بالفعل، وجّهه مباشرة
    if request.session.get("user_id"):
        target = request.session.pop("next_url", None) or "/dashboard"
        return RedirectResponse(url=target, status_code=303)

    # إذا كنت تستخدم Jinja2، أرجِع صفحة HTML حقيقية.
    # إن لم يكن القالب موجوداً بعد، يمكنك استخدام JSON مؤقتاً.
    try:
        from app.templates import templates

        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "error": error,
            },
        )
    except Exception:
        # fallback مؤقت إذا لم يوجد القالب
        return {
            "authenticated": False,
            "message": "الرجاء تسجيل الدخول",
            "login_url": "/auth/google",
        }


# ------------------------------------------------------------------
# 1) بدء تسجيل الدخول — توجيه إلى Google
# ------------------------------------------------------------------
@router.get("/google")
async def google_login(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    يبدأ عملية OAuth:
    - يولّد state عشوائي
    - يخزّنه في الجلسة
    - يعيد التوجيه إلى Google
    """
    service = AuthService(db)
    state = AuthService.generate_state()
    request.session["oauth_state"] = state

    auth_url = await service.get_login_redirect(state)
    return RedirectResponse(url=auth_url, status_code=302)


# ------------------------------------------------------------------
# 2) معالجة رد Google (callback)
# ------------------------------------------------------------------
@router.get("/google/callback")
async def google_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """
    - يستقبل code و state من Google
    - يتحقق من state (حماية CSRF)
    - يتبادل code بـ tokens
    - ينشئ جلسة للمستخدم
    - يعيد التوجيه إلى /dashboard أو next_url
    """
    # خطأ من Google مباشرة
    if error:
        return RedirectResponse(
            url=f"{settings.APP_URL}/auth/login?error={error}",
            status_code=302,
        )

    if not code or not state:
        raise UnauthorizedError("Missing code or state in OAuth callback")

    # التحقق من state (يُحذف فوراً لمنع إعادة الاستخدام)
    stored_state = request.session.pop("oauth_state", None)
    if not stored_state or stored_state != state:
        raise UnauthorizedError("Invalid OAuth state")

    try:
        service = AuthService(db)
        user = await service.handle_callback(code)
        service.create_session(request, user)
    except UnauthorizedError:
        raise
    except Exception:
        # تسجيل الخطأ وإعادة التوجيه لصفحة خطأ
        import logging

        logging.getLogger(__name__).exception("oauth_callback_failed")
        return RedirectResponse(
            url=f"{settings.APP_URL}/auth/login?error=oauth_failed",
            status_code=302,
        )

    # وجّه المستخدم للمسار الذي كان يقصده، أو /dashboard
    target = request.session.pop("next_url", None) or "/dashboard"
    return RedirectResponse(url=target, status_code=302)


# ------------------------------------------------------------------
# 3) صفحة الخطأ (لعرض رسالة عند فشل OAuth)
# ------------------------------------------------------------------
@router.get("/error")
async def auth_error(
    request: Request,
    error: str | None = None,
):
    """
    يعيد رسالة خطأ بسيطة كـ JSON.
    إن كنت تستخدم Jinja2، استبدله بـ TemplateResponse.
    """
    return {
        "authenticated": False,
        "error": error or "auth_error",
        "message": "فشل تسجيل الدخول. الرجاء المحاولة مرة أخرى.",
    }


# ------------------------------------------------------------------
# 4) تسجيل الخروج — يدمّر الجلسة ويوجّه لصفحة تسجيل الدخول
# ------------------------------------------------------------------
@router.post("/logout")
async def logout(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    - يدمّر جلسة المستخدم
    - يحذف كوكي الجلسة من المتصفح
    - يوجّه إلى /auth/login بحالة 303
    لا نطلب CurrentUser هنا حتى ينجح الخروج
    حتى لو كانت الجلسة منتهية أصلاً.
    """
    service = AuthService(db)
    service.destroy_session(request)

    response = RedirectResponse(
        url="/auth/login",
        status_code=303,  # 303 = POST → GET redirect
    )

    # احذف كوكي الجلسة من المتصفح أيضاً (احتياط مزدوج)
    response.delete_cookie(
        key=settings.SESSION_COOKIE_NAME if hasattr(settings, "SESSION_COOKIE_NAME") else "session",
        path="/",
        httponly=True,
        secure=True,
        samesite="lax",
    )
    return response


# ------------------------------------------------------------------
# 5) حالة المصادقة
# ------------------------------------------------------------------
@router.get("/status")
async def auth_status(request: Request, user: CurrentUser):
    """يعيد معلومات المستخدم الحالي."""
    return {
        "authenticated": True,
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role.value,
        },
    }
