"""
arxiv_client.py
----------------
Fetches papers from the free arXiv API (no key required).
Docs: https://info.arxiv.org/help/api/user-manual.html
"""

import requests
import feedparser


ARXIV_API_URL = "http://export.arxiv.org/api/query"


def search_arxiv(topic: str, max_results: int = 12) -> list[dict]:
    """
    Search arXiv for papers matching a topic.
    Returns a list of dicts with: title, authors, summary, published, url, pdf_url
    """
    params = {
        "search_query": f"all:{topic}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }

    response = requests.get(ARXIV_API_URL, params=params, timeout=15)
    response.raise_for_status()

    feed = feedparser.parse(response.text)

    papers = []
    for entry in feed.entries:
        pdf_url = None
        for link in entry.links:
            if link.get("title") == "pdf" or link.get("type") == "application/pdf":
                pdf_url = link.href
                break

        papers.append({
            "title": entry.title.replace("\n", " ").strip(),
            "authors": [a.name for a in entry.get("authors", [])],
            "summary": entry.summary.replace("\n", " ").strip(),
            "published": entry.get("published", "")[:10],  # YYYY-MM-DD
            "url": entry.link,
            "pdf_url": pdf_url,
        })

    return papers


if __name__ == "__main__":
    # Quick manual test: python arxiv_client.py
    results = search_arxiv("federated learning IoT", max_results=5)
    for p in results:
        print("-", p["title"], "(", p["published"], ")")