"""Uploaded file -> plain text, for PDF, DOCX, TXT and images (OCR)."""
from __future__ import annotations

import io
import os

# Override with OCR_LANG=eng to force English only, or OCR_LANG=nep for Nepali only.
_LANG_OVERRIDE = os.environ.get('OCR_LANG', '')
_resolved_lang: str | None = None


def ocr_lang() -> str:
    """Read Devanagari too when its traineddata is present, else stay on English."""
    global _resolved_lang
    if _LANG_OVERRIDE:
        return _LANG_OVERRIDE
    if _resolved_lang is None:
        try:
            import pytesseract

            installed = set(pytesseract.get_languages(config=''))
        except Exception:
            installed = set()
        _resolved_lang = 'eng+nep' if 'nep' in installed else 'eng'
    return _resolved_lang


def _from_txt(data: bytes) -> str:
    return data.decode('utf-8', errors='ignore')


def _from_pdf(data: bytes) -> str:
    import pdfplumber

    text = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            text.append(page.extract_text() or '')
    joined = '\n'.join(text).strip()
    # Scanned PDF with no text layer -> fall back to OCR of page images.
    if not joined:
        return _ocr_pdf(data)
    return joined


def _ocr_pdf(data: bytes) -> str:
    try:
        import pdfplumber
        import pytesseract

        text = []
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for page in pdf.pages:
                image = page.to_image(resolution=200).original
                text.append(pytesseract.image_to_string(image, lang=ocr_lang()))
        return '\n'.join(text).strip()
    except Exception:
        return ''


def _from_docx(data: bytes) -> str:
    import docx

    document = docx.Document(io.BytesIO(data))
    return '\n'.join(p.text for p in document.paragraphs)


def _from_image(data: bytes) -> str:
    import pytesseract
    from PIL import Image

    image = Image.open(io.BytesIO(data))
    return pytesseract.image_to_string(image, lang=ocr_lang())


_EXTRACTORS = {
    '.txt': _from_txt,
    '.md': _from_txt,
    '.pdf': _from_pdf,
    '.docx': _from_docx,
    '.png': _from_image,
    '.jpg': _from_image,
    '.jpeg': _from_image,
    '.bmp': _from_image,
    '.tiff': _from_image,
}


def extract_text(filename: str, data: bytes) -> str:
    """Route an uploaded file to the right extractor based on its extension.

    Every failure leaves through ValueError with a message safe to show the user.
    """
    if not data:
        raise ValueError('The file is empty.')

    ext = os.path.splitext(filename.lower())[1]
    extractor = _EXTRACTORS.get(ext)
    if extractor is None:
        supported = ', '.join(sorted(_EXTRACTORS))
        raise ValueError(f'Unsupported file type "{ext or filename}". Supported: {supported}.')

    try:
        text = extractor(data).strip()
    except Exception as exc:                      # corrupt file, broken archive, bad image
        raise ValueError(f'The file could not be read ({type(exc).__name__}).') from exc

    if not text:
        raise ValueError('No text could be read. If this is a scan, use a clearer image.')
    return text
