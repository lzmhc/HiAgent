import json
import requests
from pathlib import Path

def _load_api_key() -> str:
    config_path = Path(__file__).parent.parent.parent / "config" / "config.json"
    with open(config_path) as f:
        config = json.load(f)
    return config.get("brave_api", "")

def brave_search(query: str, count: int = 5):
    api_key = _load_api_key()
    url = "https://api.search.brave.com/res/v1/web/search"
    # proxies = {
    #     "http": "http://127.0.0.1:7897",
    #     "https": "http://127.0.0.1:7897"
    # }
    data = json.dumps({
        "q": query,
        "search_lang": "ca",
        "count": count
    })
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key
    }
    response = requests.post(
        url,
        data=data,
        headers=headers,
        # proxies=proxies,
        timeout=10
    )
    return response.json()

if __name__ == '__main__':
    print(brave_search("""{"query":"星穹列车 崩坏 星穹铁道 官方 星穹列车 帕姆 姬子 阿基维利","count":5}"""))
