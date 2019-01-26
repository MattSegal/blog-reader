"""
Synthesizes speech from the input string of text.
"""
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


def text_to_speech_mp3(text, mp3_path):
    client = texttospeech.TextToSpeechClient.from_service_account_json(CREDS_JSON)
    text_batches = batch(text, MAX_REQUEST_LENGTH)
    speech_audio = None
    # TODO - split this up based on paragraph, end of sentence, commas
    # and use pydub to insert pauses where appropriate
    # Add tokens upstream and interpret them here.
    for text_batch in text_batches:
        mp3_bytes_file = text_to_mp3_bytes(client, text_batch)
        audio_segment = AudioSegment.from_mp3(mp3_bytes_file)
        if speech_audio:
            speech_audio += audio_segment
        else:
            speech_audio = audio_segment

    speech_audio.export(mp3_path, format='mp3')
    print(f'Audio content written to file \"{mp3_path}\"')

def text_to_mp3_bytes(client, text):
    assert len(text) <= 5000
    synthesis_input = texttospeech.types.SynthesisInput(text=text)
    response = client.synthesize_speech(synthesis_input, voice, audio_config)
    return BytesIO(response.audio_content)


# TODO - modify batching to split on whitespace rather than anywhere
def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]
