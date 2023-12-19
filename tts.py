import wave
import sys
import json
from vosk import Model, KaldiRecognizer, SetLogLevel
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip

# You can set log level to -1 to disable debug messages
SetLogLevel(0)

# wf = wave.open(sys.argv[1], "rb")
wf = wave.open("post0.wav", "rb")
if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
    print("Audio file must be WAV format mono PCM.")
    sys.exit(1)

model = Model(lang="en-us")

# You can also init model by name or with a folder path
# model = Model(model_name="vosk-model-en-us-0.21")
# model = Model("models/en")

rec = KaldiRecognizer(model, wf.getframerate())
rec.SetWords(True)
rec.SetPartialWords(True)

resultsList = []

while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        result = json.loads(rec.Result())
        print("Result:", result["text"])

        wordCount = len(result["result"])

        if wordCount > 12:
            text = result["text"]
            words = text.split()
            start = result["result"][0]["start"]

            # Split into chunks of max 12 words with a minimum length of 6 words
            chunk_size = 12
            min_chunk_size = 6
            chunks = []
            i = 0

            while i < len(words):
                chunk = words[i:i + chunk_size]
                chunk_start = result["result"][i]["start"]  # Set start time based on the position of the first word in the chunk

                # Ensure the last chunk has at least min_chunk_size words
                if len(chunk) < min_chunk_size and len(chunks) > 0:
                    chunks[-1][1].extend(chunk)  # Extend the existing list in the list
                else:
                    chunks.append([chunk_start, chunk])

                i += chunk_size

            # Add chunks to the resultsList
            for chunk_start, chunk_words in chunks:
                chunk_text = ' '.join(chunk_words)
                resultsList.append((chunk_text, chunk_start))
        else:
            resultsList.append((result["text"], result["result"][0]["start"]))

final_result = json.loads(rec.FinalResult())
resultsList.append((final_result["text"], final_result["result"][0]["start"]))

print(resultsList)

for count, i in enumerate(resultsList):
    print(f'{count}: {i}')

# Modify the structure of resultsList to match the expected format
subtitles_list = [(start, start + len(chunk.split()) / wf.getframerate(), chunk) for chunk, start in resultsList]

# Function to generate subtitles at specific time intervals
def generate_subtitles(subtitles_list):
    return SubtitlesClip(subtitles_list, make_texts)

# Function to create text clips
def make_texts(subtitles, video):
    return [(subtitle[0], subtitle[1], TextClip(subtitle[2], fontsize=24, color='white').set_pos('center')) for subtitle in subtitles]

# Function to add subtitles to a video
def add_subtitles(video_path, subtitles_list, output_path):
    video_clip = VideoFileClip(video_path)
    subtitles_clip = generate_subtitles(subtitles_list)

    # Overlay subtitles on the video
    video_with_subtitles = CompositeVideoClip([video_clip, subtitles_clip.set_duration(video_clip.duration)])

    # Write the result to a file
    video_with_subtitles.write_videofile(output_path, codec='libx264', audio_codec='aac')

# Example usage
video_path = 'Video11.mp4'
output_path = 'short0.mp4'

add_subtitles(video_path, subtitles_list, output_path)
