# ==============================================================================
# 🍛 MOCK DATABASE (50 Curated Items)
# ออกแบบ Tags ให้ครอบคลุม เพื่อทดสอบ AI/KNN ได้แม่นยำที่สุด
# ==============================================================================

MOCK_FOOD_DB = [
    # --- หมวด: อาหารจานเดียว (ไทย/จีน) ---
    {"id": 1, "name": "ข้าวมันไก่ต้ม", "tags": ["chinese", "rice", "chicken", "bland", "steam"]},
    {"id": 2, "name": "ข้าวมันไก่ทอด", "tags": ["chinese", "rice", "chicken", "fried", "crispy"]},
    {"id": 3, "name": "ข้าวขาหมู", "tags": ["chinese", "rice", "pork", "sweet", "fat", "stew"]},
    {"id": 4, "name": "ข้าวกะเพราหมูสับไข่ดาว", "tags": ["thai", "rice", "spicy", "basil", "pork", "stir-fry"]},
    {"id": 5, "name": "ข้าวผัดปู", "tags": ["chinese", "rice", "seafood", "stir-fry", "bland"]},
    {"id": 6, "name": "ข้าวไข่เจียวหมูสับ", "tags": ["thai", "rice", "egg", "fried", "pork", "budget"]},
    {"id": 7, "name": "ราดหน้าหมูหมัก", "tags": ["chinese", "noodle", "gravy", "pork", "vegetable"]},
    {"id": 8, "name": "ผัดซีอิ๊วเส้นใหญ่", "tags": ["chinese", "noodle", "stir-fry", "sweet", "pork"]},
    {"id": 9, "name": "สุกี้น้ำรวมมิตร", "tags": ["thai", "soup", "vegetable", "healthy", "seafood", "pork"]},
    {"id": 10, "name": "ข้าวหมูแดงหมูกรอบ", "tags": ["chinese", "rice", "pork", "sweet", "sauce", "crispy"]},

    # --- หมวด: อาหารอีสาน/แซ่บ (Tags: isan, spicy) ---
    {"id": 11, "name": "ส้มตำไทย", "tags": ["isan", "spicy", "sour", "sweet", "papaya", "peanut"]},
    {"id": 12, "name": "ส้มตำปูปลาร้า", "tags": ["isan", "spicy", "salty", "strong", "papaya"]},
    {"id": 13, "name": "ลาบหมู", "tags": ["isan", "spicy", "sour", "pork", "herb", "dry"]},
    {"id": 14, "name": "น้ำตกคอหมูย่าง", "tags": ["isan", "spicy", "grilled", "pork", "fat"]},
    {"id": 15, "name": "ไก่ย่างวิเชียรบุรี", "tags": ["isan", "grilled", "chicken", "dry", "garlic"]},
    {"id": 16, "name": "ต้มแซ่บกระดูกอ่อน", "tags": ["isan", "soup", "spicy", "sour", "pork", "herb"]},
    {"id": 17, "name": "ยำวุ้นเส้นโบราณ", "tags": ["thai", "spicy", "sour", "noodle", "pork", "salad"]},
    {"id": 18, "name": "ยำมาม่ารวมมิตร", "tags": ["thai", "spicy", "noodle", "processed", "salad"]},
    {"id": 19, "name": "กุ้งแช่น้ำปลา", "tags": ["thai", "raw", "spicy", "seafood", "salty"]},
    {"id": 20, "name": "ซุปหน่อไม้", "tags": ["isan", "spicy", "vegetable", "strong", "herb"]},

    # --- หมวด: แกง/ต้ม (ไทย) ---
    {"id": 21, "name": "ต้มยำกุ้งน้ำข้น", "tags": ["thai", "soup", "spicy", "sour", "creamy", "seafood"]},
    {"id": 22, "name": "แกงเขียวหวานไก่", "tags": ["thai", "curry", "coconut", "sweet", "spicy", "chicken"]},
    {"id": 23, "name": "พะแนงหมู", "tags": ["thai", "curry", "coconut", "sweet", "salty", "pork"]},
    {"id": 24, "name": "แกงส้มชะอมกุ้ง", "tags": ["thai", "soup", "sour", "spicy", "seafood", "vegetable"]},
    {"id": 25, "name": "ต้มข่าไก่", "tags": ["thai", "soup", "coconut", "sour", "chicken", "herb"]},
    {"id": 26, "name": "แกงจืดเต้าหู้หมูสับ", "tags": ["thai", "soup", "bland", "healthy", "tofu", "pork"]},
    {"id": 27, "name": "ไข่พะโล้", "tags": ["chinese", "soup", "sweet", "egg", "pork", "stew"]},
    {"id": 28, "name": "แกงไตปลา", "tags": ["southern", "curry", "spicy", "salty", "fish", "strong"]},
    {"id": 29, "name": "หมูสามชั้นทอดน้ำปลา", "tags": ["thai", "fried", "salty", "pork", "fat"]},
    {"id": 30, "name": "ข้าวซอยไก่", "tags": ["northern", "curry", "coconut", "noodle", "chicken"]},

    # --- หมวด: นานาชาติ (ฝรั่ง/ญี่ปุ่น/เกาหลี) ---
    {"id": 31, "name": "สเต็กเนื้อโคขุน", "tags": ["western", "beef", "grilled", "meat"]},
    {"id": 32, "name": "สปาเก็ตตี้คาโบนาร่า", "tags": ["western", "noodle", "creamy", "cheese", "bacon"]},
    {"id": 33, "name": "พิซซ่าฮาวายเอี้ยน", "tags": ["western", "flour", "cheese", "pineapple"]},
    {"id": 34, "name": "เบอร์เกอร์เนื้อ", "tags": ["western", "bread", "beef", "fastfood"]},
    {"id": 35, "name": "สลัดผักอกไก่", "tags": ["western", "healthy", "vegetable", "chicken", "clean"]},
    {"id": 36, "name": "ซูชิแซลมอน", "tags": ["japanese", "rice", "raw", "fish", "seafood"]},
    {"id": 37, "name": "ราเมงทงคตสึ", "tags": ["japanese", "soup", "noodle", "pork", "salty"]},
    {"id": 38, "name": "ข้าวหน้าเนื้อ (Gyudon)", "tags": ["japanese", "rice", "beef", "sweet", "onion"]},
    {"id": 39, "name": "ไก่ทอดเกาหลี", "tags": ["korean", "fried", "chicken", "sweet", "spicy"]},
    {"id": 40, "name": "กิมจิชีเก (แกงกิมจิ)", "tags": ["korean", "soup", "spicy", "sour", "vegetable"]},

    # --- หมวด: ของหวาน/เครื่องดื่ม (เอาไว้ Test ว่าระบบแยกของคาวหวานได้ไหม) ---
    {"id": 41, "name": "ข้าวเหนียวมะม่วง", "tags": ["dessert", "sweet", "coconut", "fruit", "thai"]},
    {"id": 42, "name": "บิงซูสตรอว์เบอร์รี่", "tags": ["dessert", "sweet", "cold", "fruit", "korean"]},
    {"id": 43, "name": "ฮันนี่โทสต์", "tags": ["dessert", "sweet", "bread", "icecream", "western"]},
    {"id": 44, "name": "ชานมไข่มุก", "tags": ["drink", "sweet", "milk", "chewy"]},
    {"id": 45, "name": "กาแฟอเมริกาโน่", "tags": ["drink", "bitter", "cold", "caffeine"]},
    {"id": 46, "name": "ไอศกรีมกะทิ", "tags": ["dessert", "sweet", "cold", "coconut", "thai"]},
    {"id": 47, "name": "บัวลอยไข่หวาน", "tags": ["dessert", "sweet", "coconut", "warm", "thai"]},
    {"id": 48, "name": "เค้กช็อกโกแลต", "tags": ["dessert", "sweet", "cake", "western"]},
    {"id": 49, "name": "แพนเค้กเนย", "tags": ["dessert", "sweet", "flour", "breakfast"]},
    {"id": 50, "name": "ผลไม้รวม", "tags": ["dessert", "healthy", "fruit", "vitamin"]}
]

# ฟังก์ชัน Helper สำหรับแปลง ID เป็น Object (ใช้ในไฟล์ Test)
def get_food_by_ids(id_list):
    clean_ids = []
    for i in id_list:
        try:
            clean_ids.append(int(i))
        except:
            pass
    return [f for f in MOCK_FOOD_DB if f['id'] in clean_ids]