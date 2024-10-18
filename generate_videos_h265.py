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

        if source.is_hdr(source.color_primaries):
            # Low VMAF? Try CRF 14 and rdoq-level=1:psy-rdoq=3:rskip=2:aq-mode=3:no-sao=1
            # This seems to be needed to avoid dropped frames: lookahead-slices=4:rc-lookahead=25:bframes=4
            # Match Staxrip: no-hdr10-opt=1:sar=0:no-b-intra=1:no-weightb=1:subme=3:limit-refs=3:max-merge=3:limit-tu=0:tu-intra-depth=1:tu-inter-depth=1:no-amp=1:lookahead-slices=4:rc-lookahead=25:bframes=4:aud=1:ref=4
            color_params = f"-x265-params rdoq-level=1:psy-rdoq=3:rskip=2:aq-mode=3:no-sao=1:hdr-opt=1:repeat-headers=1:colorprim={source.color_primaries}:transfer={source.color_transfer}:colormatrix={source.color_space}:master-display=G({source.green_x},{source.green_y})B({source.blue_x},{source.blue_y})R({source.red_x},{source.red_y})WP({source.white_point_x},{source.white_point_y})L({source.max_luminance},{source.min_luminance}):max-cll={source.max_content},{source.max_average}:chromaloc=2"
        else:
            color_params = f"-x265-params rdoq-level=1:psy-rdoq=3:rskip=2:aq-mode=3:no-sao=1:colorprim={source.color_primaries}:transfer={source.color_transfer}:colormatrix={source.color_space}"

        if audio_indicator.upper() == "Y":
            ffmpeg_extract_audio = f'ffmpeg -probesize 42M -i "{input_path}{input_file}" -vn{audio_filter}-acodec pcm_f32le -f wav extracted_audio.wav'
            qaac_encode_audio = f"qaac64 -i extracted_audio.wav --tvbr 127 --no-delay -o encoded_audio.m4a"
            ffmpeg_combine_audio_and_encode_video = f"ffmpeg -probesize 42M -i {input_path}{input_file} -i encoded_audio.m4a -map 0:v:0 -map 1:a -c:a copy {vf_filter}-c:v libx265 -preset slow -crf 18 -pix_fmt yuv420p10le {color_params} -profile:v main10 -map_metadata -1 -map_chapters -1 -write_tmcd 0 -tag:v hvc1 -movflags +faststart {output_path}{source.file_name}.mp4"

            print(f"\nRunning command: {ffmpeg_extract_audio}")
            subprocess.call(ffmpeg_extract_audio, shell=True)
            print(f"\nRunning command: {qaac_encode_audio}")
            subprocess.call(qaac_encode_audio, shell=True)
            print(f"\nRunning command: {ffmpeg_combine_audio_and_encode_video}")
            subprocess.call(ffmpeg_combine_audio_and_encode_video, shell=True)

            os.remove("extracted_audio.wav")
            os.remove("encoded_audio.m4a")

        else:
            ffmpeg_command = f"ffmpeg -probesize 42M -i {input_path}{input_file} -map 0:v:0 -an {vf_filter}-c:v libx265 -preset slow -crf 14 -pix_fmt yuv420p10le {color_params} -profile:v main10 -map_metadata -1 -map_chapters -1 -write_tmcd 0 -tag:v hvc1 -movflags +faststart {output_path}{source.file_name}.mp4"
            print(f"\nRunning command: {ffmpeg_command}")
            subprocess.call(ffmpeg_command, shell=True)

        if verify_vmaf.upper() == "Y":
            video.verify_vmaf(
                f"{input_path}{input_file}", f"{output_path}{source.file_name}.mp4"
            )

        source.cleanup()
        del source
