import subprocess
from utilities import audio
from utilities import video
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
    input_file_minus_extension = os.path.splitext(input_file)[0]

    if input_file.endswith(tuple(video_ext)):
        print(f"\nProcessing file: {input_file}\n")

        source = Source(f"{input_path}{input_file}")

        output_height = source.height
        output_width = source.width

        keyframe_spacing = video.set_keyframe_spacing(source.fps)

        loudnorm = audio.get_loudnorm(source.input_file)
        audio_filter = f" -af {loudnorm} "

        ffmpeg_pass_1 = f"ffmpeg -probesize 42M -i {input_path}{input_file} -an -c:v libvpx-vp9 -b:v 0 -g {keyframe_spacing} -crf 14 -pass 1 -pix_fmt yuv420p10le -profile:v 2 -row-mt 1 -color_primaries {source.color_primaries} -color_trc {source.color_transfer} -colorspace {source.color_space} -map_metadata -1 -map_chapters -1 -write_tmcd 0 -f null /dev/null"
        ffmpeg_pass_2 = f"ffmpeg -probesize 42M -i {input_path}{input_file} -c:a libopus -application lowdelay -b:a 192K{audio_filter}-c:v libvpx-vp9 -b:v 0 -g {keyframe_spacing} -crf 14 -pass 2 -pix_fmt yuv420p10le -profile:v 2 -row-mt 1 -color_primaries {source.color_primaries} -color_trc {source.color_transfer} -colorspace {source.color_space} -map_metadata -1 -map_chapters -1 -write_tmcd 0 {output_path}{source.file_name}.webm"
        print(f"\nRunning command: {ffmpeg_pass_1}")
        subprocess.call(ffmpeg_pass_1, shell=True)
        print(f"\nRunning command: {ffmpeg_pass_2}")
        subprocess.call(ffmpeg_pass_2, shell=True)

        source.cleanup()
        del source

        os.remove("ffmpeg2pass-0.log")
