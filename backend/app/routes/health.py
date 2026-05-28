from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import boto3
from app.config import settings

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    """Health check da API e serviços"""
    services_status = {}
    
    # Verificar LocalStack (S3)
    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=settings.aws_endpoint_url,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )
        s3_client.head_bucket(Bucket=settings.s3_videos_bucket)
        services_status['localstack_s3'] = 'healthy'
    except Exception as e:
        services_status['localstack_s3'] = f'unhealthy: {str(e)}'
    
    # Verificar DynamoDB
    try:
        dynamodb = boto3.client(
            'dynamodb',
            endpoint_url=settings.aws_endpoint_url,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )
        dynamodb.describe_table(TableName=settings.dynamodb_sessions_table)
        services_status['localstack_dynamodb'] = 'healthy'
    except Exception as e:
        services_status['localstack_dynamodb'] = f'unhealthy: {str(e)}'
    
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "services": services_status,
        "api_version": settings.api_version
    }

@router.get("/status")
async def api_status():
    """Status geral da API"""
    return {
        "api": settings.api_title,
        "version": settings.api_version,
        "timestamp": datetime.utcnow().isoformat(),
        "environment": {
            "localstack_endpoint": settings.aws_endpoint_url,
            "s3_bucket": settings.s3_videos_bucket,
            "dynamodb_sessions": settings.dynamodb_sessions_table
        }
    }
