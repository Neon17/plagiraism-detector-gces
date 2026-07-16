"""HTTP layer -- thin. Views only parse the request, call a service, return JSON."""
from __future__ import annotations

from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import highlighter, similarity, web_scraper
from .services.text_extraction import extract_text


def _collect_documents(request) -> list[dict]:
    """Build [{name, text}] from uploaded files and/or pasted texts."""
    documents = []
    for f in request.FILES.getlist('files'):
        try:
            text = extract_text(f.name, f.read())
        except ValueError as exc:
            text = f''  # skip unsupported; report handled by caller
            documents.append({'name': f.name, 'text': text, 'error': str(exc)})
            continue
        documents.append({'name': f.name, 'text': text})

    # Pasted texts: JSON list of {name, text}
    for i, item in enumerate(request.data.get('texts', []) or []):
        documents.append({
            'name': item.get('name', f'text-{i + 1}'),
            'text': item.get('text', ''),
        })
    return documents


class CompareView(APIView):
    """POST /api/compare -- intra-class all-pairs comparison + highlights."""

    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        documents = [d for d in _collect_documents(request) if d.get('text')]
        if len(documents) < 2:
            return Response(
                {'detail': 'Upload at least 2 documents (files or texts) to compare.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        method = request.data.get('method', 'sbert')
        texts = [d['text'] for d in documents]
        names = [d['name'] for d in documents]

        matrix = similarity.all_pairs_matrix(texts, method=method)

        # Sentence-level highlights for every flagged pair (score above threshold).
        pairs = []
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                score = matrix[i][j]
                if score >= similarity.DEFAULT_THRESHOLD:
                    detail = highlighter.compare_documents(texts[i], texts[j])
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
            'threshold': similarity.DEFAULT_THRESHOLD,
            'matrix': matrix,
            'flagged_pairs': pairs,
        })


class WebCheckView(APIView):
    """POST /api/check-web -- compare one document against web pages."""

    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        documents = [d for d in _collect_documents(request) if d.get('text')]
        if not documents:
            return Response(
                {'detail': 'Provide one document (file or text) to check against the web.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        text = documents[0]['text']
        # URLs may arrive as a JSON list or as repeated form fields.
        if hasattr(request.data, 'getlist'):
            urls = request.data.getlist('urls')
        else:
            urls = request.data.get('urls')
        urls = [u for u in (urls or []) if u] or None
        results = web_scraper.check_web(text, urls=urls)
        return Response({
            'document': documents[0]['name'],
            'threshold': similarity.DEFAULT_THRESHOLD,
            'sources': results,
        })


class HealthView(APIView):
    def get(self, request):
        return Response({'status': 'ok',
                         'model_fine_tuned': similarity.SbertEngine.is_fine_tuned()})
