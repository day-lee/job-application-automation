"""
Google Sheets API 연동 모듈
"""
import gspread
from google.oauth2.service_account import Credentials
from pathlib import Path
from config import GOOGLE_SHEET_ID, GOOGLE_CREDENTIALS_PATH, SHEET_NAME

class GoogleSheetsClient:
    """Google Sheets API 클라이언트"""
    
    def __init__(self):
        """클라이언트 초기화"""
        self.client = None
        self.sheet = None
        self._init_auth()
    
    def _init_auth(self):
        """Google 인증 초기화"""
        try:
            # 경로가 상대 경로인 경우 절대 경로로 변환
            creds_path = Path(GOOGLE_CREDENTIALS_PATH)
            if not creds_path.is_absolute():
                creds_path = Path(__file__).parent.parent / creds_path
            
            if not creds_path.exists():
                raise FileNotFoundError(f"❌ credentials.json을 찾을 수 없습니다: {creds_path}")
            
            # Google Service Account 인증
            scope = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            creds = Credentials.from_service_account_file(
                str(creds_path),
                scopes=scope
            )
            self.client = gspread.authorize(creds)
            print(f"✅ Google Sheets 인증 성공")
            
        except FileNotFoundError as e:
            raise Exception(f"❌ Google Sheets 인증 실패: {e}")
        except Exception as e:
            raise Exception(f"❌ Google Sheets 인증 실패: {e}")
    
    def get_worksheet(self):
        """워크시트 객체 가져오기"""
        try:
            spreadsheet = self.client.open_by_key(GOOGLE_SHEET_ID)
            self.sheet = spreadsheet.worksheet(SHEET_NAME)
            print(f"✅ 워크시트 '{SHEET_NAME}' 열림")
            return self.sheet
        except gspread.SpreadsheetNotFound:
            raise Exception(f"❌ 구글 시트를 찾을 수 없습니다. ID: {GOOGLE_SHEET_ID}")
        except gspread.WorksheetNotFound:
            raise Exception(f"❌ 워크시트 '{SHEET_NAME}'을 찾을 수 없습니다.")
        except Exception as e:
            raise Exception(f"❌ 워크시트 접근 실패: {e}")
    
    def append_row(self, values):
        """새롭게 행을 추가
        
        Args:
            values (list): 추가할 행의 값 목록
            
        Returns:
            dict: 추가 결과 (업데이트 범위, 업데이트 행 수)
        """
        try:
            if not self.sheet:
                self.get_worksheet()
            
            response = self.sheet.append_row(values,
                                             value_input_option='USER_ENTERED',
                                             table_range='A1')
            print(f"✅ 행 추가 성공: {len(values)}개 셀")
            return response
        except Exception as e:
            raise Exception(f"❌ 행 추가 실패: {e}")
    
    def append_rows(self, rows):
        """여러 행을 추가
        
        Args:
            rows (list[list]): 추가할 행들의 리스트
            
        Returns:
            dict: 추가 결과
        """
        try:
            if not self.sheet:
                self.get_worksheet()
            
            response = self.sheet.append_rows(rows,
                                              value_input_option='USER_ENTERED',
                                              table_range='A1')
            print(f"✅ {len(rows)}개 행 추가 성공")
            return response
        except Exception as e:
            raise Exception(f"❌ 행 추가 실패: {e}")
    
    def get_sheet_url(self):
        """시트 URL 생성"""
        return f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}"


# 글로벌 클라이언트 인스턴스
_sheets_client = None

def get_sheets_client():
    """Google Sheets 클라이언트 획득 (싱글톤)"""
    global _sheets_client
    if _sheets_client is None:
        _sheets_client = GoogleSheetsClient()
    return _sheets_client
