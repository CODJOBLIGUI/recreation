import io
import os
from pathlib import Path

from django.conf import settings

_EASYOCR_READER = None

MAX_PAGES_FOR_CONVERSION = 250
PDF_OCR_DPI = 150
PDF_BATCH_SIZE = 25


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


def _update_progress(progress_cb, value):
    if progress_cb:
        try:
            progress_cb(int(value))
        except Exception:
            pass


def _extract_text_from_pdf(local_path, progress_cb=None):
    try:
        from PyPDF2 import PdfReader
    except Exception as exc:
        raise RuntimeError("PyPDF2 n'est pas installe.") from exc

    with open(local_path, "rb") as f:
        reader = PdfReader(f)
        total_pages = len(reader.pages)

        texts = []
        has_text = False
        for idx, page in enumerate(reader.pages, start=1):
            extracted = page.extract_text() or ""
            if extracted.strip():
                has_text = True
            texts.append(extracted)
            _update_progress(progress_cb, min(40, int(idx / max(1, total_pages) * 40)))

        merged = "\n".join(texts).strip()
        if has_text and merged:
            _update_progress(progress_cb, 50)
            return merged

    # OCR fallback for scanned PDFs
    try:
        import easyocr
        from PIL import Image
        import numpy as np
    except Exception as exc:
        raise RuntimeError("OCR PDF indisponible (EasyOCR/Pillow manquant).") from exc

    global _EASYOCR_READER
    if _EASYOCR_READER is None:
        _EASYOCR_READER = easyocr.Reader(["fr"], gpu=False)
    reader_ocr = _EASYOCR_READER

    ocr_texts = []
    try:
        from pdf2image import convert_from_path
        with open(local_path, "rb") as f:
            reader = PdfReader(f)
            total_pages = len(reader.pages)
        for start in range(1, total_pages + 1, PDF_BATCH_SIZE):
            end = min(total_pages, start + PDF_BATCH_SIZE - 1)
            images = convert_from_path(local_path, dpi=PDF_OCR_DPI, first_page=start, last_page=end)
            for img in images:
                img_arr = np.array(img)
                results = reader_ocr.readtext(img_arr, detail=0, paragraph=True)
                ocr_texts.extend(results)
            progress = 50 + int(end / max(1, total_pages) * 45)
            _update_progress(progress_cb, min(progress, 95))
    except Exception:
        with open(local_path, "rb") as f:
            reader = PdfReader(f)
            total_pages = len(reader.pages)
            for idx, page in enumerate(reader.pages, start=1):
                images = getattr(page, "images", []) or []
                for img in images:
                    try:
                        image = Image.open(io.BytesIO(img.data))
                        img_arr = np.array(image)
                        results = reader_ocr.readtext(img_arr, detail=0, paragraph=True)
                        ocr_texts.extend(results)
                    except Exception:
                        continue
                progress = 50 + int(idx / max(1, total_pages) * 45)
                _update_progress(progress_cb, min(progress, 95))

    _update_progress(progress_cb, 98)
    return "\n".join(ocr_texts)


def extract_text_from_file(file_field, progress_cb=None):
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
            raise RuntimeError("python-docx n'est pas installe.") from exc
        doc = Document(local_path)
        return "\n".join(p.text for p in doc.paragraphs if p.text)

    if ext in {".pdf"}:
        return _extract_text_from_pdf(local_path, progress_cb=progress_cb)

    if ext in {".jpg", ".jpeg", ".png"}:
        try:
            import easyocr
        except Exception as exc:
            raise RuntimeError("easyocr n'est pas installe.") from exc
        if _EASYOCR_READER is None:
            _EASYOCR_READER = easyocr.Reader(["fr"], gpu=False)
        reader = _EASYOCR_READER
        results = reader.readtext(local_path, detail=0, paragraph=True)
        return "\n".join(results)

    if ext in {".pptx"}:
        try:
            from pptx import Presentation
        except Exception as exc:
            raise RuntimeError("python-pptx n'est pas installe.") from exc
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
            raise RuntimeError("openpyxl n'est pas installe.") from exc
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
            raise RuntimeError("EbookLib ou beautifulsoup4 n'est pas installe.") from exc
        book = epub.read_epub(local_path)
        texts = []
        for item in book.get_items():
            if item.get_type() == epub.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), "html.parser")
                texts.append(soup.get_text(" ", strip=True))
        return "\n".join(texts)

    raise RuntimeError("Type de fichier non pris en charge.")


def generate_audio_from_text(text, lang="fr", slow=False):
    from gtts import gTTS
    from django.core.files.base import ContentFile
    import uuid

    tts = gTTS(text, lang=lang, slow=slow)
    audio_bytes = ContentFile(b"")
    filename = f"conversion-{uuid.uuid4().hex}.mp3"
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    return filename, audio_bytes


def run_audio_conversion_job(demande_id):
    import threading
    from django.utils import timezone
    from django.db import transaction
    from django.core.files.base import ContentFile
    from apps.catalogue.models import AudioConversionRequest

    def _job():
        try:
            demande = AudioConversionRequest.objects.get(id=demande_id)
        except Exception:
            return

        def progress_cb(value):
            AudioConversionRequest.objects.filter(id=demande_id).update(async_progress=value)

        AudioConversionRequest.objects.filter(id=demande_id).update(
            statut="processing",
            async_status="started",
            async_progress=0,
            async_error="",
            async_started_at=timezone.now(),
        )

        try:
            text = (demande.texte or "").strip()
            if demande.fichier and not text:
                text = extract_text_from_file(demande.fichier, progress_cb=progress_cb)
            if not text.strip():
                raise RuntimeError("Texte vide apres extraction.")
            if not demande.fichier:
                progress_cb(15)
            slow = True if demande.voix == "slow" else False
            progress_cb(60)
            filename, audio_bytes = generate_audio_from_text(text, lang=demande.langue, slow=slow)
            progress_cb(90)
            demande.audio.save(filename, audio_bytes, save=False)
            demande.statut = "free_generated" if not demande.paiement_requis else "delivered"
            demande.async_status = "finished"
            demande.async_progress = 100
            demande.async_finished_at = timezone.now()
            demande.async_error = ""
            demande.save(update_fields=[
                "audio",
                "statut",
                "async_status",
                "async_progress",
                "async_finished_at",
                "async_error",
                "updated_at",
            ])
        except Exception as exc:
            AudioConversionRequest.objects.filter(id=demande_id).update(
                statut="error",
                async_status="failed",
                async_error=str(exc),
                async_progress=0,
                async_finished_at=timezone.now(),
            )

    threading.Thread(target=_job, daemon=True).start()



