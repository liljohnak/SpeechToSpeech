import openai
import os
import uuid
import winsound
from pvrecorder import PvRecorder
import wave
import struct
from pynput import keyboard

openai.api_key = os.getenv("OPENAI_API_KEY")
audio_device = [index for index, _ in enumerate(PvRecorder.get_audio_devices())] # _ is a device name
recorder = PvRecorder(device_index=0, frame_length=512)
audio = []
random_uuid = uuid.uuid4()
path = os.path.join(os.environ['USERPROFILE'], "Documents", "Sound recordings", f"CodeThis{str(random_uuid)[0:5]}.m4a")
is_recording = False

def on_press(key):
    global is_recording
    if key == keyboard.Key.f8:
        if is_recording:
            frame = recorder.read()
            audio.extend(frame)
        else:
            winsound.Beep(1000, 100)  # Beep at 1000 Hz for 100 ms
            recorder.start()
            is_recording = True

def on_release(key):
    global is_recording
    if key == keyboard.Key.f8:
        if is_recording:
            recorder.stop()
            winsound.Beep(1000, 100)  # Beep at 1000 Hz for 100 ms
            with wave.open(path, 'w') as f:
                f.setparams((1, 2, 16000, 512, "NONE", "NONE"))
                f.writeframes(struct.pack("h" * len(audio), *audio))
            recorder.delete()
            audio_file = open(path, "rb")
            transcript = openai.Audio.transcribe("whisper-1", audio_file) #price: $0.006 / minute (rounded to the nearest second)
            SYSTEM_PROMPT = ""
            print(os.path.join(os.path.dirname(__file__), "prompt.txt"))
            with open(os.path.join(os.path.dirname(__file__), "prompt.txt"), "r") as f:
                SYSTEM_PROMPT = f.read()
            response = openai.Completion.create(
                        model="text-davinci-003",
                        prompt=f"{SYSTEM_PROMPT}\n\n{transcript.text}",
                        top_p=1.0,
                        max_tokens=90,
                    )
            with open(f"{path[:-4]}_out.py", 'w') as f:
                f.write(response.choices[0].text)
            return False
            

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()