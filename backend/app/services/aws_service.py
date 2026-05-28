import boto3
import json
from datetime import datetime
from app.config import settings

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.aws_endpoint_url,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )

    async def upload_video(self, file_key: str, file_content: bytes) -> str:
        """Upload vídeo para S3 local"""
        try:
            self.s3_client.put_object(
                Bucket=settings.s3_videos_bucket,
                Key=file_key,
                Body=file_content,
                ContentType='video/mp4'
            )
            return f"s3://{settings.s3_videos_bucket}/{file_key}"
        except Exception as e:
            raise Exception(f"Erro ao upload S3: {str(e)}")

    async def get_video_url(self, file_key: str) -> str:
        """Gera URL local para acessar o vídeo"""
        return f"{settings.aws_endpoint_url}/{settings.s3_videos_bucket}/{file_key}"

class DynamoDBService:
    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb',
            endpoint_url=settings.aws_endpoint_url,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )

    async def create_session(self, session_id: str, candidate_name: str) -> dict:
        """Cria uma nova sessão de entrevista"""
        try:
            table = self.dynamodb.Table(settings.dynamodb_sessions_table)
            session_data = {
                'session_id': session_id,
                'candidate_name': candidate_name,
                'created_at': datetime.utcnow().isoformat(),
                'status': 'active',
                'video_key': None,
                'analysis_status': 'pending'
            }
            table.put_item(Item=session_data)
            return session_data
        except Exception as e:
            raise Exception(f"Erro ao criar sessão: {str(e)}")

    async def update_session(self, session_id: str, **kwargs) -> dict:
        """Atualiza sessão de entrevista"""
        try:
            table = self.dynamodb.Table(settings.dynamodb_sessions_table)
            update_expr = "SET " + ", ".join([f"{k}=:{k}" for k in kwargs.keys()])
            expr_values = {f":{k}": v for k, v in kwargs.items()}
            
            response = table.update_item(
                Key={'session_id': session_id},
                UpdateExpression=update_expr,
                ExpressionAttributeValues=expr_values,
                ReturnValues='ALL_NEW'
            )
            return response['Attributes']
        except Exception as e:
            raise Exception(f"Erro ao atualizar sessão: {str(e)}")

    async def get_session(self, session_id: str) -> dict:
        """Busca sessão por ID"""
        try:
            table = self.dynamodb.Table(settings.dynamodb_sessions_table)
            response = table.get_item(Key={'session_id': session_id})
            return response.get('Item', {})
        except Exception as e:
            raise Exception(f"Erro ao buscar sessão: {str(e)}")

    async def save_feedback(self, session_id: str, feedback: dict) -> dict:
        """Salva feedback da entrevista"""
        try:
            table = self.dynamodb.Table(settings.dynamodb_feedback_table)
            feedback_data = {
                'session_id': session_id,
                'timestamp': datetime.utcnow().isoformat(),
                'eye_contact_score': feedback.get('eye_contact_score', 0),
                'posture_score': feedback.get('posture_score', 0),
                'nervousness_score': feedback.get('nervousness_score', 0),
                'expression_score': feedback.get('expression_score', 0),
                'overall_score': feedback.get('overall_score', 0),
                'comments': feedback.get('comments', ''),
                'recommendations': feedback.get('recommendations', [])
            }
            table.put_item(Item=feedback_data)
            return feedback_data
        except Exception as e:
            raise Exception(f"Erro ao salvar feedback: {str(e)}")

    async def get_feedback(self, session_id: str) -> dict:
        """Busca feedback por session_id"""
        try:
            table = self.dynamodb.Table(settings.dynamodb_feedback_table)
            response = table.get_item(Key={'session_id': session_id})
            return response.get('Item', {})
        except Exception as e:
            raise Exception(f"Erro ao buscar feedback: {str(e)}")
