"""
필터링 로직 - 6가지 Filter-Out 규칙 적용
"""
import re
from typing import List, Dict, Tuple
from config import (
    MAX_SALARY_FILTER,
    MIN_EXPERIENCE_FILTER,
    CLEARANCE_KEYWORDS, 
    LEVEL_EXCLUDE_KEYWORDS,
    TECH_STACK_KEYWORDS
)


class JobFilter:
    """LinkedIn Job 필터링 엔진"""
    
    def __init__(self, processed_ids: set):
        """
        필터 초기화
        
        Args:
            processed_ids (set): 이미 처리된 job ID set
        """
        self.processed_ids = processed_ids
        
        # 필터 규칙별 거부 건수
        self.reject_stats = {
            "duplicates": 0,
            "salary": 0,
            "experience": 0,
            "clearance": 0,
            "education": 0,
            "level": 0,
            "stack": 0
        }
    
    def extract_salary_from_text(self, text: str) -> int:
        """
        텍스트에서 연봉 숫자 추출 (£ 또는 GBP 기준)
        
        예: "£115,000.00" → 115000
           "£45K" → 45000
           "GBP 50,000" → 50000
        
        Args:
            text (str): 검색할 텍스트
        
        Returns:
            int: 추출된 최대 연봉 (없으면 0)
        """
        if not text:
            return 0
        
        # £ 또는 GBP 뒤의 숫자 패턴 찾기
        # 예: "£45,000", "£45K", "GBP 50000"
        patterns = [
            r'[£][\s]?(\d+(?:,\d+)*(?:\.\d+)?)[K]?',  # £45,000 또는 £45K
            r'GBP[\s]?(\d+(?:,\d+)*(?:\.\d+)?)',  # GBP 50,000
        ]
        
        matches = []
        for pattern in patterns:
            found = re.findall(pattern, text, re.IGNORECASE)
            for match in found:
                # 쉼표 제거 및 숫자 변환
                num_str = match.replace(',', '')
                try:
                    num = float(num_str)
                    # K 접미사 처리 (이미 패턴에서 K를 선택적으로 처리)
                    if num < 1000:  # 1000 이하면 K 단위로 간주
                        num *= 1000
                    matches.append(int(num))
                except ValueError:
                    continue
        
        return max(matches) if matches else 0
    
    def extract_max_salary(self, job: Dict) -> int:
        """
        job에서 최대 연봉 추출 (우선순위 적용)
        
        우선순위:
        1. salaryInfo 배열
        2. salary, salaryInsights 필드
        3. descriptionText에서 추출
        4. 없으면 0 (필터 통과)
        
        Args:
            job (dict): Job 객체
        
        Returns:
            int: 최대 연봉 (추출 실패 시 0 = 필터 통과)
        """
        # 1순위: salaryInfo 배열
        if isinstance(job.get("salaryInfo"), list) and len(job["salaryInfo"]) > 0:
            # 배열의 마지막 요소가 최대값
            last_item = job["salaryInfo"][-1]
            if isinstance(last_item, str):
                salary_num = self.extract_salary_from_text(last_item)
                if salary_num > 0:
                    return salary_num
        
        # 2순위: salary 또는 salaryInsights 필드
        if isinstance(job.get("salary"), str) and job["salary"]:
            salary_num = self.extract_salary_from_text(job["salary"])
            if salary_num > 0:
                return salary_num
        
        # salaryInsights는 보통 빈 dict이므로 스킵
        
        # 3순위: descriptionText에서 추출
        description = job.get("descriptionText", "")
        if description:
            salary_num = self.extract_salary_from_text(description)
            if salary_num > 0:
                return salary_num
        
        # 4순위: 없으면 0 (필터 통과)
        return 0
    
    def extract_min_experience(self, text: str) -> int:
        """
        텍스트에서 최소 요구 경력 추출
        
        패턴:
        - "3+ years" → 3
        - "3-5 years" → 3 (범위는 최소값)
        - "minimum 3 years" → 3
        - "at least 3 years" → 3
        - "5 years experience" → 5
        
        Args:
            text (str): 검색할 텍스트
        
        Returns:
            int: 최소 경력 (없으면 -1)
        """
        if not text:
            return -1
        
        text_lower = text.lower()
        
        # 패턴 찾기 (우선순위 순)
        patterns = [
            r'(\d+)\+\s*years',                          # "3+ years"
            r'(\d+)\s*-\s*\d+\s*years',                 # "3-5 years" (첫 숫자)
            r'minimum\s+(\d+)\s*years',                 # "minimum 3 years"
            r'at\s+least\s+(\d+)\s*years',             # "at least 3 years"
            r'(?:require|require[ds]?|need[s]?)\s+(\d+)\s*years',  # "require 3 years"
            r'(\d+)\s*years?\s+(?:experience|of)',     # "5 years experience"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    return int(match.group(1))
                except (ValueError, IndexError):
                    continue
        
        return -1  # 경력 요구사항 없음
    
    def check_clearance_required(self, text: str) -> bool:
        """
        보안 인가 요구 여부 확인
        
        키워드: SC Clearance, Security Clearance, DV Clearance,
               Open to UK nationals only, BPSS, security check
        
        Args:
            text (str): 검색할 텍스트
        
        Returns:
            bool: 보안 인가 필요하면 True
        """
        if not text:
            return False
        
        text_lower = text.lower()
        for keyword in CLEARANCE_KEYWORDS:
            if keyword.lower() in text_lower:
                return True
        return False
    
    def check_education_2_1_required(self, text: str) -> bool:
        """
        2:1 이상 학위 요구 여부 확인
        
        "2:1 or above required" → True
        "degree required" → False (통과)
        
        Args:
            text (str): 검색할 텍스트
        
        Returns:
            bool: 2:1 이상 요구하면 True
        """
        if not text:
            return False
        
        text_lower = text.lower()
        
        # "2:1 or above" 또는 "2.1 or above" 패턴
        if re.search(r'2[:\.]1\s+or\s+above', text_lower):
            return True
        
        # "first class degree" 또는 "1st class" 패턴
        if re.search(r'(?:first\s+class|1st\s+class)\s+degree', text_lower):
            return True
        
        return False
    
    def check_level_required(self, text: str) -> bool:
        """
        제외할 직급 확인
        
        키워드: "staff", "lead", "principal", "senior"
        
        Args:
            text (str): 검색할 텍스트 (title + standardizedTitle)
        
        Returns:
            bool: 제외 대상이면 True
        """
        if not text:
            return False
        
        text_lower = text.lower()
        for keyword in LEVEL_EXCLUDE_KEYWORDS:
            # 정확한 단어 매치 (앞뒤로 공백 또는 문장부호)
            if re.search(rf'\b{keyword}\b', text_lower):
                return True
        
        return False

    def check_stack_excluded(self, text: str) -> bool:
        """
        제외할 기술 확인
        
        키워드: "c++", "c#", "kafka", "salesforce", "wordpress", "php", "spring", "ruby", "laravel"
        
        Args:
            text (str): 검색할 텍스트 (title)
        
        Returns:
            bool: 제외 대상이면 True
        """
        if not text:
            return False
        
        text_lower = text.lower()
        for keyword in TECH_STACK_KEYWORDS["Unwanted"]:
            # 정확한 단어 매치 (앞뒤로 공백 또는 문장부호)
            if re.search(rf'\b{keyword}\b', text_lower):
                return True
        
        return False
    
    def filter_job(self, job: Dict) -> Tuple[bool, str]:
        """
        단일 job 필터링
        
        Args:
            job (dict): Job 객체
        
        Returns:
            Tuple[bool, str]: (통과 여부, 탈락 사유)
                - 통과: (True, "")
                - 탈락: (False, "salary"|"experience"|"clearance"|"education"|"level")
        """
        job_id = str(job.get("id", ""))
        
        # Step 1: 중복 확인
        if job_id in self.processed_ids:
            self.reject_stats["duplicates"] += 1
            return False, "duplicates"
        
        # Step 2: 연봉 필터 (£50K 이상 제외)
        max_salary = self.extract_max_salary(job)
        if max_salary >= MAX_SALARY_FILTER:
            self.reject_stats["salary"] += 1
            return False, "salary"
        
        # Step 3: 경력 필터 (3년 이상 요구 시 제외)
        description = job.get("descriptionText", "")
        min_experience = self.extract_min_experience(description)
        if min_experience >= MIN_EXPERIENCE_FILTER:  # 3년 이상 → 제외
            self.reject_stats["experience"] += 1
            return False, "experience"
        
        # Step 4: 보안 인가 필터
        if self.check_clearance_required(description):
            self.reject_stats["clearance"] += 1
            return False, "clearance"
        
        # Step 5: 교육 필터 (2:1 이상 학위 요구 시 제외)
        if self.check_education_2_1_required(description):
            self.reject_stats["education"] += 1
            return False, "education"
        
        # Step 6: 레벨 필터 (staff, lead, principal 제외)
        # title + standardizedTitle에서 검색
        level_check_text = f"{job.get('title', '')} {job.get('standardizedTitle', '')}"
        if self.check_level_required(level_check_text):
            self.reject_stats["level"] += 1
            return False, "level"
        
        # Step 7: 기술 스택 필터 (제외할 기술 포함 시 제외)
        if self.check_stack_excluded(job.get("title", "")):
            self.reject_stats["level"] += 1
            return False, "level"   
        # 모든 필터 통과
        return True, ""
    
    def filter_jobs(self, jobs: List[Dict]) -> Tuple[List[Dict], Dict]:
        """
        여러 job들 필터링
        
        Args:
            jobs (list): Job 객체 리스트
        
        Returns:
            Tuple[List[Dict], Dict]:
                - 통과한 job 리스트
                - 통계 (total, passed, rejected 분류)
        """
        passed_jobs = []
        
        for job in jobs:
            is_passed, reject_reason = self.filter_job(job)
            if is_passed:
                passed_jobs.append(job)
        
        # 통계 구성
        total = len(jobs)
        passed = len(passed_jobs)
        rejected = total - passed
        
        stats = {
            "total": total,
            "passed": passed,
            "rejected": rejected,
            "duplicatesRemoved": self.reject_stats["duplicates"],
            "breakdown": {
                "salary": self.reject_stats["salary"],
                "experience": self.reject_stats["experience"],
                "clearance": self.reject_stats["clearance"],
                "education": self.reject_stats["education"],
                "level": self.reject_stats["level"]
            }
        }
        
        return passed_jobs, stats
