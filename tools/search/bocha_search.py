import json
import os
import requests
from pathlib import Path


def _load_api_key() -> str:
    """从 config/config.json 加载 bocha API key"""
    config_path = Path(__file__).parent.parent.parent / "config" / "config.json"
    with open(config_path) as f:
        config = json.load(f)
    return config.get("bocha_api", "")


def bocha_search(query: str, count: int = 5):
    api_key = _load_api_key()
    url = "https://api.bocha.cn/v1/web-search"
    data = json.dumps({
        "query": query,
        "count": count
    })
    headers = {
        'Content-Type': 'application/json',
        "Authorization": "Bearer " + api_key
    }
    response = requests.post(
        url,
        data=data,
        headers=headers,
        timeout=10
    )
    return response.json()

if __name__ == '__main__':
    print(bocha_search("佛得角世界杯"))
