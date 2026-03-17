import io
import os
from pathlib import Path

from django.conf import settings

_EASYOCR_READER = None


def estimate_pages_from_text(text):
    if not text:
        return 0
    words = len([w for w in text.split() if w.strip()])
    if words == 0:
        return 0
    # Estimation rapide : 300 mots ~ 1 page
    return max(1, int((words + 299) / 300))


def count_pages_for_file(file_field):
    if not file_field:
        return 0
    name = file_field.name or ""
    ext = Path(name).suffix.lower()
    local_path = _ensure_local_path(file_field)

    if ext in {".pdf"}:
        try:
            from PyPDF2 import PdfReader
        except Exception:
            return 0
        with open(local_path, "rb") as f:
            reader = PdfReader(f)
            try:
                return len(reader.pages)
            except Exception:
                return 0

    if ext in {".pptx"}:
        try:
            from pptx import Presentation
        except Exception:
            return 0
        prs = Presentation(local_path)
        return len(prs.slides)

    if ext in {".xlsx"}:
        try:
            import openpyxl
        except Exception:
            return 0
        wb = openpyxl.load_workbook(local_path, data_only=True)
        return max(1, len(wb.worksheets))

    if ext in {".jpg", ".jpeg", ".png"}:
        return 1

    # Pour les autres formats, estimation via texte extrait
    try:
        text = extract_text_from_file(file_field)
    except Exception:
        text = ""
    return estimate_pages_from_text(text)


def _ensure_local_path(file_field):
    if hasattr(file_field, "path") and os.path.exists(file_field.path):
        return file_field.path
    tmp_dir = Path(settings.BASE_DIR) / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(file_field.name).suffix or ".bin"
    tmp_path = tmp_dir / f"upload_{os.path.basename(file_field.name)}"
    if hasattr(file_field, "read") and hasattr(file_field, "seek"):
        data = file_field.read()
        try:
            file_field.seek(0)
        except Exception:
            pass
        with open(tmp_path, "wb") as dst:
            dst.write(data)
        return str(tmp_path)
    with file_field.open("rb") as src, open(tmp_path, "wb") as dst:
        dst.write(src.read())
    return str(tmp_path)


def extract_text_from_file(file_field):
    global _EASYOCR_READER
    if not file_field:
        return ""

    name = file_field.name or ""
    ext = Path(name).suffix.lower()
    local_path = _ensure_local_path(file_field)

    if ext in {".txt"}:
        with open(local_path, "rb") as f:
            return f.read().decode(errors="ignore")

    if ext in {".docx"}:
        try:
            from docx import Document
        except Exception as exc:
            raise RuntimeError("python-docx n'est pas installÃ©.") from exc
        doc = Document(local_path)
        return "\n".join(p.text for p in doc.paragraphs if p.text)

    if ext in {".pdf"}:
        try:
            from PyPDF2 import PdfReader
        except Exception as exc:
            raise RuntimeError("PyPDF2 n'est pas installÃ©.") from exc
        with open(local_path, "rb") as f:
            reader = PdfReader(f)
            pages = [p.extract_text() or "" for p in reader.pages]
        text = "\n".join(pages).strip()
        if text:
            return text
        # OCR fallback for scanned PDFs (extract embedded images)
        try:
            import easyocr
            from PIL import Image
            import numpy as np
        except Exception as exc:
            raise RuntimeError("OCR PDF indisponible (EasyOCR/Pillow manquant).") from exc
        if _EASYOCR_READER is None:
            _EASYOCR_READER = easyocr.Reader(["fr"], gpu=False)
        reader_ocr = _EASYOCR_READER
        texts = []
        for page in reader.pages:
            images = getattr(page, "images", []) or []
            if images:
                for img in images:
                    try:
                        img_data = img.data
                        image = Image.open(io.BytesIO(img_data))
                        img_arr = np.array(image)
                        results = reader_ocr.readtext(img_arr, detail=0, paragraph=True)
                        texts.extend(results)
                    except Exception:
                        continue
        return "\n".join(texts)

    if ext in {".jpg", ".jpeg", ".png"}:
        try:
            import easyocr
        except Exception as exc:
            raise RuntimeError("easyocr n'est pas installÃ©.") from exc
        if _EASYOCR_READER is None:
            _EASYOCR_READER = easyocr.Reader(["fr"], gpu=False)
        reader = _EASYOCR_READER
        results = reader.readtext(local_path, detail=0, paragraph=True)
        return "\n".join(results)

    if ext in {".pptx"}:
        try:
            from pptx import Presentation
        except Exception as exc:
            raise RuntimeError("python-pptx n'est pas installÃ©.") from exc
        prs = Presentation(local_path)
        texts = []
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    texts.append(shape.text)
        return "\n".join(t for t in texts if t)

    if ext in {".xlsx"}:
        try:
            import openpyxl
        except Exception as exc:
            raise RuntimeError("openpyxl n'est pas installÃ©.") from exc
        wb = openpyxl.load_workbook(local_path, data_only=True)
        texts = []
        for ws in wb.worksheets:
            for row in ws.iter_rows(values_only=True):
                for cell in row:
                    if cell is not None:
                        texts.append(str(cell))
        return "\n".join(texts)

    if ext in {".epub"}:
        try:
            from ebooklib import epub
            from bs4 import BeautifulSoup
        except Exception as exc:
            raise RuntimeError("EbookLib ou beautifulsoup4 n'est pas installÃ©.") from exc
        book = epub.read_epub(local_path)
        texts = []
        for item in book.get_items():
            if item.get_type() == epub.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), "html.parser")
                texts.append(soup.get_text(" ", strip=True))
        return "\n".join(texts)

    raise RuntimeError("Type de fichier non pris en charge.")


def _chunk_text(text, chunk_size=1000):
    text = (text or "").strip()
    if not text:
        return []
    chunks = []
    start = 0
    length = len(text)
    while start < length:
        end = min(start + chunk_size, length)
        if end < length:
            split_at = text.rfind(" ", start, end)
            if split_at <= start:
                split_at = end
        else:
            split_at = end
        chunk = text[start:split_at].strip()
        if chunk:
            chunks.append(chunk)
        start = split_at
    return chunks


def generate_tts_mp3(text, lang="fr", slow=False, chunk_size=1000):
    from gtts import gTTS
    chunks = _chunk_text(text, chunk_size=chunk_size)
    if not chunks:
        raise RuntimeError("Texte vide après extraction.")
    output = io.BytesIO()
    for part in chunks:
        tts = gTTS(part, lang=lang, slow=slow)
        tmp = io.BytesIO()
        tts.write_to_fp(tmp)
        output.write(tmp.getvalue())
    output.seek(0)
    return output
