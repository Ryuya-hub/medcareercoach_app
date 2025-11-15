from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import auth, clients, applications, appointments, resumes, coaches, admin

app = FastAPI(
    title="転職支援顧客管理システム API",
    description="転職支援会社向けの顧客管理WEBアプリケーション",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターの登録
app.include_router(auth.router)
app.include_router(admin.router)  # 統括管理者用API
app.include_router(coaches.router)
app.include_router(clients.router)
app.include_router(applications.router)
app.include_router(appointments.router)
app.include_router(resumes.router)


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "転職支援顧客管理システム API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
