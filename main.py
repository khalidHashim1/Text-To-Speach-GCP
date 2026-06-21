
import json
import uuid
import datetime
from google.cloud import texttospeech
from google.cloud import storage

tts_client = texttospeech.TextToSpeechClient()
storage_client = storage.Client()
BUCKET_NAME = "bootcamp.khalidhashim.com"

def handler(request):
    if request.method == "OPTIONS":
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "3600"
        }
        return ("", 204, headers)

    headers = {"Access-Control-Allow-Origin": "*"}

    try:
        request_json = request.get_json(silent=True)
        text = request_json.get("text", "").strip() if request_json else ""

        if not text:
            return (json.dumps({"error": "Text is required"}), 400, headers)

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
        
        file_key = f"tts-{uuid.uuid4()}.mp3"

        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(file_key)
        blob.upload_from_string(response.audio_content, content_type="audio/mp3")

        blob.upload_from_string(response.audio_content, content_type="audio/mp3")

        audio_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{file_key}"

        return (json.dumps({"audio_url": audio_url}), 200, headers)

    except Exception as e:
        print("Error:", str(e))
        return (json.dumps({"error": "Failed to generate speech", "details": str(e)}), 500, headers)
