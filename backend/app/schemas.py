from pydantic import BaseModel
from typing import List, Optional

class CreateSessionRequest(BaseModel):
    candidate_name: str

class SessionResponse(BaseModel):
    session_id: str
    candidate_name: str
    status: str
    created_at: str
    analysis_status: str

class UploadVideoRequest(BaseModel):
    session_id: str

class FeedbackData(BaseModel):
    eye_contact_score: int
    posture_score: int
    nervousness_score: int
    expression_score: int
    overall_score: int
    comments: str
    recommendations: List[str]

class FeedbackRequest(BaseModel):
    session_id: str
    feedback: FeedbackData

class AnalysisRequest(BaseModel):
    session_id: str
    questions: List[str]

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    services: dict
