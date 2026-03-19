# 카드 지출 통합 관리 시스템

50대 가장을 위한 전문적인 카드 지출 관리 웹 애플리케이션입니다.
주택구입과 노후준비를 위한 재무 계획을 체계적으로 수립하고 관리할 수 있습니다.

## 주요 기능

### 📊 대시보드
- 월별 지출 현황 요약
- 전월 대비 증감률 분석
- 카테고리별 지출 분포
- 재무 목표 진행 현황

### 💳 카드 내역 통합 관리
- 여러 카드사 엑셀 파일 자동 통합
- 지원 카드사: 삼성, 현대, 신한, KB 등
- 자동 카테고리 분류 (AI 학습)
- 중복 거래 자동 제거

### 📈 지출 분석
- 카테고리별 상세 통계
- 월별 지출 추이
- 가맹점별 이용 현황
- 기간별 비교 분석

### 🎯 재무 목표 관리
- 주택구입 목표 설정
- 노후자금 목표 관리
- 월별 저축 목표 추적
- 목표 달성률 실시간 확인

## 기술 스택

### Backend
- **FastAPI** - 고성능 Python 웹 프레임워크
- **SQLite** - 로컬 데이터베이스
- **Pandas** - 엑셀 파일 파싱 및 데이터 분석
- **Uvicorn** - ASGI 서버

### Frontend
- **React 18** - 사용자 인터페이스
- **Vite** - 빌드 도구
- **Lucide React** - 아이콘
- **Modern CSS** - 반응형 디자인

## 설치 방법

### 사전 요구사항
- Python 3.8 이상
- Node.js 16 이상
- npm 또는 yarn

### 1. 백엔드 설치

```bash
cd card-expense-manager/backend

# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. 프론트엔드 설치

```bash
cd card-expense-manager/frontend

# 패키지 설치
npm install
```

## 실행 방법

### 백엔드 서버 시작

```bash
cd backend
python main.py
```

서버가 `http://localhost:8000` 에서 실행됩니다.

### 프론트엔드 개발 서버 시작

새 터미널을 열고:

```bash
cd frontend
npm run dev
```

웹 앱이 `http://localhost:3000` 에서 실행됩니다.

## 사용 방법

### 1. 카드 내역 업로드

1. 각 카드사 웹사이트/앱에서 사용내역을 엑셀 파일로 다운로드
2. 웹 앱 상단의 "카드 내역 업로드" 버튼 클릭
3. 여러 파일을 한 번에 선택 가능
4. 자동으로 파싱 및 DB 저장

### 2. 지출 분석

- **대시보드**: 이번 달 지출 현황 한눈에 확인
- **거래내역**: 모든 카드 거래를 통합 조회
- **분석**: 카테고리별, 기간별 상세 분석
- **재무목표**: 주택구입/노후자금 목표 설정 및 추적

### 3. 재무 목표 설정

1. "재무목표" 탭 클릭
2. "+ 새 목표 추가" 버튼 클릭
3. 목표 정보 입력:
   - 목표 이름 (예: 아파트 구매 자금)
   - 목표 금액 (예: 200,000,000원)
   - 목표 날짜
   - 월 저축액 (선택)
4. 진행률 자동 계산 및 추적

## 카드사별 엑셀 다운로드 방법

### 삼성카드
1. 삼성카드 앱/웹 로그인
2. 이용내역 조회 → 엑셀 다운로드

### 현대카드
1. 현대카드 앱/웹 로그인
2. 이용내역 → 엑셀 저장

### 신한카드
1. 신한카드 앱/웹 로그인
2. 카드 이용내역 → 다운로드

### KB국민카드
1. KB국민카드 앱/웹 로그인
2. 이용내역 조회 → 엑셀 다운로드

## 디렉토리 구조

```
card-expense-manager/
├── backend/
│   ├── main.py              # FastAPI 서버
│   ├── database.py          # 데이터베이스 관리
│   ├── parser.py            # 카드사별 파서
│   ├── analyzer.py          # 지출 분석 엔진
│   ├── models.py            # 데이터 모델
│   └── requirements.txt     # Python 패키지
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # 메인 앱
│   │   ├── App.css          # 스타일시트
│   │   └── index.jsx        # 진입점
│   ├── public/
│   │   └── index.html
│   ├── package.json
│   └── vite.config.js
├── data/                    # SQLite DB 저장
└── uploads/                 # 업로드 파일 임시 저장
```

## API 엔드포인트

### 거래 관리
- `POST /api/upload` - 카드 파일 업로드
- `GET /api/transactions` - 거래 내역 조회
- `PUT /api/transactions/{id}/category` - 카테고리 수정
- `DELETE /api/transactions/{id}` - 거래 삭제

### 분석
- `GET /api/dashboard` - 대시보드 데이터
- `GET /api/monthly-report/{year}/{month}` - 월간 리포트
- `GET /api/category-stats` - 카테고리 통계
- `GET /api/trend/{months}` - 지출 추이

### 재무 목표
- `POST /api/goals` - 목표 생성
- `GET /api/goals` - 목표 조회

## 보안 고려사항

- 모든 데이터는 로컬 SQLite DB에 저장
- 외부 서버로 전송되지 않음
- 민감한 금융 정보 보호
- CORS 설정으로 허가된 도메인만 접근

## 확장 계획

- [ ] 계좌 잔고 연동
- [ ] 자동 예산 추천
- [ ] 지출 패턴 AI 분석
- [ ] 모바일 앱 개발
- [ ] 가계부 공유 기능
- [ ] PDF 리포트 생성
- [ ] 은행 API 연동

## 문제 해결

### 백엔드 실행 오류
```bash
# 포트 충돌 시
python main.py --port 8001
```

### 프론트엔드 실행 오류
```bash
# node_modules 재설치
rm -rf node_modules package-lock.json
npm install
```

### 파일 업로드 실패
- 엑셀 파일 형식 확인 (.xlsx)
- 파일 크기 제한 (최대 10MB)
- 컬럼명이 한글인지 확인

## 라이센스

이 프로젝트는 개인 사용을 위한 것입니다.

## 문의

기술적 질문이나 개선 제안은 이슈로 등록해주세요.

---

**제작**: 50대 가장을 위한 맞춤형 재무 관리 솔루션
**목적**: 주택구입 및 노후준비 체계적 관리
