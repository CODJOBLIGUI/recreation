from django.utils import timezone
from django.core.files.base import ContentFile
from django.utils.text import slugify
from huey.contrib.djhuey import db_task

from .models import AudioConversionRequest
from .utils.audio_conversion import extract_text_from_file, generate_tts_mp3


def _set_progress(obj, status, progress, error=""):
    obj.async_status = status
    obj.async_progress = progress
    if error:
        obj.async_error = error
    obj.save(update_fields=["async_status", "async_progress", "async_error", "updated_at"])


@db_task()
def convert_audio_request(request_id):
    obj = AudioConversionRequest.objects.filter(id=request_id).first()
    if not obj:
        return

    obj.async_started_at = timezone.now()
    obj.async_error = ""
    _set_progress(obj, "started", 5)

    try:
        text = obj.texte or ""
        if obj.fichier and not text.strip():
            _set_progress(obj, "started", 20)
            text = extract_text_from_file(obj.fichier)

        if not text.strip():
            _set_progress(obj, "failed", 100, "Texte vide après extraction.")
            return

        _set_progress(obj, "started", 60)
        import uuid

        slow = True if obj.voix == "slow" else False
        audio_stream = generate_tts_mp3(text, lang=obj.langue, slow=slow, chunk_size=1000)
        audio_bytes = ContentFile(audio_stream.getvalue())
        filename = f"conversion-{slugify(obj.email) or obj.id}-{uuid.uuid4().hex}.mp3"
        obj.audio.save(filename, audio_bytes, save=False)
        obj.statut = "delivered"
        obj.async_finished_at = timezone.now()
        _set_progress(obj, "finished", 100)
        obj.save(update_fields=["audio", "statut", "async_finished_at", "updated_at"])
    except Exception as exc:
        obj.async_finished_at = timezone.now()
        _set_progress(obj, "failed", 100, str(exc))
        obj.save(update_fields=["async_finished_at", "updated_at"])
