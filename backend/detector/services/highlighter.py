"""Sentence-level matching (proposal step 6-7): 'this much copied' + highlights.

Given two documents, find which sentences of A closely match a sentence in B, using
the same SBERT embeddings. Returns the matched sentences and an overall % copied.
"""
from __future__ import annotations

from sentence_transformers import util

from .preprocess import split_sentences
from .similarity import DEFAULT_THRESHOLD, SbertEngine


def compare_documents(text_a: str, text_b: str, threshold: float = DEFAULT_THRESHOLD) -> dict:
    """Return matched sentences and the percentage of A that appears copied from B."""
    sents_a = split_sentences(text_a)
    sents_b = split_sentences(text_b)
    if not sents_a or not sents_b:
        return {'percent_copied': 0.0, 'matches': []}

    emb_a = SbertEngine.embed(sents_a)
    emb_b = SbertEngine.embed(sents_b)
    sim = util.cos_sim(emb_a, emb_b)  # shape [len(a), len(b)]

    matches = []
    copied = 0
    for i, sentence in enumerate(sents_a):
        best_score, best_j = float(sim[i].max()), int(sim[i].argmax())
        is_copied = best_score >= threshold
        if is_copied:
            copied += 1
        matches.append({
            'sentence': sentence,
            'matched_with': sents_b[best_j] if is_copied else None,
            'score': round(best_score, 3),
            'copied': is_copied,
        })

    percent = round(100.0 * copied / len(sents_a), 1)
    return {'percent_copied': percent, 'matches': matches}
