from typing import Dict, List
from datetime import datetime, timedelta
from collections import defaultdict

class ExpenseAnalyzer:
    def __init__(self, db):
        self.db = db
    
    def get_monthly_report(self, year: int, month: int) -> Dict:
        """월간 리포트 생성"""
        transactions = self.db.get_monthly_transactions(year, month)
        
        if not transactions:
            return {
                'year': year,
                'month': month,
                'total_expense': 0,
                'total_income': 0,
                'by_category': {},
                'transaction_count': 0,
                'avg_daily_expense': 0
            }
        
        total_expense = 0
        by_category = defaultdict(lambda: {'total': 0, 'count': 0})
        
        for trans in transactions:
            amount = trans['amount']
            category = trans['category']
            
            total_expense += amount
            by_category[category]['total'] += amount
            by_category[category]['count'] += 1
        
        # 일평균 지출 계산
        import calendar
        days_in_month = calendar.monthrange(year, month)[1]
        avg_daily = total_expense / days_in_month
        
        return {
            'year': year,
            'month': month,
            'total_expense': total_expense,
            'total_income': 0,  # 추후 수입 추적 기능 추가 시
            'by_category': dict(by_category),
            'transaction_count': len(transactions),
            'avg_daily_expense': round(avg_daily)
        }
    
    def get_category_stats(
        self, 
        start_date: str = None, 
        end_date: str = None
    ) -> List[Dict]:
        """카테고리별 통계"""
        transactions = self.db.get_transactions(
            start_date=start_date,
            end_date=end_date,
            limit=10000
        )
        
        if not transactions:
            return []
        
        total_amount = sum(t['amount'] for t in transactions)
        by_category = defaultdict(lambda: {'total': 0, 'count': 0})
        
        for trans in transactions:
            category = trans['category']
            amount = trans['amount']
            
            by_category[category]['total'] += amount
            by_category[category]['count'] += 1
        
        stats = []
        for category, data in by_category.items():
            stats.append({
                'category': category,
                'total': data['total'],
                'count': data['count'],
                'percentage': round(data['total'] / total_amount * 100, 1) if total_amount > 0 else 0,
                'avg_per_transaction': round(data['total'] / data['count'])
            })
        
        # 금액 기준 정렬
        stats.sort(key=lambda x: x['total'], reverse=True)
        
        return stats
    
    def get_spending_trend(self, months: int = 6) -> List[Dict]:
        """지출 추이 분석"""
        trend = []
        now = datetime.now()
        
        for i in range(months - 1, -1, -1):
            target_date = now - timedelta(days=30 * i)
            year = target_date.year
            month = target_date.month
            
            report = self.get_monthly_report(year, month)
            
            trend.append({
                'year': year,
                'month': month,
                'label': f"{year}.{month:02d}",
                'total': report['total_expense'],
                'count': report['transaction_count'],
                'categories': report['by_category']
            })
        
        return trend
    
    def calculate_goal_progress(self, goal: Dict) -> Dict:
        """재무 목표 달성률 계산"""
        target_amount = goal['target_amount']
        target_date = datetime.strptime(goal['target_date'], '%Y-%m-%d')
        created_at = datetime.strptime(goal['created_at'], '%Y-%m-%d %H:%M:%S')
        
        now = datetime.now()
        
        # 전체 기간
        total_days = (target_date - created_at).days
        elapsed_days = (now - created_at).days
        
        # 월별 저축 목표 계산
        if goal.get('monthly_saving'):
            monthly_target = goal['monthly_saving']
        else:
            total_months = max(1, total_days // 30)
            monthly_target = target_amount // total_months
        
        # 현재까지의 목표 저축액
        elapsed_months = elapsed_days // 30
        expected_amount = monthly_target * elapsed_months
        
        # 실제 저축액 (추후 저축 계좌 연동 시 실제 데이터 사용)
        # 현재는 월 지출 기반 추정
        current_amount = expected_amount  # 임시값
        
        percentage = min(100, round(current_amount / target_amount * 100, 1)) if target_amount > 0 else 0
        
        return {
            'current_amount': current_amount,
            'target_amount': target_amount,
            'percentage': percentage,
            'monthly_target': monthly_target,
            'remaining_amount': max(0, target_amount - current_amount),
            'remaining_months': max(0, (target_date - now).days // 30)
        }
    
    def get_top_merchants(self, limit: int = 10) -> List[Dict]:
        """가장 많이 이용한 가맹점 TOP N"""
        transactions = self.db.get_transactions(limit=10000)
        
        merchant_stats = defaultdict(lambda: {'total': 0, 'count': 0})
        
        for trans in transactions:
            merchant = trans['merchant']
            amount = trans['amount']
            
            merchant_stats[merchant]['total'] += amount
            merchant_stats[merchant]['count'] += 1
        
        top_merchants = []
        for merchant, data in merchant_stats.items():
            top_merchants.append({
                'merchant': merchant,
                'total': data['total'],
                'count': data['count'],
                'avg': round(data['total'] / data['count'])
            })
        
        top_merchants.sort(key=lambda x: x['total'], reverse=True)
        
        return top_merchants[:limit]
    
    def compare_months(self, year1: int, month1: int, year2: int, month2: int) -> Dict:
        """두 달 비교 분석"""
        report1 = self.get_monthly_report(year1, month1)
        report2 = self.get_monthly_report(year2, month2)
        
        total_diff = report2['total_expense'] - report1['total_expense']
        percentage_change = (
            round(total_diff / report1['total_expense'] * 100, 1) 
            if report1['total_expense'] > 0 else 0
        )
        
        return {
            'period1': {'year': year1, 'month': month1, 'total': report1['total_expense']},
            'period2': {'year': year2, 'month': month2, 'total': report2['total_expense']},
            'difference': total_diff,
            'percentage_change': percentage_change,
            'increased': total_diff > 0
        }
