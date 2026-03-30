"""
AI Food Recommendation Service — Integration Tests

Usage:
  Local:   python test_api.py
  Remote:  API_URL=https://your-app.vercel.app python test_api.py
"""
import os
import sys
import json
import requests

API_URL = os.getenv("API_URL", "http://localhost:8000")

PASS = "✅"
FAIL = "❌"
results = []


def log(name: str, ok: bool, detail: str = ""):
    status = PASS if ok else FAIL
    results.append(ok)
    print(f"  {status} {name}" + (f"  —  {detail}" if detail else ""))


def test_health():
    print("\n── Health Check ──")
    try:
        r = requests.get(f"{API_URL}/api/health", timeout=10)
        log("GET /api/health returns 200", r.status_code == 200)
        body = r.json()
        log("Response has 'status' field", "status" in body)
        log("status == 'ok'", body.get("status") == "ok")
    except Exception as e:
        log("Health reachable", False, str(e))


def test_recommend_cold_start():
    print("\n── POST /api/recommend  (cold start, no history) ──")
    payload = {
        "filter": {
            "tags": [],
            "priceMin": 0,
            "priceMax": 999999
        },
        "history": []
    }
    try:
        r = requests.post(f"{API_URL}/api/recommend", json=payload, timeout=15)
        log("Status 200", r.status_code == 200)
        body = r.json()
        log("Response has 'itemIds'", "itemIds" in body)
        ids = body.get("itemIds", [])
        log(f"Returns items (got {len(ids)})", len(ids) > 0, json.dumps(ids))
        log("itemIds are strings", all(isinstance(i, str) for i in ids))
    except Exception as e:
        log("Cold start request", False, str(e))


def test_recommend_with_filter():
    print("\n── POST /api/recommend  (filter by tags) ──")
    payload = {
        "filter": {
            "tags": ["thai", "spicy"],
            "priceMin": 0,
            "priceMax": 200
        },
        "history": []
    }
    try:
        r = requests.post(f"{API_URL}/api/recommend", json=payload, timeout=15)
        log("Status 200", r.status_code == 200)
        body = r.json()
        ids = body.get("itemIds", [])
        log(f"Returns items (got {len(ids)})", len(ids) > 0, json.dumps(ids))
    except Exception as e:
        log("Filter request", False, str(e))


def test_recommend_with_history():
    print("\n── POST /api/recommend  (with history) ──")
    payload = {
        "filter": {
            "tags": [],
            "priceMin": 0,
            "priceMax": 999999
        },
        "history": [
            {"itemId": "1", "status": "EAT"},
            {"itemId": "2", "status": "LIKE"},
            {"itemId": "11", "status": "LIKE"},
            {"itemId": "5", "status": "DISLIKE"}
        ]
    }
    try:
        r = requests.post(f"{API_URL}/api/recommend", json=payload, timeout=15)
        log("Status 200", r.status_code == 200)
        body = r.json()
        ids = body.get("itemIds", [])
        log(f"Returns items (got {len(ids)})", len(ids) > 0, json.dumps(ids))

        # Items from history should NOT appear in results
        seen = {"1", "2", "11", "5"}
        duplicates = [i for i in ids if i in seen]
        log("No duplicates from history", len(duplicates) == 0,
            f"duplicates={duplicates}" if duplicates else "")
    except Exception as e:
        log("History request", False, str(e))


def test_recommend_max_10():
    print("\n── POST /api/recommend  (max 10 items) ──")
    payload = {
        "filter": {"tags": [], "priceMin": 0, "priceMax": 999999},
        "history": []
    }
    try:
        r = requests.post(f"{API_URL}/api/recommend", json=payload, timeout=15)
        body = r.json()
        ids = body.get("itemIds", [])
        log(f"Returns <= 10 items (got {len(ids)})", len(ids) <= 10)
    except Exception as e:
        log("Max-10 check", False, str(e))


def test_recommend_empty_candidates():
    print("\n── POST /api/recommend  (impossible filter → empty) ──")
    payload = {
        "filter": {
            "tags": ["nonexistent_cuisine_xyz"],
            "priceMin": 0,
            "priceMax": 999999
        },
        "history": []
    }
    try:
        r = requests.post(f"{API_URL}/api/recommend", json=payload, timeout=15)
        log("Status 200", r.status_code == 200)
        body = r.json()
        ids = body.get("itemIds", [])
        log("Returns empty list", len(ids) == 0, json.dumps(ids))
    except Exception as e:
        log("Empty candidates", False, str(e))


def test_recommend_default_filter():
    print("\n── POST /api/recommend  (minimal body, defaults) ──")
    payload = {
        "filter": {},
        "history": []
    }
    try:
        r = requests.post(f"{API_URL}/api/recommend", json=payload, timeout=15)
        log("Status 200 with empty filter object", r.status_code == 200)
        body = r.json()
        log("Returns itemIds", "itemIds" in body)
    except Exception as e:
        log("Default filter", False, str(e))


# ─── Run all tests ───
if __name__ == "__main__":
    print(f"🚀 AI Food Service — Test Suite")
    print(f"   Target: {API_URL}")

    test_health()
    test_recommend_cold_start()
    test_recommend_with_filter()
    test_recommend_with_history()
    test_recommend_max_10()
    test_recommend_empty_candidates()
    test_recommend_default_filter()

    passed = sum(results)
    total = len(results)
    print(f"\n{'='*40}")
    print(f"  Results: {passed}/{total} passed")
    print(f"{'='*40}")

    if passed < total:
        sys.exit(1)
