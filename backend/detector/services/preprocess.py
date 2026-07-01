"""Text preprocessing (proposal step 2): lowercase, stopword removal, sentence split."""
import re

STOPWORDS = set(
    'the a an and or but of to in on for is are was were be been being with as at by this '
    'that these those it its from we you they he she i our your their has have had do does '
    'not no so if then than too very can will just'.split()
)


def clean(text: str) -> str:
    """Lowercase and collapse whitespace. Kept simple on purpose."""
    return re.sub(r'\s+', ' ', text.lower()).strip()


def tokenize(text: str) -> list[str]:
    """Split into word tokens, drop stopwords and very short tokens."""
    words = re.findall(r'[a-z0-9]{2,}', clean(text))
    return [w for w in words if w not in STOPWORDS]


def split_sentences(text: str) -> list[str]:
    """Naive sentence splitter -- good enough for highlighting."""
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in parts if len(s.strip()) > 10]


def keywords(text: str, k: int = 6) -> list[str]:
    """Top-k most frequent content words -- used to build a web search query."""
    freq: dict[str, int] = {}
    for w in tokenize(text):
        if len(w) >= 4:
            freq[w] = freq.get(w, 0) + 1
    return [w for w, _ in sorted(freq.items(), key=lambda x: -x[1])[:k]]
