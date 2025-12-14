from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.models.user import Client, UserAuth
from app.schemas.user import ClientResponse, ClientCreate, ClientUpdate
from app.utils.auth import get_current_coach, get_current_user

router = APIRouter(prefix="/api/clients", tags=["clients"])


@router.get("/me", response_model=ClientResponse)
async def get_my_profile(
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """自分の利用者情報取得（利用者のみ）"""
    client = db.query(Client).filter(Client.user_id == current_user.user_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.get("", response_model=List[ClientResponse])
async def get_clients(
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_coach)
):
    """顧客一覧取得（コーチのみ・全顧客表示）"""
    from app.models.user import Coach

    # 現在のコーチ情報を取得（認証確認のため）
    coach = db.query(Coach).filter(Coach.user_id == current_user.user_id).first()
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")

    # すべての顧客を返す（担当コーチの概念を削除）
    clients = db.query(Client).all()
    return clients


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """顧客詳細取得"""
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # 権限チェック：コーチまたは本人のみ
    if current_user.user_type != "coach" and client.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Access forbidden")

    return client


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientCreate,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_coach)
):
    """顧客登録（コーチのみ）"""
    # メールアドレスの重複チェック
    existing_client = db.query(Client).filter(Client.email == client_data.email).first()
    if existing_client:
        raise HTTPException(status_code=400, detail="Email already registered")

    # ユーザー認証情報は別途作成される必要がある
    # ここではClient情報のみ作成
    client = Client(**client_data.dict())
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: UUID,
    client_data: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """顧客情報更新"""
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # 権限チェック：コーチまたは本人のみ
    if current_user.user_type != "coach" and client.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Access forbidden")

    # 更新
    update_data = client_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)

    db.commit()
    db.refresh(client)
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_coach)
):
    """顧客削除（論理削除）（コーチのみ）"""
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # 論理削除
    client.status = 'cancelled'
    db.commit()
    return None


@router.post("/{client_id}/coaches/{coach_id}", response_model=ClientResponse)
async def add_coach_to_client(
    client_id: UUID,
    coach_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """利用者にコーチを追加"""
    from app.models.user import Coach

    client = db.query(Client).filter(Client.client_id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    coach = db.query(Coach).filter(Coach.coach_id == coach_id).first()
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")

    # 権限チェック：本人のみ
    if current_user.user_type == "client" and client.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Access forbidden")

    # 既に追加されているかチェック
    if coach not in client.coaches:
        client.coaches.append(coach)
        # 主担当コーチが未設定の場合は設定
        if not client.coach_id:
            client.coach_id = coach_id
        db.commit()
        db.refresh(client)

    return client


@router.delete("/{client_id}/coaches/{coach_id}", response_model=ClientResponse)
async def remove_coach_from_client(
    client_id: UUID,
    coach_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """利用者からコーチを削除"""
    from app.models.user import Coach

    client = db.query(Client).filter(Client.client_id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    coach = db.query(Coach).filter(Coach.coach_id == coach_id).first()
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")

    # 権限チェック：本人のみ
    if current_user.user_type == "client" and client.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Access forbidden")

    # コーチを削除
    if coach in client.coaches:
        client.coaches.remove(coach)
        # 主担当コーチが削除されたコーチの場合、別のコーチを主担当に設定
        if client.coach_id == coach_id:
            if client.coaches:
                client.coach_id = client.coaches[0].coach_id
            else:
                client.coach_id = None
        db.commit()
        db.refresh(client)

    return client
