from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
import os
import requests
import asyncio
from dotenv import load_dotenv
from collections import Counter

# Import Mock Data
from api.mock_db import MOCK_FOOD_DB

# Import Engines
from api.engines.knn import KNNEngine
from api.engines.typhoon import TyphoonEngine

load_dotenv()
app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")

# ================= CONFIGURATION =================
MAIN_API_URL = os.getenv("MAIN_API_URL")
TYPHOON_API_KEY = os.getenv("TYPHOON_API_KEY")

# Adaptive threshold - ปรับตามพฤติกรรม User
KNN_THRESHOLD = 8  # ลดลงเล็กน้อย เพื่อให้ KNN เข้ามาช่วยเร็วขึ้น
HYBRID_MODE_THRESHOLD = 15  # เมื่อมีประวัติมากพอ ใช้ Hybrid Mode

# ================= STATE =================
knn_bot = KNNEngine()
typhoon_bot = None

if TYPHOON_API_KEY:
    typhoon_bot = TyphoonEngine(api_key=TYPHOON_API_KEY)

is_trained = False
FOOD_CACHE = []
USER_PATTERNS = {}  # เก็บ pattern การกินของ user แต่ละคน

# ================= HELPER FUNCTIONS =================
def fetch_and_train():
    global FOOD_CACHE, is_trained, knn_bot
    print("🌍 Serverless Waking up: Fetching Data...")
    
    try:
        if not MAIN_API_URL:
            raise Exception("MAIN_API_URL not set in .env")

        url = f"{MAIN_API_URL}/items?partial=true&limit=1000"
        print(f"   Trying Real API: {url}")
        
        res = requests.get(url, timeout=3)  # เพิ่ม timeout เล็กน้อย
        
        if res.status_code == 200:
            data = res.json()
            cleaned = []
            for item in data:
                tags = [t['name'] for t in item['food'].get('tags', [])]
                cleaned.append({
                    "id": str(item['id']), 
                    "name": item['food']['name'], 
                    "tags": tags,
                    "category": item['food'].get('category', 'unknown'),  # เพิ่ม category
                    "popularity": item.get('likeCount', 0)  # เพิ่ม popularity
                })
            
            FOOD_CACHE = cleaned
            print(f"✅ Loaded REAL DATA: {len(FOOD_CACHE)} items")
        else:
            raise Exception(f"API returned status {res.status_code}")

    except Exception as e:
        print(f"⚠️ Real API Failed ({e}) -> Switching to Mock Data")
        FOOD_CACHE = MOCK_FOOD_DB
        print(f"✅ Loaded MOCK DATA: {len(FOOD_CACHE)} items")

    if FOOD_CACHE:
        knn_bot.train(FOOD_CACHE)
        is_trained = True
    else:
        print("❌ Error: No data available")

def analyze_user_preferences(records: List) -> Dict:
    """วิเคราะห์รูปแบบการกินของ User"""
    eat_now = [r for r in records if r.status in ["eat_now", "super_like"]]
    liked = [r for r in records if r.status == "like"]
    
    all_preferences = eat_now + liked
    
    # หา Tags ที่ User ชอบบ่อยๆ
    tag_frequency = Counter()
    for record in all_preferences:
        food = next((f for f in FOOD_CACHE if f['id'] == record.itemId), None)
        if food:
            for tag in food.get('tags', []):
                tag_frequency[tag] += 2 if record.status in ["eat_now", "super_like"] else 1
    
    return {
        "favorite_tags": [tag for tag, _ in tag_frequency.most_common(5)],
        "engagement_level": len(all_preferences),
        "super_like_ratio": len(eat_now) / max(len(all_preferences), 1)
    }

def get_diversity_bonus(candidates: List, selected_ids: List) -> List:
    """เพิ่มความหลากหลายในผลลัพธ์"""
    if len(selected_ids) >= 10:
        return selected_ids[:10]
    
    # หา tags ที่มีอยู่แล้วใน selected
    selected_foods = [f for f in FOOD_CACHE if str(f['id']) in selected_ids]
    existing_tags = set()
    for food in selected_foods:
        existing_tags.update(food.get('tags', []))
    
    # หาอาหารที่มี tags แตกต่างออกไป
    diverse_candidates = []
    for c in candidates:
        if str(c['id']) not in selected_ids:
            food_tags = set(c.get('tags', []))
            # ถ้ามี tags ที่ไม่ซ้ำกับที่มีอยู่ ให้คะแนนโบนัส
            unique_tags = food_tags - existing_tags
            if len(unique_tags) > 0:
                diverse_candidates.append(c['id'])
                if len(selected_ids) + len(diverse_candidates) >= 10:
                    break
    
    return selected_ids + diverse_candidates[:10 - len(selected_ids)]

# ================= INPUT MODELS =================
class RecordItem(BaseModel):
    itemId: str
    status: str

class RecommendReq(BaseModel):
    dislikeId: List[str] = []
    records: List[RecordItem] = []

# ================= ENDPOINT =================
@app.post("/api/py/recommend")
async def recommend(req: RecommendReq):
    if not is_trained:
        fetch_and_train()

    # 1. แยกประวัติ
    eat_now_ids = [r.itemId for r in req.records if r.status in ["eat_now", "super_like"]]
    liked_ids = [r.itemId for r in req.records if r.status == "like"]
    disliked_ids = [r.itemId for r in req.records if r.status == "dislike"] + req.dislikeId

    # 2. วิเคราะห์ User
    user_prefs = analyze_user_preferences(req.records)
    print(f"👤 User Analysis: {user_prefs}")

    # 3. เตรียม Candidates
    seen_ids = set(eat_now_ids + liked_ids + disliked_ids)
    candidates = [f for f in FOOD_CACHE if f['id'] not in seen_ids]

    if not candidates:
        return {"foodIds": []}

    # Helper functions
    def get_objs(ids): 
        return [f for f in FOOD_CACHE if f['id'] in ids]

    eat_now_objs = get_objs(eat_now_ids)
    liked_objs = get_objs(liked_ids)
    disliked_objs = get_objs(disliked_ids)

    # 4. Smart Strategy Selection
    good_history_count = len(eat_now_ids) + len(liked_ids)
    result_ids = []
    
    # STRATEGY 1: Cold Start with Typhoon (AI เดา)
    if good_history_count < KNN_THRESHOLD and typhoon_bot:
        print(f"🌪️ Cold Start ({good_history_count}/{KNN_THRESHOLD}): Typhoon Mode")
        try:
            # ให้ Typhoon เลือกจาก candidates ที่มี popularity สูง
            popular_candidates = sorted(
                candidates, 
                key=lambda x: x.get('popularity', 0), 
                reverse=True
            )[:30]
            
            result_ids = await typhoon_bot.predict(
                popular_candidates,
                [f['name'] for f in eat_now_objs], 
                [f['name'] for f in liked_objs], 
                [f['name'] for f in disliked_objs],
                user_prefs['favorite_tags']  # ส่ง favorite tags ไปด้วย
            )
        except Exception as e:
            print(f"⚠️ Typhoon Failed: {e}")
            result_ids = knn_bot.predict(candidates, eat_now_objs, liked_objs, disliked_objs)

    # STRATEGY 2: Hybrid Mode (ผสม AI + Math)
    elif good_history_count < HYBRID_MODE_THRESHOLD and typhoon_bot:
        print(f"🔮 Hybrid Mode ({good_history_count}/{HYBRID_MODE_THRESHOLD})")
        
        # ใช้ KNN หาผล 70%
        knn_results = knn_bot.predict(candidates, eat_now_objs, liked_objs, disliked_objs)
        knn_top = knn_results[:7]
        
        # ใช้ Typhoon หาผล 30% จาก candidates ที่เหลือ
        remaining_candidates = [c for c in candidates if c['id'] not in knn_top]
        try:
            typhoon_results = await typhoon_bot.predict(
                remaining_candidates[:20],
                [f['name'] for f in eat_now_objs],
                [f['name'] for f in liked_objs],
                [f['name'] for f in disliked_objs],
                user_prefs['favorite_tags']
            )
            result_ids = knn_top + typhoon_results[:3]
        except:
            result_ids = knn_top

    # STRATEGY 3: Pure KNN (Math เต็มที่)
    else:
        print(f"🧮 Expert Mode ({good_history_count} records): KNN Only")
        result_ids = knn_bot.predict(
            candidates, 
            eat_now_objs, 
            liked_objs, 
            disliked_objs,
            boost_recent=True  # ให้ KNN ให้ความสำคัญกับรายการล่าสุดมากขึ้น
        )

    # 5. เพิ่ม Diversity
    final_ids = get_diversity_bonus(candidates, result_ids)
    
    print(f"📤 Returning {len(final_ids)} recommendations")
    return {"foodIds": final_ids[:10]}


@app.get("/api/py/health")
async def health_check():
    return {
        "status": "healthy",
        "trained": is_trained,
        "food_count": len(FOOD_CACHE),
        "engines": {
            "knn": True,
            "typhoon": typhoon_bot is not None
        }
    }