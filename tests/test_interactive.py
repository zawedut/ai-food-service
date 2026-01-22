import sys
import os
import random
import asyncio
from dotenv import load_dotenv

# Hack path ให้เจอ folder engines
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engines.knn import KNNEngine
from engines.typhoon import TyphoonEngine
from tests.mock_db import MOCK_FOOD_DB, get_food_by_ids

# โหลด API Key
load_dotenv()
TYPHOON_API_KEY = os.getenv("TYPHOON_API_KEY")

def main():
    print("\n" + "="*60)
    print("🍱  ULTIMATE FOOD AI TESTER (ML Edition)")
    print("="*60)

    # 1. เตรียม KNN Engine และสั่ง TRAIN ทันที
    print("🧠 Initializing & Training KNN Model...")
    knn_bot = KNNEngine()
    knn_bot.train(MOCK_FOOD_DB) # <--- [สำคัญมาก] ต้อง Train ก่อนใช้
    print("✅ KNN Ready!")

    # 2. เตรียม Typhoon Engine
    typhoon_bot = None
    if TYPHOON_API_KEY:
        typhoon_bot = TyphoonEngine(api_key=TYPHOON_API_KEY)
    else:
        print("⚠️ Warning: ไม่เจอ TYPHOON_API_KEY (เล่นได้แค่ KNN)")

    
    while True:
        # --- SHOW MENU ---
        print("\n" + "-"*30)
        print("📋 MENU EXAMPLES (สุ่ม 10 เมนู):")
        display_sample = random.sample(MOCK_FOOD_DB, 10)
        display_sample.sort(key=lambda x: x['id'])
        
        for item in display_sample:
            print(f"  [{item['id']:2}] {item['name']:<22} | Tags: {item['tags']}")
        print("-"*30)
        
        # --- USER INPUT ---
        print("\n📝 กรอก ID อาหาร (เว้นวรรค เช่น: 1 5 12)")
        
        try:
            eat_input = input("🚀 กินเลย! (Eat Now +5): ")
            eat_objs = get_food_by_ids(eat_input.split())

            like_input = input("👍 ชอบนะ (Like +1): ")
            like_objs = get_food_by_ids(like_input.split())

            dislike_input = input("👎 ไม่เอา (Dislike -5): ")
            dislike_objs = get_food_by_ids(dislike_input.split())
        except KeyboardInterrupt:
            break

        # รวม ID ที่เลือกแล้ว เพื่อตัดออกจาก Candidates
        seen_ids = [f['id'] for f in eat_objs + like_objs + dislike_objs]
        candidates = [f for f in MOCK_FOOD_DB if f['id'] not in seen_ids]

        if not candidates:
            print("❌ เมนูหมดร้านแล้วพี่!")
            break

        # --- SELECT ENGINE ---
        print("\n🤖 เลือกสมองที่จะใช้คิด:")
        print("   [1] KNN Engine     (Scikit-Learn ML - เร็ว/แม่น)")
        print("   [2] Typhoon Engine (LLM Context - ฉลาด)")
        engine_choice = input("👉 เลือก (1 หรือ 2): ").strip()

        recommended_ids = []
        engine_name = ""

        print("\n⏳ กำลังประมวลผล...")

        # --- RUN LOGIC ---
        if engine_choice == '1':
            engine_name = "KNN (ML Vector)"
            recommended_ids = knn_bot.predict(candidates, eat_objs, like_objs, dislike_objs)

        elif engine_choice == '2':
            if not typhoon_bot:
                print("❌ ใช้ Typhoon ไม่ได้ (ไม่มี API Key)")
                continue
            
            engine_name = "Typhoon AI"
            eat_names = [f['name'] for f in eat_objs]
            liked_names = [f['name'] for f in like_objs]
            disliked_names = [f['name'] for f in dislike_objs]
            
            try:
                recommended_ids = asyncio.run(
                    typhoon_bot.predict(candidates, eat_names, liked_names, disliked_names)
                )
            except Exception as e:
                print(f"❌ Typhoon Error: {e}")
                continue
        else:
            print("❌ เลือกผิด!")
            continue

        # --- SHOW RESULT ---
        print("\n" + "⭐"*15 + f" RESULT BY {engine_name} " + "⭐"*15)
        
        found = False
        for rank, fid in enumerate(recommended_ids, 1):
            food = next((f for f in MOCK_FOOD_DB if f['id'] == fid), None)
            if not food: continue
            found = True
            
            print(f"  #{rank} 🍲 {food['name']}")
            print(f"      Tags: {food['tags']}")
        
        if not found:
            print("  (AI หาคำตอบไม่ได้ หรือ Error)")

        print("="*60)
        
        if input("\n🔄 ลองอีกรอบไหม? (y/n): ").lower() != 'y':
            break

if __name__ == "__main__":
    main()