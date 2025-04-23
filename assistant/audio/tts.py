import io
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from ..config import AUDIO_LANGUAGE, AUDIO_TLD

def speak(text):
    tts = gTTS(text=text, lang=AUDIO_LANGUAGE, tld=AUDIO_TLD)
    buffer = io.BytesIO()
    tts.write_to_fp(buffer)
    buffer.seek(0)
    audio = AudioSegment.from_file(buffer, format="mp3")
    play(audio) 