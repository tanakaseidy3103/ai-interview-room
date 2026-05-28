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
    """Criar nova sessão de entrevista"""
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
    """Buscar dados da sessão"""
    try:
        session_data = await dynamodb_service.get_session(session_id)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sessão não encontrada"
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
    """Upload de vídeo para a sessão"""
    try:
        # Validar sessão
        session_data = await dynamodb_service.get_session(session_id)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sessão não encontrada"
            )
        
        # Ler conteúdo do arquivo
        content = await file.read()
        
        # Gerar chave do arquivo
        file_key = f"{session_id}/{file.filename}"
        
        # Upload para S3
        s3_url = await s3_service.upload_video(file_key, content)
        
        # Atualizar sessão com referência do vídeo
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
            "message": "Vídeo enviado com sucesso"
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
    """Salvar feedback e score da entrevista"""
    try:
        # Validar sessão
        session_data = await dynamodb_service.get_session(request.session_id)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sessão não encontrada"
            )
        
        # Salvar feedback
        feedback_data = await dynamodb_service.save_feedback(
            session_id=request.session_id,
            feedback=request.feedback.model_dump()
        )
        
        # Atualizar status da sessão
        await dynamodb_service.update_session(
            session_id=request.session_id,
            analysis_status='completed'
        )
        
        return {
            "status": "success",
            "session_id": request.session_id,
            "feedback": feedback_data,
            "message": "Feedback salvo com sucesso"
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
    """Buscar feedback da entrevista"""
    try:
        feedback_data = await dynamodb_service.get_feedback(session_id)
        if not feedback_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback não encontrado"
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
    """Iniciar análise da entrevista (mock para agora)"""
    try:
        session_data = await dynamodb_service.get_session(request.session_id)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sessão não encontrada"
            )
        
        return {
            "status": "analysis_started",
            "session_id": request.session_id,
            "questions": request.questions,
            "message": "Análise iniciada. Isso é um mock - em produção seria feita pela IA"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
