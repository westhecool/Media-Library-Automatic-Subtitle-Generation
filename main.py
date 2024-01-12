import time
import os
import argparse
import subprocess
import pathlib
import sys

args = argparse.ArgumentParser()
args.description = "Automatic subtitle generation using OpenAI's Whisper for jellyfin."
args.add_argument("--model", type=str, help="Model to use. (Default: large-v3)", default="large-v3")
args.add_argument("--language", type=str, help="Language to transcribe for. (Default: en)", default="en")
args.add_argument("--gpu", type=bool, help="Use GPU.", default=False, action=argparse.BooleanOptionalAction)
args.add_argument("--gpu-index", type=int, help="The index of the GPU to use. (Starting from 0) (Default: 0)", default=0)
args.add_argument("input", type=str, help="Input file or directory. (Is recursive if a directory is provided.)")
args = args.parse_args()

def seconds_to_hmsms(seconds):
    # Calculate hours, minutes, and seconds
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    # Split seconds into whole and fractional parts
    seconds_whole = int(seconds)
    milliseconds = int((seconds - seconds_whole) * 1000)

    # Format the result as a string
    result = f'{int(hours):02d}:{int(minutes):02d}:{seconds_whole:02d},{milliseconds:03d}'

    return result

def seconds_to_hms(seconds):
    # Calculate hours, minutes, and seconds
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    # Split seconds into whole and fractional parts
    seconds_whole = int(seconds)

    # Format the result as a string
    result = f'{int(hours):02d}:{int(minutes):02d}:{seconds_whole:02d}'

    return result

model_size = args.model

from faster_whisper import WhisperModel

if args.gpu:
    model = WhisperModel(args.model, device="cuda", compute_type="int8_float16", device_index=args.gpu_index)
else:
    model = WhisperModel(args.model, device="cpu", compute_type="int8")

def process_file(path):
    start = time.time()
    _path = pathlib.Path(path)
    print(f"Processing {path}...")
    mp3file = _path.with_suffix(".mp3")
    print(f"Converting {_path.as_posix()} to {mp3file.as_posix()}...")
    subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-ac", "2", mp3file.as_posix(), "-y"])
    print(f"Transcribing {mp3file.as_posix()}...")
    segments, info = model.transcribe(mp3file.as_posix(), language=args.language)
    #print("Detected language '%s' with probability %f." % (info.language, info.language_probability))
    text = ""
    i = 0
    for segment in segments:
        i += 1
        t = "%i\n%s --> %s\n%s\n" % (i, seconds_to_hmsms(segment.start), seconds_to_hmsms(segment.end), segment.text.strip())
        print("\rProcessed: " + seconds_to_hms(segment.end), end="") # just to show progress
        text += t
    print("")
    with open(_path.with_suffix('.srt').as_posix(), "w") as f:
        f.write(text)
    end = time.time()
    total = int(end - start)
    os.remove(mp3file.as_posix())
    print(f"Finished transcribing {mp3file.as_posix()} in {total} seconds\n") # new line as a separator


input = pathlib.Path(args.input)
if not input.exists():
    print(f"{input.as_posix()} does not exist!")
    exit(1)
if input.is_file():
    process_file(args.input)
elif input.is_dir():
    for root, dirs, files in os.walk(input.as_posix()):
        for file in files:
            if file.endswith(".mkv") or file.endswith(".mp4") or file.endswith(".avi") or file.endswith(".mov") or file.endswith(".webm"):
                if not os.path.exists(pathlib.Path(os.path.join(root, file)).with_suffix(".srt").as_posix()):
                    try:
                        process_file(os.path.join(root, file))
                    except Exception as e:
                        print(e)
                else:
                    print(f"Skipping {os.path.join(root, file)} because the subtitles already exist.")