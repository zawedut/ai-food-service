from fastapi.testclient import TestClient
from api.index import app
client = TestClient(app)
res = client.post("/api/recommend", json={"history":[]})
print("POST /api/recommend -> Status:", res.status_code)
