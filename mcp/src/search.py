import requests
from typing import List, Dict
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from transformers import AutoTokenizer


tokenizer = AutoTokenizer.from_pretrained("./tokenizer/qwen3-4b-awq")


def get_content(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    response = requests.get(url, timeout=10, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "aside"]):
        tag.decompose()

    return soup.get_text(separator=" ", strip=True)


def ddg_search(
    keywords: str,
    region: str = "wt-wt",
    max_results: int = 10,
    num_token_page: int = 2000,
    num_token_limit: int = 8000
) -> List[Dict[str, str]]:
    
    with DDGS() as ddgs:
        pages = ddgs.text(
            keywords = keywords,
            region = region,
            safesearch = "moderate",
            timelimit = None,
            max_results = max_results
        )

    outputs = []
    remain_tokens = num_token_limit

    for page in pages:
        if remain_tokens <= 0:
            break

        title = page.get("title", "").strip()
        summary = page.get("body", "").strip()
        url = page.get("href", "").strip()

        try:
            content = get_content(url)
        except:
            continue

        if not content.strip():
            continue

        tokens = tokenizer.encode(content)
        num_tokens = min([len(tokens), num_token_page, remain_tokens])

        if num_tokens == 0:
            continue

        content = tokenizer.decode(tokens[:num_tokens], skip_special_tokens=True)
        remain_tokens -= num_tokens

        output = {
            "title": title,
            "summary": summary,
            "url": url,
            "content": content,
            "num_tokens": num_tokens
        }
        outputs.append(output)

    return outputs