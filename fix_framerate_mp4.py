import subprocess
import os
from os import listdir
from os.path import isfile, join
from classes.source import Source

video_ext = [
    ".3g2",
    ".3gp",
    ".asf",
    ".asx",
    ".avi",
    ".flv",
    ".m2ts",
    ".mkv",
    ".mov",
    ".mp4",
    ".mpg",
    ".mpeg",
    ".rm",
    ".swf",
    ".vob",
    ".wmv",
]

input_path = "input/"
output_path = "output/"
files = [f for f in listdir(input_path) if isfile(join(input_path, f))]

fps = input("What is the original FPS?: ")

for input_file in files:
    input_file_minus_extension = os.path.splitext(input_file)[0]

    if input_file.endswith(tuple(video_ext)):
        print(f"\nProcessing file: {input_file}\n")

        source = Source(f"{input_path}{input_file}")

        file_name = source.file_name

        # FFmpeg command to remux into mp4 container
        ffmpeg_command_1 = f'ffmpeg -i "{input_path}{input_file}" -c copy "{output_path}{file_name}.mp4"'

        # mp4fpsmod command to fix frame rate
        mp4fpsmod_command_1 = f'mp4fpsmod -r 0:{fps} -o "{output_path}{file_name}_Fixed.mp4" "{output_path}{file_name}.mp4"'

        # Run FFmpeg command
        subprocess.call(ffmpeg_command_1, shell=True)
        print(f"\nRan command: {ffmpeg_command_1}")

        # Run mp4fpsmod command
        subprocess.call(mp4fpsmod_command_1, shell=True)
        print(f"\nRan command: {mp4fpsmod_command_1}")

        # Remove incorrect mp4
        os.remove(f"{output_path}{file_name}.mp4")

        del source
