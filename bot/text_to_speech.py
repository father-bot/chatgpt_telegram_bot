# import os
# import time
#
# from bark import SAMPLE_RATE, generate_audio, preload_models
# from scipy.io.wavfile import write as write_wav
#
# # download and load all models
# preload_models()
#
# def create_audio(text_prompt):
#     audio_array = generate_audio(text_prompt)
#
#     if not os.path.exists('audio'):
#         os.makedirs('audio')
#
#     path = 'audio/' + str(time.time()) + '.wav'
#     write_wav(path, SAMPLE_RATE, audio_array)
#
#     return path
