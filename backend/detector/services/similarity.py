"""Similarity engines (proposal step 3-4).

Two engines, both PyTorch-based (NOT scikit-learn):
  * TfidfEngine  -- classical baseline, TF-IDF vectors built with torch tensors.
  * SbertEngine  -- the fine-tuned Sentence-BERT model (falls back to pretrained).

Public helpers:
  all_pairs_matrix(texts, method) -> n x n cosine-similarity matrix (list of lists)
"""
from __future__ import annotations

import math
import os

import torch

DEFAULT_THRESHOLD = 0.7

# Path where notebook 01 saves the fine-tuned checkpoint.
_MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models', 'plagiarism-sbert')


def _cosine_matrix(vectors: torch.Tensor) -> list[list[float]]:
    """Cosine similarity between every pair of row vectors. Returns a plain list matrix."""
    normed = vectors / vectors.norm(dim=1, keepdim=True).clamp_min(1e-8)
    sim = (normed @ normed.T).clamp(-1.0, 1.0)
    return [[round(float(v), 4) for v in row] for row in sim]


class TfidfEngine:
    """TF-IDF + cosine similarity implemented from scratch with PyTorch tensors."""

    def __init__(self, documents: list[list[str]]):
        # documents = list of token lists (already preprocessed)
        self.documents = documents
        self.vocab = self._build_vocab(documents)
        self.idf = self._compute_idf(documents)

    @staticmethod
    def _build_vocab(documents: list[list[str]]) -> dict[str, int]:
        vocab: dict[str, int] = {}
        for doc in documents:
            for tok in doc:
                if tok not in vocab:
                    vocab[tok] = len(vocab)
        return vocab

    def _compute_idf(self, documents: list[list[str]]) -> torch.Tensor:
        n = len(documents)
        df = torch.zeros(len(self.vocab))
        for doc in documents:
            for tok in set(doc):
                df[self.vocab[tok]] += 1
        # smoothed idf
        return torch.log((1 + n) / (1 + df)) + 1.0

    def _vectorize(self, doc: list[str]) -> torch.Tensor:
        vec = torch.zeros(len(self.vocab))
        if not doc:
            return vec
        for tok in doc:
            vec[self.vocab[tok]] += 1
        vec = vec / len(doc)          # term frequency
        return vec * self.idf         # tf-idf

    def matrix(self) -> list[list[float]]:
        if not self.vocab:
            n = len(self.documents)
            return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
        vectors = torch.stack([self._vectorize(d) for d in self.documents])
        return _cosine_matrix(vectors)


class SbertEngine:
    """Sentence-BERT semantic similarity. Lazily loads the model once (singleton)."""

    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            from sentence_transformers import SentenceTransformer

            path = _MODEL_DIR if os.path.isdir(_MODEL_DIR) else 'all-MiniLM-L6-v2'
            cls._model = SentenceTransformer(path)
        return cls._model

    @classmethod
    def is_fine_tuned(cls) -> bool:
        return os.path.isdir(_MODEL_DIR)

    @classmethod
    def embed(cls, texts: list[str]) -> torch.Tensor:
        model = cls.get_model()
        return model.encode(texts, convert_to_tensor=True)

    @classmethod
    def matrix(cls, texts: list[str]) -> list[list[float]]:
        embeddings = cls.embed(texts)
        return _cosine_matrix(embeddings)


def all_pairs_matrix(texts: list[str], method: str = 'sbert') -> list[list[float]]:
    """Compare every text against every other (intra-class all-pairs).

    method: 'sbert' (fine-tuned model) or 'tfidf' (baseline).
    """
    if method == 'tfidf':
        from .preprocess import tokenize

        return TfidfEngine([tokenize(t) for t in texts]).matrix()
    return SbertEngine.matrix(texts)
