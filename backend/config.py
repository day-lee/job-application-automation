"""
환경 설정 및 공통 상수 관리
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

# .env 파일 로드
load_dotenv(ENV_PATH)

# Google Sheets 설정
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "./credentials.json")

# 데이터 디렉토리
DATA_DIR = PROJECT_ROOT / "data"
RAWDATA_DIR = DATA_DIR / "rawdata"
PROCESSED_IDS_FILE = DATA_DIR / "processed_ids.json"

# 디렉토리 생성 (없는 경우)
DATA_DIR.mkdir(exist_ok=True)
RAWDATA_DIR.mkdir(exist_ok=True)

# FastAPI 서버 설정
API_HOST = "0.0.0.0"
API_PORT = 8888

# Google Sheets 워크시트 이름
SHEET_NAME = "Jobs"

# 필터링 규칙 상수
MAX_SALARY_FILTER = 60000  # £60K 이상 제외
MIN_EXPERIENCE_FILTER = 3  # 3년 이상 경력 요구 시 제외

# 기술 스택 키워드
TECH_STACK_KEYWORDS = {
    "JS": ["javascript", "typescript", "js", "ts"],
    "Python": ["python", "django", "flask", "fastapi"],
    "DB": ["sql", "mysql", "postgresql", "postgres", "mongodb", "nosql"],
    "React": ["react", "react.js", "reactjs", "next.js", "nextjs"],
    "Node": ["node.js", "nodejs", "express"],
    "Unwanted": ["c++", "c#", "kafka", "salesforce", "wordpress", "php", "java", "spring", "ruby", "laravel", 'llm', "contract", "adobe", "flutter", "swift", "kotlin", "machine learning", "yaml", "qa", "quality assurance", "cloud"],
}

# 보안 인가 키워드
CLEARANCE_KEYWORDS = ["sc clearance", "security clearance", "dv clearance", "open to uk nationals only", "bpss", "security check"]

LEVEL_EXCLUDE_KEYWORDS = ["staff", "lead", "principal", "senior", "iii", "sr.", "manager", "director", "vp", "c-level", "chief"]

print(f"✅ Config loaded from {ENV_PATH}")
print(f"Google Sheet ID: {GOOGLE_SHEET_ID}")
print(f"Credentials: {GOOGLE_CREDENTIALS_PATH}")


# ============================================================================
# processed_ids.json 관리 함수
# ============================================================================

def load_processed_ids() -> set:
    """
    처리된 job ID set 로드
    파일이 없으면 빈 set 반환
    """
    try:
        if PROCESSED_IDS_FILE.exists():
            with open(PROCESSED_IDS_FILE, 'r', encoding='utf-8') as f:
                ids_list = json.load(f)
                return set(ids_list) if isinstance(ids_list, list) else set()
        return set()
    except Exception as e:
        print(f"⚠️ processed_ids.json 로드 실패: {e}, 빈 set으로 시작")
        return set()


def save_processed_ids(ids_set: set) -> bool:
    """
    처리된 job ID set 저장
    """
    try:
        ids_list = sorted(list(ids_set))
        with open(PROCESSED_IDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(ids_list, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ processed_ids.json 저장 실패: {e}")
        return False


def add_processed_ids(new_ids: list[str]) -> bool:
    """
    처리된 job ID 추가 저장
    """
    try:
        processed = load_processed_ids()
        processed.update(new_ids)
        return save_processed_ids(processed)
    except Exception as e:
        print(f"❌ ID 추가 저장 실패: {e}")
        return False
