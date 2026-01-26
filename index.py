from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import os
import requests
from dotenv import load_dotenv

# Import แบบ Relative สำหรับ Vercel
from api.engines.knn import KNNEngine
from api.engines.typhoon import TyphoonEngine

load_dotenv()
app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")

# --- Config & State ---
MAIN_API_URL = os.getenv("MAIN_API_URL")
knn_bot = KNNEngine()
typhoon_bot = None # (Initial logic)
is_trained = False
FOOD_CACHE = []

# --- Helper Function ---
def fetch_and_train():
    global FOOD_CACHE, is_trained, knn_bot
    print("🌍 Serverless Waking up: Fetching Data...")
    try:
        url = f"{MAIN_API_URL}/items?partial=true&limit=1000"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            # แปลง Data (Mapping)
            cleaned = []
            for item in data:
                tags = [t['name'] for t in item['food'].get('tags', [])]
                cleaned.append({"id": str(item['id']), "tags": tags})
            
            FOOD_CACHE = cleaned
            if FOOD_CACHE:
                knn_bot.train(FOOD_CACHE)
                is_trained = True
                print(f"✅ Trained with {len(FOOD_CACHE)} items")
    except Exception as e:
        print(f"❌ Error: {e}")

# --- Models ---
class RecordItem(BaseModel):
    itemId: str
    status: str

class RecommendReq(BaseModel):
    dislikeId: List[str] = []
    records: List[RecordItem] = []

# --- Endpoint ---
@app.post("/api/py/recommend")
async def recommend(req: RecommendReq):
    # ปลุก AI ให้ตื่นมา Train ถ้ายังไม่พร้อม
    if not is_trained:
        fetch_and_train()

    # แยกข้อมูล
    eat_now_ids = [r.itemId for r in req.records if r.status in ["eat_now", "super_like"]]
    liked_ids = [r.itemId for r in req.records if r.status == "like"]
    disliked_ids = [r.itemId for r in req.records if r.status == "dislike"] + req.dislikeId

    # หา Candidates (อาหารที่ยังไม่เคยเล่น)
    seen_ids = set(eat_now_ids + liked_ids + disliked_ids)
    candidates = [f for f in FOOD_CACHE if f['id'] not in seen_ids]

    # Helper ดึง Object
    def get_objs(ids): return [f for f in FOOD_CACHE if f['id'] in ids]

    # คำนวณ (ใช้ KNN เป็นหลัก)
    if candidates:
        result_ids = knn_bot.predict(
            candidates, 
            get_objs(eat_now_ids), 
            get_objs(liked_ids), 
            get_objs(disliked_ids)
        )
    else:
        result_ids = []

    return {"foodIds": result_ids}