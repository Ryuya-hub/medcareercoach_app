from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload, contains_eager
from typing import List, Optional
from uuid import UUID
from app.database import get_db
from app.models.application import Application, ApplicationHistory, CompanyAnalysis
from app.models.user import UserAuth, Client
from app.schemas.application import (
    ApplicationResponse,
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationHistoryResponse,
    CompanyAnalysisResponse,
    CompanyAnalysisCreate,
    CompanyAnalysisUpdate
)
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/applications", tags=["applications"])


# ============================================
# 応募管理API（固定パスを先に定義）
# ============================================

@router.get("", response_model=List[ApplicationResponse])
async def get_applications(
    client_id: Optional[UUID] = Query(None),
    status_filter: Optional[str] = Query(None),
    preference_rating: Optional[int] = Query(None),
    selection_stage: Optional[str] = Query(None),
    client_status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """応募一覧取得"""
    from app.models.user import Coach

    # 利用者の場合は自分の応募のみ
    if current_user.user_type == "client":
        client = db.query(Client).filter(Client.user_id == current_user.user_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        query = db.query(Application).filter(Application.client_id == client.client_id)
    elif current_user.user_type == "coach":
        # コーチの場合は全顧客の応募を表示（担当コーチの概念を削除）
        coach = db.query(Coach).filter(Coach.user_id == current_user.user_id).first()
        if not coach:
            raise HTTPException(status_code=404, detail="Coach not found")

        # 基本クエリ
        query = db.query(Application)

        # 利用者のステータスでフィルター（コーチのみ）
        has_client_join = False
        if client_status:
            query = query.join(Client, Application.client_id == Client.client_id).filter(Client.status == client_status)
            has_client_join = True

        # 特定の顧客でフィルター可能
        if client_id:
            query = query.filter(Application.client_id == client_id)
    else:
        query = db.query(Application)
        has_client_join = False

    # ステータスフィルター
    if status_filter:
        query = query.filter(Application.status == status_filter)

    # 志望度フィルター
    if preference_rating:
        query = query.filter(Application.preference_rating == preference_rating)

    # 選考段階フィルター
    if selection_stage:
        query = query.filter(Application.selection_stage == selection_stage)

    # Client情報のeager loading（join済みの場合はcontains_eager、未joinの場合はjoinedload）
    if current_user.user_type == "coach" and has_client_join:
        query = query.options(contains_eager(Application.client))
    else:
        query = query.options(joinedload(Application.client))

    applications = query.order_by(Application.next_interview_date.asc()).all()
    return applications


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    application_data: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """応募登録"""
    # 利用者の場合は自分のclient_idを使用
    if current_user.user_type == "client":
        client = db.query(Client).filter(Client.user_id == current_user.user_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        application_data.client_id = client.client_id
    elif current_user.user_type in ["coach", "super_admin"]:
        # コーチまたは管理者の場合は、リクエストボディからclient_idを取得
        if not application_data.client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="client_id is required for coach or admin users"
            )
        # client_idが有効か確認
        client = db.query(Client).filter(Client.client_id == application_data.client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
    else:
        raise HTTPException(status_code=403, detail="Invalid user type")

    application = Application(**application_data.dict())
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


# ============================================
# 企業分析API（固定パス、パスパラメータより前）
# ============================================

@router.get("/companies-analysis", response_model=List[CompanyAnalysisResponse])
async def get_companies_analysis(
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """企業分析一覧取得"""
    companies = db.query(CompanyAnalysis).all()
    return companies


@router.post("/companies-analysis", response_model=CompanyAnalysisResponse, status_code=status.HTTP_201_CREATED)
async def create_company_analysis(
    company_data: CompanyAnalysisCreate,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """企業分析情報作成（コーチのみ）"""
    if current_user.user_type != "coach":
        raise HTTPException(status_code=403, detail="Coach access required")

    # 重複チェック
    existing = db.query(CompanyAnalysis).filter(
        CompanyAnalysis.company_name == company_data.company_name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Company analysis already exists")

    company = CompanyAnalysis(**company_data.dict())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.get("/companies-analysis/{company_id}", response_model=CompanyAnalysisResponse)
async def get_company_analysis(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """企業分析情報取得"""
    company = db.query(CompanyAnalysis).filter(CompanyAnalysis.company_id == company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company analysis not found")

    return company


@router.put("/companies-analysis/{company_id}", response_model=CompanyAnalysisResponse)
async def update_company_analysis(
    company_id: UUID,
    company_data: CompanyAnalysisUpdate,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """企業分析情報更新（コーチのみ）"""
    if current_user.user_type != "coach":
        raise HTTPException(status_code=403, detail="Coach access required")

    company = db.query(CompanyAnalysis).filter(CompanyAnalysis.company_id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company analysis not found")

    update_data = company_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)

    db.commit()
    db.refresh(company)
    return company


# ============================================
# 応募履歴API（固定パス "history" を含む）
# ============================================

@router.get("/history/{application_id}", response_model=List[ApplicationHistoryResponse])
async def get_application_history(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """応募履歴取得"""
    application = db.query(Application).filter(Application.application_id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # 権限チェック
    if current_user.user_type == "client":
        client = db.query(Client).filter(Client.user_id == current_user.user_id).first()
        if not client or application.client_id != client.client_id:
            raise HTTPException(status_code=403, detail="Access forbidden")

    history = db.query(ApplicationHistory).filter(
        ApplicationHistory.application_id == application_id
    ).order_by(ApplicationHistory.changed_date.desc()).all()

    return history


# ============================================
# 個別応募API（パスパラメータのみ、最後に定義）
# ============================================

@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """応募詳細取得"""
    application = db.query(Application).options(joinedload(Application.client)).filter(
        Application.application_id == application_id
    ).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # 権限チェック
    if current_user.user_type == "client":
        client = db.query(Client).filter(Client.user_id == current_user.user_id).first()
        if not client or application.client_id != client.client_id:
            raise HTTPException(status_code=403, detail="Access forbidden")

    return application


@router.put("/{application_id}", response_model=ApplicationResponse)
async def update_application(
    application_id: UUID,
    application_data: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """応募情報更新"""
    application = db.query(Application).filter(Application.application_id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # 権限チェック
    if current_user.user_type == "client":
        client = db.query(Client).filter(Client.user_id == current_user.user_id).first()
        if not client or application.client_id != client.client_id:
            raise HTTPException(status_code=403, detail="Access forbidden")

    # 変更履歴の記録
    update_data = application_data.dict(exclude_unset=True)
    for field, new_value in update_data.items():
        old_value = getattr(application, field)
        if old_value != new_value:
            history = ApplicationHistory(
                application_id=application.application_id,
                changed_field=field,
                old_value=str(old_value) if old_value else None,
                new_value=str(new_value) if new_value else None,
                changed_by=current_user.user_id
            )
            db.add(history)
            setattr(application, field, new_value)

    db.commit()
    db.refresh(application)
    return application


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """応募情報削除"""
    # アプリケーションを取得
    application = db.query(Application).filter(Application.application_id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # 権限チェック
    if current_user.user_type == "client":
        client = db.query(Client).filter(Client.user_id == current_user.user_id).first()
        if not client or application.client_id != client.client_id:
            raise HTTPException(status_code=403, detail="Access forbidden")

    # 削除実行
    db.delete(application)
    db.commit()
    return None

