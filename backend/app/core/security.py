import uuid
import pyotp
import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from app.config import settings


# ---------- Password ----------

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


# ---------- JWT ----------

def create_access_token(user_id: str, email: str, plan: str = "free") -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "user_id": user_id,
        "email": email,
        "plan": plan,
        "exp": expire,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token() -> str:
    return str(uuid.uuid4())


def create_temp_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=10)
    payload = {
        "user_id": user_id,
        "type": "2fa_temp",
        "exp": expire,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])


def decode_token_safe(token: str) -> dict | None:
    try:
        return decode_token(token)
    except JWTError:
        return None


# ---------- TOTP 2FA ----------

def generate_totp_secret() -> str:
    return pyotp.random_base32()


def get_totp_uri(secret: str, email: str) -> str:
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name="AIveilix")


def verify_totp(secret: str, code: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(code)


# ---------- Backup Codes ----------

def generate_backup_codes(count: int = 8) -> list[str]:
    return [str(uuid.uuid4()).replace("-", "")[:10].upper() for _ in range(count)]
