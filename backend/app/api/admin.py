"""
統括管理者専用APIエンドポイント
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.database import get_db
from app.models.user import UserAuth, Coach, Client
from app.utils.auth import get_current_user, get_password_hash
from pydantic import BaseModel, EmailStr


router = APIRouter(prefix="/api/admin", tags=["admin"])


# スキーマ定義
class UserListResponse(BaseModel):
    user_id: str
    email: str
    user_type: str
    role: str
    status: str
    name: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class UserStatusUpdate(BaseModel):
    status: str  # 'active', 'inactive', 'suspended'


class AdminCreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    user_type: str  # 'coach' or 'client'
    last_name: str
    first_name: str
    last_name_kana: Optional[str] = None
    first_name_kana: Optional[str] = None
    phone: Optional[str] = None


# 統括管理者チェック用デコレーター
def require_super_admin(current_user: UserAuth = Depends(get_current_user)):
    """統括管理者権限が必要"""
    if current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return current_user


@router.get("/users", response_model=List[UserListResponse])
async def get_all_users(
    user_type: Optional[str] = None,
    role: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: UserAuth = Depends(require_super_admin)
):
    """全ユーザーリストを取得（統括管理者のみ）"""
    query = db.query(UserAuth)

    # フィルター適用
    if user_type:
        query = query.filter(UserAuth.user_type == user_type)
    if role:
        query = query.filter(UserAuth.role == role)
    if status_filter:
        query = query.filter(UserAuth.status == status_filter)

    users = query.all()

    # レスポンス作成
    result = []
    for user in users:
        name = None
        if user.coach:
            name = f"{user.coach.last_name or ''} {user.coach.first_name or ''}".strip() or user.coach.name
        elif user.client:
            name = f"{user.client.last_name or ''} {user.client.first_name or ''}".strip() or user.client.name

        result.append(UserListResponse(
            user_id=str(user.user_id),
            email=user.email,
            user_type=user.user_type,
            role=user.role,
            status=user.status,
            name=name,
            created_at=user.created_at.isoformat()
        ))

    return result


@router.patch("/users/{user_id}/status")
async def update_user_status(
    user_id: UUID,
    status_update: UserStatusUpdate,
    db: Session = Depends(get_db),
    admin: UserAuth = Depends(require_super_admin)
):
    """ユーザーのステータスを変更（統括管理者のみ）"""
    # ステータスの検証
    valid_statuses = ['active', 'inactive', 'suspended']
    if status_update.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )

    # ユーザー取得
    user = db.query(UserAuth).filter(UserAuth.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # 自分自身のステータスは変更できない
    if user.user_id == admin.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own status"
        )

    # ステータス更新
    user.status = status_update.status
    db.commit()

    return {
        "message": "Status updated successfully",
        "user_id": str(user.user_id),
        "email": user.email,
        "new_status": user.status
    }


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    admin: UserAuth = Depends(require_super_admin)
):
    """ユーザーを強制削除（統括管理者のみ）"""
    # ユーザー取得
    user = db.query(UserAuth).filter(UserAuth.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # 自分自身は削除できない
    if user.user_id == admin.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    # ユーザー削除（CASCADE設定により関連データも削除される）
    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully",
        "user_id": str(user_id),
        "email": user.email
    }


@router.post("/users", response_model=UserListResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: AdminCreateUserRequest,
    db: Session = Depends(get_db),
    admin: UserAuth = Depends(require_super_admin)
):
    """新規ユーザーを作成（統括管理者のみ）"""
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
            detail="Invalid user type. Must be 'coach' or 'client'"
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

    # プロフィールの作成
    name = f"{request.last_name or ''} {request.first_name or ''}".strip()
    furigana = f"{request.last_name_kana or ''} {request.first_name_kana or ''}".strip() if request.last_name_kana or request.first_name_kana else None

    if request.user_type == 'coach':
        profile = Coach(
            user_id=user_auth.user_id,
            last_name=request.last_name,
            first_name=request.first_name,
            last_name_kana=request.last_name_kana,
            first_name_kana=request.first_name_kana,
            name=name,
            furigana=furigana,
            email=request.email,
            phone=request.phone
        )
        db.add(profile)
    else:  # client
        profile = Client(
            user_id=user_auth.user_id,
            last_name=request.last_name,
            first_name=request.first_name,
            last_name_kana=request.last_name_kana,
            first_name_kana=request.first_name_kana,
            name=name,
            furigana=furigana,
            email=request.email,
            phone=request.phone,
            status='active'
        )
        db.add(profile)

    db.commit()
    db.refresh(user_auth)

    return UserListResponse(
        user_id=str(user_auth.user_id),
        email=user_auth.email,
        user_type=user_auth.user_type,
        role=user_auth.role,
        status=user_auth.status,
        name=name,
        created_at=user_auth.created_at.isoformat()
    )
