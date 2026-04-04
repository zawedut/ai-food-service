import os
import sys
import asyncio

# ==================================================
# 1. SETUP ENVIRONMENT FOR TESTING
# ==================================================
# ฝัง DATABASE_URL ใส่ไว้เพื่อใช้ในการเทสเท่านั้น
test_db_url = "postgresql://neondb_owner:npg_pHW3rRU8YBNS@ep-polished-haze-aeqxzxbs-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
os.environ["DATABASE_URL"] = test_db_url

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import โค้ดหลักจาก api.index เพื่อมาเทส
from api.index import recommend, RecommendRequest, Filter, HistoryItem, fetch_and_train, FOOD_CACHE

# ==================================================
# 2. RUN TESTS FOR STRATEGIES
# ==================================================
async def run_strategy_tests():
    print("🚀 Initializing Database & Backend...")
    fetch_and_train()  # ดึงข้อมูลจากฐานข้อมูลของจริงจาก Neon DB
    
    # Import ตัวแปร FOOD_CACHE ข้ามโมดูลต้อง import ให้ตรงหลังอัพเดตค่า
    from api.index import FOOD_CACHE
    
    if not FOOD_CACHE:
        print("❌ Could not load FOOD_CACHE from DB.")
        return
    else:
        print(f"📦 Successfully loaded {len(FOOD_CACHE)} items from DB!")
    
    def get_food(idx):
        return FOOD_CACHE[idx % len(FOOD_CACHE)]

    # --- Scenario 1: Typhoon (Cold Start / ประวัติน้อยกว่า 5 อัน) ---
    print("\n" + "🥗 "*25)
    print("🧪 SCENARIO 1: TYPHOON ONLY (Cold Start < 5 items)")
    req1 = RecommendRequest(
        filter=Filter(tags=["อาหารจานเดียว"], priceMin=0, priceMax=100),
        history=[
            HistoryItem(itemId=get_food(0)["id"], status="LIKE"),
            HistoryItem(itemId=get_food(1)["id"], status="EAT")
        ]
    )
    res1 = await recommend(req1)
    print(f"🎁 Scenario 1 Final JSON ID List: {res1['itemIds']}")


    # --- Scenario 2: Hybrid Mode (ประวัติระหว่าง 5-11 อัน) ---
    print("\n" + "🍱 "*25)
    print("🧪 SCENARIO 2: HYBRID MODE (History 5-11 items)")
    history2 = []
    # จำลองผู้ใช้มีประวัติประมาณ 8 อัน
    for i in range(8):
        status = "EAT" if i % 2 == 0 else "LIKE"
        history2.append(HistoryItem(itemId=get_food(i)["id"], status=status))
        
    req2 = RecommendRequest(
        filter=Filter(tags=["อาหารจานเดียว", "ไม่เผ็ด"], priceMin=50, priceMax=200), 
        history=history2
    )
    res2 = await recommend(req2)
    print(f"🎁 Scenario 2 Final JSON ID List: {res2['itemIds']}")


    # --- Scenario 3: KNN Expert (ประวัติเยอะ > 11 อัน) ---
    print("\n" + "🍲 "*25)
    print("🧪 SCENARIO 3: KNN EXPERT (Heavy History > 11 items)")
    history3 = []
    # จำลองผู้ใช้มีประวัติเยอะมากๆ (15 อัน)
    for i in range(15):
        status = "EAT" if i % 3 == 0 else "LIKE"
        history3.append(HistoryItem(itemId=get_food(i)["id"], status=status))
        
    req3 = RecommendRequest(
        filter=Filter(tags=["เผ็ด"], priceMin=20, priceMax=120), 
        history=history3
    )
    res3 = await recommend(req3)
    print(f"🎁 Scenario 3 Final JSON ID List: {res3['itemIds']}")


if __name__ == "__main__":
    if "TYPHOON_API_KEY" not in os.environ:
        print("⚠️ Warning: TYPHOON_API_KEY is not set in your .env file!")
        print("⚠️ Typhoon strategies will likely fail or fallback to KNN.")
        
    asyncio.run(run_strategy_tests())
