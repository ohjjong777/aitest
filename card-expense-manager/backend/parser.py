import pandas as pd
import io
from typing import List, Dict
from datetime import datetime

class CardParser:
    def __init__(self):
        self.category_rules = {}
    
    def set_category_rules(self, rules: Dict[str, str]):
        """카테고리 분류 규칙 설정"""
        self.category_rules = rules
    
    def auto_categorize(self, merchant: str) -> str:
        """가맹점명 기반 자동 카테고리 분류"""
        merchant_lower = merchant.lower()
        
        # 학습된 규칙 우선 적용
        for pattern, category in self.category_rules.items():
            if pattern.lower() in merchant_lower:
                return category
        
        # 기본 키워드 기반 분류
        if any(keyword in merchant_lower for keyword in ['gs25', 'cu', '세븐', '편의점']):
            return '편의점'
        elif any(keyword in merchant_lower for keyword in ['스타벅스', '커피', '카페', '이디야']):
            return '카페'
        elif any(keyword in merchant_lower for keyword in ['마트', '이마트', '홈플러스', '롯데마트']):
            return '식료품'
        elif any(keyword in merchant_lower for keyword in ['맥도날드', '버거킹', '맘스터치', '음식점', '치킨', '피자']):
            return '외식'
        elif any(keyword in merchant_lower for keyword in ['cgv', '영화', '시네마']):
            return '문화/여가'
        elif any(keyword in merchant_lower for keyword in ['주유소', 'gs칼텍스', 's-oil', '현대오일']):
            return '교통'
        elif any(keyword in merchant_lower for keyword in ['택시', '버스', '지하철', 'ktx']):
            return '교통'
        elif any(keyword in merchant_lower for keyword in ['쿠팡', '네이버', '온라인']):
            return '온라인쇼핑'
        elif any(keyword in merchant_lower for keyword in ['병원', '약국', '의원']):
            return '의료'
        elif any(keyword in merchant_lower for keyword in ['skt', 'kt', 'lgu', '통신']):
            return '통신비'
        elif any(keyword in merchant_lower for keyword in ['넷플릭스', '유튜브', '멜론', '구독']):
            return '구독서비스'
        else:
            return '기타'
    
    def parse_file(self, file_content: bytes, filename: str) -> List[Dict]:
        """엑셀 파일 파싱 (카드사 자동 감지)"""
        try:
            # 엑셀 파일 읽기
            df = pd.read_excel(io.BytesIO(file_content))
            
            # 카드사 감지 및 파싱
            if self._is_samsung_card(df):
                return self._parse_samsung_card(df, filename)
            elif self._is_hyundai_card(df):
                return self._parse_hyundai_card(df, filename)
            elif self._is_shinhan_card(df):
                return self._parse_shinhan_card(df, filename)
            elif self._is_kb_card(df):
                return self._parse_kb_card(df, filename)
            else:
                # 범용 파서 시도
                return self._parse_generic(df, filename)
        
        except Exception as e:
            print(f"파일 파싱 오류: {str(e)}")
            return []
    
    def _is_samsung_card(self, df: pd.DataFrame) -> bool:
        """삼성카드 파일 감지"""
        columns = [str(col).lower() for col in df.columns]
        return '승인일시' in columns or '이용일시' in columns
    
    def _parse_samsung_card(self, df: pd.DataFrame, filename: str) -> List[Dict]:
        """삼성카드 파싱"""
        transactions = []
        
        # 컬럼명 정규화
        df.columns = df.columns.str.strip()
        
        for _, row in df.iterrows():
            try:
                # 날짜 추출
                date_col = '승인일시' if '승인일시' in df.columns else '이용일시'
                date_str = str(row[date_col])
                
                if pd.isna(date_str) or date_str == 'nan':
                    continue
                
                # 날짜 파싱
                if len(date_str) >= 8:
                    date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                else:
                    continue
                
                # 가맹점명
                merchant = str(row.get('가맹점명', row.get('이용가맹점', '')))
                if pd.isna(merchant) or merchant == 'nan':
                    continue
                
                # 금액 (원 단위)
                amount_col = '이용금액' if '이용금액' in df.columns else '승인금액'
                amount = int(row[amount_col])
                
                if amount <= 0:
                    continue
                
                # 자동 카테고리 분류
                category = self.auto_categorize(merchant)
                
                transactions.append({
                    'date': date,
                    'merchant': merchant,
                    'amount': amount,
                    'category': category,
                    'card_name': '삼성카드',
                    'memo': ''
                })
            
            except Exception as e:
                continue
        
        return transactions
    
    def _is_hyundai_card(self, df: pd.DataFrame) -> bool:
        """현대카드 파일 감지"""
        columns = [str(col).lower() for col in df.columns]
        return '이용일' in columns or '승인일' in columns
    
    def _parse_hyundai_card(self, df: pd.DataFrame, filename: str) -> List[Dict]:
        """현대카드 파싱"""
        transactions = []
        
        for _, row in df.iterrows():
            try:
                date_str = str(row.get('이용일', row.get('승인일', '')))
                
                if pd.isna(date_str) or date_str == 'nan':
                    continue
                
                # 날짜 형식 변환 (YYYYMMDD)
                if len(date_str) >= 8:
                    date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                else:
                    continue
                
                merchant = str(row.get('가맹점', row.get('가맹점명', '')))
                amount = int(row.get('이용금액', row.get('승인금액', 0)))
                
                if amount <= 0 or pd.isna(merchant):
                    continue
                
                category = self.auto_categorize(merchant)
                
                transactions.append({
                    'date': date,
                    'merchant': merchant,
                    'amount': amount,
                    'category': category,
                    'card_name': '현대카드',
                    'memo': ''
                })
            
            except Exception:
                continue
        
        return transactions
    
    def _is_shinhan_card(self, df: pd.DataFrame) -> bool:
        """신한카드 파일 감지"""
        return '이용일자' in df.columns or '승인일자' in df.columns
    
    def _parse_shinhan_card(self, df: pd.DataFrame, filename: str) -> List[Dict]:
        """신한카드 파싱"""
        transactions = []
        
        for _, row in df.iterrows():
            try:
                date_str = str(row.get('이용일자', row.get('승인일자', '')))
                
                if pd.isna(date_str):
                    continue
                
                if len(date_str) >= 8:
                    date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                else:
                    continue
                
                merchant = str(row.get('가맹점명', ''))
                amount = int(row.get('이용금액', 0))
                
                if amount <= 0 or pd.isna(merchant):
                    continue
                
                category = self.auto_categorize(merchant)
                
                transactions.append({
                    'date': date,
                    'merchant': merchant,
                    'amount': amount,
                    'category': category,
                    'card_name': '신한카드',
                    'memo': ''
                })
            
            except Exception:
                continue
        
        return transactions
    
    def _is_kb_card(self, df: pd.DataFrame) -> bool:
        """KB국민카드 파일 감지"""
        return '거래일자' in df.columns or 'KB' in str(df.columns)
    
    def _parse_kb_card(self, df: pd.DataFrame, filename: str) -> List[Dict]:
        """KB국민카드 파싱"""
        transactions = []
        
        for _, row in df.iterrows():
            try:
                date_str = str(row.get('거래일자', row.get('이용일', '')))
                
                if pd.isna(date_str):
                    continue
                
                if '-' in date_str:
                    date = date_str[:10]
                elif len(date_str) >= 8:
                    date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                else:
                    continue
                
                merchant = str(row.get('가맹점명', ''))
                amount = int(row.get('이용금액', 0))
                
                if amount <= 0 or pd.isna(merchant):
                    continue
                
                category = self.auto_categorize(merchant)
                
                transactions.append({
                    'date': date,
                    'merchant': merchant,
                    'amount': amount,
                    'category': category,
                    'card_name': 'KB국민카드',
                    'memo': ''
                })
            
            except Exception:
                continue
        
        return transactions
    
    def _parse_generic(self, df: pd.DataFrame, filename: str) -> List[Dict]:
        """범용 파서 (컬럼명 추정)"""
        transactions = []
        
        # 날짜 컬럼 찾기
        date_cols = [col for col in df.columns if any(
            keyword in str(col).lower() for keyword in ['일', 'date', '날짜']
        )]
        
        # 가맹점 컬럼 찾기
        merchant_cols = [col for col in df.columns if any(
            keyword in str(col).lower() for keyword in ['가맹점', '상호', 'merchant', '업체']
        )]
        
        # 금액 컬럼 찾기
        amount_cols = [col for col in df.columns if any(
            keyword in str(col).lower() for keyword in ['금액', 'amount', '원']
        )]
        
        if not (date_cols and merchant_cols and amount_cols):
            return []
        
        date_col = date_cols[0]
        merchant_col = merchant_cols[0]
        amount_col = amount_cols[0]
        
        for _, row in df.iterrows():
            try:
                date_str = str(row[date_col])
                
                if pd.isna(date_str):
                    continue
                
                # 날짜 형식 정규화
                date_str = date_str.replace('.', '-').replace('/', '-')
                if len(date_str) >= 10:
                    date = date_str[:10]
                else:
                    continue
                
                merchant = str(row[merchant_col])
                amount = int(float(row[amount_col]))
                
                if amount <= 0 or pd.isna(merchant):
                    continue
                
                category = self.auto_categorize(merchant)
                
                transactions.append({
                    'date': date,
                    'merchant': merchant,
                    'amount': amount,
                    'category': category,
                    'card_name': filename.split('.')[0],
                    'memo': ''
                })
            
            except Exception:
                continue
        
        return transactions
