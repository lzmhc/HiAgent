import json
import requests
api_key = "sk-xxxxxx"
def bocha_search(query: str, count: int = 5):
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