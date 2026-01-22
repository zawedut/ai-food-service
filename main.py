import os
import random
import requests
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

# Import สมองทั้งสอง
from engines.typhoon import TyphoonEngine
from engines.knn import KNNEngine

# โหลด Config
load_dotenv()
TYPHOON_API_KEY = os.getenv("TYPHOON_API_KEY")
FRIEND_DB_URL = os.getenv("FRIEND_DB_URL")

# สร้าง Instance ของ Engine
typhoon_bot = TyphoonEngine(api_key=TYPHOON_API_KEY)
knn_bot = KNNEngine()

# ตัวแปร Global (RAM Cache)
FOOD_CACHE = []

# ================= LIFESPAN (ทำงานตอนเปิด-ปิด) =================
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Food AI Service Starting...")
    refresh_data() # ดึงข้อมูล + Train Model
    yield
    FOOD_CACHE.clear()
    print("💤 Service Stopped.")

app = FastAPI(lifespan=lifespan)

# ================= HELPER FUNCTIONS =================
def refresh_data():
    global FOOD_CACHE
    try:
        # [Production] ให้ Uncomment 2 บรรทัดล่างเพื่อดึงจริงจากเพื่อน
        # res = requests.get(FRIEND_DB_URL)
        # FOOD_CACHE = res.json()
        
        # [MOCK DATA] จำลองข้อมูล 100 เมนู (สำหรับรันเทสตอนนี้)
        print("⚠️ Using Mock Data for Server...")
        tags_pool = ["spicy", "sweet", "sour", "soup", "fried", "healthy", "noodle", "rice", "isan", "chinese", "western"]
        FOOD_CACHE = []
        for i in range(1, 101):
            # สุ่มสร้างอาหาร
            FOOD_CACHE.append({
                "id": i, 
                "name": f"Menu-{i}", 
                "tags": random.sample(tags_pool, k=random.randint(2, 4))
            })
        print(f"✅ Loaded {len(FOOD_CACHE)} items into RAM.")

        # ======================================================
        # [IMPORTANT] สั่งให้ KNN เรียนรู้ข้อมูล (Train ML)
        # ======================================================
        print("🧠 Training KNN (Scikit-Learn) Model...")
        knn_bot.train(FOOD_CACHE)
        print("✅ Model Trained!")
        
    except Exception as e:
        print(f"❌ Load/Train Error: {e}")

# ================= API MODELS =================
class RecommendReq(BaseModel):
    user_id: str
    eat_now: list[str] = []     
    eat_now_full: list[dict] = [] 
    liked: list[str] = []
    liked_full: list[dict] = []
    disliked: list[str] = []
    disliked_full: list[dict] = []
    seen_ids: list[int] = []

# ================= ENDPOINT =================
@app.post("/recommend")
async def recommend(req: RecommendReq):
    # 1. กรองอาหารที่เคยเห็นแล้วทิ้ง (Candidates Generation)
    seen_set = set(req.seen_ids)
    available = [f for f in FOOD_CACHE if f['id'] not in seen_set]
    
    if len(available) < 5:
        return {"ids": [f['id'] for f in available], "engine": "exhausted"}

    # 2. สุ่มผู้ท้าชิงมา 50 ตัว (เพื่อส่งไปคัดเลือก)
    # ส่งไปเยอะหน่อยได้ เพราะ KNN แบบ ML คำนวณไวมาก
    candidates = random.sample(available, min(50, len(available)))
    
    # นับจำนวน Interaction ทั้งหมด
    total_actions = len(req.eat_now) + len(req.liked) + len(req.disliked)

    # ==========================================
    # 🚦 THE SWITCHER (จุดสับราง)
    # ==========================================
    
    # เงื่อนไข: Data เยอะ (เกิน 3 ครั้ง) และมีข้อมูล Full Object -> ใช้ KNN (ML)
    has_full_data = (len(req.eat_now_full) + len(req.liked_full) + len(req.disliked_full)) > 0
    
    if total_actions >= 3 and has_full_data:
        print(f"🧮 Mode: KNN ML (Actions: {total_actions})")
        selected_ids = knn_bot.predict(
            candidates, 
            req.eat_now_full, 
            req.liked_full, 
            req.disliked_full
        )
        return {"ids": selected_ids, "engine": "knn_ml"}

    else:
        # เงื่อนไข: User ใหม่ -> ใช้ Typhoon ช่วยเดา
        print(f"🌪️ Mode: Typhoon (Actions: {total_actions})")
        try:
            # ตั้งเวลา 3 วินาที ถ้าเกินให้ตัดจบ
            selected_ids = await asyncio.wait_for(
                typhoon_bot.predict(candidates, req.eat_now, req.liked, req.disliked),
                timeout=3.0
            )
            return {"ids": selected_ids, "engine": "typhoon"}
            
        except Exception as e:
            print(f"⚠️ Typhoon Error/Timeout: {e}")
            # Fallback
            return {"ids": [c['id'] for c in candidates[:5]], "engine": "fallback_random"}

@app.post("/admin/refresh")
def force_refresh():
    refresh_data()
    return {"status": "ok", "items": len(FOOD_CACHE)}