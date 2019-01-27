"""
Synthesizes speech from the input string of text.
"""
import time
from io import BytesIO

from google.cloud import texttospeech
from pydub import AudioSegment

MAX_REQUEST_LENGTH = 5000
CREDS_JSON = 'creds.secret.json'
VOICE_NAME = 'en-AU-Wavenet-B'
AUDIO_ENCODING = texttospeech.enums.AudioEncoding.MP3
SPEAKING_RATE = 0.9

voice = texttospeech.types.VoiceSelectionParams(
    name=VOICE_NAME,
    language_code='en-AU',

)
audio_config = texttospeech.types.AudioConfig(
    audio_encoding=AUDIO_ENCODING,
    speaking_rate=SPEAKING_RATE,
)


def text_to_speech_mp3(paragraphs, mp3_path):
    start = time.time()
    client = texttospeech.TextToSpeechClient.from_service_account_json(CREDS_JSON)
    speech_audio = None
    half_sec_pause = AudioSegment.silent(duration=500)
    num_paras = len(paragraphs) - 1
    for counter, paragraph in enumerate(paragraphs):
        print(f'\tTranslating paragraph {counter} / {num_paras}')
        text_batches = batch(paragraph, MAX_REQUEST_LENGTH)
        for text_batch in text_batches:
            mp3_bytes_file = text_to_mp3_bytes(client, text_batch)
            audio_segment = AudioSegment.from_mp3(mp3_bytes_file)
            if speech_audio:
                speech_audio += audio_segment
            else:
                speech_audio = audio_segment

        # Add a 0.5s pause after a paragraph
        speech_audio += half_sec_pause

    speech_audio.export(mp3_path, format='mp3')
    seconds = int(time.time() - start)
    print(f'Audio content written to file \"{mp3_path}\" - took {seconds}s')

def text_to_mp3_bytes(client, text):
    assert len(text) <= 5000
    synthesis_input = texttospeech.types.SynthesisInput(text=text)
    response = client.synthesize_speech(synthesis_input, voice, audio_config)
    return BytesIO(response.audio_content)


def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]
