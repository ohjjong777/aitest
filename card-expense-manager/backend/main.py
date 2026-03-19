from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime, timedelta
import uvicorn

from database import Database
from parser import CardParser
from analyzer import ExpenseAnalyzer
from models import (
    TransactionCreate, Transaction, Category, 
    FinancialGoal, MonthlyReport, CategoryStats
)

app = FastAPI(title="카드 지출 관리 시스템")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = Database()
parser = CardParser()
analyzer = ExpenseAnalyzer(db)

@app.on_event("startup")
async def startup():
    """서버 시작 시 데이터베이스 초기화"""
    db.init_db()

@app.get("/")
async def root():
    return {"message": "카드 지출 관리 API 서버"}

@app.post("/api/upload")
async def upload_card_file(file: UploadFile = File(...)):
    """카드사 엑셀 파일 업로드 및 파싱"""
    try:
        contents = await file.read()
        
        # 카드사별 파서 실행
        transactions = parser.parse_file(contents, file.filename)
        
        if not transactions:
            raise HTTPException(status_code=400, detail="파일 파싱 실패")
        
        # DB에 저장
        saved_count = 0
        for trans in transactions:
            if db.add_transaction(trans):
                saved_count += 1
        
        return {
            "success": True,
            "filename": file.filename,
            "total": len(transactions),
            "saved": saved_count,
            "duplicates": len(transactions) - saved_count
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"업로드 오류: {str(e)}")

@app.get("/api/transactions")
async def get_transactions(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    card_name: Optional[str] = None,
    limit: int = 100
):
    """거래 내역 조회"""
    transactions = db.get_transactions(
        start_date=start_date,
        end_date=end_date,
        category=category,
        card_name=card_name,
        limit=limit
    )
    return {"transactions": transactions}

@app.get("/api/monthly-report/{year}/{month}")
async def get_monthly_report(year: int, month: int):
    """월간 리포트 조회"""
    report = analyzer.get_monthly_report(year, month)
    return report

@app.get("/api/category-stats")
async def get_category_stats(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """카테고리별 통계"""
    stats = analyzer.get_category_stats(start_date, end_date)
    return {"categories": stats}

@app.get("/api/trend/{months}")
async def get_trend(months: int = 6):
    """지출 추이 분석 (최근 N개월)"""
    trend = analyzer.get_spending_trend(months)
    return {"trend": trend}

@app.post("/api/goals")
async def create_goal(goal: FinancialGoal):
    """재무 목표 생성"""
    goal_id = db.add_goal(goal.dict())
    return {"id": goal_id, "message": "목표가 생성되었습니다"}

@app.get("/api/goals")
async def get_goals():
    """재무 목표 조회"""
    goals = db.get_goals()
    
    # 각 목표별 진행률 계산
    for goal in goals:
        progress = analyzer.calculate_goal_progress(goal)
        goal['progress'] = progress
    
    return {"goals": goals}

@app.put("/api/transactions/{transaction_id}/category")
async def update_category(transaction_id: int, category: str):
    """거래 카테고리 수동 변경"""
    success = db.update_transaction_category(transaction_id, category)
    
    if success:
        # 학습 데이터로 저장
        transaction = db.get_transaction(transaction_id)
        if transaction:
            db.add_category_rule(transaction['merchant'], category)
        
        return {"message": "카테고리가 업데이트되었습니다"}
    else:
        raise HTTPException(status_code=404, detail="거래 내역을 찾을 수 없습니다")

@app.get("/api/dashboard")
async def get_dashboard():
    """대시보드 요약 정보"""
    now = datetime.now()
    current_month = analyzer.get_monthly_report(now.year, now.month)
    
    last_month = now.replace(day=1) - timedelta(days=1)
    previous_month = analyzer.get_monthly_report(last_month.year, last_month.month)
    
    # 목표 대비 실적
    goals = db.get_goals()
    goals_progress = []
    for goal in goals:
        progress = analyzer.calculate_goal_progress(goal)
        goals_progress.append({
            "name": goal['name'],
            "target": goal['target_amount'],
            "current": progress['current_amount'],
            "percentage": progress['percentage']
        })
    
    return {
        "current_month": current_month,
        "previous_month": previous_month,
        "month_over_month_change": (
            (current_month['total_expense'] - previous_month['total_expense']) 
            / previous_month['total_expense'] * 100 
            if previous_month['total_expense'] > 0 else 0
        ),
        "goals": goals_progress
    }

@app.delete("/api/transactions/{transaction_id}")
async def delete_transaction(transaction_id: int):
    """거래 내역 삭제"""
    success = db.delete_transaction(transaction_id)
    if success:
        return {"message": "삭제되었습니다"}
    else:
        raise HTTPException(status_code=404, detail="거래 내역을 찾을 수 없습니다")

@app.post("/api/budgets")
async def create_budget(budget: dict):
    """카테고리별 예산 설정"""
    budget_id = db.add_budget(budget['category'], budget['monthly_budget'])
    return {"id": budget_id, "message": "예산이 설정되었습니다"}

@app.get("/api/budgets")
async def get_budgets():
    """예산 조회"""
    budgets = db.get_budgets()
    return {"budgets": budgets}

@app.put("/api/budgets/{budget_id}")
async def update_budget(budget_id: int, amount: int):
    """예산 수정"""
    success = db.update_budget(budget_id, amount)
    if success:
        return {"message": "예산이 수정되었습니다"}
    else:
        raise HTTPException(status_code=404, detail="예산을 찾을 수 없습니다")

@app.delete("/api/budgets/{budget_id}")
async def delete_budget(budget_id: int):
    """예산 삭제"""
    success = db.delete_budget(budget_id)
    if success:
        return {"message": "예산이 삭제되었습니다"}
    else:
        raise HTTPException(status_code=404, detail="예산을 찾을 수 없습니다")

@app.post("/api/export/excel")
async def export_to_excel(request: dict):
    """Excel 리포트 생성"""
    from export_utils import generate_excel_report
    from fastapi.responses import FileResponse
    import os
    
    months = request.get('months', 6)
    include_charts = request.get('include_charts', True)
    
    # Excel 파일 생성
    filepath = generate_excel_report(db, analyzer, months, include_charts)
    
    if os.path.exists(filepath):
        return FileResponse(
            filepath,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename=f'지출분석_리포트_{datetime.now().strftime("%Y%m%d")}.xlsx'
        )
    else:
        raise HTTPException(status_code=500, detail="리포트 생성 실패")

@app.get("/api/export/csv")
async def export_to_csv(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """CSV 내보내기"""
    from fastapi.responses import StreamingResponse
    import csv
    import io
    
    transactions = db.get_transactions(
        start_date=start_date,
        end_date=end_date,
        limit=10000
    )
    
    # CSV 생성
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=['날짜', '가맹점', '카테고리', '카드', '금액']
    )
    writer.writeheader()
    
    for trans in transactions:
        writer.writerow({
            '날짜': trans['date'],
            '가맹점': trans['merchant'],
            '카테고리': trans['category'],
            '카드': trans['card_name'],
            '금액': trans['amount']
        })
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=transactions_{datetime.now().strftime('%Y%m%d')}.csv"
        }
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
