from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import requests
import asyncio
from collections import Counter

# ─── Relative imports for Vercel ───
# ─── Relative imports for Vercel ───
from api.engines.knn import KNNEngine
from api.engines.typhoon import TyphoonEngine

# ================= APP =================
app = FastAPI(
    title="AI Food Recommendation Service",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= CONFIG =================
MAIN_API_URL = os.getenv("MAIN_API_URL")
TYPHOON_API_KEY = os.getenv("TYPHOON_API_KEY")

KNN_THRESHOLD = 5
HYBRID_MODE_THRESHOLD = 12

# ================= STATE =================
knn_bot = KNNEngine()
typhoon_bot = TyphoonEngine(api_key=TYPHOON_API_KEY) if TYPHOON_API_KEY else None

is_trained = False
FOOD_CACHE: list = []


# ================= MODELS =================
class Filter(BaseModel):
    tags: List[str] = []
    priceMin: Optional[float] = 0
    priceMax: Optional[float] = 999999


class HistoryItem(BaseModel):
    itemId: str
    status: str  # "LIKE" | "DISLIKE" | "EAT"


class RecommendRequest(BaseModel):
    filter: Filter = Filter()
    history: List[HistoryItem] = []

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "filter": {
                        "tags": ["ไทย", "ไม่เผ็ด"],
                        "priceMin": 30,
                        "priceMax": 150
                    },
                    "history": [
                        {
                            "itemId": "cmndfk2sa0000hcus0vl61tuy",
                            "status": "EAT"
                        },
                        {
                            "itemId": "cmndfk2sb0001hcuseejlh1g4",
                            "status": "LIKE"
                        },
                        {
                            "itemId": "cmndfk2sb0007hcusd0ijdg5y",
                            "status": "DISLIKE"
                        }
                    ]
                }
            ]
        }
    }


# ================= HELPERS =================
def fetch_and_train():
    """Fetch items from Next Server, fallback to mock data."""
    global FOOD_CACHE, is_trained, knn_bot

    try:
        if not MAIN_API_URL:
            raise Exception("MAIN_API_URL not set")

        # Add Vercel protection bypass cookie
        # Add Vercel protection bypass
        bypass_token = os.getenv("VERCEL_BYPASS_TOKEN", "")
        cookies = {}
        headers = {}
        if bypass_token:
            cookies["x-vercel-protection-bypass"] = bypass_token
            headers["x-vercel-protection-bypass"] = bypass_token
            # Also use authorization bearer just in case NextAuth or Vercel needs it for the API
            headers["Authorization"] = f"Bearer {bypass_token}"

        url = f"{MAIN_API_URL}/api/items/data?limit=1000"
        res = requests.get(url, headers=headers, cookies=cookies, timeout=10)

        if res.status_code == 200:
            body = res.json()
            raw_data = body.get("data", [])
            cleaned = []
            for item in raw_data:
                # Handle possible Next.js / Prisma nested format
                food_obj = item.get("Food") or item.get("food") or {}
                
                # Extract Name
                name = item.get("name") or food_obj.get("name") or "Unknown"
                
                # Extract Price
                price = item.get("price") or item.get("priceMin") or food_obj.get("price") or 0
                
                # Extract Tags
                raw_tags = item.get("tags") or food_obj.get("tags") or []
                tags = []
                for t in raw_tags:
                    if isinstance(t, dict):
                        # Nested Prisma tags e.g. {"tag": {"name": "ไทย"}} or {"name": "ไทย"}
                        if "tag" in t and isinstance(t["tag"], dict):
                            tags.append(t["tag"].get("name", ""))
                        else:
                            tags.append(t.get("name", ""))
                    elif isinstance(t, str):
                        tags.append(t)
                
                cleaned.append({
                    "id": str(item["id"]),
                    "name": name,
                    "tags": [tag for tag in tags if tag],
                    "price": float(price),
                })
            FOOD_CACHE = cleaned
            print(f"✅ Loaded {len(FOOD_CACHE)} items from API")
        else:
            raise Exception(f"API returned {res.status_code}")

    except Exception as e:
        print(f"❌ Failed to fetch data from API: {e}")
        # Not falling back to mock data
        pass
    if FOOD_CACHE:
        knn_bot.train(FOOD_CACHE)
        is_trained = True


def analyze_user_preferences(history: List[HistoryItem]) -> dict:
    """Analyze user taste from history."""
    tag_frequency = Counter()
    for record in history:
        food = next((f for f in FOOD_CACHE if f["id"] == record.itemId), None)
        if food:
            weight = 3 if record.status == "EAT" else (1 if record.status == "LIKE" else -5)
            for tag in food.get("tags", []):
                tag_frequency[tag] += weight

    return {
        "favorite_tags": [tag for tag, score in tag_frequency.most_common(5) if score > 0],
        "engagement_level": len(history),
    }


# ================= ENDPOINTS =================
@app.post("/api/recommend")
async def recommend(req: RecommendRequest):
    """
    AI recommends menu items (Soft Filtering with Fallbacks).
    Returns: { itemIds: string[] }
    """
    print("\n" + "="*40)
    print("📨 NEW REQUEST RECEIVED (SOFT FILTERS)")
    print("="*40)

    if not is_trained:
        print("⏳ Training model first...")
        fetch_and_train()

    print(f"📦 Total in DB (Cache): {len(FOOD_CACHE)}")

    # แยกของเป็น 2 กอง: ของที่คนยังไม่เคยกิน
    eat_ids = [h.itemId for h in req.history if h.status == "EAT"]
    like_ids = [h.itemId for h in req.history if h.status == "LIKE"]
    dislike_ids = [h.itemId for h in req.history if h.status == "DISLIKE"]
    seen_ids = set(eat_ids + like_ids + dislike_ids)

    # กองที่ 1: ของที่ยังไม่เคยเห็น และ "อยู่ในงบ" (Preferred)
    candidates_in_budget = []
    # กองที่ 2: ของที่ยังไม่เคยเห็น แต่ "อยู่นอกงบ" (Backup)
    candidates_out_budget = []

    for f in FOOD_CACHE:
        if f["id"] in seen_ids:
            continue # ข้ามของที่เคยกินแล้ว
            
        price = f.get("price", 0)
        # ตรวจสอบว่าอยู่ในงบไหม
        if (req.filter.priceMin or 0) <= price <= (req.filter.priceMax or 999999):
            candidates_in_budget.append(f)
        else:
            candidates_out_budget.append(f)

    print(f"💰 In-budget candidates: {len(candidates_in_budget)}")
    print(f"💸 Out-of-budget candidates: {len(candidates_out_budget)}")

    def get_objs(ids):
        return [f for f in FOOD_CACHE if f["id"] in ids]

    eat_objs = get_objs(eat_ids)
    like_objs = get_objs(like_ids)
    dislike_objs = get_objs(dislike_ids)

    user_prefs = analyze_user_preferences(req.history)
    combined_tags = list(set(user_prefs["favorite_tags"] + req.filter.tags))
    history_count = len(eat_ids) + len(like_ids)
    
    result_ids = []
    
    # โยน "ของที่อยู่ในงบ" ให้ AI วิเคราะห์เป็นหลักก่อน
    target_candidates = candidates_in_budget if candidates_in_budget else candidates_out_budget

    if target_candidates:
        if history_count < KNN_THRESHOLD and typhoon_bot:
            print("🌪️ Strategy: Typhoon AI")
            try:
                result_ids = await typhoon_bot.predict(
                    target_candidates[:50],
                    [f["name"] for f in eat_objs],
                    [f["name"] for f in like_objs],
                    [f["name"] for f in dislike_objs],
                    combined_tags,
                )
            except Exception as e:
                print(f"❌ Typhoon Error: {e}. Falling back to KNN.")
                result_ids = knn_bot.predict(target_candidates, eat_objs, like_objs, dislike_objs)
        elif history_count < HYBRID_MODE_THRESHOLD and typhoon_bot:
            print("🔮 Strategy: Hybrid")
            result_ids = knn_bot.predict(target_candidates, eat_objs, like_objs, dislike_objs)[:7]
        else:
            print("🧮 Strategy: KNN Expert")
            result_ids = knn_bot.predict(target_candidates, eat_objs, like_objs, dislike_objs)

    # ==========================================
    # 4. FORCE 10 ITEMS LOGIC (ระบบตัวสำรอง)
    # ==========================================
    final_ids = []

    for rid in result_ids:
        if rid not in final_ids:
            final_ids.append(rid)

    # Fallback 1: เติมด้วยของที่ "อยู่ในงบ" ให้เต็ม
    if len(final_ids) < 10:
        for c in candidates_in_budget:
            if c["id"] not in final_ids:
                final_ids.append(c["id"])
            if len(final_ids) >= 10: break

    # Fallback 2: ถ้าในงบหมดแล้ว ก็ต้องเอาของที่ "เกินงบ" มาโชว์
    if len(final_ids) < 10:
        print("⚠️ Not enough in-budget items. Padding with out-of-budget...")
        for c in candidates_out_budget:
            if c["id"] not in final_ids:
                final_ids.append(c["id"])
            if len(final_ids) >= 10: break

    # Fallback 3: ถ้ายกมาหมดโลกแล้วยังไม่ครบ 10 ยอมเอาของที่เคยกินแล้วมาวนซ้ำ
    if len(final_ids) < 10:
        print("🚨 Desperate Mode. Padding with Seen items...")
        for f in FOOD_CACHE:
            if f["id"] not in final_ids:
                final_ids.append(f["id"])
            if len(final_ids) >= 10: break

    final_ids = final_ids[:10]
    
    print(f"🚀 FINISHED! Returning {len(final_ids)} items.")
    print("="*40 + "\n")

    return {"itemIds": final_ids}