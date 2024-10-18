import subprocess
import re
import os


def set_audio(codec):
    match codec:
        case "FDK-AAC":
            return "libfdk_aac -b:a 320k"
        case "Discord":
            return "libfdk_aac -b:a 128k"
        case _:
            print("Invalid audio codec")
            exit()


def get_loudnorm(file):

    loudnorm_json_command = f"ffmpeg -y -hide_banner -i {file} -af loudnorm=I=-24:TP=-2.0:LRA=7:print_format=json -f null - 2> loudnorm.txt"

    print(f"\nRunning command: {loudnorm_json_command}")
    subprocess.call(loudnorm_json_command, shell=True)

    loudnorm = open("loudnorm.txt", "r")
    for line in loudnorm:
        if re.search("input_i", line):
            input_i = line.replace('\t"input_i" : "', "")
            input_i = input_i.replace('",', "")
            input_i = input_i.rstrip()
        if re.search("input_tp", line):
            input_tp = line.replace('\t"input_tp" : "', "")
            input_tp = input_tp.replace('",', "")
            input_tp = input_tp.rstrip()
        if re.search("input_lra", line):
            input_lra = line.replace('\t"input_lra" : "', "")
            input_lra = input_lra.replace('",', "")
            input_lra = input_lra.rstrip()
        if re.search("input_thresh", line):
            input_thresh = line.replace('\t"input_thresh" : "', "")
            input_thresh = input_thresh.replace('",', "")
            input_thresh = input_thresh.rstrip()
        if re.search("target_offset", line):
            target_offset = line.replace('\t"target_offset" : "', "")
            target_offset = target_offset.replace('"', "")
            target_offset = target_offset.rstrip()
    loudnorm.close()
    os.remove("loudnorm.txt")

    print(f"\nLoudnorm requested for file: {file}")
    print(f"Measured integrated: {input_i}")
    print(f"Measured true peak: {input_tp}")
    print(f"Measured LRA: {input_lra}")
    print(f"Measured threshold: {input_thresh}")
    print(f"Target offset: {target_offset}\n")

    loudnorm_filter = f"loudnorm=I=-16:TP=-2.0:LRA=7:measured_I={input_i}:measured_LRA={input_lra}:measured_TP={input_tp}:measured_thresh={input_thresh}:offset={target_offset}:linear=true"

    return loudnorm_filter


def set_downmix():
    return '"pan=stereo|FL=0.5*FC+0.707*FL+0.707*BL+0.5*LFE|FR=0.5*FC+0.707*FR+0.707*BR+0.5*LFE,volume=1.640625"'
