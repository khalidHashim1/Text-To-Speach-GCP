import json
import uuid
from google.cloud import texttospeech
from google.cloud import storage

tts_client = texttospeech.TextToSpeechClient()
storage_client = storage.Client()

BUCKET_NAME = "bootcamp.khalidhashim.com"

ALLOWED_ORIGIN = "https://bootcamp.khalidhashim.com"

def cors_headers():
    return {
        "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json"
    }

def handler(request):
    ALLOWED_ORIGIN = "https://bootcamp.khalidhashim.com"
    # ---------------------------
    # CORS preflight handling
    # ---------------------------
    if request.method == "OPTIONS":
        return ("", 204, cors_headers())
    
    headers = {
        "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json"
    }

    try:
        # ---------------------------
        # Parse request safely
        # ---------------------------
        request_json = request.get_json(silent=True) or {}
        text = request_json.get("text", "").strip()

        if not text:
            return (json.dumps({"error": "Text is required"}), 400, cors_headers())

        # ---------------------------
        # Google Text-to-Speech
        # ---------------------------
        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Wavenet-F"
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        # ---------------------------
        # Save to Cloud Storage
        # ---------------------------
        file_key = f"tts-{uuid.uuid4()}.mp3"

        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(file_key)

        blob.upload_from_string(
            response.audio_content,
            content_type="audio/mpeg"
        )

        # ---------------------------
        # IMPORTANT: CDN-friendly URL
        # ---------------------------
        audio_url = f"https://bootcamp.khalidhashim.com/{file_key}"

        return (
            json.dumps({"audio_url": audio_url}),
            200,
            cors_headers()
        )

    except Exception as e:
        print("Error:", str(e))
        return (
            json.dumps({
                "error": "Failed to generate speech",
                "details": str(e)
            }),
            500,
            cors_headers()
        )
