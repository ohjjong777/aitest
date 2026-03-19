import React, { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle, TrendingUp, DollarSign } from 'lucide-react';

const API_URL = 'http://localhost:8000';

export default function BudgetManager() {
  const [budgets, setBudgets] = useState([]);
  const [currentSpending, setCurrentSpending] = useState({});
  const [showForm, setShowForm] = useState(false);
  const [newBudget, setNewBudget] = useState({
    category: '',
    monthly_budget: ''
  });

  useEffect(() => {
    loadBudgets();
    loadCurrentMonthSpending();
  }, []);

  const loadBudgets = async () => {
    try {
      const response = await fetch(`${API_URL}/api/budgets`);
      const data = await response.json();
      setBudgets(data.budgets || []);
    } catch (error) {
      console.error('예산 로드 실패:', error);
    }
  };

  const loadCurrentMonthSpending = async () => {
    try {
      const now = new Date();
      const response = await fetch(
        `${API_URL}/api/monthly-report/${now.getFullYear()}/${now.getMonth() + 1}`
      );
      const data = await response.json();
      setCurrentSpending(data.by_category || {});
    } catch (error) {
      console.error('이번 달 지출 로드 실패:', error);
    }
  };

  const handleCreateBudget = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch(`${API_URL}/api/budgets`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          category: newBudget.category,
          monthly_budget: parseInt(newBudget.monthly_budget)
        })
      });

      if (response.ok) {
        setShowForm(false);
        setNewBudget({ category: '', monthly_budget: '' });
        loadBudgets();
      }
    } catch (error) {
      console.error('예산 생성 실패:', error);
    }
  };

  const calculateBudgetStatus = (category, budgetAmount) => {
    const spent = currentSpending[category]?.total || 0;
    const percentage = (spent / budgetAmount) * 100;
    const remaining = budgetAmount - spent;

    let status = 'safe';
    if (percentage >= 100) status = 'exceeded';
    else if (percentage >= 80) status = 'warning';

    return { spent, percentage, remaining, status };
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('ko-KR').format(amount) + '원';
  };

  const categories = [
    '식료품', '외식', '카페', '편의점', '교통', '문화/여가',
    '온라인쇼핑', '의료', '통신비', '구독서비스', '기타'
  ];

  return (
    <div className="budget-manager">
      <div className="section-header">
        <div>
          <h2>예산 관리</h2>
          <p className="subtitle">카테고리별 예산을 설정하고 지출을 추적하세요</p>
        </div>
        <button 
          onClick={() => setShowForm(!showForm)} 
          className="btn-primary"
        >
          + 예산 추가
        </button>
      </div>

      {showForm && (
        <div className="budget-form">
          <form onSubmit={handleCreateBudget}>
            <div className="form-row">
              <div className="form-group">
                <label>카테고리</label>
                <select
                  value={newBudget.category}
                  onChange={(e) => setNewBudget({ ...newBudget, category: e.target.value })}
                  required
                >
                  <option value="">선택하세요</option>
                  {categories.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>월 예산</label>
                <input
                  type="number"
                  value={newBudget.monthly_budget}
                  onChange={(e) => setNewBudget({ ...newBudget, monthly_budget: e.target.value })}
                  placeholder="500000"
                  required
                />
              </div>
            </div>

            <div className="form-actions">
              <button type="submit" className="btn-primary">생성</button>
              <button 
                type="button" 
                onClick={() => setShowForm(false)}
                className="btn-secondary"
              >
                취소
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="budgets-grid">
        {budgets.map((budget) => {
          const status = calculateBudgetStatus(budget.category, budget.monthly_budget);
          
          return (
            <div key={budget.id} className={`budget-card ${status.status}`}>
              <div className="budget-card-header">
                <h3>{budget.category}</h3>
                {status.status === 'exceeded' && <AlertCircle size={20} className="icon-warning" />}
                {status.status === 'safe' && <CheckCircle size={20} className="icon-safe" />}
                {status.status === 'warning' && <TrendingUp size={20} className="icon-caution" />}
              </div>

              <div className="budget-amounts">
                <div className="amount-row">
                  <span className="label">예산</span>
                  <span className="value">{formatCurrency(budget.monthly_budget)}</span>
                </div>
                <div className="amount-row">
                  <span className="label">사용</span>
                  <span className="value spent">{formatCurrency(status.spent)}</span>
                </div>
                <div className="amount-row">
                  <span className="label">잔액</span>
                  <span className={`value ${status.remaining < 0 ? 'negative' : 'positive'}`}>
                    {formatCurrency(Math.abs(status.remaining))}
                    {status.remaining < 0 && ' 초과'}
                  </span>
                </div>
              </div>

              <div className="budget-progress">
                <div className="progress-bar-wrapper">
                  <div 
                    className={`progress-bar-inner ${status.status}`}
                    style={{ width: `${Math.min(100, status.percentage)}%` }}
                  />
                </div>
                <div className="progress-text">
                  {status.percentage.toFixed(1)}% 사용
                </div>
              </div>

              {status.status === 'warning' && (
                <div className="budget-alert warning">
                  <AlertCircle size={16} />
                  예산의 80% 이상 사용했습니다
                </div>
              )}

              {status.status === 'exceeded' && (
                <div className="budget-alert danger">
                  <AlertCircle size={16} />
                  예산을 {formatCurrency(Math.abs(status.remaining))} 초과했습니다
                </div>
              )}
            </div>
          );
        })}
      </div>

      {budgets.length === 0 && !showForm && (
        <div className="empty-state">
          <DollarSign size={48} />
          <p>아직 설정된 예산이 없습니다.</p>
          <p className="subtitle">카테고리별 예산을 설정하여 지출을 관리하세요.</p>
        </div>
      )}

      {/* 전체 예산 요약 */}
      {budgets.length > 0 && (
        <div className="budget-summary">
          <h3>이번 달 전체 예산 요약</h3>
          <div className="summary-grid">
            <div className="summary-item">
              <span className="summary-label">총 예산</span>
              <span className="summary-value">
                {formatCurrency(budgets.reduce((sum, b) => sum + b.monthly_budget, 0))}
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">총 지출</span>
              <span className="summary-value">
                {formatCurrency(
                  budgets.reduce((sum, b) => {
                    const spent = currentSpending[b.category]?.total || 0;
                    return sum + spent;
                  }, 0)
                )}
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">남은 예산</span>
              <span className="summary-value positive">
                {formatCurrency(
                  budgets.reduce((sum, b) => {
                    const spent = currentSpending[b.category]?.total || 0;
                    return sum + (b.monthly_budget - spent);
                  }, 0)
                )}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
