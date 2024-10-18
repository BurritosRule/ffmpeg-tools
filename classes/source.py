import subprocess
import os
from datetime import datetime
import json


class Source:
    def __init__(self, input_file):

        ffprobe = f'ffprobe -hide_banner -loglevel warning -select_streams v:0 -print_format json -show_frames -read_intervals "%+#1" -show_entries "frame=color_space,color_primaries,color_transfer,side_data_list,pix_fmt" -show_entries "stream=r_frame_rate,width,height,nb_frames" -show_entries "format=duration" -sexagesimal "{input_file}" > ffprobe.txt'

        print(f"\nRunning command: {ffprobe}")
        subprocess.call(ffprobe, shell=True)

        f = open("ffprobe.txt")
        ffprobe_results = json.load(f)
        f.close

        self.width = ffprobe_results["streams"][0]["width"]
        self.height = ffprobe_results["streams"][0]["height"]
        self.fps = ffprobe_results["streams"][0]["r_frame_rate"]
        if self.fps == "19001/317":
            self.fps = "60000/1001"
        self.num_of_frames = (
            ffprobe_results["streams"][0]["nb_frames"]
            if "nb_frames" in ffprobe_results["streams"][0]
            else 0
        )
        self.duration_sexagesimal = ffprobe_results["format"]["duration"]
        duration_delta = datetime.strptime(
            self.duration_sexagesimal, "%H:%M:%S.%f"
        ) - datetime.strptime("00:00:00.000000", "%H:%M:%S.%f")
        self.duration_seconds = float(duration_delta.total_seconds())
        self.aspect_ratio = round(int(self.width) / int(self.height), 4)
        self.input_file = input_file
        self.file_without_path = input_file.rsplit("/", 1)[1]
        self.file_name = os.path.splitext(self.file_without_path)[0]
        self.file_extension = os.path.splitext(input_file)[1].replace('"', "")
        self.pix_fmt = ffprobe_results["frames"][0]["pix_fmt"]
        self.color_space = (
            ffprobe_results["frames"][0]["color_space"]
            if "color_space" in ffprobe_results["frames"][0]
            else "bt709"
        )
        self.color_primaries = (
            ffprobe_results["frames"][0]["color_primaries"]
            if "color_primaries" in ffprobe_results["frames"][0]
            else "bt709"
        )
        self.color_transfer = (
            ffprobe_results["frames"][0]["color_transfer"]
            if "color_transfer" in ffprobe_results["frames"][0]
            else "bt709"
        )
        if self.is_hdr(self.color_primaries):
            self.red_x = ffprobe_results["frames"][0]["side_data_list"][0][
                "red_x"
            ].replace("/50000", "")
            self.red_y = ffprobe_results["frames"][0]["side_data_list"][0][
                "red_y"
            ].replace("/50000", "")
            self.green_x = ffprobe_results["frames"][0]["side_data_list"][0][
                "green_x"
            ].replace("/50000", "")
            self.green_y = ffprobe_results["frames"][0]["side_data_list"][0][
                "green_y"
            ].replace("/50000", "")
            self.blue_x = ffprobe_results["frames"][0]["side_data_list"][0][
                "blue_x"
            ].replace("/50000", "")
            self.blue_y = ffprobe_results["frames"][0]["side_data_list"][0][
                "blue_y"
            ].replace("/50000", "")
            self.white_point_x = ffprobe_results["frames"][0]["side_data_list"][0][
                "white_point_x"
            ].replace("/50000", "")
            self.white_point_y = ffprobe_results["frames"][0]["side_data_list"][0][
                "white_point_y"
            ].replace("/50000", "")
            self.min_luminance = ffprobe_results["frames"][0]["side_data_list"][0][
                "min_luminance"
            ].replace("/10000", "")
            self.max_luminance = ffprobe_results["frames"][0]["side_data_list"][0][
                "max_luminance"
            ].replace("/10000", "")
            self.max_content = ffprobe_results["frames"][0]["side_data_list"][1][
                "max_content"
            ]
            self.max_average = ffprobe_results["frames"][0]["side_data_list"][1][
                "max_average"
            ]

        print(f"\nFull path: {input_file}")
        print(f"File: {self.file_name}")
        print(f"File extension: {self.file_extension}")
        print(f"Horizontal resolution: {self.width}")
        print(f"Vertical resolution: {self.height}")
        print(f"Frame rate: {self.fps}")
        print(f"Number of frames: {self.num_of_frames}")
        print(f"Duration (sexagesimal): {self.duration_sexagesimal}")
        print(f"Duration (seconds): {self.duration_seconds}")
        print(f"Aspect ratio: {self.aspect_ratio}")
        print(f"\nColor Info:")
        print(f"pix_fmt: {self.pix_fmt}")
        print(f"color_space: {self.color_space}")
        print(f"color_primaries: {self.color_primaries}")
        print(f"color_transfer: {self.color_transfer}")
        if self.is_hdr(self.color_primaries):
            print(f"red_y: {self.red_x}")
            print(f"red_y: {self.red_y}")
            print(f"green_x: {self.green_x}")
            print(f"green_y: {self.green_y}")
            print(f"blue_x: {self.blue_x}")
            print(f"blue_y: {self.blue_y}")
            print(f"white_point_x: {self.white_point_x}")
            print(f"white_point_y: {self.white_point_y}")
            print(f"min_luminance: {self.min_luminance}")
            print(f"max_luminance: {self.max_luminance}")
            print(f"max_content: {self.max_content}")
            print(f"max_average: {self.max_average}\n")

    def is_hdr(self, color_primaries):
        if color_primaries == "bt2020":
            return True
        else:
            return False

    def cleanup(self):
        os.remove("ffprobe.txt")
