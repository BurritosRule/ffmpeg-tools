import subprocess
import os
import glob
from utilities import gif
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
    ".mxf",
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

for input_file in files:
    if input_file.endswith(tuple(video_ext)):
        print(f"\nProcessing file: {input_file}\n")

        source = Source(f"{input_path}{input_file}")

        frame_delay = 4

        scale = gif.gifski_resize(source.width, source.aspect_ratio)

        gif_commands = gif.get_gif_commands_gifski(
            input_path, input_file, output_path, source.file_name, scale, frame_delay
        )

        for command in gif_commands:
            print(f"\nRunning command: {command}\n")
            subprocess.call(command, shell=True)

        for frame in glob.glob("output/frame*.png"):
            os.remove(frame)

        source.cleanup()

        del source
