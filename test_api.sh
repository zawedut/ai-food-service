#!/bin/bash
# test_api.sh - ทดสอบ AI Food Service API

API_URL="https://ai-food-service.vercel.app"

echo "🧪 AI Food Service - API Test"
echo "=============================="
echo ""

# 1. Health Check
echo "1️⃣ Health Check..."
curl -s "$API_URL/api/py/health" | python3 -m json.tool
echo ""

# 2. Cold Start (ไม่มีประวัติ)
echo "2️⃣ Cold Start Test (ไม่มีประวัติ)..."
curl -s -X POST "$API_URL/api/py/recommend" \
  -H "Content-Type: application/json" \
  -d '{"records": [], "dislikeId": []}' | python3 -m json.tool
echo ""

# 3. With History
echo "3️⃣ With History Test (มีประวัติ)..."
curl -s -X POST "$API_URL/api/py/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "records": [
      {"itemId": "1", "status": "eat_now"},
      {"itemId": "2", "status": "like"},
      {"itemId": "10", "status": "dislike"}
    ],
    "dislikeId": ["20", "21"]
  }' | python3 -m json.tool

echo ""
echo "✅ Test Complete!"
