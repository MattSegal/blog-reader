"""
Synthesizes speech from the input string of text.
"""
import os
import time
from io import BytesIO
import base64
import json

from google.cloud import texttospeech
from google.oauth2.service_account import Credentials
from pydub import AudioSegment


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
    client = texttospeech.TextToSpeechClient()
    speech_audio = None
    half_sec_pause = AudioSegment.silent(duration=500)
    num_paras = len(paragraphs) - 1
    for counter, paragraph in enumerate(paragraphs):
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
    if article.posted_at:
        posted_time = article.posted_at.strftime('%B %-d, %Y')
    else:
        posted_time = 'an unknown time.'

    intro = (
        f'{article.title}. '
        f'This article, written by {article.author}, '
        f'was published on {article.site.name} '
        f'on {posted_time}. Let\'s begin.'
    )
    outro = (
        f'That\'s the end of {article.title}, by {article.author}. '
        'I hope you enjoyed this podcast. See you next time.'
    )
    return [intro, *body, outro]
