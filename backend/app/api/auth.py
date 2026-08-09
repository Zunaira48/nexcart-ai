from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.core.security import hash_password, verify_password, create_access_token
from datetime import datetime, timedelta, timezone

from app.models.token import EmailToken
from app.schemas.user import ForgotPasswordRequest, ResetPasswordRequest, ResendVerificationRequest
from app.core.security import generate_token
from app.core.email import send_email
from app.core.config import settings

def _create_and_send_verification_email(user: User, db: Session):
    token = generate_token()
    expires = datetime.now(timezone.utc) + timedelta(hours=24)
    db.add(EmailToken(user_id=user.id, token=token, token_type="email_verification", expires_at=expires))
    db.commit()

    verify_link = f"{settings.frontend_url}/verify-email?token={token}"
    send_email(
        to_email=user.email,
        subject="Verify your NexCart AI account",
        html_body=f"""
            <h2>Welcome to NexCart AI, {user.full_name}!</h2>
            <p>Please verify your email address to activate your account.</p>
            <p><a href="{verify_link}">Click here to verify your email</a></p>
            <p>This link expires in 24 hours.</p>
        """,
    )

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists",
        )

    new_user = User(
        full_name=user_in.full_name,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    _create_and_send_verification_email(new_user, db)
    return new_user


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

from app.core.security import get_current_user

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    # Security: hamesha same message dete hain, chahe email exist kare ya nahi —
    # taake attacker ye pata na laga sake konsi emails registered hain
    if user:
        token = generate_token()
        expires = datetime.now(timezone.utc) + timedelta(hours=1)
        db.add(EmailToken(user_id=user.id, token=token, token_type="password_reset", expires_at=expires))
        db.commit()

        reset_link = f"{settings.frontend_url}/reset-password?token={token}"
        send_email(
            to_email=user.email,
            subject="Reset your NexCart AI password",
            html_body=f"""
                <h2>Password Reset Request</h2>
                <p>Click the link below to reset your password. This link expires in 1 hour.</p>
                <p><a href="{reset_link}">Reset my password</a></p>
                <p>If you didn't request this, you can safely ignore this email.</p>
            """,
        )

    return {"message": "If an account with that email exists, a reset link has been sent."}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    email_token = (
        db.query(EmailToken)
        .filter(EmailToken.token == payload.token, EmailToken.token_type == "password_reset")
        .first()
    )

    if not email_token or email_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset link")

    user = db.query(User).filter(User.id == email_token.user_id).first()
    user.hashed_password = hash_password(payload.new_password)
    db.delete(email_token)
    db.commit()

    return {"message": "Password reset successfully"}


@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    email_token = (
        db.query(EmailToken)
        .filter(EmailToken.token == token, EmailToken.token_type == "email_verification")
        .first()
    )

    if not email_token or email_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification link")

    user = db.query(User).filter(User.id == email_token.user_id).first()
    user.is_verified = True
    db.delete(email_token)
    db.commit()

    return {"message": "Email verified successfully"}


@router.post("/resend-verification")
def resend_verification(payload: ResendVerificationRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if user and not user.is_verified:
        _create_and_send_verification_email(user, db)

    return {"message": "If an unverified account with that email exists, a new link has been sent."}

