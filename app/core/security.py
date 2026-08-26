import secrets
from datetime import datetime, timedelta, timezone

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

serializer = URLSafeTimedSerializer(settings.SECRET_KEY, salt="session")

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def generate_token() -> str:
    return secrets.token_urlsafe(32)


def create_session_token(data: dict, expires: int | None = None) -> str:
    return serializer.dumps(data)


def decode_session_token(token: str, max_age: int | None = None) -> dict | None:
    try:
        return serializer.loads(token, max_age=max_age or settings.SESSION_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None


def create_jwt(subject: str, extra: dict | None = None, expires_minutes: int = 60) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_jwt(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
