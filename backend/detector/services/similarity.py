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

# Long documents are cut into chunks of this many sentences before encoding, because
# the model truncates anything longer than its input window.
CHUNK_SENTENCES = 5
# Sentences/chunks are encoded this many at a time instead of one call per sentence.
BATCH_SIZE = 32

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


def chunk_text(text: str, sentences_per_chunk: int = CHUNK_SENTENCES) -> list[str]:
    """Split a document into chunks of a few sentences each.

    A whole document does not fit in the model input, so the tail of a long document
    used to be silently dropped. Encoding chunks and averaging them keeps all of it.
    """
    from .preprocess import split_sentences

    sentences = split_sentences(text)
    if not sentences:
        stripped = text.strip()
        return [stripped] if stripped else []
    return [
        ' '.join(sentences[i:i + sentences_per_chunk])
        for i in range(0, len(sentences), sentences_per_chunk)
    ]


class SbertEngine:
    """Sentence-BERT semantic similarity. Lazily loads the model once (singleton)."""

    _model = None
    # Same sentence is compared in many pairs of the matrix, so encode it only once.
    _cache: dict[str, torch.Tensor] = {}
    _CACHE_LIMIT = 4096

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
    def clear_cache(cls) -> None:
        cls._cache.clear()

    @classmethod
    def embed(cls, texts: list[str]) -> torch.Tensor:
        """Encode texts in batches, reusing anything that was encoded earlier."""
        if not texts:
            return torch.empty(0)

        missing = list(dict.fromkeys(t for t in texts if t not in cls._cache))
        if missing:
            model = cls.get_model()
            fresh = model.encode(missing, batch_size=BATCH_SIZE, convert_to_tensor=True)
            if len(cls._cache) + len(missing) > cls._CACHE_LIMIT:
                cls._cache.clear()
            for text, vector in zip(missing, fresh):
                cls._cache[text] = vector
        return torch.stack([cls._cache[t] for t in texts])

    @classmethod
    def document_embeddings(cls, texts: list[str]) -> torch.Tensor:
        """One vector per document, built from the mean of its chunk vectors.

        Every chunk of every document goes into a single batched call, so the model
        is entered once per request instead of once per document.
        """
        chunks_per_doc = [chunk_text(t) for t in texts]
        flat = [c for chunks in chunks_per_doc for c in chunks]
        if not flat:
            return torch.zeros(len(texts), 1)

        vectors = cls.embed(flat)
        out, cursor = [], 0
        for chunks in chunks_per_doc:
            if not chunks:
                out.append(torch.zeros_like(vectors[0]))
                continue
            out.append(vectors[cursor:cursor + len(chunks)].mean(dim=0))
            cursor += len(chunks)
        return torch.stack(out)

    @classmethod
    def matrix(cls, texts: list[str]) -> list[list[float]]:
        return _cosine_matrix(cls.document_embeddings(texts))


def all_pairs_matrix(texts: list[str], method: str = 'sbert') -> list[list[float]]:
    """Compare every text against every other (intra-class all-pairs).

    method: 'sbert' (fine-tuned model) or 'tfidf' (baseline).
    """
    if method == 'tfidf':
        from .preprocess import tokenize

        return TfidfEngine([tokenize(t) for t in texts]).matrix()
    return SbertEngine.matrix(texts)
