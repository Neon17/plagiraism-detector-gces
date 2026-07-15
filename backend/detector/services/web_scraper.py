"""External plagiarism (proposal step 5): scrape web pages and compare.

Search via the DuckDuckGo HTML endpoint (no API key). Always degrades gracefully:
if search fails, the caller can pass explicit URLs. The demo never dies on a bad network.
"""
from __future__ import annotations

import re

import requests
from bs4 import BeautifulSoup
from sentence_transformers import util

from . import highlighter
from .preprocess import keywords
from .similarity import DEFAULT_THRESHOLD, SbertEngine

_HEADERS = {'User-Agent': 'Mozilla/5.0 (plagiarism-detector)'}


def search_urls(query: str, max_results: int = 10) -> list[str]:
    try:
        r = requests.post('https://html.duckduckgo.com/html/',
                          data={'q': query}, headers=_HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        urls = []
        for a in soup.select('a.result__a'):
            href = a.get('href')
            if href and href.startswith('http'):
                urls.append(href)
            if len(urls) >= max_results:
                break
        return urls
    except Exception:
        return []


def scrape_text(url: str, max_chars: int = 5000) -> str:
    try:
        r = requests.get(url, headers=_HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
            tag.decompose()
        text = ' '.join(p.get_text(' ', strip=True) for p in soup.find_all('p'))
        return re.sub(r'\s+', ' ', text)[:max_chars]
    except Exception:
        return ''


def check_web(text: str, urls: list[str] | None = None, max_sources: int = 10,
              threshold: float = DEFAULT_THRESHOLD) -> list[dict]:
    """Compare a document against web pages. Returns scored sources, highest first."""
    if not urls:
        urls = search_urls(' '.join(keywords(text)), max_results=max_sources)
    urls = urls[:max_sources]

    doc_emb = SbertEngine.embed([text])[0]
    results = []
    for url in urls:
        page = scrape_text(url)
        if not page:
            continue
        page_emb = SbertEngine.embed([page])[0]
        score = float(util.cos_sim(doc_emb, page_emb))
        # Sentence-level highlights: which of the user's sentences appear on this page.
        detail = highlighter.compare_documents(text, page, threshold=threshold)
        # Only surface pages that actually share copied sentences. A high document-level
        # score alone is just topical overlap, not plagiarism -- skip those.
        if detail['percent_copied'] <= 0:
            continue
        results.append({
            'url': url,
            'score': round(score, 3),
            'plagiarised': score >= threshold,
            'percent_copied': detail['percent_copied'],
            'matches': detail['matches'],
        })
    return sorted(results, key=lambda r: r['score'], reverse=True)
