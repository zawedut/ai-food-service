import requests
import json
import asyncio
import random

class TyphoonEngine:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://api.opentyphoon.ai/v1/chat/completions"

    async def predict(self, candidates, eat_now_names, liked_names, disliked_names):
        # 1. ลดขนาด Prompt: สุ่มมาแค่ 15 ตัวพอ (กัน Token ล้น)
        if len(candidates) > 15:
            shortlist = random.sample(candidates, 15)
        else:
            shortlist = candidates

        # Format: "id:Name(tags)"
        cand_str = ", ".join([f"{c['id']}:{c['name']}({','.join(c['tags'])})" for c in shortlist])
        
        prompt = f"""
        User Taste:
        - SUPER LIKE: {eat_now_names}
        - LIKE: {liked_names}
        - HATE: {disliked_names}

        Task: Pick 5 IDs from the list below that match 'SUPER LIKE'.
        List: [{cand_str}]
        
        Output: JSON List of IDs ONLY e.g. [10, 25].
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "typhoon-v2.1-12b-instruct",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.4,
            "max_tokens": 2048, # ตั้งไว้เยอะๆ กันเหนียว
            "top_p": 0.9
        }

        # ยิง Request
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, lambda: requests.post(
            self.url, headers=headers, json=payload
        ))
        
        if response.status_code != 200:
            print(f"❌ API Error Details: {response.text}")
            raise Exception(f"Typhoon API Error: {response.text}")
            
        content = response.json()['choices'][0]['message']['content']
        
        # [DEBUG] โชว์ให้เห็นเลยว่า AI ตอบอะไรมา
        print(f"\n[DEBUG] Raw AI Response: {content}")

        # Clean string
        clean_content = content.replace("```json", "").replace("```", "").strip()
        
        try:
            raw_ids = json.loads(clean_content)
            
            # [FIX] บังคับแปลงเป็น int ทุกตัว (กัน AI ส่ง string มา)
            clean_ids = []
            for item in raw_ids:
                try:
                    clean_ids.append(int(item))
                except:
                    continue # ถ้าแปลงไม่ได้ให้ข้ามไป
            
            return clean_ids

        except Exception as e:
            print(f"❌ JSON Parse Error: {e} | Content: {clean_content}")
            return [] # ถ้าพังให้ส่ง list ว่างไปก่อน