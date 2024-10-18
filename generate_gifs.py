import subprocess
import os
from utilities import gif
from utilities import common
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

        fps = gif.set_fps(source.fps)
        translated_fps = common.translate_fps(fps)
        is_widescreen = common.is_widescreen(source.width, source.height)
        discord_scale = gif.set_resize_discord(source.aspect_ratio)

        fps = 23.976
        num_of_output_frames = round(fps * source.duration_seconds)
        frame_delay = gif.get_frame_delay_by_num_frames(num_of_output_frames, 3)

        gif_commands = gif.get_gif_commands_ffmpeg(
            input_path,
            input_file,
            output_path,
            source.file_name,
            discord_scale,
            translated_fps,
            frame_delay,
        )

        for command in gif_commands:
            print(f"Running command: {command}\n")
            subprocess.call(command, shell=True)

        os.remove("temp.gif")
        source.cleanup()

        del source
