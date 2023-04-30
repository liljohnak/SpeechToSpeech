import openai
import os
import uuid
import winsound
from pvrecorder import PvRecorder
import wave
import struct
from gtts import gTTS
openai.api_key = os.getenv("OPENAI_API_KEY")
audo_device = [index for index, _ in enumerate(PvRecorder.get_audio_devices())] # _ is a device name
recorder = PvRecorder(device_index=0, frame_length=512)
audio = []
random_uuid = uuid.uuid4()
path = os.path.join(os.environ['USERPROFILE'], "Documents", "Sound recordings", f"Recording{str(random_uuid)[0:5]}.m4a")
try:
    winsound.Beep(1000, 100)  # Beep at 1000 Hz for 100 ms
    recorder.start()

    while True:
        frame = recorder.read()
        audio.extend(frame)
except KeyboardInterrupt:
    recorder.stop()
    winsound.Beep(1000, 100)  # Beep at 1000 Hz for 100 ms
    with wave.open(path, 'w') as f:
        f.setparams((1, 2, 16000, 512, "NONE", "NONE"))
        f.writeframes(struct.pack("h" * len(audio), *audio))
finally:
    recorder.delete()

audio_file= open(path, "rb")
transcript = openai.Audio.transcribe("whisper-1", audio_file)
language = 'en'
myobj = gTTS(text = transcript.text, lang = language, slow = False)
myobj.save(f"{path[:-4]}_exact.mp3")
response = openai.Completion.create(
  model="text-davinci-003",
  prompt=f"{transcript.text}\n\nTl;dr", # TL;DR summarization
  temperature=0.001,
  max_tokens=64,
  top_p=1.0,
  frequency_penalty=0.0,
  presence_penalty=0.0
)
myobj = gTTS(text = response.choices[0].text, lang = language, slow = False)
myobj.save(f"{path[:-4]}_out.mp3")