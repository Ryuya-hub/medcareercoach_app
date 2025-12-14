from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from uuid import UUID
from datetime import datetime
from app.database import get_db
from app.models.resume import (
    Resume, WorkExperience, EducationHistory, Certification, Skill,
    ResumeReview, ReviewComment, ReviewTemplate
)
from app.models.user import UserAuth, Client, Coach
from app.schemas.resume import (
    ResumeResponse, ResumeCreate, ResumeUpdate,
    WorkExperienceResponse, WorkExperienceCreate, WorkExperienceUpdate,
    EducationHistoryResponse, EducationHistoryCreate, EducationHistoryUpdate,
    CertificationResponse, CertificationCreate, CertificationUpdate,
    SkillResponse, SkillCreate, SkillUpdate,
    ResumeReviewResponse, ResumeReviewCreate, ResumeReviewUpdate,
    ReviewCommentResponse, ReviewCommentCreate, ReviewCommentUpdate,
    ReviewTemplateResponse, ReviewTemplateCreate, ReviewTemplateUpdate
)
from app.utils.auth import get_current_user, get_current_coach, get_current_client

router = APIRouter(prefix="/api/resumes", tags=["resumes"])


# 職務経歴書CRUD
@router.get("/me", response_model=List[ResumeResponse])
async def get_my_resumes(
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """自分の職務経歴書一覧取得（利用者のみ）"""
    if current_user.user_type != "client":
        raise HTTPException(status_code=403, detail="Only clients can access this endpoint")

    client = db.query(Client).filter(Client.user_id == current_user.user_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    resumes = db.query(Resume).filter(Resume.client_id == client.client_id).order_by(Resume.version_number.desc()).all()
    return resumes


@router.get("/client/{client_id}", response_model=List[ResumeResponse])
async def get_client_resumes(
    client_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """顧客の職務経歴書一覧取得（コーチ用）"""
    # コーチのみアクセス可能
    if current_user.user_type != "coach":
        raise HTTPException(status_code=403, detail="Only coaches can access this endpoint")

    coach = db.query(Coach).filter(Coach.user_id == current_user.user_id).first()
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")

    # 全クライアントの職務経歴書を閲覧可能（担当コーチの概念を削除）
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    resumes = db.query(Resume).filter(Resume.client_id == client_id).order_by(Resume.version_number.desc()).all()
    return resumes


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """職務経歴書詳細取得"""
    from sqlalchemy.orm import joinedload

    resume = db.query(Resume).options(
        joinedload(Resume.reviews).joinedload(ResumeReview.coach)
    ).filter(Resume.resume_id == resume_id).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # 権限チェック
    if current_user.user_type == "client":
        client = db.query(Client).filter(Client.user_id == current_user.user_id).first()
        if not client or resume.client_id != client.client_id:
            raise HTTPException(status_code=403, detail="Access forbidden")

    return resume


@router.post("", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def create_resume(
    resume_data: ResumeCreate,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_client)
):
    """職務経歴書作成（利用者のみ）"""
    client = db.query(Client).filter(Client.user_id == current_user.user_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # バージョン番号の決定
    last_resume = db.query(Resume).filter(
        Resume.client_id == client.client_id
    ).order_by(Resume.version_number.desc()).first()

    version_number = 1 if not last_resume else last_resume.version_number + 1

    # 職務経歴書作成
    resume = Resume(
        client_id=client.client_id,
        version_number=version_number,
        **resume_data.dict(exclude={'client_id'})
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


@router.put("/{resume_id}", response_model=ResumeResponse)
async def update_resume(
    resume_id: UUID,
    resume_data: ResumeUpdate,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_client)
):
    """職務経歴書更新（利用者のみ）"""
    resume = db.query(Resume).filter(Resume.resume_id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # 権限チェック
    client = db.query(Client).filter(Client.user_id == current_user.user_id).first()
    if not client or resume.client_id != client.client_id:
        raise HTTPException(status_code=403, detail="Access forbidden")

    # 更新
    update_data = resume_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resume, field, value)

    db.commit()
    db.refresh(resume)
    return resume


@router.post("/{resume_id}/submit", response_model=ResumeResponse)
async def submit_resume(
    resume_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_client)
):
    """職務経歴書提出（利用者のみ）"""
    resume = db.query(Resume).filter(Resume.resume_id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # 権限チェック
    client = db.query(Client).filter(Client.user_id == current_user.user_id).first()
    if not client or resume.client_id != client.client_id:
        raise HTTPException(status_code=403, detail="Access forbidden")

    # ステータス更新
    resume.status = 'submitted'
    resume.submitted_at = datetime.utcnow()

    db.commit()
    db.refresh(resume)
    return resume


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_client)
):
    """職務経歴書削除（利用者のみ）"""
    resume = db.query(Resume).filter(Resume.resume_id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # 権限チェック
    client = db.query(Client).filter(Client.user_id == current_user.user_id).first()
    if not client or resume.client_id != client.client_id:
        raise HTTPException(status_code=403, detail="Access forbidden")

    db.delete(resume)
    db.commit()
    return None


# 職務経歴セクションCRUD
@router.get("/{resume_id}/work-experiences", response_model=List[WorkExperienceResponse])
async def get_work_experiences(
    resume_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """職務経歴一覧取得"""
    experiences = db.query(WorkExperience).filter(
        WorkExperience.resume_id == resume_id
    ).order_by(WorkExperience.display_order).all()
    return experiences


@router.post("/{resume_id}/work-experiences", response_model=WorkExperienceResponse, status_code=status.HTTP_201_CREATED)
async def create_work_experience(
    resume_id: UUID,
    experience_data: WorkExperienceCreate,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_client)
):
    """職務経歴追加"""
    resume = db.query(Resume).filter(Resume.resume_id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # 権限チェック
    client = db.query(Client).filter(Client.user_id == current_user.user_id).first()
    if not client or resume.client_id != client.client_id:
        raise HTTPException(status_code=403, detail="Access forbidden")

    experience = WorkExperience(resume_id=resume_id, **experience_data.dict())
    db.add(experience)
    db.commit()
    db.refresh(experience)
    return experience


@router.put("/work-experiences/{experience_id}", response_model=WorkExperienceResponse)
async def update_work_experience(
    experience_id: UUID,
    experience_data: WorkExperienceUpdate,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_client)
):
    """職務経歴更新"""
    experience = db.query(WorkExperience).filter(WorkExperience.experience_id == experience_id).first()
    if not experience:
        raise HTTPException(status_code=404, detail="Work experience not found")

    # 権限チェック
    resume = db.query(Resume).filter(Resume.resume_id == experience.resume_id).first()
    client = db.query(Client).filter(Client.user_id == current_user.user_id).first()
    if not client or resume.client_id != client.client_id:
        raise HTTPException(status_code=403, detail="Access forbidden")

    # 更新
    update_data = experience_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(experience, field, value)

    db.commit()
    db.refresh(experience)
    return experience


@router.delete("/work-experiences/{experience_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_work_experience(
    experience_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_client)
):
    """職務経歴削除"""
    experience = db.query(WorkExperience).filter(WorkExperience.experience_id == experience_id).first()
    if not experience:
        raise HTTPException(status_code=404, detail="Work experience not found")

    # 権限チェック
    resume = db.query(Resume).filter(Resume.resume_id == experience.resume_id).first()
    client = db.query(Client).filter(Client.user_id == current_user.user_id).first()
    if not client or resume.client_id != client.client_id:
        raise HTTPException(status_code=403, detail="Access forbidden")

    db.delete(experience)
    db.commit()
    return None


# 学歴セクションCRUD (同様のパターン)
@router.get("/{resume_id}/education", response_model=List[EducationHistoryResponse])
async def get_education_history(
    resume_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """学歴一覧取得"""
    education = db.query(EducationHistory).filter(
        EducationHistory.resume_id == resume_id
    ).order_by(EducationHistory.display_order).all()
    return education


@router.post("/{resume_id}/education", response_model=EducationHistoryResponse, status_code=status.HTTP_201_CREATED)
async def create_education(
    resume_id: UUID,
    education_data: EducationHistoryCreate,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_client)
):
    """学歴追加"""
    resume = db.query(Resume).filter(Resume.resume_id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    client = db.query(Client).filter(Client.user_id == current_user.user_id).first()
    if not client or resume.client_id != client.client_id:
        raise HTTPException(status_code=403, detail="Access forbidden")

    education = EducationHistory(resume_id=resume_id, **education_data.dict())
    db.add(education)
    db.commit()
    db.refresh(education)
    return education


# 資格セクションCRUD
@router.get("/{resume_id}/certifications", response_model=List[CertificationResponse])
async def get_certifications(
    resume_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """資格一覧取得"""
    certifications = db.query(Certification).filter(
        Certification.resume_id == resume_id
    ).order_by(Certification.display_order).all()
    return certifications


@router.post("/{resume_id}/certifications", response_model=CertificationResponse, status_code=status.HTTP_201_CREATED)
async def create_certification(
    resume_id: UUID,
    cert_data: CertificationCreate,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_client)
):
    """資格追加"""
    resume = db.query(Resume).filter(Resume.resume_id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    client = db.query(Client).filter(Client.user_id == current_user.user_id).first()
    if not client or resume.client_id != client.client_id:
        raise HTTPException(status_code=403, detail="Access forbidden")

    certification = Certification(resume_id=resume_id, **cert_data.dict())
    db.add(certification)
    db.commit()
    db.refresh(certification)
    return certification


# スキルセクションCRUD
@router.get("/{resume_id}/skills", response_model=List[SkillResponse])
async def get_skills(
    resume_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """スキル一覧取得"""
    skills = db.query(Skill).filter(Skill.resume_id == resume_id).all()
    return skills


@router.post("/{resume_id}/skills", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
async def create_skill(
    resume_id: UUID,
    skill_data: SkillCreate,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_client)
):
    """スキル追加"""
    resume = db.query(Resume).filter(Resume.resume_id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    client = db.query(Client).filter(Client.user_id == current_user.user_id).first()
    if not client or resume.client_id != client.client_id:
        raise HTTPException(status_code=403, detail="Access forbidden")

    skill = Skill(resume_id=resume_id, **skill_data.dict())
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


# 添削機能（コーチ側）
@router.get("/coach/pending", response_model=List[ResumeResponse])
async def get_pending_resumes(
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_coach)
):
    """全ての職務経歴書一覧取得（コーチのみ）- ステータス問わず全て表示"""
    # 全ての職務経歴書を取得（draft, submitted, reviewed全て）
    resumes = db.query(Resume).options(
        joinedload(Resume.client)
    ).order_by(Resume.created_at.desc()).all()
    print(f"[DEBUG] Coach requesting resumes - found {len(resumes)} total resumes")
    return resumes


@router.post("/{resume_id}/reviews", response_model=ResumeReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    resume_id: UUID,
    review_data: ResumeReviewCreate,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_coach)
):
    """添削開始（コーチのみ）"""
    resume = db.query(Resume).filter(Resume.resume_id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    coach = db.query(Coach).filter(Coach.user_id == current_user.user_id).first()
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")

    # 添削作成
    review = ResumeReview(
        resume_id=resume_id,
        coach_id=coach.coach_id,
        **review_data.dict(exclude={'resume_id', 'coach_id'})
    )
    db.add(review)

    # 職務経歴書のステータス更新
    resume.status = 'under_review'

    db.commit()
    db.refresh(review)
    return review


@router.post("/reviews/{review_id}/comments", response_model=ReviewCommentResponse, status_code=status.HTTP_201_CREATED)
async def create_review_comment(
    review_id: UUID,
    comment_data: ReviewCommentCreate,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_coach)
):
    """添削コメント追加（コーチのみ）"""
    review = db.query(ResumeReview).filter(ResumeReview.review_id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    comment = ReviewComment(review_id=review_id, **comment_data.dict(exclude={'review_id'}))
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.post("/reviews/{review_id}/complete", response_model=ResumeReviewResponse)
async def complete_review(
    review_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_coach)
):
    """添削完了（コーチのみ）"""
    review = db.query(ResumeReview).filter(ResumeReview.review_id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    # 添削完了
    review.review_status = 'completed'
    review.reviewed_at = datetime.utcnow()

    # 職務経歴書のステータス更新
    resume = db.query(Resume).filter(Resume.resume_id == review.resume_id).first()
    resume.status = 'reviewed'
    resume.reviewed_at = datetime.utcnow()

    db.commit()
    db.refresh(review)
    return review


@router.get("/{resume_id}/reviews", response_model=List[ResumeReviewResponse])
async def get_resume_reviews(
    resume_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_user)
):
    """添削履歴取得（複数コーチ対応）"""
    reviews = db.query(ResumeReview).options(
        joinedload(ResumeReview.coach)
    ).filter(
        ResumeReview.resume_id == resume_id
    ).order_by(ResumeReview.created_at.desc()).all()
    print(f"[DEBUG] Retrieved {len(reviews)} reviews for resume {resume_id}")
    for review in reviews:
        coach_name = review.coach.name if review.coach else "Unknown"
        print(f"  - Review {review.review_id}: by coach {coach_name} (status: {review.review_status})")
    return reviews


@router.post("/{resume_id}/apply-review/{review_id}", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def apply_review_to_resume(
    resume_id: UUID,
    review_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_client)
):
    """添削を反映して新しいバージョンの職務経歴書を作成（利用者のみ）"""
    # 元の職務経歴書を取得
    original_resume = db.query(Resume).filter(Resume.resume_id == resume_id).first()
    if not original_resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # 権限チェック
    client = db.query(Client).filter(Client.user_id == current_user.user_id).first()
    if not client or original_resume.client_id != client.client_id:
        raise HTTPException(status_code=403, detail="Access forbidden")

    # 添削を取得
    review = db.query(ResumeReview).filter(ResumeReview.review_id == review_id).first()
    if not review or review.resume_id != resume_id:
        raise HTTPException(status_code=404, detail="Review not found or does not belong to this resume")

    # 新しいバージョン番号を決定
    last_resume = db.query(Resume).filter(
        Resume.client_id == client.client_id
    ).order_by(Resume.version_number.desc()).first()

    version_number = 1 if not last_resume else last_resume.version_number + 1

    # 添削のoverall_commentを新しいcontentとして使用
    new_content = review.overall_comment or original_resume.content

    # 新しいバージョンの職務経歴書を作成
    new_resume = Resume(
        client_id=client.client_id,
        version_number=version_number,
        content=new_content,
        template_type=original_resume.template_type,
        status='draft'
    )
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)
    return new_resume


@router.delete("/{resume_id}/coach", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume_by_coach(
    resume_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserAuth = Depends(get_current_coach)
):
    """職務経歴書削除（コーチのみ）"""
    resume = db.query(Resume).filter(Resume.resume_id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    db.delete(resume)
    db.commit()
    return None
