# AI Interview Room

AI Interview Room は、面接フローをローカルで再現するバックエンド中心のデモプロジェクトです。FastAPI で API を提供し、Docker Compose で環境を起動し、LocalStack で S3 と DynamoDB をエミュレートします。PostgreSQL もコンテナで用意しており、将来の拡張にも対応しやすい構成です。

## プロジェクトの特徴

- FastAPI + Pydantic による REST API
- Docker Compose で再現可能なローカル環境
- LocalStack による S3 / DynamoDB の AWS 互換検証
- Health Check と Swagger UI を搭載
- 自動テスト用スクリプトで動作確認が可能
- バックエンド、クラウド、DevOps 系のポートフォリオに向いた構成

## 技術スタック

- Backend: Python 3.11+, FastAPI, Uvicorn, Pydantic
- AWS 模擬環境: LocalStack, boto3
- Storage: S3, DynamoDB
- Database: PostgreSQL 15
- Container: Docker, Docker Compose
- Test: requests ベースの smoke test

## すぐに起動する

### 前提条件

- Docker / Docker Compose
- Python 3.11 以上
- OpenAI API Key は任意（モック用途）

### 起動手順

1. `ai-interview-room` ディレクトリを開きます。
2. `docker-compose up -d` でコンテナを起動します。
3. `localstack_init.sh` の内容を実行して、S3 バケットと DynamoDB テーブルを作成します。
4. `http://localhost:8000/docs` で Swagger UI を開きます。
5. `python test_api.py` で smoke test を実行します。

Windows ネイティブ環境では、`test_api.py` が一時ファイルとして Linux の `/tmp` を使うため、そのままだと失敗する場合があります。WSL / Linux ではそのまま動作します。

### そのまま使えるコマンド

```bash
docker-compose up -d
docker-compose logs -f backend
```

## API ドキュメント

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health
- LocalStack Endpoint: http://localhost:4566

## テスト方法

### 1. Health Check

```http
GET http://localhost:8000/health
```

### 2. セッション作成

```http
POST http://localhost:8000/interview/session/create
Content-Type: application/json

{
  "candidate_name": "João Silva"
}
```

### 3. セッション取得

```http
GET http://localhost:8000/interview/session/{session_id}
```

### 4. 動画アップロード

```http
POST http://localhost:8000/interview/video/upload?session_id={session_id}
Content-Type: multipart/form-data

file: [your_video.mp4]
```

### 5. フィードバック保存

```http
POST http://localhost:8000/interview/feedback/save
Content-Type: application/json

{
  "session_id": "{session_id}",
  "feedback": {
    "eye_contact_score": 8.5,
    "posture_score": 7.2,
    "nervousness_score": 6.8,
    "expression_score": 8.1,
    "overall_score": 7.6,
    "comments": "Good overall performance",
    "recommendations": [
      "Improve eye contact",
      "Relax your shoulders"
    ]
  }
}
```

### 6. フィードバック取得

```http
GET http://localhost:8000/interview/feedback/{session_id}
```

### 7. 分析開始

```http
POST http://localhost:8000/interview/analysis
Content-Type: application/json

{
  "session_id": "{session_id}",
  "questions": [
    "Fale sobre sua experiência",
    "Por que você quer trabalhar aqui?"
  ]
}
```

## アーキテクチャ

```text
ai-interview-room/
├── docker-compose.yml      # サービス定義
├── backend/
│   ├── app/
│   │   ├── main.py        # FastAPI アプリ
│   │   ├── config.py      # 設定
│   │   ├── schemas.py     # Pydantic モデル
│   │   ├── routes/
│   │   │   ├── interview.py  # 面接 API
│   │   │   └── health.py     # ヘルスチェック
│   │   └── services/
│   │       └── aws_service.py # S3 + DynamoDB
│   ├── Dockerfile
│   └── requirements.txt
└── frontend/               # 将来追加予定
```

## 各サービス

### LocalStack

- S3: 面接動画の保存
- DynamoDB: セッションとフィードバックの保存
- Lambda: 将来の非同期処理用

### FastAPI Backend

- セッション管理 API
- 動画アップロード API
- フィードバック保存 / 取得 API

### PostgreSQL

- セッション状態の拡張保存
- 履歴管理の基盤

## LocalStack の確認

```bash
docker exec ai-interview-localstack awslocal s3 ls
docker exec ai-interview-localstack awslocal dynamodb list-tables
docker exec ai-interview-localstack awslocal dynamodb scan --table-name interview_sessions
```

## 環境変数

設定例は `.env.local` を参照してください。

## トラブルシューティング

### LocalStack が起動しない

```bash
docker-compose down -v
docker-compose up -d
```

### S3 接続エラー

`http://localstack:4566` を使っているか確認してください。

### DynamoDB 接続エラー

`.env.local` の AWS 認証情報を確認してください。

## 今後の拡張

- OpenAI Whisper による音声認識
- OpenAI Vision による映像解析
- MediaPipe による姿勢推定
- Next.js フロントエンド
- Azure Container Apps へのデプロイ
- Entra ID 認証

## License

MIT
