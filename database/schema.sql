-- 転職支援顧客管理システム データベーススキーマ
-- Supabase (PostgreSQL) 用

-- 4.2.1 ユーザー認証テーブル(users_auth)
CREATE TABLE users_auth (
  user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('coach', 'client')),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_auth_email ON users_auth(email);
CREATE INDEX idx_users_auth_user_type ON users_auth(user_type);

-- 4.2.2 コーチ情報テーブル(coaches)
CREATE TABLE coaches (
  coach_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users_auth(user_id) ON DELETE CASCADE,
  name VARCHAR(100) NOT NULL,
  furigana VARCHAR(100),
  email VARCHAR(255) UNIQUE NOT NULL,
  phone VARCHAR(20),
  mtg_url TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_coaches_user_id ON coaches(user_id);
CREATE UNIQUE INDEX idx_coaches_email ON coaches(email);

-- 4.2.3 顧客(利用者)情報テーブル(clients)
CREATE TABLE clients (
  client_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users_auth(user_id) ON DELETE CASCADE,
  coach_id UUID REFERENCES coaches(coach_id),
  name VARCHAR(100) NOT NULL,
  furigana VARCHAR(100),
  email VARCHAR(255) UNIQUE NOT NULL,
  phone VARCHAR(20),
  company_name VARCHAR(200),
  occupation VARCHAR(100), -- 例: Nrs/PT/OT/ST/その他医療系職種
  registration_date DATE,
  contract_end_date DATE,
  status VARCHAR(20) NOT NULL DEFAULT 'active'
    CHECK (status IN ('active', 'inactive', 'cancelled')),
  will_can_must TEXT, -- 自己分析結果
  strengths_finder TEXT,
  desired_income INTEGER,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_clients_user_id ON clients(user_id);
CREATE INDEX idx_clients_coach_id ON clients(coach_id);
CREATE INDEX idx_clients_status ON clients(status);
CREATE UNIQUE INDEX idx_clients_email ON clients(email);

-- 4.2.4 応募企業管理テーブル(applications)
CREATE TABLE applications (
  application_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
  company_name VARCHAR(200) NOT NULL,
  application_date DATE,
  selection_stage VARCHAR(50)
    CHECK (selection_stage IN ('書類選考', '一次面接', '二次面接', '三次面接', '最終面接')),
  next_interview_date DATE,
  priority INTEGER DEFAULT 5,
  status VARCHAR(20) NOT NULL DEFAULT '選考中'
    CHECK (status IN ('選考中', '内定', '不採用', '辞退')),
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_applications_client_id ON applications(client_id);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_applications_company_name ON applications(company_name);

-- 4.2.5 面談予約テーブル(appointments)
CREATE TABLE appointments (
  appointment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
  coach_id UUID NOT NULL REFERENCES coaches(coach_id) ON DELETE CASCADE,
  appointment_date TIMESTAMP NOT NULL,
  appointment_type VARCHAR(20) CHECK (appointment_type IN ('定期', 'スポット')),
  status VARCHAR(20) NOT NULL DEFAULT '予約済'
    CHECK (status IN ('予約済', '確定', 'キャンセル')),
  mtg_url TEXT,
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_appointments_client_id ON appointments(client_id);
CREATE INDEX idx_appointments_coach_id ON appointments(coach_id);
CREATE INDEX idx_appointments_date ON appointments(appointment_date);
CREATE INDEX idx_appointments_status ON appointments(status);

-- 4.2.6 コーチ空き枠テーブル(coach_availability)
CREATE TABLE coach_availability (
  availability_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  coach_id UUID NOT NULL REFERENCES coaches(coach_id) ON DELETE CASCADE,
  available_start TIMESTAMP NOT NULL,
  available_end TIMESTAMP NOT NULL,
  is_booked BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_coach_availability_coach_id ON coach_availability(coach_id);
CREATE INDEX idx_coach_availability_dates ON coach_availability(available_start, available_end);
CREATE INDEX idx_coach_availability_is_booked ON coach_availability(is_booked);

-- 4.2.7 企業分析テーブル(company_analysis)
CREATE TABLE company_analysis (
  company_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_name VARCHAR(200) UNIQUE NOT NULL,
  industry VARCHAR(100),
  location VARCHAR(200),
  analysis_notes TEXT,
  success_rate DECIMAL(5,2),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_company_analysis_name ON company_analysis(company_name);

-- 4.2.8 応募履歴テーブル(application_history)
CREATE TABLE application_history (
  history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  application_id UUID NOT NULL REFERENCES applications(application_id) ON DELETE CASCADE,
  changed_date TIMESTAMP NOT NULL DEFAULT NOW(),
  changed_field VARCHAR(100),
  old_value TEXT,
  new_value TEXT,
  changed_by UUID REFERENCES users_auth(user_id)
);

CREATE INDEX idx_application_history_application_id ON application_history(application_id);
CREATE INDEX idx_application_history_changed_date ON application_history(changed_date);

-- 4.2.9 ファイル管理テーブル(files)
CREATE TABLE files (
  file_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  related_type VARCHAR(50) NOT NULL
    CHECK (related_type IN ('client', 'application')),
  related_id UUID NOT NULL,
  file_name VARCHAR(255) NOT NULL,
  file_path TEXT NOT NULL,
  file_size INTEGER,
  uploaded_by UUID REFERENCES users_auth(user_id),
  uploaded_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_files_related ON files(related_type, related_id);
CREATE INDEX idx_files_uploaded_by ON files(uploaded_by);

-- 4.2.10 職務経歴書テーブル(resumes)
CREATE TABLE resumes (
  resume_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
  version_number INTEGER NOT NULL DEFAULT 1,
  status VARCHAR(20) NOT NULL DEFAULT 'draft'
    CHECK (status IN ('draft', 'submitted', 'under_review', 'reviewed', 'approved')),

  -- フリーテキスト形式の職務経歴書内容
  content TEXT,

  -- メタ情報
  submitted_at TIMESTAMP,
  reviewed_at TIMESTAMP,
  approved_at TIMESTAMP,
  template_type VARCHAR(50) DEFAULT 'standard',

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  UNIQUE(client_id, version_number)
);

CREATE INDEX idx_resumes_client_id ON resumes(client_id);
CREATE INDEX idx_resumes_status ON resumes(status);
CREATE INDEX idx_resumes_submitted_at ON resumes(submitted_at);

-- 4.2.11 職務経歴テーブル(work_experiences)
CREATE TABLE work_experiences (
  experience_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  resume_id UUID NOT NULL REFERENCES resumes(resume_id) ON DELETE CASCADE,
  display_order INTEGER NOT NULL,

  start_date DATE NOT NULL,
  end_date DATE, -- NULL = 現在も在籍中
  company_name VARCHAR(200) NOT NULL,
  department VARCHAR(100),
  position VARCHAR(100),
  employment_type VARCHAR(50), -- '正社員', '契約社員', '派遣', 'アルバイト'

  job_description TEXT,
  achievements TEXT,
  skills_used TEXT,

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_work_experiences_resume_id ON work_experiences(resume_id);
CREATE INDEX idx_work_experiences_order ON work_experiences(resume_id, display_order);

-- 4.2.12 学歴テーブル(education_history)
CREATE TABLE education_history (
  education_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  resume_id UUID NOT NULL REFERENCES resumes(resume_id) ON DELETE CASCADE,
  display_order INTEGER NOT NULL,

  start_date DATE NOT NULL,
  end_date DATE,
  school_name VARCHAR(200) NOT NULL,
  faculty VARCHAR(100),
  major VARCHAR(100),
  graduation_status VARCHAR(20)
    CHECK (graduation_status IN ('卒業', '中退', '在学中')),

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_education_resume_id ON education_history(resume_id);
CREATE INDEX idx_education_order ON education_history(resume_id, display_order);

-- 4.2.13 資格・免許テーブル(certifications)
CREATE TABLE certifications (
  certification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  resume_id UUID NOT NULL REFERENCES resumes(resume_id) ON DELETE CASCADE,
  display_order INTEGER NOT NULL,

  acquisition_date DATE NOT NULL,
  certification_name VARCHAR(200) NOT NULL,
  issuing_organization VARCHAR(200),

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_certifications_resume_id ON certifications(resume_id);
CREATE INDEX idx_certifications_order ON certifications(resume_id, display_order);

-- 4.2.14 スキルテーブル(skills)
CREATE TABLE skills (
  skill_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  resume_id UUID NOT NULL REFERENCES resumes(resume_id) ON DELETE CASCADE,

  skill_category VARCHAR(50)
    CHECK (skill_category IN ('programming', 'tools', 'language', 'other')),
  skill_name VARCHAR(100) NOT NULL,
  proficiency_level VARCHAR(20)
    CHECK (proficiency_level IN ('beginner', 'intermediate', 'advanced', 'expert')),

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_skills_resume_id ON skills(resume_id);
CREATE INDEX idx_skills_category ON skills(skill_category);

-- 4.2.15 添削テーブル(resume_reviews)
CREATE TABLE resume_reviews (
  review_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  resume_id UUID NOT NULL REFERENCES resumes(resume_id) ON DELETE CASCADE,
  coach_id UUID NOT NULL REFERENCES coaches(coach_id),

  review_status VARCHAR(20) NOT NULL DEFAULT 'in_progress'
    CHECK (review_status IN ('in_progress', 'completed')),
  overall_comment TEXT,

  reviewed_at TIMESTAMP,

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_resume_reviews_resume_id ON resume_reviews(resume_id);
CREATE INDEX idx_resume_reviews_coach_id ON resume_reviews(coach_id);
CREATE INDEX idx_resume_reviews_status ON resume_reviews(review_status);

-- 4.2.16 添削コメントテーブル(review_comments)
CREATE TABLE review_comments (
  comment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  review_id UUID NOT NULL REFERENCES resume_reviews(review_id) ON DELETE CASCADE,

  section_type VARCHAR(50) NOT NULL
    CHECK (section_type IN ('work_experience', 'education', 'certification',
                            'skills', 'self_pr', 'motivation', 'overall')),
  section_id UUID, -- 対象セクションのID(全体コメントの場合はNULL)

  comment_type VARCHAR(20) NOT NULL
    CHECK (comment_type IN ('correction', 'suggestion', 'praise')),
  priority VARCHAR(10) CHECK (priority IN ('high', 'medium', 'low')),

  original_text TEXT,
  suggested_text TEXT,
  comment_text TEXT NOT NULL,

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_review_comments_review_id ON review_comments(review_id);
CREATE INDEX idx_review_comments_section ON review_comments(section_type, section_id);
CREATE INDEX idx_review_comments_type ON review_comments(comment_type);

-- 4.2.17 添削テンプレートテーブル(review_templates)
CREATE TABLE review_templates (
  template_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  coach_id UUID NOT NULL REFERENCES coaches(coach_id) ON DELETE CASCADE,

  template_name VARCHAR(100) NOT NULL,
  section_type VARCHAR(50),
  comment_type VARCHAR(20),
  template_text TEXT NOT NULL,

  usage_count INTEGER DEFAULT 0,

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_review_templates_coach_id ON review_templates(coach_id);
CREATE INDEX idx_review_templates_usage ON review_templates(usage_count DESC);

-- updated_at自動更新用のトリガー関数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 各テーブルにupdated_atトリガーを設定
CREATE TRIGGER update_users_auth_updated_at BEFORE UPDATE ON users_auth
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_coaches_updated_at BEFORE UPDATE ON coaches
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON clients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_applications_updated_at BEFORE UPDATE ON applications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_appointments_updated_at BEFORE UPDATE ON appointments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_company_analysis_updated_at BEFORE UPDATE ON company_analysis
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_resumes_updated_at BEFORE UPDATE ON resumes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_work_experiences_updated_at BEFORE UPDATE ON work_experiences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_education_history_updated_at BEFORE UPDATE ON education_history
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_certifications_updated_at BEFORE UPDATE ON certifications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_skills_updated_at BEFORE UPDATE ON skills
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_resume_reviews_updated_at BEFORE UPDATE ON resume_reviews
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_review_comments_updated_at BEFORE UPDATE ON review_comments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_review_templates_updated_at BEFORE UPDATE ON review_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
