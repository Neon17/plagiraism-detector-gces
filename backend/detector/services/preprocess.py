"""Text preprocessing (proposal step 2): lowercase, stopword removal, sentence split.

Handles English and Devanagari (Nepali). Devanagari has no upper/lower case and ends a
sentence with the danda (।) instead of a full stop, so both are treated here.
"""
import re

STOPWORDS = set(
    'the a an and or but of to in on for is are was were be been being with as at by this '
    'that these those it its from we you they he she i our your their has have had do does '
    'not no so if then than too very can will just'.split()
)

# Frequent Nepali function words, dropped for the same reason as the English ones.
STOPWORDS.update(
    'र मा को का की ले लाई हो हुन छ छन् थियो थिए पनि तर वा यो त्यो यी ती जुन जब भने '
    'गर्न गरेको भएको हुन्छ हुने साथ बाट सम्म देखि नै अनि'.split()
)

# A sentence ends at a full stop, a question or exclamation mark, or a danda.
_SENTENCE_END = re.compile(r'(?<=[.!?।॥])\s+')
_WORD = re.compile(r'[a-z0-9ऀ-ॿ]{2,}')


def clean(text: str) -> str:
    """Lowercase and collapse whitespace. Kept simple on purpose."""
    return re.sub(r'\s+', ' ', text.lower()).strip()


def tokenize(text: str) -> list[str]:
    """Split into word tokens, drop stopwords and very short tokens."""
    words = _WORD.findall(clean(text))
    return [w for w in words if w not in STOPWORDS]


def split_sentences(text: str) -> list[str]:
    """Naive sentence splitter -- good enough for highlighting."""
    parts = _SENTENCE_END.split(text.strip())
    sentences = []
    for part in parts:
        # A danda with no space after it still ends the sentence.
        for piece in re.split(r'(?<=[।॥])(?=\S)', part):
            piece = piece.strip()
            if len(piece) > 10:
                sentences.append(piece)
    return sentences


def keywords(text: str, k: int = 6) -> list[str]:
    """Top-k most frequent content words -- used to build a web search query."""
    freq: dict[str, int] = {}
    for w in tokenize(text):
        if len(w) >= 4:
            freq[w] = freq.get(w, 0) + 1
    return [w for w, _ in sorted(freq.items(), key=lambda x: -x[1])[:k]]
