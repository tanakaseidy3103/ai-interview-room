#!/usr/bin/env python3
"""
AI Interview Room API 自動統合テストスクリプト
すべての主要エンドポイントの動作確認を行います。
"""

import requests
import json
import sys
import os
import tempfile
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
    print(f"{Colors.RED}[エラー] {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.YELLOW}[情報] {text}{Colors.END}")

def test_health():
    """テスト 1: ヘルスチェック"""
    print_header("テスト 1: ヘルスチェック (Health Check)")
    try:
        response = requests.get(f"{BASE_URL}/health")
        data = response.json()
        
        if response.status_code == 200:
            print_success(f"ステータス: {data.get('status')}")
            print(json.dumps(data, indent=2))
            
            s3_status = data['services']['localstack_s3']
            db_status = data['services']['localstack_dynamodb']
            
            if 'healthy' in s3_status and 'healthy' in db_status:
                print_success("すべてのサービスが正常に稼働しています (HEALTHY)")
                return True
            else:
                print_error(f"S3: {s3_status}, DynamoDB: {db_status}")
                return False
        else:
            print_error(f"HTTPステータスコード: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"接続エラー: {str(e)}")
        return False

def test_create_session():
    """テスト 2: 面接セッションの作成"""
    print_header("テスト 2: 面接セッションの作成")
    try:
        payload = {"candidate_name": "山田 太郎"}
        response = requests.post(
            f"{BASE_URL}/interview/session/create",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get('session_id')
            print_success(f"面接セッションが正常に作成されました！")
            print(json.dumps(data, indent=2))
            return session_id
        else:
            print_error(f"HTTPステータスコード {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print_error(f"接続エラー: {str(e)}")
        return None

def test_save_feedback(session_id):
    """テスト 3: フィードバックの保存"""
    print_header("テスト 3: フィードバックの保存")
    if not session_id:
        print_error("セッションIDが取得できませんでした")
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
                "comments": "素晴らしい回答でした。非常に論理的です。",
                "recommendations": [
                    "アイコンタクトをさらに改善する",
                    "肩の力を抜きリラックスした姿勢をとる",
                    "より自信を持ってハッキリと話す"
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
            print_success(f"フィードバックが正常に保存されました！")
            print(json.dumps(data, indent=2))
            return True
        else:
            print_error(f"HTTPステータスコード {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"接続エラー: {str(e)}")
        return False

def test_upload_video(session_id):
    """テスト 4: 動画のアップロード"""
    print_header("テスト 4: 動画のアップロード")
    if not session_id:
        print_error("セッションIDが取得できませんでした")
        return False
    
    test_file_path = None
    try:
        # OS依存しない一時ファイルパスの作成
        temp_dir = tempfile.gettempdir()
        test_file_path = os.path.join(temp_dir, "test_video.mp4")
        
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
            print_success(f"動画が正常にアップロードされました！")
            print(json.dumps(data, indent=2))
            return True
        else:
            print_error(f"HTTPステータスコード {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"接続エラー: {str(e)}")
        return False
    finally:
        # 一時ファイルの削除
        if test_file_path and os.path.exists(test_file_path):
            try:
                os.remove(test_file_path)
            except OSError:
                pass

def test_get_session(session_id):
    """テスト 5: セッション情報の取得"""
    print_header("テスト 5: セッション情報の取得")
    if not session_id:
        print_error("セッションIDが取得できませんでした")
        return False
    
    try:
        response = requests.get(
            f"{BASE_URL}/interview/session/{session_id}"
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"セッション情報が正常に取得されました！")
            print(json.dumps(data, indent=2))
            return True
        else:
            print_error(f"HTTPステータスコード {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"接続エラー: {str(e)}")
        return False

def main():
    print_info(f"APIテストを開始します: {BASE_URL}")
    print_info(f"テスト実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "health": False,
        "create_session": False,
        "save_feedback": False,
        "upload_video": False,
        "get_session": False
    }
    
    # テスト 1: Health
    results["health"] = test_health()
    
    if not results["health"]:
        print_error("\n❌ APIが正常に稼働していません。テストを中断します。")
        sys.exit(1)
    
    # テスト 2: セッション作成
    session_id = test_create_session()
    results["create_session"] = session_id is not None
    
    if not session_id:
        print_error("\n❌ セッションの作成に失敗したため、テストを中断します。")
        sys.exit(1)
    
    # テスト 3: フィードバック保存
    results["save_feedback"] = test_save_feedback(session_id)
    
    # テスト 4: 動画アップロード
    results["upload_video"] = test_upload_video(session_id)
    
    # テスト 5: セッション情報取得
    results["get_session"] = test_get_session(session_id)
    
    # 最終リザルト表示
    print_header("テスト結果サマリー")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, result in results.items():
        status = "[OK] 合格" if result else "[エラー] 不合格"
        color = Colors.GREEN if result else Colors.RED
        print(f"{color}{test_name.replace('_', ' ').title()}: {status}{Colors.END}")
    
    print(f"\n{Colors.BLUE}合計: {passed}/{total} 件のテストに合格しました{Colors.END}")
    
    if passed == total:
        print_success("\n=== すべてのテストに合格しました！APIは完全に正常動作しています！ ===")
        sys.exit(0)
    else:
        print_error(f"\n=== {total - passed} 件のテストが失敗しました。 ===")
        sys.exit(1)

if __name__ == "__main__":
    main()
