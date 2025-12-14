from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.models.user import Coach, UserAuth
from app.schemas.user import CoachResponse, CoachUpdate
from app.utils.auth import get_current_user, get_current_coach

router = APIRouter(prefix="/api/coaches", tags=["coaches"])


@router.get("/me", response_model=CoachResponse)
async def get_my_profile(
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """自分のコーチ情報取得（コーチのみ）"""
    if current_user.user_type != "coach":
        raise HTTPException(status_code=403, detail="Only coaches can access this endpoint")

    coach = db.query(Coach).filter(Coach.user_id == current_user.user_id).first()
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")
    return coach


@router.get("", response_model=List[CoachResponse])
async def get_coaches(
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """コーチ一覧取得"""
    coaches = db.query(Coach).all()
    return coaches


@router.get("/{coach_id}", response_model=CoachResponse)
async def get_coach(
    coach_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """コーチ詳細取得"""
    coach = db.query(Coach).filter(Coach.coach_id == coach_id).first()
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")
    return coach


@router.put("/{coach_id}", response_model=CoachResponse)
async def update_coach(
    coach_id: UUID,
    coach_data: CoachUpdate,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """コーチ情報更新"""
    coach = db.query(Coach).filter(Coach.coach_id == coach_id).first()
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")

    # 権限チェック：本人のみ
    if coach.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You can only update your own profile")

    # 更新
    update_data = coach_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(coach, field, value)

    db.commit()
    db.refresh(coach)
    return coach
