from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from app.database import get_db
from app.models.appointment import Appointment, CoachAvailability, appointment_coaches
from app.models.user import UserAuth, Client, Coach
from app.schemas.appointment import (
    AppointmentResponse,
    AppointmentCreate,
    AppointmentUpdate,
    CoachAvailabilityResponse,
    CoachAvailabilityCreate,
    CoachInfo
)
from app.utils.auth import get_current_user, get_current_coach
from app.utils.email import (
    send_appointment_approval_email,
    send_appointment_approval_email_multi,
    send_appointment_cancellation_email,
    send_appointment_update_email
)

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


@router.get("", response_model=List[AppointmentResponse])
async def get_appointments(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """予約一覧取得"""
    query = db.query(Appointment).options(joinedload(Appointment.client), joinedload(Appointment.coaches))

    # ユーザータイプに応じたフィルター
    if current_user.user_type == "client":
        client = db.query(Client).filter(Client.user_id == current_user.user_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        query = query.filter(Appointment.client_id == client.client_id)
    elif current_user.user_type == "coach":
        coach = db.query(Coach).filter(Coach.user_id == current_user.user_id).first()
        if not coach:
            raise HTTPException(status_code=404, detail="Coach not found")
        # コーチは自分が担当している予約のみ表示（appointment_coachesを通じて）
        query = query.join(appointment_coaches).filter(appointment_coaches.c.coach_id == coach.coach_id)

    # 日付範囲フィルター
    if start_date:
        query = query.filter(Appointment.appointment_date >= start_date)
    if end_date:
        query = query.filter(Appointment.appointment_date <= end_date)

    appointments = query.order_by(Appointment.appointment_date.asc()).all()
    return appointments


# コーチ空き枠API（特定のパスなので、/{appointment_id}より前に定義）
@router.get("/coach-availability", response_model=List[CoachAvailabilityResponse])
async def get_all_coach_availability(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """全コーチの空き枠取得（コーチ情報含む）"""
    try:
        print(f"[DEBUG] get_all_coach_availability called - start_date: {start_date}, end_date: {end_date}, user: {current_user.user_id}")
        query = db.query(CoachAvailability).options(
            joinedload(CoachAvailability.coach)
        )

        # 日付範囲フィルター
        if start_date:
            query = query.filter(CoachAvailability.available_start >= start_date)
        if end_date:
            query = query.filter(CoachAvailability.available_end <= end_date)

        # 未予約のもののみ
        query = query.filter(CoachAvailability.is_booked == False)

        availability = query.order_by(CoachAvailability.available_start.asc()).all()
        print(f"[DEBUG] Found {len(availability)} availability slots")

        # ORM オブジェクトを直接返す（from_attributes=True で自動変換）
        return availability
    except Exception as e:
        print(f"[ERROR] get_all_coach_availability failed: {e}")
        import traceback
        traceback.print_exc()
        raise


@router.get("/coach-availability/{coach_id}", response_model=List[CoachAvailabilityResponse])
async def get_coach_availability(
    coach_id: UUID,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """特定コーチの空き枠取得（コーチ情報含む）"""
    query = db.query(CoachAvailability).options(
        joinedload(CoachAvailability.coach)
    ).filter(CoachAvailability.coach_id == coach_id)

    # 日付範囲フィルター
    if start_date:
        query = query.filter(CoachAvailability.available_start >= start_date)
    if end_date:
        query = query.filter(CoachAvailability.available_end <= end_date)

    # 未予約のもののみ
    query = query.filter(CoachAvailability.is_booked == False)

    availability = query.order_by(CoachAvailability.available_start.asc()).all()
    return availability


@router.post("/coach-availability", response_model=List[CoachAvailabilityResponse], status_code=status.HTTP_201_CREATED)
async def create_coach_availability(
    availability_data: CoachAvailabilityCreate,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_coach)
):
    """コーチ空き枠登録（コーチのみ）- 30分単位に自動分割"""
    coach = db.query(Coach).filter(Coach.user_id == current_user.user_id).first()
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")

    # コーチ本人のみ自分の空き枠を登録可能
    if availability_data.coach_id != coach.coach_id:
        raise HTTPException(status_code=403, detail="Can only create your own availability")

    # 30分単位に分割
    start_time = availability_data.available_start
    end_time = availability_data.available_end

    created_slots = []
    current_time = start_time

    while current_time < end_time:
        slot_end = current_time + timedelta(minutes=30)
        if slot_end > end_time:
            slot_end = end_time

        availability = CoachAvailability(
            coach_id=availability_data.coach_id,
            available_start=current_time,
            available_end=slot_end,
            is_booked=False
        )
        db.add(availability)
        created_slots.append(availability)

        current_time = slot_end

    db.commit()
    for slot in created_slots:
        db.refresh(slot)

    return created_slots


@router.delete("/coach-availability/{availability_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_coach_availability(
    availability_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_coach)
):
    """コーチ空き枠削除（コーチのみ）"""
    availability = db.query(CoachAvailability).filter(
        CoachAvailability.availability_id == availability_id
    ).first()

    if not availability:
        raise HTTPException(status_code=404, detail="Availability not found")

    coach = db.query(Coach).filter(Coach.user_id == current_user.user_id).first()
    if not coach or availability.coach_id != coach.coach_id:
        raise HTTPException(status_code=403, detail="Access forbidden")

    # 予約済みの場合は削除不可
    if availability.is_booked:
        raise HTTPException(status_code=400, detail="Cannot delete booked availability")

    db.delete(availability)
    db.commit()
    return None


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """予約詳細取得"""
    appointment = db.query(Appointment).filter(Appointment.appointment_id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # 権限チェック
    if current_user.user_type == "client":
        client = db.query(Client).filter(Client.user_id == current_user.user_id).first()
        if not client or appointment.client_id != client.client_id:
            raise HTTPException(status_code=403, detail="Access forbidden")
    elif current_user.user_type == "coach":
        coach = db.query(Coach).filter(Coach.user_id == current_user.user_id).first()
        if not coach or appointment.coach_id != coach.coach_id:
            raise HTTPException(status_code=403, detail="Access forbidden")

    return appointment


@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """予約作成（複数コーチ対応）"""
    # 利用者の場合は自分のclient_idを自動設定
    if current_user.user_type == "client":
        client = db.query(Client).filter(Client.user_id == current_user.user_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        appointment_data.client_id = client.client_id

    # コーチIDリストを確認（coach_idsまたはcoach_idから取得）
    coach_ids = []
    if appointment_data.coach_ids:
        coach_ids = appointment_data.coach_ids
    elif appointment_data.coach_id:
        coach_ids = [appointment_data.coach_id]

    if not coach_ids:
        raise HTTPException(status_code=400, detail="At least one coach ID is required")

    # 最初のコーチをcoach_idとして設定（後方互換性）
    appointment_data.coach_id = coach_ids[0]

    # 予約作成
    appointment_dict = appointment_data.dict()
    appointment_dict.pop('coach_ids', None)  # coach_idsは保存しない
    appointment = Appointment(**appointment_dict)
    db.add(appointment)
    db.flush()  # appointment_idを生成

    # 複数コーチをappointments_coachesテーブルに登録
    for coach_id in coach_ids:
        db.execute(
            appointment_coaches.insert().values(
                appointment_id=appointment.appointment_id,
                coach_id=coach_id
            )
        )

    db.commit()
    db.refresh(appointment)

    # コーチ情報を読み込む
    appointment = db.query(Appointment).options(
        joinedload(Appointment.client),
        joinedload(Appointment.coaches)
    ).filter(Appointment.appointment_id == appointment.appointment_id).first()

    return appointment


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: UUID,
    appointment_data: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """予約更新"""
    # 予約情報を取得（クライアントとコーチ情報を含む）
    appointment = db.query(Appointment).options(
        joinedload(Appointment.client),
        joinedload(Appointment.coaches)
    ).filter(Appointment.appointment_id == appointment_id).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # 権限チェック
    if current_user.user_type == "client":
        client = db.query(Client).filter(Client.user_id == current_user.user_id).first()
        if not client or appointment.client_id != client.client_id:
            raise HTTPException(status_code=403, detail="Access forbidden")
    elif current_user.user_type == "coach":
        coach = db.query(Coach).filter(Coach.user_id == current_user.user_id).first()
        if not coach or appointment.coach_id != coach.coach_id:
            raise HTTPException(status_code=403, detail="Access forbidden")

    # 変更前の日時を保存（メール送信用）
    old_appointment_date = appointment.appointment_date
    old_appointment_date_str = old_appointment_date.strftime('%Y年%m月%d日 %H:%M')

    # 更新
    update_data = appointment_data.dict(exclude_unset=True)
    date_changed = False

    for field, value in update_data.items():
        if field == 'appointment_date' and value != old_appointment_date:
            date_changed = True
        setattr(appointment, field, value)

    db.commit()
    db.refresh(appointment)

    # 日時が変更された場合、変更通知メールを送信
    if date_changed:
        client = appointment.client
        all_coaches = appointment.coaches
        new_appointment_date_str = appointment.appointment_date.strftime('%Y年%m月%d日 %H:%M')
        coach_names = [c.name if c.name else f"{c.last_name or ''} {c.first_name or ''}".strip() for c in all_coaches]
        meeting_url = appointment.mtg_url or "未設定"

        # 利用者にメール送信
        if client:
            client_display_name = client.name if client.name else f"{client.last_name or ''} {client.first_name or ''}".strip()
            send_appointment_update_email(
                to_email=client.email,
                client_name=client_display_name,
                coach_names=coach_names,
                old_appointment_date=old_appointment_date_str,
                new_appointment_date=new_appointment_date_str,
                meeting_url=meeting_url,
                notes=appointment.notes,
                is_for_coach=False
            )

        # 各コーチにメール送信
        for coach_item in all_coaches:
            client_display_name = client.name if client.name else f"{client.last_name or ''} {client.first_name or ''}".strip()
            send_appointment_update_email(
                to_email=coach_item.email,
                client_name=client_display_name,
                coach_names=coach_names,
                old_appointment_date=old_appointment_date_str,
                new_appointment_date=new_appointment_date_str,
                meeting_url=meeting_url,
                notes=appointment.notes,
                is_for_coach=True
            )

    return appointment


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_appointment(
    appointment_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """予約キャンセル"""
    # 予約情報を取得（クライアントとコーチ情報を含む）
    appointment = db.query(Appointment).options(
        joinedload(Appointment.client),
        joinedload(Appointment.coaches)
    ).filter(Appointment.appointment_id == appointment_id).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # 権限チェック
    if current_user.user_type == "client":
        client = db.query(Client).filter(Client.user_id == current_user.user_id).first()
        if not client or appointment.client_id != client.client_id:
            raise HTTPException(status_code=403, detail="Access forbidden")
    elif current_user.user_type == "coach":
        coach = db.query(Coach).filter(Coach.user_id == current_user.user_id).first()
        if not coach or appointment.coach_id != coach.coach_id:
            raise HTTPException(status_code=403, detail="Access forbidden")

    # メール送信用のデータを準備
    client = appointment.client
    all_coaches = appointment.coaches
    appointment_date_str = appointment.appointment_date.strftime('%Y年%m月%d日 %H:%M')
    coach_names = [c.name if c.name else f"{c.last_name or ''} {c.first_name or ''}".strip() for c in all_coaches]

    # ステータスをキャンセルに更新
    appointment.status = 'キャンセル'
    db.commit()

    # キャンセル通知メールを送信
    # 利用者にメール送信
    if client:
        client_display_name = client.name if client.name else f"{client.last_name or ''} {client.first_name or ''}".strip()
        send_appointment_cancellation_email(
            to_email=client.email,
            client_name=client_display_name,
            coach_names=coach_names,
            appointment_date=appointment_date_str,
            is_for_coach=False
        )

    # 各コーチにメール送信
    for coach_item in all_coaches:
        client_display_name = client.name if client.name else f"{client.last_name or ''} {client.first_name or ''}".strip()
        send_appointment_cancellation_email(
            to_email=coach_item.email,
            client_name=client_display_name,
            coach_names=coach_names,
            appointment_date=appointment_date_str,
            is_for_coach=True
        )

    return None


@router.post("/{appointment_id}/approve", response_model=AppointmentResponse)
async def approve_appointment(
    appointment_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_coach)
):
    """予約承認（コーチのみ）- 複数コーチ対応"""
    # 予約とコーチ情報を取得
    appointment = db.query(Appointment).options(
        joinedload(Appointment.coaches),
        joinedload(Appointment.client)
    ).filter(Appointment.appointment_id == appointment_id).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    coach = db.query(Coach).filter(Coach.user_id == current_user.user_id).first()
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")

    # この予約に関わるコーチかどうかをチェック
    coach_ids = [c.coach_id for c in appointment.coaches]
    if coach.coach_id not in coach_ids:
        raise HTTPException(status_code=403, detail="Access forbidden")

    # クライアント情報を取得
    client = appointment.client
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # ステータスを確定に変更
    appointment.status = '確定'

    # MTG URLを設定（承認したコーチのプロフィールから取得）
    if coach.mtg_url and not appointment.mtg_url:
        appointment.mtg_url = coach.mtg_url

    db.commit()
    db.refresh(appointment)

    # メール送信の準備
    appointment_date_str = appointment.appointment_date.strftime('%Y年%m月%d日 %H:%M')
    meeting_url = appointment.mtg_url or coach.mtg_url or "未設定"

    # 全コーチの名前とメールアドレスを取得
    all_coaches = appointment.coaches
    coach_names = [c.name for c in all_coaches]

    # 利用者にメール送信
    send_appointment_approval_email_multi(
        to_email=client.email,
        client_name=client.name,
        coach_names=coach_names,
        appointment_date=appointment_date_str,
        meeting_url=meeting_url,
        notes=appointment.notes,
        is_for_coach=False
    )

    # 各コーチにメール送信
    for coach_item in all_coaches:
        send_appointment_approval_email_multi(
            to_email=coach_item.email,
            client_name=client.name,
            coach_names=coach_names,
            appointment_date=appointment_date_str,
            meeting_url=meeting_url,
            notes=appointment.notes,
            is_for_coach=True
        )

    return appointment


@router.post("/{appointment_id}/reject", response_model=AppointmentResponse)
async def reject_appointment(
    appointment_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_coach)
):
    """予約拒否（コーチのみ）- 複数コーチ対応"""
    # 予約とコーチ情報を取得
    appointment = db.query(Appointment).options(
        joinedload(Appointment.coaches)
    ).filter(Appointment.appointment_id == appointment_id).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    coach = db.query(Coach).filter(Coach.user_id == current_user.user_id).first()
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")

    # この予約に関わるコーチかどうかをチェック
    coach_ids = [c.coach_id for c in appointment.coaches]
    if coach.coach_id not in coach_ids:
        raise HTTPException(status_code=403, detail="Access forbidden")

    appointment.status = 'キャンセル'
    db.commit()
    db.refresh(appointment)
    return appointment
