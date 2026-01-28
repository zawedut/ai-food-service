# AI Food Service 🍜🤖

> AI-powered Food Recommendation API สำหรับ KU Food Swipe

## Features
- **KNN Engine** - Machine Learning สำหรับ recommendation ตาม tags
- **Typhoon Engine** - AI-powered (OpenTyphoon) สำหรับ cold start users
- **Hybrid Mode** - ผสม KNN + Typhoon เพื่อผลลัพธ์ที่ดีที่สุด

## API Endpoints

### POST `/api/py/recommend`
แนะนำอาหารตามประวัติการ swipe ของ user

**Request Body:**
```json
{
  "dislikeId": ["1", "2"],
  "records": [
    { "itemId": "3", "status": "eat_now" },
    { "itemId": "4", "status": "like" },
    { "itemId": "5", "status": "dislike" }
  ]
}
```

**Status Values:**
- `eat_now` / `super_like` - User ชอบมากอยากกินทันที
- `like` - User ชอบ
- `dislike` - User ไม่ชอบ

**Response:**
```json
{
  "foodIds": ["10", "15", "22", "8", "31"]
}
```

### GET `/api/py/health`
ตรวจสอบสถานะของ service

**Response:**
```json
{
  "status": "healthy",
  "trained": true,
  "food_count": 50,
  "engines": { "knn": true, "typhoon": true }
}
```

## Environment Variables
สร้างไฟล์ `.env` และเพิ่ม:

```env
MAIN_API_URL=https://your-main-api.vercel.app/api
TYPHOON_API_KEY=your-typhoon-api-key-here
```

## Deploy to Vercel

1. Push code ไปยัง GitHub
2. ไปที่ [vercel.com](https://vercel.com) → Import Project
3. เลือก repo `ai-food-service`
4. ตั้ง Environment Variables:
   - `MAIN_API_URL` - URL ของ API หลัก
   - `TYPHOON_API_KEY` - API Key จาก OpenTyphoon
5. Deploy!

## Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn api.index:app --reload --port 8000
```

เข้าถึง API Docs: http://localhost:8000/api/py/docs
