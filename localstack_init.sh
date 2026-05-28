#!/bin/bash

# Criar bucket S3
awslocal s3 mb s3://ai-interview-videos --region us-east-1
awslocal s3 mb s3://ai-interview-feedback --region us-east-1

# Criar tabela DynamoDB para sessões de entrevista
awslocal dynamodb create-table \
  --table-name interview_sessions \
  --attribute-definitions \
    AttributeName=session_id,AttributeType=S \
  --key-schema \
    AttributeName=session_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

# Criar tabela DynamoDB para feedback
awslocal dynamodb create-table \
  --table-name interview_feedback \
  --attribute-definitions \
    AttributeName=session_id,AttributeType=S \
  --key-schema \
    AttributeName=session_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

echo "LocalStack initialized successfully!"
