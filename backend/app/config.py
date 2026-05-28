import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # AWS/LocalStack
    aws_endpoint_url: str = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "test")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "test")
    aws_region: str = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    
    # S3 Buckets
    s3_videos_bucket: str = "ai-interview-videos"
    s3_feedback_bucket: str = "ai-interview-feedback"
    
    # DynamoDB Tables
    dynamodb_sessions_table: str = "interview_sessions"
    dynamodb_feedback_table: str = "interview_feedback"
    
    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "sk-test")
    
    # API
    api_title: str = "AI Interview Room API"
    api_version: str = "1.0.0"
    debug: bool = True
    
    class Config:
        env_file = ".env.local"
        case_sensitive = False

settings = Settings()
