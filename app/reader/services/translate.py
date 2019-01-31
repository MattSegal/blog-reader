"""
Synthesizes speech from the input string of text.
"""
import os
import time
from io import BytesIO
import tempfile
import base64

from google.cloud import texttospeech
from pydub import AudioSegment


GOOGLE_SERVICE_ACCOUNT = os.environ.get('GOOGLE_SERVICE_ACCOUNT')
MAX_REQUEST_LENGTH = 5000
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


def text_to_speech_mp3(article, out_file):
    paragraphs = parse_paragraphs(article)
    client = get_client()
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

    speech_audio.export(out_file, format='mp3')


def get_client():
    """This melts my brain, I hate this."""
    creds_json_text = base64.b64decode(GOOGLE_SERVICE_ACCOUNT.encode('utf-8')).decode('utf-8')
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tf:
        path = tf.name
        print(creds_json_text)
        tf.write(creds_json_text.strip())

    client = texttospeech.TextToSpeechClient.from_service_account_json(path)
    os.remove(path)
    return client

def text_to_mp3_bytes(client, text):
    assert len(text) <= 5000
    synthesis_input = texttospeech.types.SynthesisInput(text=text)
    response = client.synthesize_speech(synthesis_input, voice, audio_config)
    return BytesIO(response.audio_content)


def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


def parse_paragraphs(article):
    body = article.content.split('\n')
    intro = 'This is the intro.'
    # intro = (
    #     '{title}. '
    #     'This article, written by {author}, was posted on {channel_name} on {posted_at}. '
    #     'Let\'s begin.'
    # ).format(**post)
    outro = (
        'This is the outro.'
    )
    return [intro, *body, outro]
