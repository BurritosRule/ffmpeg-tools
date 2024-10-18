import subprocess
import re
import os


def set_h264_level(height, width, fps):
    if int(width) >= 1200 and (fps == "60000/1001" or fps == "50/1" or fps == "60/1"):
        h264_level = "-level 4.2"
    elif (int(width) > 1920 or int(height) > 1080) and not (
        fps == "60000/1001" or fps == "50/1" or fps == "60/1"
    ):
        h264_level = "-level 5.1"
    elif int(width) > 1920 and (fps == "60000/1001" or fps == "50/1" or fps == "60/1"):
        h264_level = "-level 5.2"
    else:
        h264_level = "-level 4.1"
    print(f"Setting h264 profile to {h264_level}")
    return h264_level


def set_keyframe_spacing(fps):
    if fps == "60000/1001" or fps == "60/1":
        keyframe_spacing = "120"
    elif fps == fps == "50/1":
        keyframe_spacing = "100"
    elif fps == "30000/1001" or fps == "30/1" or fps == "2997/100":
        keyframe_spacing = "60"
    elif fps == "24000/1001" or fps == "24/1":
        keyframe_spacing = "48"
    elif fps == fps == "25/1":
        keyframe_spacing = "50"
    else:
        print(f"Unknown fps {fps} exiting script")
        exit()
    print(f"Setting keyframe spacing to {keyframe_spacing}")
    return keyframe_spacing


# Convert target output filesize from MB to KB (8 * 8192 = 65536)
# Divide by duration of input (65536 / video.duration_seconds)
# Subtract audio bitrate ((65536 / video.duration_seconds) - 128)


def set_calculated_discord_bitrate(duration):
    bitrate = ((8 * 8192) / int(float(duration))) - 128
    print("\n\nDiscord version selected...")
    print(f"Using calculation: ((8 * 8192)/int(float({duration}))) - 128")
    print(f"Calculated bitrate for 8MB output: {int(bitrate)}kbs\n")
    return bitrate


def set_discord_bitrate():
    bitrate = 4000
    return bitrate


def set_resize(new_width):
    print(f"Resizing to {new_width}")
    return f"scale={new_width}:-1:flags=lanczos"


# Resize to standard output width to keep quality consistent


def set_discord_resize(aspect_ratio):
    match aspect_ratio:
        # 16:9 aspect ratio
        case 1.7778:
            resize = "scale=768:432:flags=lanczos"
            print(f"Aspect ratio is: {aspect_ratio} setting height to 432")
        # 4:3 aspect ratio
        case 1.3333:
            resize = "scale=640:480:flags=lanczos"
            print(f"Aspect ratio is: {aspect_ratio} setting height to 480")
        # 9:16 aspect ratio
        case 0.5625:
            resize = "scale=432:768:flags=lanczos"
            print(f"Aspect ratio is: {aspect_ratio} setting height to 768")
        # Near 9:16 aspect ratio (actually 76:135). It looks like certain iPhones use this
        case 0.5630:
            resize = "scale=456:810:flags=lanczos"
            print(f"Aspect ratio is: {aspect_ratio} setting height to 810")
        # 2.40:1
        case 2.4:
            resize = "scale=960:400:flags=lanczos"
            print(f"Aspect ratio is: {aspect_ratio} setting height to 400")
        # 2.39:1
        case 2.39:
            resize = "scale=956:400:flags=lanczos"
            print(f"Aspect ratio is: {aspect_ratio} setting height to 400")
        # 2.35:1
        case 2.35:
            resize = "scale=940:400:flags=lanczos"
            print(f"Aspect ratio is: {aspect_ratio} setting height to 400")
        # 2:3
        case 0.6667:
            resize = "scale=520:780:flags=lanczos"
            print(f"Aspect ratio is: {aspect_ratio} setting height to 780")
        # 3:2
        case 1.5000:
            resize = "scale=720:480:flags=lanczos"
            print(f"Aspect ratio is: {aspect_ratio} setting height to 480")
        # 1:1
        case 1.0:
            resize = "scale=576:576:flags=lanczos"
            print(f"Aspect ratio is: {aspect_ratio} setting height to 576")
        case _:
            print(f"Unknown aspect ratio {aspect_ratio} exiting script")
            exit()
    return resize


def verify_vmaf(original_file, encoded_file):
    encoded_vmaf_score = float(0.000000)
    target_vmaf_score = float(96.000000)

    ffmpeg_command = f"ffmpeg -i {encoded_file} -i {original_file} -lavfi libvmaf -f null – 2> vmaf.txt"
    print(f"\nRunning command: {ffmpeg_command}")
    subprocess.call(ffmpeg_command, shell=True)

    vmaf = open("vmaf.txt", "r")
    for line in vmaf:
        if re.search("VMAF score", line):
            line = line.rstrip()
            encoded_vmaf_score = line[-9:]
    if float(encoded_vmaf_score) < target_vmaf_score:
        print(
            f"VMAF Score {encoded_vmaf_score} less than target {target_vmaf_score}: FAIL"
        )
    else:
        print(f"VMAF Score {encoded_vmaf_score} meets target {target_vmaf_score}: PASS")

    vmaf.close()
    os.remove("vmaf.txt")
