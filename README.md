# LinkedIn Job Filter - 자동화 도구

LinkedIn 채용공고를 필터링하여 Google Sheets에 자동으로 기록하는 웹 애플리케이션입니다.

## 📋 프로젝트 개요

- **목적**: LinkedIn 잡 서치를 필터링해서 부분 자동화
  - LinkedIn에서 job을 scrape한 JSON 파일을 업로드
  - 버튼을 눌러 필터링 실행
  - Google Spreadsheet에 연동하여 자동 기록

- **기술 스택**:
  - **프론트엔드**: Vite + React (JS), localhost:5178
  - **백엔드**: FastAPI (Python), localhost:8888
  - **데이터 저장소**: Google Sheets API

## 🚀 Phase 1: 프로젝트 세팅 + 구글 시트 연동 확인 ✅

✅ 완료됨



## 🚀 Phase 2: 파일 업로드 기능 ✅

### 기능

- **POST /upload**: JSON 파일 업로드
  - multipart/form-data로 JSON 파일 수신
  - `upload_YYYYMMDD_HHMMSS.json` 형태로 `rawdata/` 폴더에 저장
  - 업로드된 job 개수 반환
  - processed_ids.json 로드 (중복 체크용)

### 설치

1. **Python 의존성 설치**:
```bash
pip install -r requirements.txt
```

2. **필수 파일 확인**:
   - `.env`: Google Sheet ID와 credentials 경로 (이미 설정됨)
   - `credentials.json`: Google Service Account JSON 키 파일 (이미 설정됨)

### 실행

#### 1단계: 백엔드 서버 시작 ✅
```bash
cd backend
python main.py
```

**예상 출력**:
```
╔════════════════════════════════════════════╗
║  📋 LinkedIn Job Filter API               ║
║  🚀 Server starting...                     ║
╚════════════════════════════════════════════╝

INFO:     Uvicorn running on http://0.0.0.0:8888
```

#### 2단계: JSON 파일 업로드 테스트 ✅

**터미널에서 (curl)**:
```bash
curl -X POST -F "file=@test_jobs.json" http://localhost:8888/upload
```

**또는 Python에서**:
```python
import requests

with open('test_jobs.json', 'rb') as f:
    files = {'file': f}
    response = requests.post("http://localhost:8888/upload", files=files)
    print(response.json())
```

**성공 응답 (200)**:
```json
{
  "success": true,
  "filename": "upload_20260410_225928.json",
  "jobCount": 3
}
```

**에러 응답 (400)**:
```json
{
  "detail": {
    "error": "Invalid JSON format"
  }
}
```

#### 3단계: 파일 저장 확인 ✅

업로드된 파일이 저장되었는지 확인:
```bash
ls -lh data/rawdata/
# 예상 결과: upload_20260410_225928.json
```

#### 4단계: 중복 체크 파일 확인 ✅

처리된 ID 파일:
```bash
cat data/processed_ids.json
# 예상 결과: [] (필터링 후 ID가 기록됨)
```

### 테스트 케이스

| 케이스 | 입력 | 예상 결과 |
|-------|------|---------|
| ✅ 정상 | 유효한 JSON 배열 | 200: 파일 저장, jobCount 반환 |
| ✅ 형식 오류 | .txt, .pdf 등 | 400: "Invalid file format" |
| ✅ 파싱 오류 | 잘못된 JSON 문법 | 400: "Invalid JSON format" |
| ✅ 배열 아님 | {"job": "test"} | 400: "Invalid JSON format" |
| ✅ 빈 배열 | [] | 400: "빈 JSON 배열은 업로드할 수 없습니다" |

## 📁 프로젝트 구조

```
linkedin-job-filter/
├── .env                          # 환경변수 설정
├── .gitignore                    # Git 제외 목록
├── credentials.json              # Google Service Account 키
├── requirements.txt              # Python 의존성
├── test_jobs.json                # 테스트용 샘플 데이터
└── README.md                     # 이 파일

backend/
├── main.py                       # FastAPI 앱 (포트 8888)
├── config.py                     # 환경 설정 로드 + processed_ids 관리 ✅
├── sheets.py                     # Google Sheets API 연동 ✅
├── filter.py                     # 필터링 로직 (Phase 3)
├── parser.py                     # 데이터 변환 (Phase 3)
└── data/
    ├── rawdata/                  # 업로드 파일 보관 ✅
    └── processed_ids.json        # 처리된 ID 추적 (Phase 2) ✅

frontend/
├── index.html
├── package.json
├── vite.config.js
└── src/
```


    ├── rawdata/                  # 업로드 파일 보관
    └── processed_ids.json        # 처리된 job ID 추적

frontend/
├── index.html
├── package.json
├── vite.config.js
└── src/
    ├── App.jsx
    ├── main.jsx
    ├── api.js                    # API 통신 (Phase 2)
    ├── components/
    │   ├── FileUpload.jsx        # 파일 업로드 UI (Phase 2)
    │   ├── FilterButton.jsx      # 필터링 버튼 (Phase 2)
    │   └── ResultPanel.jsx       # 결과 표시 (Phase 2)
    └── styles/
        └── App.css
```

## 🔧 API 엔드포인트

### Phase 1 ✅

#### `GET /health`
서버 헬스 체크
```bash
curl http://localhost:8888/health
```

#### `POST /test-sheet`
Google Sheets 연동 테스트 (테스트 행 1개 추가)
```bash
curl -X POST http://localhost:8888/test-sheet
```

### Phase 2 ✅

#### `POST /upload`
JSON 파일 업로드 (multipart/form-data)

**요청**:
```bash
curl -X POST -F "file=@jobs.json" http://localhost:8888/upload
```

**응답 200**:
```json
{
  "success": true,
  "filename": "upload_20260410_225928.json",
  "jobCount": 150
}
```

**에러 응답 400**:
```json
{
  "detail": {
    "error": "Invalid JSON format"
  }
}
```

### Phase 3 (구현 예정)

#### `POST /filter`
필터링 실행 및 Google Sheets에 append

**요청**: body 없음

**응답 200**:
```json
{
  "total": 150,
  "duplicatesRemoved": 12,
  "filtered": 138,
  "passed": 23,
  "savedToSheet": 23,
  "rejected": {
    "salary": 15,
    "experience": 35,
    "clearance": 8,
    "education": 3,
    "level": 54
  },
  "sheetUrl": "https://docs.google.com/spreadsheets/d/SHEET_ID"
}
```

**에러 응답 400, 500**:
```json
{"error": "No uploaded file found" | "Google Sheets API failed"}
```

#### `POST /test-sheet` ✅
Google Sheets 연동 테스트 (테스트 행 1개 추가)
```bash
curl -X POST http://localhost:8888/test-sheet
```

### Phase 2 (구현 예정)

#### `POST /upload`
JSON 파일 업로드
```
요청: multipart/form-data (JSON 파일)
응답: { "filename": "upload_YYYYMMDD_HHMMSS.json", "jobCount": 150 }
```

#### `POST /filter`
최근 파일 필터링 및 시트 업로드
```
요청: body 없음
응답: { "total": 150, "passed": 23, "rejected": {...}, "sheetUrl": "..." }
```

## ⚙️ 환경변수 (.env)

```env
GOOGLE_SHEET_ID=1NYSkgirlc6gsrB5rvVt1K1YZzPoDaHL62xUn_g7azbM
GOOGLE_CREDENTIALS_PATH=./credentials.json
```

## 🔐 Google Sheets 인증

### 필요한 설정:

1. **Service Account 생성**: Google Cloud Console
2. **JSON 키 다운로드**: `credentials.json`으로 저장
3. **시트에 공유**: credentials.json의 이메일로 시트 공유
4. **필요한 스코프**:
   - `https://www.googleapis.com/auth/spreadsheets`
   - `https://www.googleapis.com/auth/drive`

## 📊 구글 시트 구조 (예상)

| Applied at | Interview date | Memo | Posting Title | standardizedTitle | CompanyName | seniorityLevel | salaryInfo | ... |
|---|---|---|---|---|---|---|---|---|
| (수동입력) | (수동입력) | (수동입력) | Software Engineer | Software Engineer | Google | Senior | £100K-£120K | ... |
| | | | ... | ... | ... | ... | ... | ... |

## ⚠️ 주의사항

- **credentials.json**: `.gitignore`에 포함됨 (커밋 금지)
- **rawdata 폴더**: 업로드된 JSON 파일 저장
- **processed_ids.json**: 중복 방지용 ID 추적 (git 제외)

## 🔄 다음 단계 (Phase 2)

1. 프론트엔드 기본 회면 (React + Vite)
2. 필터링 로직 구현 (filter.py, parser.py)
3. JSON 파일 업로드 및 처리
4. 필터링 결과를 Google Sheets에 append

## 📝 라이선스

개인 프로젝트

## 💡 문제해결

### `ModuleNotFoundError: No module named 'fastapi'`
```bash
pip install -r requirements.txt
```

### `Google Sheets 인증 실패`
1. credentials.json 경로 확인
2. 시트 공유 설정 확인
3. `.env` 파일의 GOOGLE_CREDENTIALS_PATH 확인

### Uvicorn 포트 충돌 (Port 8888 already in use)
```bash
# 다른 포트 사용
uvicorn backend.main:app --port 8889
```
