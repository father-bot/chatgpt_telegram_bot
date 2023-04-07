import os
import tempfile
import azure.cognitiveservices.speech as speechsdk
from config import azure_tts_key, azure_tts_region, azure_tts_name


def get_tts_speak_audio_stream(text: str) -> bytes:
    SPEECH_KEY = azure_tts_key
    SPEECH_REGION = azure_tts_region
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)

    # Use a temporary file for the audio output
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        audio_config = speechsdk.audio.AudioOutputConfig(filename=temp_file.name)

        # The language of the voice that speaks.
        speech_config.speech_synthesis_voice_name = azure_tts_name

        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        try:
            synthesizer.speak_text_async(text).get()
        finally:
            # Release resources used by the SpeechSynthesizer object
            synthesizer = None

        # Read the contents of the audio file and return them as bytes
        with open(temp_file.name, "rb") as f:
            audio_stream = f.read()

    # Delete the temporary file
    os.remove(temp_file.name)
    return audio_stream
