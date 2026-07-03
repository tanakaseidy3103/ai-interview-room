from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
import uuid
from app.services.aws_service import S3Service, DynamoDBService
from app.schemas import (
    CreateSessionRequest, 
    SessionResponse, 
    UploadVideoRequest,
    FeedbackRequest,
    AnalysisRequest
)

router = APIRouter(prefix="/interview", tags=["interview"])
s3_service = S3Service()
dynamodb_service = DynamoDBService()

@router.post("/session/create", response_model=SessionResponse)
async def create_session(request: CreateSessionRequest):
    """新規面接セッションの作成"""
    try:
        session_id = str(uuid.uuid4())
        session_data = await dynamodb_service.create_session(
            session_id=session_id,
            candidate_name=request.candidate_name
        )
        return SessionResponse(**session_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """セッション情報の取得"""
    try:
        session_data = await dynamodb_service.get_session(session_id)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="セッションが見つかりません"
            )
        return session_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/video/upload")
async def upload_video(session_id: str, file: UploadFile = File(...)):
    """面接回答動画のアップロード"""
    try:
        # セッションの有効性検証
        session_data = await dynamodb_service.get_session(session_id)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="セッションが見つかりません"
            )
        
        # ファイルコンテンツの読み込み
        content = await file.read()
        
        # S3オブジェクトキーの生成
        file_key = f"{session_id}/{file.filename}"
        
        # S3へのアップロード
        s3_url = await s3_service.upload_video(file_key, content)
        
        # セッション情報を更新（動画キーの設定と分析ステータスの更新）
        await dynamodb_service.update_session(
            session_id=session_id,
            video_key=file_key,
            analysis_status='processing'
        )
        
        return {
            "status": "success",
            "session_id": session_id,
            "s3_url": s3_url,
            "file_key": file_key,
            "message": "動画のアップロードが完了しました"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/feedback/save")
async def save_feedback(request: FeedbackRequest):
    """面接評価・フィードバックの保存"""
    try:
        # セッションの有効性検証
        session_data = await dynamodb_service.get_session(request.session_id)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="セッションが見つかりません"
            )
        
        # フィードバックデータの保存
        feedback_data = await dynamodb_service.save_feedback(
            session_id=request.session_id,
            feedback=request.feedback.model_dump()
        )
        
        # セッションステータスの更新
        await dynamodb_service.update_session(
            session_id=request.session_id,
            analysis_status='completed'
        )
        
        return {
            "status": "success",
            "session_id": request.session_id,
            "feedback": feedback_data,
            "message": "フィードバックが正常に保存されました"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/feedback/{session_id}")
async def get_feedback(session_id: str):
    """面接フィードバック情報の取得"""
    try:
        feedback_data = await dynamodb_service.get_feedback(session_id)
        if not feedback_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="フィードバックデータが見つかりません"
            )
        return feedback_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/analysis")
async def start_analysis(request: AnalysisRequest):
    """面接分析プロセスの開始（現在はモック動作）"""
    try:
        session_data = await dynamodb_service.get_session(request.session_id)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="セッションが見つかりません"
            )
        
        return {
            "status": "analysis_started",
            "session_id": request.session_id,
            "questions": request.questions,
            "message": "分析が開始されました。この処理はモックです。本番環境ではAIモデルによる自動分析が実行されます。"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
