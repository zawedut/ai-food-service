# AI Food Recommendation Service

AI-powered food recommendation API built with FastAPI + scikit-learn (KNN) + Typhoon LLM.  
Deploys to **Vercel** as a serverless Python function.

## API Endpoints

### `POST /api/recommend` — AI เเนะนำเมนู

**Request Body:**
```json
{
  "filter": {
    "tags": ["thai", "spicy"],
    "priceMin": 0,
    "priceMax": 200
  },
  "history": [
    { "itemId": "1", "status": "EAT" },
    { "itemId": "2", "status": "LIKE" },
    { "itemId": "5", "status": "DISLIKE" }
  ]
}
```

**Response Body:**
```json
{
  "itemIds": ["3", "11", "13", "14"]
}
```

- `filter.tags` — กรองตาม tags (ส่ง `[]` = ไม่กรอง)
- `filter.priceMin / priceMax` — กรองตามราคา (optional)
- `history[].status` — `"LIKE"` | `"DISLIKE"` | `"EAT"`
- Response คืน item IDs ให้ Next Server ไป query ต่อ (สูงสุด 10 รายการ)

### `GET /api/health` — Health Check

```json
{ "status": "ok", "items_loaded": 20, "is_trained": true, "typhoon_enabled": false }
```

## Data Fetch

AI Server จะดึงข้อมูลจาก Next Server ผ่าน:
```
GET {MAIN_API_URL}/api/items/data?limit=1000
```

ถ้า `MAIN_API_URL` ไม่ได้ตั้งค่า จะใช้ mock data 20 รายการแทน.

## Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt
pip install uvicorn

# 2. (Optional) set env vars
export MAIN_API_URL=https://your-next-app.vercel.app
export TYPHOON_API_KEY=your-key

# 3. Run server
uvicorn api.index:app --reload --port 8000

# 4. Run tests
python test_api.py
```

## Deploy to Vercel

```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Deploy
vercel

# 3. Set environment variables on Vercel Dashboard:
#    MAIN_API_URL = https://your-next-server.vercel.app
#    TYPHOON_API_KEY = (optional, for LLM-powered cold-start recommendations)

# 4. Test deployed version
API_URL=https://your-app.vercel.app python test_api.py
```

## Architecture

```
Request → POST /api/recommend
            │
            ├─ history < 5 items  → 🌪️ Typhoon LLM (cold start)
            ├─ history < 12 items → 🔮 Hybrid (KNN)
            └─ history ≥ 12 items → 🧮 KNN Expert
            │
            ▼
        { itemIds: [...] }
```

## Project Structure

```
ai-food-service/
├── api/
│   ├── index.py          # FastAPI main app
│   ├── mock_db.py        # Mock data (fallback)
│   └── engines/
│       ├── knn.py        # KNN recommendation engine
│       └── typhoon.py    # Typhoon LLM engine
├── test_api.py           # Integration test suite
├── requirements.txt      # Python dependencies
├── vercel.json           # Vercel deployment config
└── README.md
```
