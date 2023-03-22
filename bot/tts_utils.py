import os
import azure.cognitiveservices.speech as speechsdk
from config import azure_tts_key, azure_tts_region, azure_tts_name


def get_tts_speak_audio_stream(text: str) -> bytes:
    SPEECH_KEY = azure_tts_key
    SPEECH_REGION = azure_tts_region
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    audio_config = speechsdk.audio.AudioOutputConfig(filename="audio.wav")

    # The language of the voice that speaks.
    speech_config.speech_synthesis_voice_name = azure_tts_name
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    print("get text: {}".format(text))
    speech_synthesizer.speak_text_async(text).get()

    # Read the contents of the audio file and return them as bytes
    with open("audio.wav", "rb") as f:
        audio_stream = f.read()

    # Delete the audio file
    os.remove("audio.wav")

    return audio_stream


if __name__ == '__main__':
    s = get_tts_speak_audio_stream("你好")
    print(s)
