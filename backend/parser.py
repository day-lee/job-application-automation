"""
데이터 변환 - JSON → Google Sheets 행 변환, 기술 스택 추출
"""
from typing import List, Dict
from datetime import datetime
import re
from config import TECH_STACK_KEYWORDS


class JobParser:
    """LinkedIn Job을 Google Sheets 행으로 변환"""
    
    def __init__(self, created_at: datetime = None):
        """
        파서 초기화
        
        Args:
            created_at (datetime): 필터링이 실행되는 시각 (createdAt 컬럼용)
        """
        self.created_at = created_at or datetime.now()
    
    def extract_salary_display(self, job: Dict) -> str:
        """
        Google Sheets에 표시할 연봉 추출
        
        시파: "£115,000 - £130,000" 또는 "£45,000" 또는 ""
        
        Args:
            job (dict): Job 객체
        
        Returns:
            str: 표시할 연봉 (없으면 빈 문자열)
        """
        # 1순위: salaryInfo 배열
        if isinstance(job.get("salaryInfo"), list) and len(job["salaryInfo"]) > 0:
            salaries = [str(s).strip() for s in job["salaryInfo"] if s]
            if len(salaries) == 2:
                return f"{salaries[0]} - {salaries[1]}"
            elif len(salaries) == 1:
                return salaries[0]
        
        # 2순위: salary 필드
        if isinstance(job.get("salary"), str) and job["salary"]:
            return job["salary"]
        
        # 3순위: descriptionText에서 추출
        description = job.get("descriptionText", "")
        salary_match = self._extract_salary_range_from_text(description)
        if salary_match:
            return salary_match
        
        # 4순위: 없으면 빈 문자열
        return ""
    
    def _extract_salary_range_from_text(self, text: str) -> str:
        """
        텍스트에서 연봉 범위 추출 (예: "£45K - £55K")
        
        Args:
            text (str): 검색할 텍스트
        
        Returns:
            str: 연봉 범위 ("£45K - £55K" 형식) 또는 ""
        """
        if not text:
            return ""
        
        # £XX,XXX - £YY,YYY 또는 £XXK - £YYK 패턴
        pattern = r'(£[\d,]+(?:\.\d+)?[K]?)\s*-\s*(£[\d,]+(?:\.\d+)?[K]?)'
        match = re.search(pattern, text)
        if match:
            return f"{match.group(1)} - {match.group(2)}"
        
        return ""
    
    def extract_tech_stack(self, job: Dict) -> Dict[str, str]:
        """
        기술 스택 매칭 (JS, Python, DB, React, Node, Unwanted)
        
        description과 title에서 키워드 검색
        
        Args:
            job (dict): Job 객체
        
        Returns:
            dict: {
                "JS": "O" or "",
                "Python": "O" or "",
                "DB": "O" or "",
                "React": "O" or "",
                "Node": "O" or "",
                "Unwanted": "O" or ""
            }
        """
        tech_stack = {
            "JS": "",
            "Python": "",
            "DB": "",
            "React": "",
            "Node": "",
            "Unwanted": ""
        }
        
        # 검색할 텍스트 (title + description)
        search_text = f"{job.get('title', '')} {job.get('descriptionText', '')}".lower()
        
        # JSON은 JS 매칭에서 제외
        search_text_no_json = search_text.replace("json", " ")
        
        for tech, keywords in TECH_STACK_KEYWORDS.items():
            tech_key = tech if tech != "Unwanted" else "Unwanted"
            
            for keyword in keywords:
                keyword_lower = keyword.lower()
                
                # JSON 제외 체크 (JS 키워드에만 적용)
                if tech == "JS" and keyword_lower in ["js", "javascript", "typescript", "ts"]:
                    # JSON 제외 후 매칭
                    if re.search(rf'\b{keyword_lower}\b', search_text_no_json):
                        tech_stack[tech_key] = "O"
                        break
                else:
                    if re.search(rf'\b{keyword_lower}\b', search_text):
                        tech_stack[tech_key] = "O"
                        break
        
        return tech_stack
    
    def extract_workplace_type(self, job: Dict) -> str:
        """
        workplaceTypes 추출
        
        우선순위:
        1. workplaceTypes 배열이 있으면 첫 번째 항목 사용
        2. 빈 배열 또는 없으면 descriptionText에서 추출
        3. 아무것도 없으면 "Unknown"
        
        Args:
            job (dict): Job 객체
        
        Returns:
            str: "Hybrid", "Remote", "On-site", 또는 "Unknown"
        """
        # 1순위: workplaceTypes 배열
        workplace_types = job.get("workplaceTypes", [])
        if isinstance(workplace_types, list) and len(workplace_types) > 0:
            first_type = str(workplace_types[0]).lower()
            if "hybrid" in first_type:
                return "Hybrid"
            elif "remote" in first_type:
                return "Remote"
            elif "on-site" in first_type or "onsite" in first_type or "office" in first_type:
                return "On-site"
        
        # 2순위: descriptionText에서 추출
        description = job.get("descriptionText", "").lower()
        if "hybrid" in description:
            return "Hybrid"
        elif "remote" in description:
            return "Remote"
        elif "on-site" in description or "onsite" in description or "office" in description:
            return "On-site"
        
        # 3순위: Unknown
        return "Unknown"
    
    def format_posted_at(self, job: Dict) -> str:
        """
        PostedAt 시간 포맷팅
        
        "X분 전", "X시간 전" 형식으로 변환
        
        Args:
            job (dict): Job 객체 (postedAtTimestamp 또는 postedAt 필드 필요)
        
        Returns:
            str: "10분 전", "2시간 전" 등
        """
        # postedAtTimestamp (밀리초) 또는 postedAt (ISO 문자열) 사용
        posted_timestamp = job.get("postedAtTimestamp")
        posted_at_str = job.get("postedAt")
        
        posted_dt = None
        
        if posted_timestamp:
            try:
                # 밀리초를 초로 변환
                posted_dt = datetime.fromtimestamp(posted_timestamp / 1000)
            except (ValueError, TypeError):
                pass
        
        if not posted_dt and posted_at_str:
            try:
                # ISO 형식 파싱 (예: "2026-04-09T15:44:06.000Z")
                posted_at_str = posted_at_str.replace("Z", "+00:00")
                posted_dt = datetime.fromisoformat(posted_at_str)
            except (ValueError, AttributeError):
                pass
        
        if not posted_dt:
            return ""
        
        # 현재 시각과의 차이 계산 (timezone-naive로 통일)
        if posted_dt.tzinfo:
            # UTC로 변환 후 timezone 제거
            posted_dt = posted_dt.replace(tzinfo=None)
        
        now = datetime.now()
        diff = now - posted_dt
        
        seconds = int(diff.total_seconds())
        
        # 음수인 경우 처리 (미래의 date인 경우)
        if seconds < 0:
            return ""
        
        if seconds < 60:
            return "방금 전"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}분 전"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"{hours}시간 전"
        elif seconds < 604800:
            days = seconds // 86400
            return f"{days}일 전"
        else:
            return ""
    
    def format_apply_method(self, job: Dict) -> str:
        """
        applyMethod 변환
        
        "SimpleOnsiteApply" → "easy"
        "OffsiteApply" → "company"
        기타 → ""
        
        Args:
            job (dict): Job 객체
        
        Returns:
            str: "easy", "company", 또는 ""
        """
        apply_method = job.get("applyMethod", "")
        
        if apply_method == "SimpleOnsiteApply" or apply_method == "ComplexOnsiteApply":
            return "easy"
        elif apply_method == "OffsiteApply":
            return "company"
        return ""
    
    def parse_job_to_row(self, job: Dict) -> List[str]:
        """
        Job 객체를 Google Sheets 행으로 변환
        
        컬럼 순서:
        
        Args:
            job (dict): Job 객체
        
        Returns:
            list: Google Sheets 행 (26개 셀)
        """
        # 기술 스택 추출
        tech_stack = self.extract_tech_stack(job)
        
        # 연봉 포맷
        salary_display = self.extract_salary_display(job)
        
        # Workplace 타입
        workplace_type = self.extract_workplace_type(job)
        
        # Posted 시간
        posted_at_display = self.format_posted_at(job)
        
        # Apply 방법
        apply_method = self.format_apply_method(job)
        
        # createdAt (현재 시각, YYYY-MM-DD HH:MM 형식)
        created_at_str = self.created_at.strftime("%Y-%m-%d %H:%M")
        
        # 행 구성
        row = [
            " ",  # 1. Applied at (MANUAL - 수동입력)
            " ",  # 2. Interview date (MANUAL - 수동입력)
            " ",  # 3. Memo (MANUAL - 수동입력)
            job.get("link", ""),  # 4. Link
            job.get("applyUrl", ""),  # 5. applyUrl
            job.get("title", ""),  # 6. Posting Title
            job.get("standardizedTitle", ""),  # 7. standardizedTitle
            job.get("companyName", ""),  # 8. CompanyName
            job.get("seniorityLevel", ""),  # 9. seniorityLevel
            salary_display,  # 10. salaryInfo
            workplace_type,  # 11. workplaceTypes
            job.get("employmentType", ""),  # 12. employmentType
            tech_stack.get("JS", ""),  # 13. JS
            tech_stack.get("Python", ""),  # 14. Python
            tech_stack.get("DB", ""),  # 15. DB
            tech_stack.get("React", ""),  # 16. React
            tech_stack.get("Node", ""),  # 17. Node
            tech_stack.get("Unwanted", ""),  # 18. unwanted stack
            job.get("applicantsCount", ""),  # 19. applicantsCount
            job.get("industries", ""),  # 20. industries
            apply_method,  # 21. applyMethod        
            str(job.get("companyEmployeesCount", "")),  # 22. companyEmployeesCount
            posted_at_display,  # 23. PostedAt
            job.get("companyWebsite", ""),  # 24. companyWebsite
            created_at_str,  # 25. createdAt
            str(job.get("id", ""))  # 26. id
        ]
        
        return row
    
    def parse_jobs_to_rows(self, jobs: List[Dict]) -> List[List[str]]:
        """
        여러 Job 객체를 Google Sheets 행 배열로 변환
        
        Args:
            jobs (list): Job 객체 리스트
        
        Returns:
            list: 행 배열 (각 행은 26개 셀)
        """
        rows = []
        for job in jobs:
            row = self.parse_job_to_row(job)
            rows.append(row)
        return rows
