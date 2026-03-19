import React, { useState, useEffect } from 'react';
import { 
  Upload, TrendingUp, PieChart, Target, Calendar, 
  DollarSign, AlertCircle, Check, BarChart3 
} from 'lucide-react';
import AdvancedAnalytics from './components/AdvancedAnalytics';
import BudgetManager from './components/BudgetManager';
import './App.css';

const API_URL = 'http://localhost:8000';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [dashboardData, setDashboardData] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [goals, setGoals] = useState([]);
  const [categoryStats, setCategoryStats] = useState([]);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadDashboard();
    loadGoals();
  }, []);

  const loadDashboard = async () => {
    try {
      const response = await fetch(`${API_URL}/api/dashboard`);
      const data = await response.json();
      setDashboardData(data);
    } catch (error) {
      console.error('대시보드 로드 실패:', error);
    }
  };

  const loadGoals = async () => {
    try {
      const response = await fetch(`${API_URL}/api/goals`);
      const data = await response.json();
      setGoals(data.goals || []);
    } catch (error) {
      console.error('목표 로드 실패:', error);
    }
  };

  const loadTransactions = async () => {
    try {
      const response = await fetch(`${API_URL}/api/transactions?limit=100`);
      const data = await response.json();
      setTransactions(data.transactions || []);
    } catch (error) {
      console.error('거래내역 로드 실패:', error);
    }
  };

  const loadCategoryStats = async () => {
    try {
      const response = await fetch(`${API_URL}/api/category-stats`);
      const data = await response.json();
      setCategoryStats(data.categories || []);
    } catch (error) {
      console.error('카테고리 통계 로드 실패:', error);
    }
  };

  const handleFileUpload = async (event) => {
    const files = event.target.files;
    if (!files.length) return;

    setLoading(true);
    setUploadStatus(null);

    let successCount = 0;
    let totalSaved = 0;

    for (const file of files) {
      try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_URL}/api/upload`, {
          method: 'POST',
          body: formData
        });

        const result = await response.json();
        
        if (result.success) {
          successCount++;
          totalSaved += result.saved;
        }
      } catch (error) {
        console.error(`${file.name} 업로드 실패:`, error);
      }
    }

    setUploadStatus({
      success: successCount > 0,
      message: `${successCount}개 파일 업로드 완료 (${totalSaved}건 저장)`
    });

    setLoading(false);
    
    // 데이터 새로고침
    loadDashboard();
    if (activeTab === 'transactions') loadTransactions();
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('ko-KR').format(amount) + '원';
  };

  const renderDashboard = () => {
    if (!dashboardData) return <div className="loading">로딩 중...</div>;

    const { current_month, previous_month, month_over_month_change, goals: goalProgress } = dashboardData;

    return (
      <div className="dashboard">
        <h2>대시보드</h2>
        
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon"><DollarSign /></div>
            <div className="stat-content">
              <div className="stat-label">이번 달 지출</div>
              <div className="stat-value">{formatCurrency(current_month.total_expense)}</div>
              <div className={`stat-change ${month_over_month_change > 0 ? 'negative' : 'positive'}`}>
                {month_over_month_change > 0 ? '↑' : '↓'} {Math.abs(month_over_month_change).toFixed(1)}%
              </div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon"><Calendar /></div>
            <div className="stat-content">
              <div className="stat-label">거래 건수</div>
              <div className="stat-value">{current_month.transaction_count}건</div>
              <div className="stat-subtitle">일평균 {current_month.avg_daily_expense ? formatCurrency(current_month.avg_daily_expense) : '0원'}</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon"><TrendingUp /></div>
            <div className="stat-content">
              <div className="stat-label">지난 달 지출</div>
              <div className="stat-value">{formatCurrency(previous_month.total_expense)}</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon"><Target /></div>
            <div className="stat-content">
              <div className="stat-label">활성 목표</div>
              <div className="stat-value">{goalProgress.length}개</div>
            </div>
          </div>
        </div>

        {goalProgress.length > 0 && (
          <div className="goals-summary">
            <h3>재무 목표 진행 현황</h3>
            <div className="goals-list">
              {goalProgress.map((goal, index) => (
                <div key={index} className="goal-item">
                  <div className="goal-header">
                    <span className="goal-name">{goal.name}</span>
                    <span className="goal-percentage">{goal.percentage.toFixed(1)}%</span>
                  </div>
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{ width: `${Math.min(100, goal.percentage)}%` }}
                    ></div>
                  </div>
                  <div className="goal-amounts">
                    <span>{formatCurrency(goal.current)}</span>
                    <span className="goal-target">목표: {formatCurrency(goal.target)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="category-overview">
          <h3>이번 달 카테고리별 지출</h3>
          <div className="category-list">
            {Object.entries(current_month.by_category || {})
              .sort((a, b) => b[1].total - a[1].total)
              .slice(0, 5)
              .map(([category, data]) => (
                <div key={category} className="category-item">
                  <span className="category-name">{category}</span>
                  <div className="category-bar-container">
                    <div 
                      className="category-bar"
                      style={{ 
                        width: `${(data.total / current_month.total_expense * 100)}%` 
                      }}
                    ></div>
                  </div>
                  <span className="category-amount">{formatCurrency(data.total)}</span>
                </div>
              ))}
          </div>
        </div>
      </div>
    );
  };

  const renderTransactions = () => {
    return (
      <div className="transactions">
        <div className="section-header">
          <h2>거래 내역</h2>
          <button onClick={loadTransactions} className="btn-secondary">
            새로고침
          </button>
        </div>

        {transactions.length === 0 ? (
          <div className="empty-state">
            <p>거래 내역이 없습니다. 카드 내역 파일을 업로드해주세요.</p>
          </div>
        ) : (
          <div className="transactions-table">
            <table>
              <thead>
                <tr>
                  <th>날짜</th>
                  <th>가맹점</th>
                  <th>카테고리</th>
                  <th>카드</th>
                  <th>금액</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((trans) => (
                  <tr key={trans.id}>
                    <td>{trans.date}</td>
                    <td>{trans.merchant}</td>
                    <td>
                      <span className="category-tag">{trans.category}</span>
                    </td>
                    <td>{trans.card_name}</td>
                    <td className="amount">{formatCurrency(trans.amount)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    );
  };

  const renderAnalytics = () => {
    return (
      <div className="analytics">
        <h2>지출 분석</h2>
        <div className="section-header">
          <button onClick={loadCategoryStats} className="btn-secondary">
            통계 불러오기
          </button>
        </div>

        {categoryStats.length > 0 && (
          <div className="analytics-grid">
            <div className="analytics-card">
              <h3>카테고리별 지출</h3>
              <div className="category-stats">
                {categoryStats.map((stat) => (
                  <div key={stat.category} className="stat-row">
                    <span className="category-name">{stat.category}</span>
                    <div className="stat-details">
                      <span className="stat-amount">{formatCurrency(stat.total)}</span>
                      <span className="stat-percentage">{stat.percentage}%</span>
                      <span className="stat-count">{stat.count}건</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderGoals = () => {
    const [showGoalForm, setShowGoalForm] = useState(false);
    const [newGoal, setNewGoal] = useState({
      name: '',
      target_amount: '',
      target_date: '',
      goal_type: 'housing',
      monthly_saving: ''
    });

    const handleCreateGoal = async (e) => {
      e.preventDefault();
      
      try {
        const response = await fetch(`${API_URL}/api/goals`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            ...newGoal,
            target_amount: parseInt(newGoal.target_amount),
            monthly_saving: newGoal.monthly_saving ? parseInt(newGoal.monthly_saving) : null
          })
        });

        if (response.ok) {
          setShowGoalForm(false);
          setNewGoal({
            name: '',
            target_amount: '',
            target_date: '',
            goal_type: 'housing',
            monthly_saving: ''
          });
          loadGoals();
        }
      } catch (error) {
        console.error('목표 생성 실패:', error);
      }
    };

    return (
      <div className="goals">
        <div className="section-header">
          <h2>재무 목표</h2>
          <button 
            onClick={() => setShowGoalForm(!showGoalForm)} 
            className="btn-primary"
          >
            + 새 목표 추가
          </button>
        </div>

        {showGoalForm && (
          <div className="goal-form">
            <form onSubmit={handleCreateGoal}>
              <div className="form-group">
                <label>목표 이름</label>
                <input
                  type="text"
                  value={newGoal.name}
                  onChange={(e) => setNewGoal({ ...newGoal, name: e.target.value })}
                  placeholder="예: 아파트 구매 자금"
                  required
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>목표 금액</label>
                  <input
                    type="number"
                    value={newGoal.target_amount}
                    onChange={(e) => setNewGoal({ ...newGoal, target_amount: e.target.value })}
                    placeholder="200000000"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>목표 날짜</label>
                  <input
                    type="date"
                    value={newGoal.target_date}
                    onChange={(e) => setNewGoal({ ...newGoal, target_date: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>목표 유형</label>
                  <select
                    value={newGoal.goal_type}
                    onChange={(e) => setNewGoal({ ...newGoal, goal_type: e.target.value })}
                  >
                    <option value="housing">주택 구입</option>
                    <option value="retirement">노후 자금</option>
                    <option value="other">기타</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>월 저축액 (선택)</label>
                  <input
                    type="number"
                    value={newGoal.monthly_saving}
                    onChange={(e) => setNewGoal({ ...newGoal, monthly_saving: e.target.value })}
                    placeholder="5000000"
                  />
                </div>
              </div>

              <div className="form-actions">
                <button type="submit" className="btn-primary">생성</button>
                <button 
                  type="button" 
                  onClick={() => setShowGoalForm(false)}
                  className="btn-secondary"
                >
                  취소
                </button>
              </div>
            </form>
          </div>
        )}

        <div className="goals-grid">
          {goals.map((goal) => (
            <div key={goal.id} className="goal-card">
              <div className="goal-card-header">
                <h3>{goal.name}</h3>
                <span className="goal-type-badge">{
                  goal.goal_type === 'housing' ? '주택' :
                  goal.goal_type === 'retirement' ? '노후' : '기타'
                }</span>
              </div>
              
              <div className="goal-progress">
                <div className="progress-bar large">
                  <div 
                    className="progress-fill"
                    style={{ width: `${Math.min(100, goal.progress?.percentage || 0)}%` }}
                  ></div>
                </div>
                <div className="progress-label">
                  {(goal.progress?.percentage || 0).toFixed(1)}% 달성
                </div>
              </div>

              <div className="goal-details">
                <div className="detail-row">
                  <span>목표 금액</span>
                  <strong>{formatCurrency(goal.target_amount)}</strong>
                </div>
                <div className="detail-row">
                  <span>현재 금액</span>
                  <strong>{formatCurrency(goal.progress?.current_amount || 0)}</strong>
                </div>
                <div className="detail-row">
                  <span>목표 날짜</span>
                  <span>{goal.target_date}</span>
                </div>
                {goal.monthly_saving && (
                  <div className="detail-row">
                    <span>월 저축액</span>
                    <span>{formatCurrency(goal.monthly_saving)}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {goals.length === 0 && !showGoalForm && (
          <div className="empty-state">
            <Target size={48} />
            <p>아직 설정된 재무 목표가 없습니다.</p>
            <p className="subtitle">주택 구입이나 노후 준비 목표를 추가해보세요.</p>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>💳 카드 지출 관리 시스템</h1>
        <div className="upload-section">
          <label className="upload-button">
            <Upload size={20} />
            카드 내역 업로드
            <input
              type="file"
              multiple
              accept=".xlsx,.xls"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />
          </label>
          {loading && <span className="loading-text">업로드 중...</span>}
          {uploadStatus && (
            <div className={`upload-status ${uploadStatus.success ? 'success' : 'error'}`}>
              {uploadStatus.success ? <Check size={16} /> : <AlertCircle size={16} />}
              {uploadStatus.message}
            </div>
          )}
        </div>
      </header>

      <nav className="app-nav">
        <button
          className={activeTab === 'dashboard' ? 'active' : ''}
          onClick={() => setActiveTab('dashboard')}
        >
          <TrendingUp size={20} />
          대시보드
        </button>
        <button
          className={activeTab === 'transactions' ? 'active' : ''}
          onClick={() => {
            setActiveTab('transactions');
            loadTransactions();
          }}
        >
          <Calendar size={20} />
          거래내역
        </button>
        <button
          className={activeTab === 'analytics' ? 'active' : ''}
          onClick={() => setActiveTab('analytics')}
        >
          <BarChart3 size={20} />
          고급분석
        </button>
        <button
          className={activeTab === 'budget' ? 'active' : ''}
          onClick={() => setActiveTab('budget')}
        >
          <PieChart size={20} />
          예산관리
        </button>
        <button
          className={activeTab === 'goals' ? 'active' : ''}
          onClick={() => setActiveTab('goals')}
        >
          <Target size={20} />
          재무목표
        </button>
      </nav>

      <main className="app-main">
        {activeTab === 'dashboard' && renderDashboard()}
        {activeTab === 'transactions' && renderTransactions()}
        {activeTab === 'analytics' && <AdvancedAnalytics />}
        {activeTab === 'budget' && <BudgetManager />}
        {activeTab === 'goals' && renderGoals()}
      </main>
    </div>
  );
}

export default App;
