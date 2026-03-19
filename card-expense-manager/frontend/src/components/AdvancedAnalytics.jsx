import React, { useState, useEffect } from 'react';
import { LineChart, BarChart, DoughnutChart } from './Charts';
import { TrendingUp, PieChart as PieChartIcon, Download } from 'lucide-react';

const API_URL = 'http://localhost:8000';

export default function AdvancedAnalytics() {
  const [trendData, setTrendData] = useState(null);
  const [categoryStats, setCategoryStats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMonths, setSelectedMonths] = useState(6);

  useEffect(() => {
    loadAnalyticsData();
  }, [selectedMonths]);

  const loadAnalyticsData = async () => {
    setLoading(true);
    try {
      // 지출 추이 데이터
      const trendResponse = await fetch(`${API_URL}/api/trend/${selectedMonths}`);
      const trendResult = await trendResponse.json();
      setTrendData(trendResult.trend);

      // 카테고리 통계
      const statsResponse = await fetch(`${API_URL}/api/category-stats`);
      const statsResult = await statsResponse.json();
      setCategoryStats(statsResult.categories || []);
    } catch (error) {
      console.error('분석 데이터 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = async () => {
    try {
      const response = await fetch(`${API_URL}/api/export/excel`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          months: selectedMonths,
          include_charts: true
        })
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `지출분석_리포트_${new Date().toISOString().split('T')[0]}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('리포트 다운로드 실패:', error);
    }
  };

  if (loading) {
    return (
      <div className="analytics-container">
        <div className="loading">데이터 분석 중...</div>
      </div>
    );
  }

  // 차트 데이터 준비
  const prepareLineChartData = () => {
    if (!trendData || trendData.length === 0) return null;

    return {
      labels: trendData.map(item => item.label),
      datasets: [
        {
          label: '총 지출',
          data: trendData.map(item => item.total),
          borderColor: 'rgb(102, 126, 234)',
          backgroundColor: 'rgba(102, 126, 234, 0.1)',
          tension: 0.4,
          fill: true
        }
      ]
    };
  };

  const prepareBarChartData = () => {
    if (!categoryStats || categoryStats.length === 0) return null;

    const topCategories = categoryStats.slice(0, 8);

    return {
      labels: topCategories.map(stat => stat.category),
      datasets: [
        {
          label: '지출',
          data: topCategories.map(stat => stat.total),
          backgroundColor: [
            'rgba(102, 126, 234, 0.8)',
            'rgba(118, 75, 162, 0.8)',
            'rgba(237, 100, 166, 0.8)',
            'rgba(255, 154, 158, 0.8)',
            'rgba(250, 208, 196, 0.8)',
            'rgba(180, 217, 204, 0.8)',
            'rgba(162, 210, 223, 0.8)',
            'rgba(138, 173, 244, 0.8)'
          ]
        }
      ]
    };
  };

  const prepareDoughnutData = () => {
    if (!categoryStats || categoryStats.length === 0) return null;

    const topCategories = categoryStats.slice(0, 6);
    const othersTotal = categoryStats.slice(6).reduce((sum, stat) => sum + stat.total, 0);

    const labels = topCategories.map(stat => stat.category);
    const data = topCategories.map(stat => stat.total);

    if (othersTotal > 0) {
      labels.push('기타');
      data.push(othersTotal);
    }

    return {
      labels: labels,
      datasets: [
        {
          data: data,
          backgroundColor: [
            'rgba(102, 126, 234, 0.8)',
            'rgba(118, 75, 162, 0.8)',
            'rgba(237, 100, 166, 0.8)',
            'rgba(255, 154, 158, 0.8)',
            'rgba(250, 208, 196, 0.8)',
            'rgba(180, 217, 204, 0.8)',
            'rgba(162, 210, 223, 0.8)'
          ],
          borderWidth: 2,
          borderColor: '#fff'
        }
      ]
    };
  };

  const lineChartData = prepareLineChartData();
  const barChartData = prepareBarChartData();
  const doughnutData = prepareDoughnutData();

  return (
    <div className="analytics-container">
      <div className="analytics-header">
        <div>
          <h2>고급 분석</h2>
          <p className="subtitle">지출 패턴과 추이를 한눈에 확인하세요</p>
        </div>
        <div className="analytics-actions">
          <select 
            value={selectedMonths} 
            onChange={(e) => setSelectedMonths(Number(e.target.value))}
            className="month-selector"
          >
            <option value={3}>최근 3개월</option>
            <option value={6}>최근 6개월</option>
            <option value={12}>최근 12개월</option>
          </select>
          <button onClick={downloadReport} className="btn-download">
            <Download size={18} />
            Excel 리포트 다운로드
          </button>
        </div>
      </div>

      <div className="charts-grid">
        {/* 지출 추이 차트 */}
        <div className="chart-card full-width">
          <div className="chart-header">
            <TrendingUp size={20} />
            <h3>월별 지출 추이</h3>
          </div>
          <div className="chart-container" style={{ height: '300px' }}>
            {lineChartData && <LineChart data={lineChartData} />}
          </div>
        </div>

        {/* 카테고리별 막대 차트 */}
        <div className="chart-card">
          <div className="chart-header">
            <PieChartIcon size={20} />
            <h3>카테고리별 지출 (Top 8)</h3>
          </div>
          <div className="chart-container" style={{ height: '300px' }}>
            {barChartData && <BarChart data={barChartData} />}
          </div>
        </div>

        {/* 도넛 차트 */}
        <div className="chart-card">
          <div className="chart-header">
            <PieChartIcon size={20} />
            <h3>지출 비율</h3>
          </div>
          <div className="chart-container" style={{ height: '300px' }}>
            {doughnutData && <DoughnutChart data={doughnutData} />}
          </div>
        </div>
      </div>

      {/* 상세 통계 테이블 */}
      <div className="stats-table-card">
        <h3>카테고리별 상세 통계</h3>
        <table className="stats-table">
          <thead>
            <tr>
              <th>카테고리</th>
              <th>총 지출</th>
              <th>거래 건수</th>
              <th>비율</th>
              <th>평균 금액</th>
            </tr>
          </thead>
          <tbody>
            {categoryStats.map((stat, index) => (
              <tr key={index}>
                <td>
                  <div className="category-badge" style={{
                    background: `hsl(${index * 40}, 70%, 95%)`
                  }}>
                    {stat.category}
                  </div>
                </td>
                <td className="amount-cell">
                  {new Intl.NumberFormat('ko-KR').format(stat.total)}원
                </td>
                <td>{stat.count}건</td>
                <td>
                  <div className="percentage-bar-container">
                    <div 
                      className="percentage-bar-fill"
                      style={{ width: `${stat.percentage}%` }}
                    />
                    <span className="percentage-text">{stat.percentage}%</span>
                  </div>
                </td>
                <td className="amount-cell">
                  {new Intl.NumberFormat('ko-KR').format(stat.avg_per_transaction)}원
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
