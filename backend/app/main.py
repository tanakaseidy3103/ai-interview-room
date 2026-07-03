from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from app.config import settings
from app.routes import interview, health

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPIアプリケーション初期化
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="LocalStackを使用したAI Interview Room用APIバックエンド"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーティング設定
app.include_router(health.router)
app.include_router(interview.router)

@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "🎥 AI Interview Room - Backend",
        "version": settings.api_version,
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """グローバル例外ハンドラー"""
    logger.error(f"エラー発生: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
