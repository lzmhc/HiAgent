import json
import requests
api_key = "xxxxx"
url = "https://api.search.brave.com/res/v1/web/search"
proxies = {
    "http": "http://127.0.0.1:7897",
    "https": "http://127.0.0.1:7897"
}
def brave_search(query: str, count: int = 5):
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
        proxies=proxies,
        timeout=10
    )
    return response.json()

if __name__ == '__main__':
    pass