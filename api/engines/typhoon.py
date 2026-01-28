import requests
import json
import asyncio
import random
from typing import List

class TyphoonEngine:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://api.opentyphoon.ai/v1/chat/completions"
        self.conversation_memory = []  # เก็บ context การแนะนำครั้งก่อน
    
    async def predict(self, candidates, eat_now_names, liked_names, disliked_names, favorite_tags=None):
        """
        AI-powered recommendation with context awareness
        """
        # 1. Smart sampling - เลือก candidates แบบฉลาด
        shortlist = self._smart_sample(candidates, favorite_tags, size=20)
        
        # 2. สร้าง Prompt ที่รัดกุมและชัดเจน
        prompt = self._build_smart_prompt(
            shortlist, 
            eat_now_names, 
            liked_names, 
            disliked_names,
            favorite_tags
        )
        
        # 3. Call API with optimized settings
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "typhoon-v2.5-30b-a3b-instruct",
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a food recommendation expert. Analyze user preferences and return ONLY a JSON array of food IDs."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": 0.5,
            "max_tokens": 1024,  # เพิ่มเป็น 1024 เพื่อรองรับ prompt ที่ยาว
            "top_p": 0.85
        }
        
        # 4. Execute request
        loop = asyncio.get_running_loop()
        try:
            response = await loop.run_in_executor(
                None, 
                lambda: requests.post(self.url, headers=headers, json=payload, timeout=10)
            )
            
            if response.status_code != 200:
                print(f"❌ Typhoon API Error: {response.status_code}")
                print(f"   Response: {response.text}")
                return self._fallback_recommendation(shortlist, favorite_tags)
            
            # 5. Parse response
            content = response.json()['choices'][0]['message']['content']
            print(f"🤖 Typhoon Response: {content[:100]}...")
            
            result_ids = self._parse_ai_response(content, shortlist)
            
            # 6. Validate and return
            if len(result_ids) < 3:
                print("⚠️ Typhoon returned too few results, using fallback")
                return self._fallback_recommendation(shortlist, favorite_tags)
            
            return result_ids[:10]
            
        except Exception as e:
            print(f"❌ Typhoon Exception: {e}")
            return self._fallback_recommendation(shortlist, favorite_tags)
    
    def _smart_sample(self, candidates, favorite_tags, size=20):
        """
        เลือก candidates แบบฉลาด โดยให้ความสำคัญกับ tags ที่ user ชอบ
        """
        # ลด size ลงเหลือ 12 เพื่อให้ prompt สั้นลง
        size = min(size, 12)
        
        if not favorite_tags or len(candidates) <= size:
            return random.sample(candidates, min(size, len(candidates)))
        
        # แบ่งเป็น 2 กลุ่ม
        matching = []
        others = []
        
        for c in candidates:
            food_tags = set(c.get('tags', []))
            if food_tags.intersection(set(favorite_tags)):
                matching.append(c)
            else:
                others.append(c)
        
        # เลือก 70% จากที่ match, 30% จากอื่นๆ (เพื่อความหลากหลาย)
        target_matching = int(size * 0.7)
        target_others = size - target_matching
        
        selected = []
        if matching:
            selected.extend(random.sample(matching, min(target_matching, len(matching))))
        if others and len(selected) < size:
            selected.extend(random.sample(others, min(target_others, len(others))))
        
        return selected
    
    def _build_smart_prompt(self, foods, eat_now, liked, disliked, favorite_tags):
        """
        สร้าง Prompt ที่กระชับและมีประสิทธิภาพ (ลด tokens)
        """
        # Format food list แบบกระชับมาก
        food_list = []
        for f in foods:
            tags_str = ",".join(f.get('tags', [])[:2])  # ลดเหลือแค่ 2 tags
            # ใช้รูปแบบสั้นๆ: ID:Name[tags]
            food_list.append(f"{f['id']}:{f['name'][:25]}[{tags_str}]")  # ตัดชื่อสั้นๆ
        
        foods_str = " | ".join(food_list)
        
        # สร้าง context แบบกระชับ
        parts = []
        
        if eat_now:
            parts.append(f"LOVES: {', '.join(eat_now[:3])}")  # ลดเหลือ 3
        
        if liked:
            parts.append(f"LIKES: {', '.join(liked[:3])}")  # ลดเหลือ 3
        
        if disliked:
            parts.append(f"HATES: {', '.join(disliked[:2])}")  # ลดเหลือ 2
        
        if favorite_tags:
            parts.append(f"FAV_TAGS: {', '.join(favorite_tags[:3])}")  # ลดเหลือ 3
        
        context = " | ".join(parts)
        
        # Prompt สั้นกระชับ
        prompt = f"""User: {context}

Options: {foods_str}

Pick 5 IDs matching LOVES. Return: [12,45,78]"""
        
        return prompt
    
    def _parse_ai_response(self, content, shortlist):
        """
        Parse AI response แบบ robust
        """
        # ลบ markdown formatting
        clean = content.replace("```json", "").replace("```", "").strip()
        
        # ลบ text อธิบายถ้ามี
        if '\n' in clean:
            lines = clean.split('\n')
            for line in lines:
                if line.strip().startswith('['):
                    clean = line.strip()
                    break
        
        try:
            # Parse JSON
            raw_ids = json.loads(clean)
            
            # Validate และแปลงเป็น string
            valid_ids = []
            valid_id_set = {str(f['id']) for f in shortlist}
            
            for item in raw_ids:
                # ลองแปลงเป็น string
                str_id = str(int(item)) if isinstance(item, (int, float)) else str(item)
                
                # ตรวจสอบว่า ID นี้อยู่ใน shortlist หรือไม่
                if str_id in valid_id_set:
                    valid_ids.append(str_id)
            
            print(f"✅ Parsed {len(valid_ids)} valid IDs from Typhoon")
            return valid_ids
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON Parse Failed: {e}")
            print(f"   Content: {clean}")
            return []
        except Exception as e:
            print(f"❌ Parse Exception: {e}")
            return []
    
    def _fallback_recommendation(self, shortlist, favorite_tags):
        """
        Fallback ถ้า AI ล้ม - ใช้ logic ง่ายๆ
        """
        print("🔄 Using fallback recommendation")
        
        if not favorite_tags:
            # สุ่มเลย
            return [f['id'] for f in random.sample(shortlist, min(8, len(shortlist)))]
        
        # เรียงตาม tags ที่ตรงกับ favorite
        scored = []
        for food in shortlist:
            food_tags = set(food.get('tags', []))
            score = len(food_tags.intersection(set(favorite_tags)))
            scored.append((food['id'], score))
        
        # เรียงตาม score สูงสุด
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return [item[0] for item in scored[:8]]