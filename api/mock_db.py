# api/mock_db.py
import random

# จำลองข้อมูลเหมือนที่ Main API จะส่งมาให้ในงานแข่ง
# เพิ่มฟิลด์ price เพื่อให้รองรับ Filter priceMin, priceMax
raw_data = [
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
]

# สุ่มราคา 40 - 300 บาทเพื่อให้ทดสอบ filter ได้
MOCK_FOOD_DB = []
for item in raw_data:
    item_with_price = item.copy()
    item_with_price["price"] = random.randint(4, 30) * 10 # 40, 50, ..., 300
    MOCK_FOOD_DB.append(item_with_price)
