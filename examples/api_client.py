import json
import os
from urllib import request


BASE_URL = os.environ.get("MVP_API_BASE_URL", "http://127.0.0.1:8000")


def get(path: str):
    with request.urlopen(f"{BASE_URL}{path}", timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def post(path: str, payload: dict):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        f"{BASE_URL}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def print_json(title: str, data: dict):
    print(f"\n== {title} ==")
    print(json.dumps(data, ensure_ascii=False, indent=2))

