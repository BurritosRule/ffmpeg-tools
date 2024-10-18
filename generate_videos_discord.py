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

        # Run 2 pass loudnorm filter if user selects loudnorm
        loudnorm = audio.get_loudnorm(source.input_file)

        audio_filter = f" -af {loudnorm} "

        bitrate = video.set_calculated_discord_bitrate(source.duration_seconds)
        resize = video.set_discord_resize(source.aspect_ratio)
        vf_filter = f"-vf {resize},unsharp=3:3:0.3:3:3:0.0 "

        ffmpeg_extract_audio = f'ffmpeg -probesize 42M -i "{input_path}{input_file}" -vn{audio_filter}-acodec pcm_f32le -f wav extracted_audio.wav'
        qaac_encode_audio = (
            f"qaac64 -i extracted_audio.wav -c 128 --no-delay -o encoded_audio.m4a"
        )
        # 2 pass FFmpeg commmands for Discord version
        ffmpeg_command_1 = f"ffmpeg -probesize 42M -y -loglevel error -i {input_path}{input_file} -i encoded_audio.m4a -map 0:v:0 -map 1:a -c:a copy {vf_filter}-c:v libx264 -preset veryslow -b:v {int(bitrate)}k -pix_fmt yuv420p -pass 1 -map_metadata -1 -map_chapters -1 -write_tmcd 0 -f mp4 dummy"
        ffmpeg_command_2 = f"ffmpeg -probesize 42M -i {input_path}{input_file} -i encoded_audio.m4a -map 0:v:0 -map 1:a -c:a copy {vf_filter}-c:v libx264 -preset veryslow -b:v {int(bitrate)}k -pix_fmt yuv420p -color_primaries 1 -color_trc 1 -colorspace 1 -pass 2 -profile:v high -level 4.1 -map_metadata -1 -map_chapters -1 -write_tmcd 0 -movflags +faststart {output_path}{source.file_name}-discord.mp4"

        print(f"\nRunning command: {ffmpeg_extract_audio}")
        subprocess.call(ffmpeg_extract_audio, shell=True)
        print(f"\nRunning command: {qaac_encode_audio}")
        subprocess.call(qaac_encode_audio, shell=True)
        # Run pass 1 FFmpeg command
        print(f"\nRunning command: {ffmpeg_command_1}")
        subprocess.call(ffmpeg_command_1, shell=True)
        # Run pass 2 FFmpeg command
        print(f"\nRunning command: {ffmpeg_command_2}")
        subprocess.call(ffmpeg_command_2, shell=True)

        os.remove("extracted_audio.wav")
        os.remove("encoded_audio.m4a")
        os.remove("dummy")
        os.remove("ffmpeg2pass-0.log")
        os.remove("ffmpeg2pass-0.log.mbtree")

        source.cleanup()
        del source
