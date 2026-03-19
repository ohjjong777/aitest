#!/bin/bash

echo "====================================="
echo "카드 지출 관리 시스템 설치 및 실행"
echo "====================================="
echo ""

# 백엔드 설정
echo "📦 백엔드 패키지 설치 중..."
cd backend
pip install -r requirements.txt --break-system-packages

echo ""
echo "✅ 백엔드 설치 완료!"
echo ""

# 프론트엔드 설정
echo "📦 프론트엔드 패키지 설치 중..."
cd ../frontend
npm install

echo ""
echo "✅ 프론트엔드 설치 완료!"
echo ""

echo "====================================="
echo "설치가 완료되었습니다!"
echo "====================================="
echo ""
echo "실행 방법:"
echo ""
echo "1. 터미널 1 (백엔드):"
echo "   cd backend"
echo "   python main.py"
echo ""
echo "2. 터미널 2 (프론트엔드):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. 브라우저에서 http://localhost:3000 접속"
echo ""
echo "====================================="
