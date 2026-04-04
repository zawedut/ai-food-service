import requests
import json
import asyncio
import random
from typing import List

class TyphoonEngine:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://api.opentyphoon.ai/v1/chat/completions"
    
    async def predict(self, candidates, eat_now_names, liked_names, disliked_names, favorite_tags=None):
        """
        AI-powered recommendation with context awareness
        """
        # 1. Smart sampling - คัดมา 20 เมนูให้ AI เลือก จะได้มีตัวเลือกเยอะพอ
        shortlist = self._smart_sample(candidates, favorite_tags, size=20)
        
        # 2. สร้าง Prompt ที่ AI ดิ้นหลุดไม่ได้
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
            "model": "typhoon-v2.1-12b-instruct",
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a recommendation API. You must output ONLY a valid JSON array of strings. No explanations."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            # ปรับลด Temperature ลงเพื่อให้ AI ตอบเป็น JSON เป๊ะๆ ไม่สร้างสรรค์คำพูดเกินไป
            "temperature": 0.3, 
            "max_tokens": 2048,
            "top_p": 0.85
        }
        
        # 4. Execute request
        loop = asyncio.get_running_loop()
        try:
            response = await loop.run_in_executor(
                None, 
                lambda: requests.post(self.url, headers=headers, json=payload, timeout=12)
            )
            
            if response.status_code != 200:
                print(f"❌ Typhoon API Error: {response.status_code}")
                print(f"🔍 Error Detail: {response.text}")
                return self._fallback_recommendation(shortlist, favorite_tags)
            
            # 5. Parse response
            content = response.json()['choices'][0]['message']['content']
            print(f"🤖 Typhoon Raw Response: {content[:150]}...")
            
            result_ids = self._parse_ai_response(content, shortlist)
            
            # 6. Validate and return
            if len(result_ids) < 3:
                print("⚠️ Typhoon returned too few valid IDs, triggering fallback...")
                return self._fallback_recommendation(shortlist, favorite_tags)
            
            return result_ids[:10]
            
        except Exception as e:
            print(f"❌ Typhoon Prediction Exception: {e}")
            return self._fallback_recommendation(shortlist, favorite_tags)
    
    def _smart_sample(self, candidates, favorite_tags, size=20):
        """
        เลือก candidates แบบฉลาด เน้นอันที่ตรง Tag ไปให้ AI ดู
        """
        if not favorite_tags or len(candidates) <= size:
            return random.sample(candidates, min(size, len(candidates)))
        
        matching = []
        others = []
        
        for c in candidates:
            food_tags = set(c.get('tags', []))
            if food_tags.intersection(set(favorite_tags)):
                matching.append(c)
            else:
                others.append(c)
        
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
        Prompt ใหม่: บังคับให้ตอบเป็น ["id", "id"] ชัดเจน
        """
        food_list = []
        for f in foods:
            tags_str = ",".join(f.get('tags', [])[:3])
            # ส่ง ID และ Name ให้ AI ดู
            food_list.append(f"ID: {f['id']} | Name: {f['name']} [{tags_str}]")
        
        foods_str = "\n".join(food_list)
        
        context_parts = []
        if eat_now: context_parts.append(f"Most Loved: {', '.join(eat_now[:3])}")
        if liked: context_parts.append(f"Liked: {', '.join(liked[:3])}")
        if disliked: context_parts.append(f"Disliked: {', '.join(disliked[:3])}")
        if favorite_tags: context_parts.append(f"Favorite Tags: {', '.join(favorite_tags)}")
        
        context = "\n".join(context_parts) if context_parts else "New User (No history)"
        
        prompt = f"""Based on the user profile, select up to 10 best food items from the options.

USER PROFILE:
{context}

OPTIONS:
{foods_str}

CRITICAL INSTRUCTIONS:
1. Return ONLY a JSON array of the selected IDs.
2. Every ID MUST be a string enclosed in double quotes.
3. Do not include markdown (```json), explanations, or any other text.

CORRECT FORMAT EXAMPLE:
["cmndfk2sb0010hcus", "cmndfk2sb0015hcus", "cmndfk2sb000ahcus"]
"""
        return prompt
    
    def _parse_ai_response(self, content, shortlist):
        """
        Bulletproof Parser: ไม่มีทางพังแม้อ่าน JSON ไม่ออก
        """
        # 1. ทำความสะอาดข้อความขยะ
        clean = content.strip().replace("```json", "").replace("```", "").strip()
        
        # 2. ถ้ามีคำอธิบายติดมา ให้ตัดเอาเฉพาะส่วนที่เป็นก้อน Array [...]
        if '[' in clean and ']' in clean:
            start = clean.find('[')
            end = clean.rfind(']') + 1
            clean = clean[start:end]
            
        raw_ids = []
        # 3. ลองใช้ JSON มาตรฐานก่อน
        try:
            raw_ids = json.loads(clean)
        except json.JSONDecodeError:
            print("⚠️ Standard JSON parsing failed. Using robust string extractor...")
            # 4. แผนสำรอง: สับสายอักขระ (String manipulation)
            clean_str = clean.replace("[", "").replace("]", "").replace('"', "").replace("'", "")
            raw_ids = [item.strip() for item in clean_str.split(",") if item.strip()]
        
        # 5. ตรวจสอบความถูกต้องและดึงเฉพาะ ID ที่มีจริง
        valid_ids = []
        valid_id_set = {str(f['id']) for f in shortlist}
        
        for item in raw_ids:
            str_id = str(item).strip() # บังคับเป็น String เท่านั้น ลบช่องว่าง
            if str_id in valid_id_set:
                if str_id not in valid_ids: # กันซ้ำ
                    valid_ids.append(str_id)
        
        print(f"✅ Extracted {len(valid_ids)} valid IDs from Typhoon")
        return valid_ids
    
    def _fallback_recommendation(self, shortlist, favorite_tags):
        """
        Fallback สบายใจ หายห่วง
        """
        print("🔄 Using fallback logic")
        if not favorite_tags:
            return [f['id'] for f in random.sample(shortlist, min(10, len(shortlist)))]
        
        scored = []
        for food in shortlist:
            food_tags = set(food.get('tags', []))
            score = len(food_tags.intersection(set(favorite_tags)))
            scored.append((food['id'], score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        return [item[0] for item in scored[:10]]