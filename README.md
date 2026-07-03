# 🎥 AI Interview Room (AI面接シミュレーション・評価システム)

AI Interview Room は、エンジニア採用や面接練習を想定した、動画撮影・クラウド保存・AI行動評価のプロセスをローカル環境で再現したフルスタック・デモプロジェクトです。

実務に即したクラウドネイティブな技術構成（FastAPI + PostgreSQL + AWS LocalStack）に加え、ユーザーのWebカメラとマイクを利用して動画をキャプチャ・保存・分析結果をダッシュボード表示するモダンなインタラクティブ・フロントエンドを搭載しています。

---

## 🚀 本プロジェクトで実証しているスキル (Skills Demonstrated)

採用担当者や技術面接官の方に向けて、以下の技術力をアピールできるアーキテクチャで設計されています。

*   **フロントエンド開発**: HTML5 `MediaRecorder` APIによる動画・音声のキャプチャ、`AudioContext`を活用したマイク音声レベルの可視化、CSSカスタム変数を用いたプレミアムなダークモードUI設計。
*   **バックエンド開発**: Python FastAPIによる高性能非同期API構築、Pydanticによる厳密な型定義とバリデーション、CORSミドルウェアの適切な管理。
*   **クラウド・DevOps**: AWS LocalStackを用いたクラウド環境（S3、DynamoDB）のローカルエミュレート、Docker Composeによるマルチコンテナ構成のオーケストレーション。
*   **データベース設計**: PostgreSQLによる将来の履歴拡張データ設計、DynamoDBのハッシュキー設計による高速なキーバリューストア操作。
*   **テスト自動化**: `requests`パッケージを用いたインテグレーション・スモークテストスクリプトの作成。

---

## 🛠️ 技術スタック (Technology Stack)

| カテゴリ | 技術・ツール | 説明 |
| :--- | :--- | :--- |
| **Frontend** | HTML5, CSS3 (Vanilla), JavaScript (ES6+) | `MediaRecorder` / `getUserMedia` / Web Audio API |
| **Backend** | Python 3.11+, FastAPI, Uvicorn, Pydantic | 非同期Webフレームワーク、型安全なAPI定義 |
| **Cloud Emulation** | LocalStack (v2.0.2) | AWS S3（動画保存） / DynamoDB（セッション & 評価） |
| **Database** | PostgreSQL 15 | 永続化データベース |
| **Container / Ops** | Docker, Docker Compose | 開発環境のコンテナコード化（IaCライク） |
| **Testing** | Requests API Test | 自動スモークテスト |

---

## 📐 システムアーキテクチャ (Architecture)

本システムは、Dockerコンテナ上で動作するマイクロサービスと、ローカルで実行される軽量なフロントエンドサーバーで構成されています。

```text
┌────────────────────────────────────────────────────────┐
│                   ブラウザ (Frontend)                  │
│       - http://localhost:3000                          │
│       - カメラ・マイク入力 (MediaRecorder)             │
│       - スコア・フィードバックダッシュボード           │
└──────────────────────────┬─────────────────────────────┘
                           │ APIコール / 動画アップロード
                           ▼
┌────────────────────────────────────────────────────────┐
│                FastAPI Backend (Docker)                │
│       - http://localhost:8000                          │
│       - ルーティング・ビジネスロジック・S3/Dynamo制御    │
└──────────────┬──────────────────────────┬──────────────┘
               │                          │
               ▼ (Boto3 SDK)              ▼ (SQLAlchemy)
┌──────────────────────────────┐  ┌──────────────────────┐
│      LocalStack (Docker)     │  │  PostgreSQL (Docker) │
│   S3: ai-interview-videos    │  │  port: 5432          │
│   DynamoDB: 2 tables         │  │  (将来の拡張用)      │
└──────────────────────────────┘  └──────────────────────┘
```

---

## 📁 プロジェクト構成 (Directory Structure)

```text
ai-interview-room/
├── docker-compose.yml         # 開発環境コンテナ定義
├── test_api.py                # バックエンド自動検証テスト
├── camera_preview.py          # Python OpenCVカメラプレビュー（おまけ）
├── COMO_RODAR.md              # ポルトガル語実行ガイド
├── README.md                  # 本ドキュメント（日本語）
│
├── backend/                   # FastAPI バックエンドコード
│   ├── app/
│   │   ├── main.py            # APIエントリーポイント
│   │   ├── config.py          # 環境変数設定
│   │   ├── schemas.py         # Pydanticデータ定義
│   │   ├── routes/            # 各APIルーティング（面接・ヘルスチェック）
│   │   └── services/          # AWS連携サービスクラス
│   ├── Dockerfile
│   └── requirements.txt
│
└── frontend/                  # インタラクティブ・フロントエンド
    ├── index.html             # UIレイアウト（SPA構成）
    ├── style.css              # Glassmorphism/ダークテーマCSS
    └── app.js                 # カメラ・録画処理、API連携JavaScript
```

---

## 🏃 起動方法 (How to Run)

### 前提条件
*   **Docker** および **Docker Compose** がインストールされ、起動していること。
*   **Python 3.11** 以上がローカル環境にインストールされていること。

### Step 1: Dockerコンテナの起動
プロジェクトのルートディレクトリで以下のコマンドを実行し、バックエンド、データベース、LocalStackコンテナを立ち上げます。
```bash
docker-compose up -d
```

### Step 2: AWSローカルリソースの初期化 (LocalStack)
LocalStack内に必要なS3バケットとDynamoDBテーブルを新規作成します。以下のコマンドを実行してください。
```bash
# S3バケットの作成
docker exec ai-interview-localstack aws --endpoint-url=http://localhost:4566 s3 mb s3://ai-interview-videos

# DynamoDB セッションテーブルの作成
docker exec ai-interview-localstack aws --endpoint-url=http://localhost:4566 dynamodb create-table --table-name interview_sessions --attribute-definitions AttributeName=session_id,AttributeType=S --key-schema AttributeName=session_id,KeyType=HASH --billing-mode PAY_PER_REQUEST --region us-east-1

# DynamoDB フィードバックテーブルの作成
docker exec ai-interview-localstack aws --endpoint-url=http://localhost:4566 dynamodb create-table --table-name interview_feedback --attribute-definitions AttributeName=session_id,AttributeType=S --key-schema AttributeName=session_id,KeyType=HASH --billing-mode PAY_PER_REQUEST --region us-east-1
```

### Step 3: フロントエンドサーバーの起動
ローカルファイルからカメラ・マイクデバイスにアクセスする際のブラウザのセキュリティ制限を回避するため、Pythonに内蔵されている軽量HTTPサーバーを利用してフロントエンドをホスティングします。
```bash
python -m http.server 3000 --directory frontend
```
起動後、ブラウザで **[http://localhost:3000](http://localhost:3000)** にアクセスしてください。

---

## 🧪 テスト・動作確認方法 (Testing)

### 1. 自動テスト (Integration Smoke Test)
バックエンドAPIが正しく起動し、S3やDynamoDBと連携できているかを検証するPythonテストスクリプトです。
```bash
# テストライブラリのインストール
pip install requests

# テストの実行
python test_api.py
```
**テスト通過時のコンソール出力:**
```text
Health: [OK] PASSOU
Create Session: [OK] PASSOU
Save Feedback: [OK] PASSOU
Upload Video: [OK] PASSOU
Get Session: [OK] PASSOU

Total: 5/5 testes passaram
=== TODOS OS TESTES PASSARAM! ===
```

### 2. APIインタラクティブドキュメント (Swagger UI)
FastAPIが自動生成するインタラクティブなAPIドキュメントにアクセスし、直接APIを実行することができます。
*   **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
*   **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
*   **APIヘルスステータス**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 📈 今後の機能拡張ロードマップ
1.  **AIリアルタイム音声認識 (STT)**: OpenAI Whisper API を用いて、撮影された面接動画の音声からテキストを文字起こしする機能。
2.  **Visionによる表情・ジェスチャー解析**: MediaPipeまたはOpenCVを利用し、面接中の顔の表情（笑顔、緊張）や姿勢をグラフ解析する機能。
3.  **LLM面接官フィードバック**: ChatGPT / Gemini APIを活用し、回答の「内容の的確さ」や「アピール度」についてプロフェッショナルなFBテキストを自動生成する機能。
4.  **クラウドデプロイ**: AWS ECS (Fargate), S3, DynamoDB を用い、TerraformなどのIaCツールを利用してAWS本番環境へデプロイ。

---

## 📝 ライセンス
本プロジェクトは **MIT License** のもとで公開されています。
