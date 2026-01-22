import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MultiLabelBinarizer

class KNNEngine:
    def __init__(self):
        self.model = NearestNeighbors(metric='cosine', algorithm='brute')
        self.encoder = MultiLabelBinarizer()
        self.food_ids = [] # เก็บ ID ไว้ map กลับตอนได้ผลลัพธ์
        self.is_trained = False
        self.food_vectors = None

    def train(self, all_foods):
        """
        [ML Training]
        รับข้อมูลอาหารทั้งหมดใน DB มาเพื่อสร้าง Vector Space
        """
        if not all_foods:
            print("⚠️ Warning: No food data to train KNN")
            return

        # 1. เตรียมข้อมูล
        self.food_ids = [f['id'] for f in all_foods]
        all_tags = [f['tags'] for f in all_foods]

        # 2. แปลง Tags เป็นตัวเลข (Vectorization)
        # เช่น ["spicy", "thai"] -> [0, 1, 1, 0, ...]
        self.food_vectors = self.encoder.fit_transform(all_tags)

        # 3. Train Model (จำตำแหน่งของอาหารทุกจานในอวกาศ Vector)
        self.model.fit(self.food_vectors)
        self.is_trained = True
        print(f"✅ KNN Trained with {len(all_foods)} items (Vector Size: {self.food_vectors.shape[1]})")

    def predict(self, candidates, eat_now_objs, liked_objs, disliked_objs):
        if not self.is_trained:
            print("❌ KNN ยังไม่ได้ Train! (ต้องเรียก .train() ก่อน)")
            return []

        # 1. สร้าง User Profile Vector (เวกเตอร์ตัวแทนความชอบ)
        # เริ่มต้นเป็นศูนย์ทั้งหมด
        user_vector = np.zeros(self.food_vectors.shape[1])

        # Helper: ฟังก์ชันบวกคะแนนเข้า Vector
        def add_weight(objs, weight):
            if not objs: return
            tags = [f['tags'] for f in objs]
            # แปลง tags กลุ่มนี้เป็น vector
            vecs = self.encoder.transform(tags) 
            # เอา vector มารวมกัน แล้วคูณน้ำหนัก
            # axis=0 คือรวมแนวตั้ง (รวมทุกจานเข้าด้วยกัน)
            combined = np.sum(vecs, axis=0)
            return combined * weight

        # บวกคะแนนตามสูตร (Weight Tuning)
        v_eat = add_weight(eat_now_objs, 5.0)  # ชอบมาก ให้ค่าเยอะๆ
        v_like = add_weight(liked_objs, 1.0)   # ชอบเฉยๆ
        v_hate = add_weight(disliked_objs, -5.0) # เกลียด (ติดลบ)

        # รวมร่างเป็น User Vector เดียว
        if v_eat is not None: user_vector += v_eat
        if v_like is not None: user_vector += v_like
        if v_hate is not None: user_vector += v_hate

        # 2. หาเพื่อนบ้านที่ใกล้ที่สุด (Nearest Neighbors)
        # เราจะหามาเผื่อเยอะๆ ก่อน (เช่น 50 อัน) แล้วค่อยกรองเอาเฉพาะ Candidates
        n_neighbors = min(50, len(self.food_ids))
        distances, indices = self.model.kneighbors([user_vector], n_neighbors=n_neighbors)
        
        # 3. แปลง Index กลับเป็น Food ID แล้วคัดเลือก
        recommended_ids = []
        candidate_ids_set = set(c['id'] for c in candidates)

        for idx in indices[0]:
            food_id = self.food_ids[idx]
            
            # ถ้า ID นี้อยู่ในรายการ Candidates (คือยังไม่เคยกิน) -> เลือกเลย
            if food_id in candidate_ids_set:
                recommended_ids.append(food_id)
                if len(recommended_ids) >= 5: # ครบ 5 อันแล้วจบ
                    break
        
        return recommended_ids