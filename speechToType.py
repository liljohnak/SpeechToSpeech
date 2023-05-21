import openai
import os
import uuid
import winsound
from pvrecorder import PvRecorder
import wave
import struct
from pynput import keyboard
import string

openai.api_key = os.getenv("OPENAI_API_KEY")
audio_device = [index for index, _ in enumerate(PvRecorder.get_audio_devices())] # _ is a device name
recorder = PvRecorder(device_index=0, frame_length=512)
audio = []
random_uuid = uuid.uuid4()
path = os.path.join(os.environ['USERPROFILE'], "Documents", "Sound recordings", f"TypeThis{str(random_uuid)[0:5]}.m4a")
is_recording = False
text_to_type = ""
kb = keyboard.Controller()

def translation_to_word(transcript_of_text_from_whisper, txt_file_name):
    translater = {}
    with open(os.path.join(os.path.dirname(__file__), txt_file_name), "r") as f:
        for line in f.readlines():
            line_match = line.split()
            translater[line_match[0].lower()] = " ".join(line_match[1:])
    return [translater[w.lower()] if w.lower() in translater.keys() else w for w in transcript_of_text_from_whisper]

def bad_translation_to_word(transcript_of_text_from_whisper):
    return translation_to_word(transcript_of_text_from_whisper, "wrong_translation.txt")

def roblox_translation_to_word(transcript_of_text_from_whisper):
    return translation_to_word(transcript_of_text_from_whisper, "roblox_translation.txt")

def minecraft_translation_to_word(transcript_of_text_from_whisper):
    return translation_to_word(transcript_of_text_from_whisper, "minecraft_translation.txt")

def word_in_list(transcript_of_text_from_whisper, word):
    for w in transcript_of_text_from_whisper:
        if word.lower() in w.lower():
            return True
    return False 


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
            print(transcript.text)
            command_prompt = f"{transcript.text}\n\nTl;dr" # TL;DR summarization
            string.punctuation
            transcript_without_punctuations = transcript.text.translate(str.maketrans('', '', string.punctuation))
            heard_words = transcript_without_punctuations.split()
            if word_in_list(heard_words, "command"): # " from the python arcpy object" " from minecraft" " from roblox"
                SYSTEM_PROMPT = "From now on, your response must be only using code, no talking, no comments."
                replacement_prompt = transcript.text
                heard_words = bad_translation_to_word(heard_words)
                if word_in_list(heard_words, "minecraft"):
                    heard_words = minecraft_translation_to_word(heard_words)
                    replacement_prompt = " ".join(heard_words)     
                elif word_in_list(heard_words, "roblox"):
                    heard_words = roblox_translation_to_word(heard_words)
                    replacement_prompt = " ".join(heard_words)
                command_prompt = f"{SYSTEM_PROMPT}\n\n{replacement_prompt}"
            elif len(heard_words) < 10:
                command_prompt = transcript.text
            response = openai.Completion.create(# price: $0.0200 / 1K tokens
            model="text-davinci-003",
            prompt= command_prompt,
            temperature=0.001,
            max_tokens=64,
            frequency_penalty=0.0,
            presence_penalty=0.0
            )
            kb.type(response.choices[0].text.strip())
            return False
            

while(True):
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
    recorder = PvRecorder(device_index=0, frame_length=512)
    audio = []
    random_uuid = uuid.uuid4()
    path = os.path.join(os.environ['USERPROFILE'], "Documents", "Sound recordings", f"TypeThis{str(random_uuid)[0:5]}.m4a")
    is_recording = False