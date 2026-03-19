from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TransactionCreate(BaseModel):
    date: str
    merchant: str
    amount: int
    category: str
    card_name: str
    memo: Optional[str] = None

class Transaction(TransactionCreate):
    id: int
    created_at: datetime

class Category(BaseModel):
    name: str
    budget: Optional[int] = None
    color: Optional[str] = None

class FinancialGoal(BaseModel):
    name: str
    target_amount: int
    target_date: str
    goal_type: str  # 'housing', 'retirement', 'other'
    monthly_saving: Optional[int] = None

class MonthlyReport(BaseModel):
    year: int
    month: int
    total_expense: int
    total_income: int
    by_category: dict
    transaction_count: int

class CategoryStats(BaseModel):
    category: str
    total: int
    count: int
    percentage: float
    avg_per_transaction: float
