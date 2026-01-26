# api/mock_db.py

# จำลองข้อมูลเหมือนที่ Main API จะส่งมาให้ในอนาคต
MOCK_FOOD_DB = [
    # --- 1-10: ชุดเดิม ---
    {"id": "1", "name": "ข้าวมันไก่", "tags": ["chinese", "chicken", "rice", "bland"]},
    {"id": "2", "name": "ต้มยำกุ้ง", "tags": ["thai", "spicy", "sour", "soup", "seafood"]},
    {"id": "3", "name": "ส้มตำไทย", "tags": ["isan", "spicy", "sweet", "papaya", "salad"]},
    {"id": "4", "name": "แกงเขียวหวาน", "tags": ["thai", "curry", "coconut", "spicy", "chicken"]},
    {"id": "5", "name": "สเต็กเนื้อ", "tags": ["western", "beef", "grilled", "steak"]},
    {"id": "6", "name": "สลัดผัก", "tags": ["western", "healthy", "vegetable", "salad"]},
    {"id": "7", "name": "ข้าวผัดปู", "tags": ["chinese", "rice", "seafood", "fried"]},
    {"id": "8", "name": "ไก่ทอดเกาหลี", "tags": ["korean", "chicken", "fried", "spicy"]},
    {"id": "9", "name": "ซูชิ", "tags": ["japanese", "rice", "fish", "raw"]},
    {"id": "10", "name": "บิงซู", "tags": ["korean", "dessert", "sweet", "cold"]},

    # --- 11-20: อาหารจานเดียว & เส้น ---
    {"id": "11", "name": "ผัดกะเพราหมูสับ", "tags": ["thai", "spicy", "stir-fried", "pork", "basil"]},
    {"id": "12", "name": "ผัดไทยกุ้งสด", "tags": ["thai", "noodle", "sweet", "fried", "seafood"]},
    {"id": "13", "name": "ก๋วยเตี๋ยวเรือ", "tags": ["thai", "noodle", "soup", "spicy", "pork"]},
    {"id": "14", "name": "ข้าวซอยไก่", "tags": ["northern", "curry", "noodle", "coconut", "spicy"]},
    {"id": "15", "name": "ราเมน", "tags": ["japanese", "noodle", "soup", "salty", "pork"]},
    {"id": "16", "name": "สปาเก็ตตี้คาโบนาร่า", "tags": ["western", "italian", "pasta", "cream", "cheese"]},
    {"id": "17", "name": "ข้าวหมูแดง", "tags": ["chinese", "pork", "rice", "sweet", "roasted"]},
    {"id": "18", "name": "โจ๊กหมู", "tags": ["chinese", "breakfast", "rice", "bland", "soup"]},
    {"id": "19", "name": "ข้าวไข่เจียว", "tags": ["thai", "egg", "rice", "fried", "cheap"]},
    {"id": "20", "name": "สุกี้น้ำ", "tags": ["thai", "soup", "healthy", "vegetable", "seafood"]},

    # --- 21-30: ของกินเล่น & ฟาสต์ฟู้ด ---
    {"id": "21", "name": "หมูสะเต๊ะ", "tags": ["thai", "pork", "grilled", "sweet", "snack"]},
    {"id": "22", "name": "ติ่มซำ", "tags": ["chinese", "steam", "snack", "pork", "shrimp"]},
    {"id": "23", "name": "พิซซ่า", "tags": ["western", "italian", "cheese", "bread", "shared"]},
    {"id": "24", "name": "แฮมเบอร์เกอร์", "tags": ["western", "beef", "bread", "fast-food"]},
    {"id": "25", "name": "เฟรนช์ฟรายส์", "tags": ["western", "snack", "fried", "potato"]},
    {"id": "26", "name": "ทาโกยากิ", "tags": ["japanese", "snack", "seafood", "fried"]},
    {"id": "27", "name": "เกี๊ยวซ่า", "tags": ["japanese", "snack", "fried", "pork"]},
    {"id": "28", "name": "ลูกชิ้นปิ้ง", "tags": ["thai", "snack", "grilled", "pork", "spicy"]},
    {"id": "29", "name": "ไส้กรอกอีสาน", "tags": ["isan", "snack", "grilled", "pork", "sour"]},
    {"id": "30", "name": "ปอเปี๊ยะทอด", "tags": ["chinese", "snack", "fried", "vegetable"]},

    # --- 31-40: ญี่ปุ่น/เกาหลี/หม่าล่า ---
    {"id": "31", "name": "ข้าวหน้าเนื้อ (กิวด้ง)", "tags": ["japanese", "beef", "rice", "sweet", "onion"]},
    {"id": "32", "name": "แกงกะหรี่ญี่ปุ่น", "tags": ["japanese", "curry", "rice", "savory", "pork"]},
    {"id": "33", "name": "ปลาดิบ (ซาชิมิ)", "tags": ["japanese", "raw", "fish", "healthy", "expensive"]},
    {"id": "34", "name": "หม่าล่าหม้อไฟ", "tags": ["chinese", "spicy", "soup", "numbing", "shared"]},
    {"id": "35", "name": "ต็อกบกกี", "tags": ["korean", "spicy", "rice-cake", "snack"]},
    {"id": "36", "name": "ซุปกิมจิ", "tags": ["korean", "soup", "spicy", "kimchi", "tofu"]},
    {"id": "37", "name": "หมูย่างเกาหลี", "tags": ["korean", "grilled", "pork", "bbq", "shared"]},
    {"id": "38", "name": "ชาบูชาบู", "tags": ["japanese", "soup", "healthy", "pork", "shared"]},
    {"id": "39", "name": "เทมปุระ", "tags": ["japanese", "fried", "shrimp", "crispy"]},
    {"id": "40", "name": "บิบิมบับ (ข้าวยำ)", "tags": ["korean", "rice", "vegetable", "spicy", "healthy"]},

    # --- 41-45: อาหารอีสาน/รสจัด ---
    {"id": "41", "name": "ลาบหมู", "tags": ["isan", "spicy", "pork", "sour", "herb"]},
    {"id": "42", "name": "น้ำตกคอหมูย่าง", "tags": ["isan", "spicy", "pork", "grilled", "sour"]},
    {"id": "43", "name": "ไก่ย่างวิเชียร", "tags": ["isan", "chicken", "grilled", "savory"]},
    {"id": "44", "name": "ยำวุ้นเส้น", "tags": ["thai", "spicy", "sour", "salad", "noodle"]},
    {"id": "45", "name": "เล้งแซ่บ", "tags": ["thai", "soup", "spicy", "pork", "sour"]},

    # --- 46-50: ของหวาน ---
    {"id": "46", "name": "ข้าวเหนียวมะม่วง", "tags": ["thai", "dessert", "sweet", "coconut", "fruit"]},
    {"id": "47", "name": "ฮันนี่โทสต์", "tags": ["western", "dessert", "sweet", "bread", "ice-cream"]},
    {"id": "48", "name": "ชานมไข่มุก", "tags": ["taiwanese", "drink", "sweet", "milk"]},
    {"id": "49", "name": "โรตี", "tags": ["thai", "dessert", "sweet", "fried", "pancake"]},
    {"id": "50", "name": "ไอศกรีมกะทิ", "tags": ["thai", "dessert", "sweet", "cold", "coconut"]}
]