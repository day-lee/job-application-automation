"""
LinkedIn Job Filter API - FastAPI 애플리케이션
Phase 1: 프로젝트 세팅 + 구글 시트 연동 확인 ✅
Phase 2: 파일 업로드 기능 ✅
Phase 3: 필터링 로직 ✅
Phase 4: 필터 + 시트 연결 ✅
Phase 5: 프론트엔드 구현 ✅
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
from filter import JobFilter
from parser import JobParser

app = FastAPI(
    title="LinkedIn Job Filter API",
    description="LinkedIn 채용공고 필터링 자동화 API",
    version="0.1.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5178", "http://127.0.0.1:5178"],
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
    [Phase 4] 필터링 + 시트 저장
    
    - 가장 최신 업로드 파일 (upload_YYYYMMDD_HHMMSS.json) 자동 검색
    - 필터링 적용 (6가지 조건)
    - 통과한 job을 Google Sheets에 append
    - processed_ids.json 업데이트
    - 통계 반환
    
    Request: body 없음 (가장 최근 파일 자동 처리)
    
    Response 200:
        {
            "success": true,
            "total": 150,
            "duplicatesRemoved": 12,
            "passed": 23,
            "savedToSheet": 23,
            "rejected": 115,
            "rejected": {
                "salary": 15,
                "experience": 35,
                "clearance": 8,
                "education": 3,
                "level": 54
            },
            "sheetUrl": "https://docs.google.com/spreadsheets/d/SHEET_ID",
            "message": "✅ 필터링 완료: 전체 150개 중 23개 통과"
        }
    
    Response 400:
        {"error": "No uploaded file found"}
    
    Response 500:
        {"error": "필터링 중 오류 발생" | "Google Sheets API 실패"}
    """
    try:
        # 1. 가장 최신 업로드 파일 검색
        print("🔍 최근 업로드 파일 검색 중...")
        
        if not RAWDATA_DIR.exists():
            raise HTTPException(
                status_code=400,
                detail={"error": "No uploaded file found"}
            )
        
        # upload_YYYYMMDD_HHMMSS.json 형식의 파일 찾기
        upload_files = sorted(RAWDATA_DIR.glob("upload_*.json"))
        
        if not upload_files:
            print("❌ 업로드된 파일 없음")
            raise HTTPException(
                status_code=400,
                detail={"error": "No uploaded file found"}
            )
        
        # 최신 파일 (마지막 파일)
        latest_file = upload_files[-1]
        print(f"✅ 최신 파일 발견: {latest_file.name}")
        
        # 2. 파일 로드
        print(f"📂 파일 로드 중: {latest_file}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            jobs = json.load(f)
        
        if not isinstance(jobs, list) or len(jobs) == 0:
            print("❌ JSON 파일이 비어있거나 배열이 아님")
            raise HTTPException(
                status_code=400,
                detail={"error": "Invalid JSON format"}
            )
        
        print(f"✅ {len(jobs)}개 job 로드됨")
        
        # 3. 처리된 ID 로드
        print("📋 처리된 ID 로드 중...")
        processed_ids = load_processed_ids()
        print(f"   기존 처리된 ID 수: {len(processed_ids)}")
        
        # 4. 필터링 실행
        print("🔬 필터링 실행 중...")
        
        filter_engine = JobFilter(processed_ids)
        passed_jobs, stats = filter_engine.filter_jobs(jobs)
        
        print(f"✅ 필터링 완료:")
        print(f"   총 job 수: {stats['total']}")
        print(f"   중복 제거: {stats['duplicatesRemoved']}")
        print(f"   통과: {stats['passed']}")
        print(f"   탈락: {stats['rejected']}")
        print(f"   - 연봉 초과: {stats['breakdown']['salary']}")
        print(f"   - 경력 초과: {stats['breakdown']['experience']}")
        print(f"   - 보안 인가: {stats['breakdown']['clearance']}")
        print(f"   - 교육 요구: {stats['breakdown']['education']}")
        print(f"   - 직급 제외: {stats['breakdown']['level']}")
        
        # 5. Phase 4: 통과한 job을 Google Sheets에 저장
        print("\n💾 Google Sheets에 저장 중...")
        
        saved_to_sheet = 0
        new_ids_to_save = []
        
        if len(passed_jobs) > 0:
            try:
                # 5-1. parser를 사용해서 passed_jobs를 rows로 변환
                parser = JobParser(created_at=datetime.now())
                rows = parser.parse_jobs_to_rows(passed_jobs)
                
                print(f"   📝 {len(rows)}개 행으로 변환 완료")
                
                # 5-2. Google Sheets에 append
                sheets_client = get_sheets_client()
                sheets_client.append_rows(rows)
                
                saved_to_sheet = len(rows)
                print(f"   ✅ {saved_to_sheet}개 행을 Google Sheets에 저장 완료")
                
                # 5-3. 저장된 job의 ID 수집
                new_ids_to_save = [job.get("id", "") for job in passed_jobs]
                print(f"   📌 저장된 ID 수: {len(new_ids_to_save)}")
                
                # 5-4. processed_ids.json 업데이트
                from config import add_processed_ids
                if add_processed_ids(new_ids_to_save):
                    print(f"   ✅ processed_ids.json 업데이트 완료")
                else:
                    print(f"   ⚠️ processed_ids.json 업데이트 실패 (계속 진행)")
            
            except Exception as e:
                print(f"   ❌ Google Sheets 저장 실패: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": str(e),
                        "message": "Google Sheets API 실패"
                    }
                )
        else:
            print("   ℹ️  통과한 job이 없어 저장하지 않음")
        
        # 6. 응답 구성
        breakdown = stats.pop("breakdown")
        
        response = {
            "success": True,
            "total": stats["total"],
            "duplicatesRemoved": stats["duplicatesRemoved"],
            "filtered": stats["rejected"],  # 필터된 (탈락한) job 개수
            "passed": stats["passed"],
            "savedToSheet": saved_to_sheet,
            "rejected": {
                "salary": breakdown["salary"],
                "experience": breakdown["experience"],
                "clearance": breakdown["clearance"],
                "education": breakdown["education"],
                "level": breakdown["level"]
            },
            "sheetUrl": f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}",
            "message": f"✅ 필터링 완료: 전체 {stats['total']}개 중 {stats['passed']}개 통과"
        }
        
        print(f"\n📊 응답 준비 완료")
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 필터링 중 오류: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "message": "필터링 중 오류 발생"}
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
