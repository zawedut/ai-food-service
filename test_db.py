import os
import psycopg2
import psycopg2.extras
import json
from decimal import Decimal

# ตั้งค่า DATABASE_URL ตรงๆ ตรงนี้ลองรันชั่วคราวได้ครับ
# ตัวอย่าง: "postgresql://user:password@host/dbname?sslmode=require"
DATABASE_URL = "postgresql://neondb_owner:npg_pHW3rRU8YBNS@ep-polished-haze-aeqxzxbs-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
DB_URL = os.getenv("DATABASE_URL", DATABASE_URL)

def fetch_db_data():
    if not DB_URL:
        print("❌ Please provide DATABASE_URL in the script or run `export DATABASE_URL=...` first.")
        return

    try:
        print(f"🔄 Connecting to {DB_URL.split('@')[-1]} ...")
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # 1. ลองเช็คชื่อ Table ทั้งหมดใน database นี้ก่อน เผื่อว่าชื่อ table ไม่ตรง
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='public' AND table_type='BASE TABLE';
        """)
        tables = [r['table_name'] for r in cur.fetchall()]
        print(f"📊 Tables in database: {tables}")
        
        # 2. คาดเดาว่า Table ชื่อ "Item", "items", "Food" หรืออื่นๆ ลองหาที่ใกล้เคียง
        target_table = None
        for t in ["Item", "item", "Items", "items", "food", "Food"]:
            if t in tables:
                target_table = t
                break
                
        if not target_table:
            print("❌ Could not find a table named 'Item' or 'items'.")
            return
            
        print(f"\n✅ Extracting from table: {target_table}")
        
        # 3. ลอง JOIN ระหว่าง Item, Food, และ Tag เพื่อดูโครงสร้างข้อมูลจริงๆ ที่เราต้องการ
        query = """
            SELECT 
                i.id as id,
                f.name as name,
                i."priceMin" as price,
                ARRAY(
                    SELECT t.name 
                    FROM "_foodsToTags" ft
                    JOIN "Tag" t ON ft."B" = t.id
                    WHERE ft."A" = f.id
                ) as tags
            FROM "Item" i
            JOIN "Food" f ON i.food_id = f.id
            LIMIT 10;
        """
        print("\n✅ Executing Join Query for AI Service Format...")
        try:
            cur.execute(query)
        except Exception as e:
            # If Prisma used different A/B column names in implicit m-n table
            print(f"❌ Error with query: {e}")
            cur.execute("ROLLBACK;")
            # Let's just look at Food table directly if join fails
            cur.execute('SELECT * FROM "Food" LIMIT 2;')
            print("Food table sample:", cur.fetchall())
            cur.execute('SELECT * FROM "_foodsToTags" LIMIT 2;')
            print("_foodsToTags sample:", cur.fetchall())
            return
            
        rows = cur.fetchall()
        
        # Helper to dump decimals as string
        import datetime
        class CustomEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, Decimal):
                    return float(obj)
                if isinstance(obj, datetime.datetime):
                    return obj.isoformat()
                return super(CustomEncoder, self).default(obj)
        
        print("\n--- SAMPLE FORMATTED DATA (First 10 items) ---")
        print(json.dumps(rows, indent=2, ensure_ascii=False, cls=CustomEncoder))
        
        # 4. นับ Item ทั้งหมด
        cur.execute('SELECT COUNT(*) as count FROM "Item";')
        count = cur.fetchone()['count']
        print(f"\n✅ Total items in table: {count}")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fetch_db_data()
