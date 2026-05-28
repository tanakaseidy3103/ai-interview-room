#!/usr/bin/env python3
"""
Script de teste automático para a API AI Interview Room
Testa todos os endpoints principais
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}[OK] {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}[ERRO] {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.YELLOW}[INFO] {text}{Colors.END}")

def test_health():
    """Teste 1: Health Check"""
    print_header("TESTE 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        data = response.json()
        
        if response.status_code == 200:
            print_success(f"Status: {data.get('status')}")
            print(json.dumps(data, indent=2))
            
            s3_status = data['services']['localstack_s3']
            db_status = data['services']['localstack_dynamodb']
            
            if 'healthy' in s3_status and 'healthy' in db_status:
                print_success("Todos os serviços estão HEALTHY")
                return True
            else:
                print_error(f"S3: {s3_status}, DynamoDB: {db_status}")
                return False
        else:
            print_error(f"HTTP {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Erro: {str(e)}")
        return False

def test_create_session():
    """Teste 2: Criar Sessão de Entrevista"""
    print_header("TESTE 2: Criar Sessão de Entrevista")
    try:
        payload = {"candidate_name": "João Silva"}
        response = requests.post(
            f"{BASE_URL}/interview/session/create",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get('session_id')
            print_success(f"Sessão criada com sucesso!")
            print(json.dumps(data, indent=2))
            return session_id
        else:
            print_error(f"HTTP {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print_error(f"Erro: {str(e)}")
        return None

def test_save_feedback(session_id):
    """Teste 3: Salvar Feedback"""
    print_header("TESTE 3: Salvar Feedback")
    if not session_id:
        print_error("Session ID não disponível")
        return False
    
    try:
        payload = {
            "session_id": session_id,
            "feedback": {
                "eye_contact_score": 8,
                "posture_score": 9,
                "nervousness_score": 7,
                "expression_score": 8,
                "overall_score": 8,
                "comments": "Excelente desempenho! Muito engajado.",
                "recommendations": [
                    "Melhorar contato visual",
                    "Relaxar os ombros",
                    "Falar com mais confiança"
                ]
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/interview/feedback/save",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Feedback salvo com sucesso!")
            print(json.dumps(data, indent=2))
            return True
        else:
            print_error(f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"Erro: {str(e)}")
        return False

def test_upload_video(session_id):
    """Teste 4: Upload de Vídeo"""
    print_header("TESTE 4: Upload de Vídeo")
    if not session_id:
        print_error("Session ID não disponível")
        return False
    
    try:
        # Cria um arquivo de teste (arquivo pequeno para teste)
        test_file_path = "/tmp/test_video.mp4"
        with open(test_file_path, 'wb') as f:
            f.write(b'fake video content for testing')
        
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_video.mp4', f, 'video/mp4')}
            response = requests.post(
                f"{BASE_URL}/interview/video/upload?session_id={session_id}",
                files=files
            )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Vídeo enviado com sucesso!")
            print(json.dumps(data, indent=2))
            return True
        else:
            print_error(f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"Erro: {str(e)}")
        return False

def test_get_session(session_id):
    """Teste 5: Recuperar Sessão"""
    print_header("TESTE 5: Recuperar Sessão")
    if not session_id:
        print_error("Session ID não disponível")
        return False
    
    try:
        response = requests.get(
            f"{BASE_URL}/interview/session/{session_id}"
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Sessão recuperada com sucesso!")
            print(json.dumps(data, indent=2))
            return True
        else:
            print_error(f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"Erro: {str(e)}")
        return False

def main():
    print_info(f"Iniciando testes da API em {BASE_URL}")
    print_info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "health": False,
        "create_session": False,
        "save_feedback": False,
        "upload_video": False,
        "get_session": False
    }
    
    # Teste 1: Health
    results["health"] = test_health()
    
    if not results["health"]:
        print_error("\n❌ API não está saudável. Abortar testes.")
        sys.exit(1)
    
    # Teste 2: Criar Sessão
    session_id = test_create_session()
    results["create_session"] = session_id is not None
    
    if not session_id:
        print_error("\n❌ Falha ao criar sessão. Abortar testes.")
        sys.exit(1)
    
    # Teste 3: Feedback
    results["save_feedback"] = test_save_feedback(session_id)
    
    # Teste 4: Upload
    results["upload_video"] = test_upload_video(session_id)
    
    # Teste 5: Get Session
    results["get_session"] = test_get_session(session_id)
    
    # Resumo Final
    print_header("RESUMO DOS TESTES")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, result in results.items():
        status = "[OK] PASSOU" if result else "[ERRO] FALHOU"
        color = Colors.GREEN if result else Colors.RED
        print(f"{color}{test_name.replace('_', ' ').title()}: {status}{Colors.END}")
    
    print(f"\n{Colors.BLUE}Total: {passed}/{total} testes passaram{Colors.END}")
    
    if passed == total:
        print_success("\n=== TODOS OS TESTES PASSARAM! API esta funcionando perfeitamente! ===")
        sys.exit(0)
    else:
        print_error(f"\n=== {total - passed} teste(s) falharam. ===")
        sys.exit(1)

if __name__ == "__main__":
    main()
