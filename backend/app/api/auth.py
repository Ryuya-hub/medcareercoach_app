from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models.user import UserAuth, Coach, Client
from app.schemas.auth import LoginRequest, RegisterRequest, Token, ClientRegisterRequest, CoachRegisterRequest
from app.utils.auth import verify_password, get_password_hash, create_access_token, get_current_user
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """ログイン"""
    # ユーザーの検索
    user = db.query(UserAuth).filter(UserAuth.email == request.email).first()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # アカウントステータスチェック
    if user.status != 'active':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is {user.status}",
        )

    # JWTトークンの生成
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.user_id), "user_type": user.user_type, "role": user.role},
        expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user_type=user.user_type,
        user_id=str(user.user_id),
        role=user.role
    )


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """ユーザー登録（旧エンドポイント - 互換性のため残す）"""
    # メールアドレスの重複チェック
    existing_user = db.query(UserAuth).filter(UserAuth.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # ユーザータイプの検証
    if request.user_type not in ['coach', 'client']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user type"
        )

    # ユーザー認証情報の作成
    user_auth = UserAuth(
        email=request.email,
        password_hash=get_password_hash(request.password),
        user_type=request.user_type,
        role=request.user_type,  # デフォルトはuser_typeと同じ
        status='active'
    )
    db.add(user_auth)
    db.flush()

    # コーチまたは利用者情報の作成
    if request.user_type == 'coach':
        coach = Coach(
            user_id=user_auth.user_id,
            name=request.name,
            furigana=request.furigana,
            email=request.email,
            phone=request.phone
        )
        db.add(coach)
    else:  # client
        client = Client(
            user_id=user_auth.user_id,
            name=request.name,
            furigana=request.furigana,
            email=request.email,
            phone=request.phone
        )
        db.add(client)

    db.commit()
    db.refresh(user_auth)

    # JWTトークンの生成
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user_auth.user_id), "user_type": user_auth.user_type, "role": user_auth.role},
        expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user_type=user_auth.user_type,
        user_id=str(user_auth.user_id),
        role=user_auth.role
    )


@router.post("/register/client", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_client(request: ClientRegisterRequest, db: Session = Depends(get_db)):
    """利用者登録"""
    # メールアドレスの重複チェック
    existing_user = db.query(UserAuth).filter(UserAuth.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # ユーザー認証情報の作成
    user_auth = UserAuth(
        email=request.email,
        password_hash=get_password_hash(request.password),
        user_type='client',
        role='client',
        status='active'
    )
    db.add(user_auth)
    db.flush()

    # 利用者情報の作成
    client = Client(
        user_id=user_auth.user_id,
        name=request.name,
        furigana=request.furigana,
        email=request.email,
        phone=request.phone,
        status='active'
    )
    db.add(client)
    db.commit()
    db.refresh(user_auth)

    # JWTトークンの生成
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user_auth.user_id), "user_type": user_auth.user_type, "role": user_auth.role},
        expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user_type=user_auth.user_type,
        user_id=str(user_auth.user_id),
        role=user_auth.role
    )


@router.post("/register/coach", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_coach(request: CoachRegisterRequest, db: Session = Depends(get_db)):
    """コーチ（管理者）登録"""
    # 招待コードの検証
    if request.invitation_code != settings.COACH_INVITATION_CODE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid invitation code"
        )

    # メールアドレスの重複チェック
    existing_user = db.query(UserAuth).filter(UserAuth.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # ユーザー認証情報の作成
    user_auth = UserAuth(
        email=request.email,
        password_hash=get_password_hash(request.password),
        user_type='coach',
        role='coach',
        status='active'
    )
    db.add(user_auth)
    db.flush()

    # コーチ情報の作成
    coach = Coach(
        user_id=user_auth.user_id,
        name=request.name,
        furigana=request.furigana,
        email=request.email,
        phone=request.phone
    )
    db.add(coach)
    db.commit()
    db.refresh(user_auth)

    # JWTトークンの生成
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user_auth.user_id), "user_type": user_auth.user_type, "role": user_auth.role},
        expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user_type=user_auth.user_type,
        user_id=str(user_auth.user_id),
        role=user_auth.role
    )


@router.get("/verify")
async def verify_token(current_user: UserAuth = Depends(get_current_user)):
    """トークンの検証"""
    return {
        "user_id": str(current_user.user_id),
        "email": current_user.email,
        "user_type": current_user.user_type
    }


@router.post("/logout")
async def logout(current_user: UserAuth = Depends(get_current_user)):
    """ログアウト（クライアント側でトークンを削除）"""
    return {"message": "Successfully logged out"}
