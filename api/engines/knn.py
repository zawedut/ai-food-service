import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MultiLabelBinarizer
from collections import Counter

class KNNEngine:
    def __init__(self):
        # ใช้ Cosine Similarity สำหรับเปรียบเทียบ Tags
        self.model = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=100)
        self.encoder = MultiLabelBinarizer()
        self.food_ids = [] 
        self.is_trained = False
        self.food_vectors = None
        self.food_metadata = {}  # เก็บข้อมูลเพิ่มเติม
        
    def train(self, all_foods):
        """
        Train KNN model with enhanced feature extraction
        """
        if not all_foods:
            print("⚠️ Warning: No food data to train KNN")
            self.is_trained = False
            return
        
        # 1. เก็บ IDs และ metadata
        self.food_ids = [str(f['id']) for f in all_foods]
        self.food_metadata = {
            str(f['id']): {
                'tags': f.get('tags', []),
                'category': f.get('category', 'unknown'),
                'popularity': f.get('popularity', 0),
                'name': f.get('name', '')
            } for f in all_foods
        }
        
        # 2. Extract tags
        all_tags = [f.get('tags', []) for f in all_foods]
        
        if not any(all_tags):  # ถ้าไม่มี tags เลย
            print("⚠️ No tags found in data")
            return
        
        # 3. Create vectors
        self.food_vectors = self.encoder.fit_transform(all_tags)
        
        # 4. Train model
        self.model.fit(self.food_vectors)
        self.is_trained = True
        
        print(f"✅ KNN Trained: {len(all_foods)} items, {len(self.encoder.classes_)} unique tags")
        
    # 🌟 แกะ 1: เพิ่มตัวแปร filter_tags เข้ามาในฟังก์ชัน predict
    def predict(self, candidates, eat_now_objs, liked_objs, disliked_objs, filter_tags=None, boost_recent=False):
        """
        Enhanced prediction with multiple strategies
        """
        if not self.is_trained:
            print("❌ KNN not trained yet!")
            return []
        
        # 1. สร้าง User Profile Vector (ส่ง filter_tags เข้าไปคำนวณด้วย)
        user_vector = self._build_user_vector(
            eat_now_objs, 
            liked_objs, 
            disliked_objs,
            filter_tags, # <-- ส่งค่าไปตรงนี้
            boost_recent
        )
        
        # 2. หา Candidates ที่เหมาะสม
        candidate_ids_set = {str(c['id']) for c in candidates}
        
        # 3. คำนวณ similarity scores
        scored_candidates = []
        
        for candidate in candidates:
            cand_id = str(candidate['id'])
            
            try:
                idx = self.food_ids.index(cand_id)
                food_vector = self.food_vectors[idx]
                
                # คำนวณ cosine similarity
                similarity = self._cosine_similarity(user_vector, food_vector)
                
                # เพิ่มโบนัสจาก metadata
                bonus = self._calculate_bonus(
                    cand_id, 
                    eat_now_objs, 
                    liked_objs
                )
                
                final_score = similarity + bonus
                scored_candidates.append((cand_id, final_score))
                
            except ValueError:
                continue
        
        # 4. เรียงตาม score
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # 5. ใช้ KNN ช่วยเพิ่มความหลากหลาย
        knn_recommendations = self._get_knn_neighbors(user_vector, candidate_ids_set)
        
        # 6. ผสมผลลัพธ์: 70% จาก scoring, 30% จาก KNN
        top_scored = [item[0] for item in scored_candidates[:15]]
        
        final_results = []
        seen = set()
        
        for food_id in top_scored:
            if food_id not in seen:
                final_results.append(food_id)
                seen.add(food_id)
                if len(final_results) >= 10:
                    break
        
        for food_id in knn_recommendations:
            if food_id not in seen and len(final_results) < 10:
                final_results.append(food_id)
                seen.add(food_id)
        
        print(f"🎯 KNN Recommendations (Total={len(final_results)} items)")
        return final_results
    
    # 🌟 แกะ 2: รับค่า filter_tags เข้ามา
    def _build_user_vector(self, eat_now_objs, liked_objs, disliked_objs, filter_tags, boost_recent):
        """
        สร้าง vector ที่แทนความชอบของ User พร้อมชั่งน้ำหนัก Filter ปัจจุบัน
        """
        user_vector = np.zeros(self.food_vectors.shape[1])
        
        def add_weighted_tags(objs, weight, apply_boost=False):
            if not objs:
                return np.zeros(self.food_vectors.shape[1])
            
            tags_list = [f.get('tags', []) for f in objs]
            if not tags_list:
                return np.zeros(self.food_vectors.shape[1])
            
            try:
                vecs = self.encoder.transform(tags_list)
            except:
                return np.zeros(self.food_vectors.shape[1])
            
            if apply_boost and len(objs) > 0:
                weights = np.linspace(1.0, 1.5, len(vecs))[::-1]
                weighted_vecs = vecs * weights.reshape(-1, 1)
                combined = np.sum(weighted_vecs, axis=0)
            else:
                combined = np.sum(vecs, axis=0)
            
            return combined * weight
        
        v_eat = add_weighted_tags(eat_now_objs, 6.0, boost_recent)
        v_like = add_weighted_tags(liked_objs, 2.0, boost_recent)
        v_hate = add_weighted_tags(disliked_objs, -7.0, False)
        
        # 🌟 แกะ 3: พลังของตัวกรอง (The Filter Overrider)
        # ถ้ายูสเซอร์ระบุ Tags ตอนนี้ แปลว่า "ต้องเอาอันนี้แหละ!" 
        # เราจึงคูณน้ำหนักไปเลย +15.0 เพื่อให้ชนะประวัติในอดีตทั้งหมด
        v_filter = np.zeros(self.food_vectors.shape[1])
        if filter_tags:
            try:
                # encoder.transform ต้องการ list of lists
                vecs = self.encoder.transform([filter_tags])
                v_filter = np.sum(vecs, axis=0) * 15.0  # น้ำหนักระดับเทพเจ้า
                print(f"🔍 KNN Context: Heavy focus on tags {filter_tags}")
            except Exception as e:
                pass
        
        user_vector = v_eat + v_like + v_hate + v_filter
        
        # Normalize vector
        norm = np.linalg.norm(user_vector)
        if norm > 0:
            user_vector = user_vector / norm
        
        return user_vector
    
    def _cosine_similarity(self, vec1, vec2):
        if hasattr(vec2, 'toarray'):
            vec2 = vec2.toarray().flatten()
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot_product / (norm1 * norm2)
    
    def _calculate_bonus(self, food_id, eat_now_objs, liked_objs):
        bonus = 0.0
        metadata = self.food_metadata.get(food_id, {})
        if eat_now_objs:
            eat_now_categories = [obj.get('category', '') for obj in eat_now_objs]
            if metadata.get('category') in eat_now_categories:
                bonus += 0.1
        
        popularity = metadata.get('popularity', 0)
        if popularity > 0:
            bonus += min(popularity / 1000, 0.05)
        return bonus
    
    def _get_knn_neighbors(self, user_vector, candidate_ids_set):
        try:
            n_neighbors = min(30, len(self.food_ids))
            distances, indices = self.model.kneighbors(
                [user_vector], 
                n_neighbors=n_neighbors
            )
            
            recommended = []
            for idx in indices[0]:
                food_id = self.food_ids[idx]
                if food_id in candidate_ids_set:
                    recommended.append(food_id)
                    if len(recommended) >= 15:
                        break
            return recommended
        except Exception as e:
            return []
    
    def get_stats(self):
        if not self.is_trained:
            return {"trained": False}
        return {
            "trained": True,
            "total_foods": len(self.food_ids),
            "unique_tags": len(self.encoder.classes_),
            "top_tags": list(self.encoder.classes_[:10])
        }