from pydantic import BaseModel, EmailStr


# ---------- Register ----------

class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class RegisterResponse(BaseModel):
    message: str


# ---------- Email Verification ----------

class VerifyEmailRequest(BaseModel):
    token: str


class VerifyEmailResponse(BaseModel):
    message: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ---------- Login ----------

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequires2FAResponse(BaseModel):
    requires_2fa: bool = True
    temp_token: str


# ---------- 2FA ----------

class Verify2FARequest(BaseModel):
    temp_token: str
    code: str


class Enable2FAResponse(BaseModel):
    secret: str
    qr_uri: str


class Confirm2FARequest(BaseModel):
    code: str


class Confirm2FAResponse(BaseModel):
    message: str
    backup_codes: list[str]


class Disable2FARequest(BaseModel):
    code: str


class Disable2FAResponse(BaseModel):
    message: str


# ---------- Token ----------

class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LogoutResponse(BaseModel):
    message: str


# ---------- Resend Verification ----------

class ResendVerificationRequest(BaseModel):
    email: EmailStr

class ResendVerificationResponse(BaseModel):
    message: str


# ---------- Password Reset ----------

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    message: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class ResetPasswordResponse(BaseModel):
    message: str


# ---------- OAuth ----------

class OAuthRequest(BaseModel):
    code: str
    redirect_uri: str


class OAuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    is_new_user: bool
