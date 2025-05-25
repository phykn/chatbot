import requests
from typing import List, Dict
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS


def ddg_search(
    keywords: str,
    region: str = "kr-kr",
    num_content: int = 3,
    max_try: int = 5
) -> List[Dict[str, str]]:
    
    with DDGS() as ddgs:
        results = ddgs.text(
            keywords = keywords,
            region = region,
            safesearch = "moderate",
            timelimit = "y",
            max_results = max_try
        )

    outputs = []

    if not results:
        return outputs

    for result in results:
        if len(outputs) >= num_content:
            break

        try:
            title = result.get("title", "").strip()
            summary = result.get("body", "").strip()
            url = result.get("href", "").strip()

            if not url:
                continue

            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            response = requests.get(url, timeout=10, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "aside"]):
                tag.decompose()

            content = soup.get_text(separator=" ", strip=True)
            if content:
                outputs.append({"title": title, "summary": summary, "content": content})

        except (requests.RequestException, UnicodeDecodeError, AttributeError):
            continue

    return outputs