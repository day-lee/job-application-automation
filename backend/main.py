"""
LinkedIn Job Filter API - FastAPI 애플리케이션
Phase 1: 프로젝트 세팅 + 구글 시트 연동 확인
Phase 2: 파일 업로드 기능
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json
from pathlib import Path
from config import (
    API_HOST, API_PORT, RAWDATA_DIR, GOOGLE_SHEET_ID,
    load_processed_ids, save_processed_ids
)
from sheets import get_sheets_client

app = FastAPI(
    title="LinkedIn Job Filter API",
    description="LinkedIn 채용공고 필터링 자동화 API",
    version="0.1.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5178"],
    allow_methods=["*"],
    allow_credentials=True,
)

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "ok",
        "message": "LinkedIN Job Filter API is running",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/test-sheet")
async def test_sheet():
    """
    [Phase 1] 구글 시트 연동 테스트
    테스트 행 1개를 구글 시트에 추가합니다.
    
    Response:
        {
            "success": true,
            "message": "테스트 행이 구글 시트에 추가되었습니다.",
            "sheetId": "SHEET_ID",
            "sheetUrl": "https://docs.google.com/spreadsheets/d/SHEET_ID"
        }
    """
    try:
        # Google Sheets 클라이언트 획득
        sheets_client = get_sheets_client()
        
        # 워크시트 획득
        worksheet = sheets_client.get_worksheet()
        
        # 테스트 행 데이터 (모든 컬럼을 채우지는 않고 일부만)
        # 실제 구조는 섹션 2의 시트 매핑 테이블 참고
        test_row = [
            "",  # Applied at (MANUAL)
            "",  # Interview date (MANUAL)
            "Phase 1 테스트",  # Memo (MANUAL)
            "[TEST] Software Engineer",  # Posting Title
            "Test Engineer",  # standardizedTitle
            "Test Company",  # CompanyName
            "Mid-level",  # seniorityLevel
            "£50K - £60K",  # salaryInfo
            "Hybrid",  # workplaceTypes
            "Full-time",  # employmentType
            "O",  # JS
            "O",  # Python
            "O",  # DB
            "O",  # React
            "O",  # Node
            "",  # unwanted stack
            "100",  # applicantsCount
            "IT Services",  # industries
            "https://example.com",  # companyWebsite
            "500",  # companyEmployeesCount
            "1 hour ago",  # PostedAt
            "https://example.com/job",  # Link
            "https://example.com/apply",  # applyUrl
            "company",  # applyMethod
            datetime.now().strftime("%Y-%m-%d %H:%M"),  # createdAt
            "TEST-ID-12345"  # id
        ]
        
        # 워크시트에 행 추가
        sheets_client.append_row(test_row)
        
        return {
            "success": True,
            "message": "✅ 테스트 행이 구글 시트에 추가되었습니다.",
            "sheetId": GOOGLE_SHEET_ID,
            "sheetUrl": sheets_client.get_sheet_url(),
            "addedRow": {
                "title": test_row[3],
                "company": test_row[5],
                "timestamp": datetime.now().isoformat()
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e),
                "message": "구글 시트 연동 테스트 실패"
            }
        )

@app.post("/upload")
async def upload_json(file: UploadFile = File(...)):
    """
    [Phase 2] JSON 파일 업로드
    
    - multipart/form-data로 JSON 파일 수신
    - rawdata/upload_YYYYMMDD_HHMMSS.json 형태로 저장
    - 업로드된 job 개수 반환
    
    Request:
        - file: JSON 파일 (multipart/form-data)
    
    Response 200:
        {
            "filename": "upload_20260409_154700.json",
            "jobCount": 150
        }
    
    Response 400:
        {
            "error": "Invalid JSON format" | "빈 JSON 배열은 업로드할 수 없습니다."
        }
    
    Response 500:
        {
            "error": "파일 업로드 중 서버 오류"
        }
    """
    try:
        # 1. 파일 확장자 검증
        if not file.filename.endswith('.json'):
            print(f"❌ 파일 형식 오류: {file.filename}")
            raise HTTPException(
                status_code=400,
                detail={"error": "Invalid file format"}
            )
        
        # 2. 파일 읽기
        content = await file.read()
        if not content:
            raise HTTPException(
                status_code=400,
                detail={"error": "빈 파일입니다"}
            )
        
        # 3. JSON 파싱 및 검증
        try:
            jobs = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 오류: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail={"error": "Invalid JSON format"}
            )
        
        # 4. JSON 형식 검증 (배열이어야 함)
        if not isinstance(jobs, list):
            print(f"❌ JSON이 배열이 아님: {type(jobs)}")
            raise HTTPException(
                status_code=400,
                detail={"error": "Invalid JSON format"}
            )
        
        # 5. 빈 배열 체크
        if len(jobs) == 0:
            print("❌ 빈 JSON 배열")
            raise HTTPException(
                status_code=400,
                detail={"error": "빈 JSON 배열은 업로드할 수 없습니다"}
            )
        
        # 6. 파일명 생성: upload_YYYYMMDD_HHMMSS.json
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"upload_{timestamp}.json"
        filepath = RAWDATA_DIR / filename
        
        # 7. 파일 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 파일 업로드 완료: {filename} ({len(jobs)}개 job)")
        
        # 8. processed_ids.json 로드 (Phase 2 컨텍스트 - 나중에 필터링에서 사용)
        _processed = load_processed_ids()
        print(f"   기존 처리된 ID 수: {len(_processed)}")
        
        # 9. 응답 반환
        return {
            "success": True,
            "filename": filename,
            "jobCount": len(jobs)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 파일 업로드 중 서버 오류: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e)}
        )

@app.post("/filter")
async def filter_jobs():
    """
    필터링 실행 (Phase 3에서 구현)
    
    - 가장 최근 업로드 파일 (upload_YYYYMMDD_HHMMSS.json) 자동 검색
    - 중복 제거, 필터링, 구글 시트 append
    - 통계 반환
    
    Request: body 없음 (가장 최근 파일 자동 처리)
    
    Response 200:
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
    
    Response 400:
        {"error": "No uploaded file found"}
    
    Response 500:
        {"error": "Google Sheets API failed"}
    """
    try:
        return {
            "success": False,
            "message": "Phase 3 필터링 기능은 아직 구현되지 않았습니다",
            "status": "not_implemented"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "message": "필터링 실패"}
        )

if __name__ == "__main__":
    import uvicorn
    
    print(f"""
    ╔════════════════════════════════════════════╗
    ║  📋 LinkedIn Job Filter API               ║
    ║  🚀 Server starting...                     ║
    ╚════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT
    )
