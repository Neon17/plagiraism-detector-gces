"""HTTP layer -- thin. Views only parse the request, call a service, return JSON."""
from __future__ import annotations

from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import highlighter, similarity, web_scraper
from .services.text_extraction import extract_text


def _collect_documents(request) -> list[dict]:
    """Build [{name, text}] from uploaded files and/or pasted texts.

    A file that cannot be read is kept in the list with an 'error' key instead of being
    dropped silently, so the user is told which upload failed and why.
    """
    documents = []
    for f in request.FILES.getlist('files'):
        try:
            text = extract_text(f.name, f.read())
        except ValueError as exc:
            documents.append({'name': f.name, 'text': '', 'error': str(exc)})
            continue
        documents.append({'name': f.name, 'text': text})

    # Pasted texts: JSON list of {name, text}
    for i, item in enumerate(request.data.get('texts', []) or []):
        name = item.get('name', f'text-{i + 1}')
        text = (item.get('text') or '').strip()
        entry = {'name': name, 'text': text}
        if not text:
            entry['error'] = 'The pasted text is empty.'
        documents.append(entry)
    return documents


def _skipped(documents: list[dict]) -> list[dict]:
    """The uploads that produced no usable text, with the reason for each."""
    return [{'name': d['name'], 'error': d['error']} for d in documents if d.get('error')]


def _threshold(request) -> float:
    """Similarity threshold chosen in the interface, or the default one."""
    try:
        value = float(request.data.get('threshold'))
    except (TypeError, ValueError):
        return similarity.DEFAULT_THRESHOLD
    return min(max(value, 0.1), 0.99)


class CompareView(APIView):
    """POST /api/compare -- intra-class all-pairs comparison + highlights."""

    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        collected = _collect_documents(request)
        skipped = _skipped(collected)
        documents = [d for d in collected if d.get('text')]
        if len(documents) < 2:
            return Response(
                {
                    'detail': 'Upload at least 2 readable documents (files or texts) to compare.',
                    'skipped': skipped,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        method = request.data.get('method', 'sbert')
        if method not in ('sbert', 'tfidf'):
            return Response(
                {'detail': f'Unknown method "{method}". Use "sbert" or "tfidf".'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        texts = [d['text'] for d in documents]
        names = [d['name'] for d in documents]

        threshold = _threshold(request)
        matrix = similarity.all_pairs_matrix(texts, method=method)

        # Sentence-level highlights for every flagged pair (score above threshold).
        pairs = []
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                score = matrix[i][j]
                if score >= threshold:
                    detail = highlighter.compare_documents(texts[i], texts[j], threshold)
                    pairs.append({
                        'doc_a': names[i],
                        'doc_b': names[j],
                        'score': score,
                        'percent_copied': detail['percent_copied'],
                        'matches': detail['matches'],
                    })

        return Response({
            'documents': names,
            'method': method,
            'model_fine_tuned': similarity.SbertEngine.is_fine_tuned(),
            'threshold': threshold,
            'matrix': matrix,
            'flagged_pairs': pairs,
            'skipped': skipped,
        })


class WebCheckView(APIView):
    """POST /api/check-web -- compare one document against web pages."""

    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        collected = _collect_documents(request)
        skipped = _skipped(collected)
        documents = [d for d in collected if d.get('text')]
        if not documents:
            return Response(
                {
                    'detail': 'Provide one readable document (file or text) to check '
                              'against the web.',
                    'skipped': skipped,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        text = documents[0]['text']
        # URLs may arrive as a JSON list or as repeated form fields.
        if hasattr(request.data, 'getlist'):
            urls = request.data.getlist('urls')
        else:
            urls = request.data.get('urls')
        urls = [u for u in (urls or []) if u] or None
        threshold = _threshold(request)
        results = web_scraper.check_web(text, urls=urls, threshold=threshold)
        return Response({
            'document': documents[0]['name'],
            'threshold': threshold,
            'sources': results,
            'skipped': skipped,
        })


class HealthView(APIView):
    def get(self, request):
        return Response({'status': 'ok',
                         'model_fine_tuned': similarity.SbertEngine.is_fine_tuned()})
