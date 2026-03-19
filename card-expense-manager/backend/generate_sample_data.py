"""
샘플 데이터 생성 스크립트
테스트용 카드 거래 데이터를 생성합니다.
"""

import pandas as pd
from datetime import datetime, timedelta
import random

# 샘플 가맹점 데이터
merchants = {
    '편의점': ['GS25강남점', 'CU서초점', '세븐일레븐역삼점'],
    '카페': ['스타벅스강남점', '이디야커피', '투썸플레이스'],
    '식료품': ['이마트역삼점', '홈플러스서초점', '마켓컬리'],
    '외식': ['맥도날드', '버거킹', '맘스터치', '도미노피자'],
    '교통': ['SK주유소', '현대오일뱅크', '카카오T'],
    '문화/여가': ['CGV강남', '롯데시네마', '메가박스'],
    '온라인쇼핑': ['쿠팡', '네이버페이', 'G마켓'],
    '의료': ['서울병원', '건강약국'],
    '통신비': ['SKT', 'KT', 'LG유플러스'],
    '구독서비스': ['넷플릭스', '유튜브프리미엄', '멜론']
}

# 카테고리별 평균 금액
category_amounts = {
    '편의점': (3000, 15000),
    '카페': (4500, 8000),
    '식료품': (30000, 150000),
    '외식': (15000, 50000),
    '교통': (30000, 80000),
    '문화/여가': (15000, 30000),
    '온라인쇼핑': (20000, 200000),
    '의료': (10000, 100000),
    '통신비': (50000, 80000),
    '구독서비스': (9900, 16900)
}

def generate_sample_data(card_name='삼성카드', num_transactions=100):
    """샘플 거래 데이터 생성"""
    
    transactions = []
    end_date = datetime.now()
    
    for i in range(num_transactions):
        # 랜덤 카테고리 선택
        category = random.choice(list(merchants.keys()))
        merchant = random.choice(merchants[category])
        
        # 금액 생성
        min_amt, max_amt = category_amounts[category]
        amount = random.randint(min_amt // 100, max_amt // 100) * 100
        
        # 날짜 생성 (최근 3개월)
        days_ago = random.randint(0, 90)
        date = end_date - timedelta(days=days_ago)
        date_str = date.strftime('%Y%m%d')
        
        transactions.append({
            '승인일시': date_str,
            '가맹점명': merchant,
            '이용금액': amount,
            '카드명': card_name
        })
    
    # 날짜 순으로 정렬
    transactions.sort(key=lambda x: x['승인일시'], reverse=True)
    
    return pd.DataFrame(transactions)

# 샘플 파일 생성
print("샘플 데이터 생성 중...")

# 삼성카드 샘플
samsung_data = generate_sample_data('삼성카드', 120)
samsung_data.to_excel('/home/claude/card-expense-manager/uploads/샘플_삼성카드.xlsx', index=False)
print("✅ 삼성카드 샘플 데이터 생성 완료")

# 현대카드 샘플
hyundai_data = generate_sample_data('현대카드', 80)
hyundai_data.columns = ['이용일', '가맹점', '이용금액', '카드명']
hyundai_data.to_excel('/home/claude/card-expense-manager/uploads/샘플_현대카드.xlsx', index=False)
print("✅ 현대카드 샘플 데이터 생성 완료")

# 신한카드 샘플
shinhan_data = generate_sample_data('신한카드', 90)
shinhan_data.columns = ['이용일자', '가맹점명', '이용금액', '카드명']
shinhan_data.to_excel('/home/claude/card-expense-manager/uploads/샘플_신한카드.xlsx', index=False)
print("✅ 신한카드 샘플 데이터 생성 완료")

print("\n" + "="*50)
print("샘플 데이터 생성 완료!")
print("="*50)
print("\n파일 위치: uploads/ 폴더")
print("- 샘플_삼성카드.xlsx")
print("- 샘플_현대카드.xlsx")
print("- 샘플_신한카드.xlsx")
print("\n웹 앱에서 이 파일들을 업로드하여 테스트할 수 있습니다.")
