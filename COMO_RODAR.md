# 🚀 Como Rodar o AI Interview Room

## ⚡ Resumo Rápido (5 passos)

```bash
# 1. Navegar ao diretório
cd "c:\Users\eduardo\OneDrive - nkz.ac.jp\デスクトップ\camera real aws\ai-interview-room"

# 2. Subir containers
docker-compose up -d

# 3. Inicializar LocalStack (copie e cole tudo de uma vez)
docker exec ai-interview-localstack aws --endpoint-url=http://localhost:4566 s3 mb s3://ai-interview-videos && docker exec ai-interview-localstack aws --endpoint-url=http://localhost:4566 dynamodb create-table --table-name interview_sessions --attribute-definitions AttributeName=session_id,AttributeType=S --key-schema AttributeName=session_id,KeyType=HASH --billing-mode PAY_PER_REQUEST --region us-east-1 && docker exec ai-interview-localstack aws --endpoint-url=http://localhost:4566 dynamodb create-table --table-name interview_feedback --attribute-definitions AttributeName=session_id,AttributeType=S --key-schema AttributeName=session_id,KeyType=HASH --billing-mode PAY_PER_REQUEST --region us-east-1

# 4. Testar (escolha uma opção)
python test_api.py          # Automático (RECOMENDADO!)
# OU
curl http://localhost:8000/health  # Health check simples

# 5. Ver documentação interativa
# Abra no navegador: http://localhost:8000/docs
```

---

## 📍 Passo a Passo Detalhado

### 1️⃣ Iniciar os Containers
```bash
cd "c:\Users\eduardo\OneDrive - nkz.ac.jp\デスクトップ\camera real aws\ai-interview-room"
docker-compose up -d
```

**O que sobe:**
- ✓ FastAPI Backend (porta 8000)
- ✓ PostgreSQL (porta 5432)
- ✓ LocalStack - AWS emulado (porta 4566)

**Verificar status:**
```bash
docker-compose ps
```

Deve mostrar 3 containers: backend, postgres, localstack (todos "Up")

### 2️⃣ Inicializar LocalStack

**Criar bucket S3:**
```bash
docker exec ai-interview-localstack aws --endpoint-url=http://localhost:4566 s3 mb s3://ai-interview-videos
```

**Criar tabela DynamoDB - Sessões:**
```bash
docker exec ai-interview-localstack aws --endpoint-url=http://localhost:4566 dynamodb create-table \
  --table-name interview_sessions \
  --attribute-definitions AttributeName=session_id,AttributeType=S \
  --key-schema AttributeName=session_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

**Criar tabela DynamoDB - Feedback:**
```bash
docker exec ai-interview-localstack aws --endpoint-url=http://localhost:4566 dynamodb create-table \
  --table-name interview_feedback \
  --attribute-definitions AttributeName=session_id,AttributeType=S \
  --key-schema AttributeName=session_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

### 3️⃣ Testar a API

#### Opção A: Script Python Automático (RECOMENDADO!)
```bash
python test_api.py
```

**Resultado esperado:**
```
Health: [OK] PASSOU
Create Session: [OK] PASSOU
Save Feedback: [OK] PASSOU
Upload Video: [OK] PASSOU
Get Session: [OK] PASSOU

Total: 5/5 testes passaram
=== TODOS OS TESTES PASSARAM! ===
```

#### Opção B: Postman (Visual)
1. Abra Postman
2. Import → `AI_Interview_Room.postman_collection.json`
3. Clique em cada endpoint e **Send**

#### Opção C: cURL (Terminal)
```bash
# Verificar health
curl http://localhost:8000/health

# Criar sessão
curl -X POST http://localhost:8000/interview/session/create \
  -H "Content-Type: application/json" \
  -d '{"candidate_name":"João Silva"}'
```

#### Opção D: Documentação Interativa
- Abra no navegador: **http://localhost:8000/docs** (Swagger UI)
- Ou: **http://localhost:8000/redoc** (ReDoc)

---

## 🎯 O que Você Consegue Fazer

### ✓ Criar uma Sessão de Entrevista
```bash
POST /interview/session/create
Body: { "candidate_name": "João Silva" }
Retorna: session_id (guarde isso!)
```

### ✓ Fazer Upload de Vídeo
```bash
POST /interview/video/upload?session_id=seu_id_aqui
Arquivo: seu_video.mp4
Salva em: S3 LocalStack
```

### ✓ Salvar Feedback/Scores
```bash
POST /interview/feedback/save
Body: {
  "session_id": "seu_id",
  "feedback": {
    "eye_contact_score": 8,
    "posture_score": 9,
    "nervousness_score": 7,
    "expression_score": 8,
    "overall_score": 8,
    "comments": "Ótimo!",
    "recommendations": ["Melhorar X"]
  }
}
```

### ✓ Recuperar Dados da Sessão
```bash
GET /interview/session/{session_id}
Retorna: Todos os dados salvos
```

### ✓ Ver Health dos Serviços
```bash
GET /health
Retorna: Status de S3 e DynamoDB
```

---

## 🔧 Comandos Úteis

```bash
# Ver logs em tempo real
docker-compose logs -f backend

# Reiniciar apenas o backend
docker-compose restart backend

# Desligar tudo
docker-compose down

# Remover tudo (containers + volumes)
docker-compose down -v

# Ver arquivos enviados para S3
docker exec ai-interview-localstack aws --endpoint-url=http://localhost:4566 s3 ls s3://ai-interview-videos --recursive

# Ver dados no DynamoDB
docker exec ai-interview-localstack aws --endpoint-url=http://localhost:4566 dynamodb scan --table-name interview_sessions --region us-east-1

# Acessar shell do container
docker exec -it ai-interview-backend bash

# Ver requisições da API em tempo real
docker-compose logs -f backend | grep -i request
```

---

## 🐛 Troubleshooting

### ❌ "Connection refused"
- **Causa:** Containers não inicializaram
- **Solução:** Espere 30 segundos e tente `curl http://localhost:8000/health`

### ❌ "Port 8000 already in use"
- **Causa:** Outra aplicação usa porta 8000
- **Solução:** Edite `docker-compose.yml` → mude `8001:8000`

### ❌ "DynamoDB table doesn't exist"
- **Causa:** Não rodou a inicialização
- **Solução:** Execute os comandos da seção 2️⃣

### ❌ Script Python não roda
- **Causa:** Falta `requests` library
- **Solução:** `pip install requests`

### ❌ PowerShell encoding error
- **Causa:** Caracteres unicode
- **Solução:** Já está corrigido no código atual

---

## 📊 Arquitetura

```
┌─────────────────────────────────────────┐
│         🎥 AI Interview Room            │
├─────────────────────────────────────────┤
│                                         │
│  FastAPI Backend (Python 3.11)          │
│  - Routes: /interview/*, /health        │
│  - Port: 8000                           │
│                                         │
│  ┌───────────────┐  ┌────────────────┐  │
│  │  PostgreSQL   │  │   LocalStack   │  │
│  │  Port: 5432   │  │   Port: 4566   │  │
│  │  (DB)         │  │   S3+DynamoDB  │  │
│  └───────────────┘  └────────────────┘  │
│       (conectado)         (conectado)   │
│                                         │
└─────────────────────────────────────────┘
        ↓ todos em containers Docker
```

---

## ✅ Checklist Final

- [ ] Docker Desktop está aberto
- [ ] Rodei `docker-compose up -d`
- [ ] Criei bucket S3
- [ ] Criei tabelas DynamoDB
- [ ] Rodei `python test_api.py` com sucesso
- [ ] Todos os 5 testes passaram
- [ ] Acessei http://localhost:8000/docs

**Se tudo está ✓, você está pronto para usar a API!**

---

**Criado:** Maio 2026  
**Status:** ✅ MVP Funcional - Todos os testes passando!
