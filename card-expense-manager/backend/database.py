import sqlite3
from typing import List, Dict, Optional
from datetime import datetime
import json

class Database:
    def __init__(self, db_path: str = "/home/claude/aitest/card-expense-manager/data/expenses.db"):
        self.db_path = db_path
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """데이터베이스 초기화"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 거래 내역 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                merchant TEXT NOT NULL,
                amount INTEGER NOT NULL,
                category TEXT NOT NULL,
                card_name TEXT NOT NULL,
                memo TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, merchant, amount, card_name)
            )
        """)
        
        # 카테고리 학습 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS category_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                merchant_pattern TEXT UNIQUE,
                category TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 재무 목표 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS financial_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                target_amount INTEGER NOT NULL,
                target_date TEXT NOT NULL,
                goal_type TEXT NOT NULL,
                monthly_saving INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 카테고리 예산 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS category_budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT UNIQUE,
                monthly_budget INTEGER NOT NULL,
                color TEXT
            )
        """)
        
        # 기본 카테고리 규칙 삽입
        default_rules = [
            ('GS25', '편의점'),
            ('CU', '편의점'),
            ('세븐일레븐', '편의점'),
            ('스타벅스', '카페'),
            ('이디야', '카페'),
            ('카페', '카페'),
            ('맘스터치', '외식'),
            ('맥도날드', '외식'),
            ('버거킹', '외식'),
            ('CGV', '문화/여가'),
            ('롯데시네마', '문화/여가'),
            ('메가박스', '문화/여가'),
            ('쿠팡', '온라인쇼핑'),
            ('네이버페이', '온라인쇼핑'),
            ('마켓컬리', '식료품'),
            ('이마트', '식료품'),
            ('홈플러스', '식료품'),
            ('롯데마트', '식료품'),
            ('SK주유소', '교통'),
            ('현대오일뱅크', '교통'),
            ('GS칼텍스', '교통'),
            ('S-OIL', '교통'),
            ('카카오T', '교통'),
            ('택시', '교통'),
            ('KTX', '교통'),
            ('SKT', '통신비'),
            ('KT', '통신비'),
            ('LGU+', '통신비'),
            ('넷플릭스', '구독서비스'),
            ('유튜브', '구독서비스'),
            ('멜론', '구독서비스'),
            ('병원', '의료'),
            ('약국', '의료'),
            ('올리브영', '생활용품'),
            ('다이소', '생활용품'),
        ]
        
        for merchant, category in default_rules:
            cursor.execute("""
                INSERT OR IGNORE INTO category_rules (merchant_pattern, category)
                VALUES (?, ?)
            """, (merchant, category))
        
        conn.commit()
        conn.close()
    
    def add_transaction(self, transaction: Dict) -> bool:
        """거래 내역 추가 (중복 체크)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO transactions (date, merchant, amount, category, card_name, memo)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                transaction['date'],
                transaction['merchant'],
                transaction['amount'],
                transaction['category'],
                transaction['card_name'],
                transaction.get('memo', '')
            ))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # 중복 데이터
            return False
    
    def get_transactions(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        category: Optional[str] = None,
        card_name: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """거래 내역 조회"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM transactions WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if card_name:
            query += " AND card_name = ?"
            params.append(card_name)
        
        query += " ORDER BY date DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def add_budget(self, category: str, monthly_budget: int) -> int:
        """예산 추가"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO category_budgets (category, monthly_budget)
            VALUES (?, ?)
        """, (category, monthly_budget))
        
        budget_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return budget_id
    
    def get_budgets(self) -> List[Dict]:
        """예산 조회"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM category_budgets ORDER BY category")
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_budget(self, budget_id: int, amount: int) -> bool:
        """예산 수정"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE category_budgets SET monthly_budget = ? WHERE id = ?
        """, (amount, budget_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def delete_budget(self, budget_id: int) -> bool:
        """예산 삭제"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM category_budgets WHERE id = ?", (budget_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def get_transaction(self, transaction_id: int) -> Optional[Dict]:
        """단일 거래 조회"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def update_transaction_category(self, transaction_id: int, category: str) -> bool:
        """거래 카테고리 업데이트"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE transactions SET category = ? WHERE id = ?
        """, (category, transaction_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """거래 삭제"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def add_category_rule(self, merchant_pattern: str, category: str):
        """카테고리 학습 규칙 추가"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO category_rules (merchant_pattern, category)
            VALUES (?, ?)
        """, (merchant_pattern, category))
        
        conn.commit()
        conn.close()
    
    def get_category_rules(self) -> Dict[str, str]:
        """카테고리 규칙 조회"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT merchant_pattern, category FROM category_rules")
        rows = cursor.fetchall()
        conn.close()
        
        return {row['merchant_pattern']: row['category'] for row in rows}
    
    def add_goal(self, goal: Dict) -> int:
        """재무 목표 추가"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO financial_goals (name, target_amount, target_date, goal_type, monthly_saving)
            VALUES (?, ?, ?, ?, ?)
        """, (
            goal['name'],
            goal['target_amount'],
            goal['target_date'],
            goal['goal_type'],
            goal.get('monthly_saving')
        ))
        
        goal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return goal_id
    
    def get_goals(self) -> List[Dict]:
        """재무 목표 조회"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM financial_goals ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_monthly_transactions(self, year: int, month: int) -> List[Dict]:
        """특정 월의 거래 내역 조회"""
        start_date = f"{year}-{month:02d}-01"
        
        # 다음 달 첫날 계산
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM transactions 
            WHERE date >= ? AND date < ?
            ORDER BY date DESC
        """, (start_date, end_date))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
