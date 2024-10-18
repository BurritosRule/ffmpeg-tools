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

        audio_indicator = input("Audio?: ")

        if audio_indicator.upper() == "Y":
            loudnorm_indicator = input("Loudnorm audio?: ")
        else:
            loudnorm_indicator = "N"

        resize_width = input("New horizontal width (leave blank for source): ")

        verify_vmaf = input("Verify with VMAF?: ")

        source = Source(f"{input_path}{input_file}")

        output_height = source.height
        output_width = resize_width if resize_width else source.width

        keyframe_spacing = video.set_keyframe_spacing(source.fps)

        h264_level = video.set_h264_level(output_height, output_width, source.fps)

        # Change output width to user entered value
        if resize_width == "":
            resize = ""
        else:
            resize = video.set_resize(resize_width)

        # Construct vf filter
        if resize:
            vf_filter = f"-vf {resize} "
        else:
            vf_filter = ""

        # Run 2 pass loudnorm filter if user selected loudnorm
        if loudnorm_indicator.upper() == "Y":
            loudnorm = audio.get_loudnorm(source.input_file)
        else:
            loudnorm = ""

        if loudnorm_indicator.upper() == "Y":
            audio_filter = f" -af {loudnorm} "
        else:
            audio_filter = f" "

        if audio_indicator.upper() == "Y":
            ffmpeg_extract_audio = f'ffmpeg -probesize 42M -i "{input_path}{input_file}" -vn{audio_filter}-acodec pcm_f32le -f wav extracted_audio.wav'
            qaac_encode_audio = f"qaac64 -i extracted_audio.wav --tvbr 127 --no-delay -o encoded_audio.m4a"
            ffmpeg_combine_audio_and_encode_video = f"ffmpeg -probesize 42M -i {input_path}{input_file} -i encoded_audio.m4a -map 0:v:0 -map 1:a -c:a copy {vf_filter}-c:v libx264 -preset veryslow -crf 16 -x264-params aq-mode=3 -pix_fmt yuv420p -color_primaries {source.color_primaries} -color_trc {source.color_transfer} -colorspace {source.color_space} -profile:v high {h264_level} -map_metadata -1 -map_chapters -1 -write_tmcd 0 -movflags +faststart {output_path}{source.file_name}.mp4"

            print(f"\nRunning command: {ffmpeg_extract_audio}")
            subprocess.call(ffmpeg_extract_audio, shell=True)
            print(f"\nRunning command: {qaac_encode_audio}")
            subprocess.call(qaac_encode_audio, shell=True)
            print(f"\nRunning command: {ffmpeg_combine_audio_and_encode_video}")
            subprocess.call(ffmpeg_combine_audio_and_encode_video, shell=True)

            os.remove("extracted_audio.wav")
            os.remove("encoded_audio.m4a")

        else:
            ffmpeg_command = f"ffmpeg -probesize 42M -i {input_path}{input_file} -map 0:v:0 -an {vf_filter}-c:v libx264 -preset veryslow -crf 16 -g {keyframe_spacing} -keyint_min {keyframe_spacing} -pix_fmt yuv420p -color_primaries {source.color_primaries} -color_trc {source.color_transfer} -colorspace {source.color_space} -profile:v high {h264_level} -map_metadata -1 -map_chapters -1 -write_tmcd 0 -movflags +faststart {output_path}{source.file_name}.mp4"
            print(f"\nRunning command: {ffmpeg_command}")
            subprocess.call(ffmpeg_command, shell=True)

        if verify_vmaf.upper() == "Y":
            video.verify_vmaf(
                f"{input_path}{input_file}", f"{output_path}{source.file_name}.mp4"
            )

        source.cleanup()
        del source
