import math


def set_fps(fps):
    if fps == "60000/1001" or fps == "50/1" or fps == "60/1" or fps == "19001/317":
        print(f"Found high FPS ({fps}), adjusting to 24000/1001\n")
        fps = "24000/1001"
    return fps


def set_resize_discord(aspect_ratio):
    match aspect_ratio:
        case 1.7778:
            scale = "640:-1"
        # 9:16
        case 0.5625:
            scale = "-1:360"
        # Near 9:16 aspect ratio (actually 76:135). It looks like certain iPhones use this
        case 0.5630:
            scale = "-1:405"
        # 3:2
        case 1.5000:
            scale = "432:-1"
        # 2:3
        case 0.6667:
            scale = "-1:432"
        # 4:3
        case 1.3333:
            scale = "552:-1"
        # 3:4
        case 0.7500:
            scale = "-1:414"
        # 5:4
        case 1.2500:
            scale = "400:-1"
        # 1:1
        case 1.0000:
            scale = "480:-1"
        # 1.90:1 (True 4K uses this)
        case 1.8963:
            scale = "494:-1"
        # 2:1 For use instead of 16:9 as 2:1 will scale down to 400x200 which will avoid Discord scaling
        case 2.0000:
            scale = "400:-1"
        # 1.6:1 For use instead of 3:2 as 1.6:1 will scale down to 400x250 which will avoid Discord scaling
        case 1.6000:
            scale = "400:-1"
        case _:
            print(f"Unknown aspect ratio {aspect_ratio} exiting script\n")
            exit()
    return scale


def get_gif_commands_ffmpeg(
    input_path, input_file, output_path, file_name, discord_scale, fps, frame_delay
):
    downscale_filter = "lanczos"
    gif_commands = []
    gif_commands.append(
        f'ffmpeg -i "{input_path}{input_file}" -filter_complex "fps={fps},scale={discord_scale}:flags={downscale_filter},split[s0][s1];[s0]palettegen=stats_mode=diff:reserve_transparent=0[p];[s1][p]paletteuse" "temp.gif"'
    )
    gif_commands.append(
        f'gifsicle -O3 --delay {frame_delay} -o "{output_path}{file_name}.gif" "temp.gif"'
    )

    return gif_commands


def get_gif_commands_gifski(
    input_path, input_file, output_path, file_name, discord_scale, frame_delay
):

    fps = "23.976"
    gif_commands = []
    gif_commands.append(
        f'ffmpeg -i "{input_path}{input_file}" -filter_complex "fps={fps},mpdecimate" {output_path}frame%03d.png'
    )
    gif_commands.append(
        f'gifski --fps {fps} --quality 100{discord_scale}-o "{output_path}{file_name}.gif" {output_path}frame*.png'
    )
    gif_commands.append(
        f'gifsicle -O3 --delay {frame_delay} -o "{output_path}{file_name}.gif" "{output_path}{file_name}.gif"'
    )

    return gif_commands


def get_frame_delay_by_num_frames(num_of_frames, desired_duration):
    frame_delay = round((desired_duration / num_of_frames) * 100)
    print(
        f"\nDesired duration of {desired_duration} / number of frames {num_of_frames} * 100 = {frame_delay}\n"
    )
    if frame_delay < 4:
        print(f"Calculated delay {frame_delay} is less than 4, adjusting to 4\n")
        frame_delay = 4
    return frame_delay


def gifski_resize(width, aspect_ratio):
    match aspect_ratio:
        case 1.0:
            if width >= 480:
                return " --width=480 "
            else:
                return " "
        case 1.3333:
            if width >= 552:
                return " --width=552 "
        case 1.7778:
            if width >= 640:
                return " --width=640 "
        case 0.5625:
            if width >= 360:
                return " --width=360 "
            else:
                return " "
        case _:
            print(f"Unknown aspect ratio {aspect_ratio} exiting script")
            exit()


def get_frame_delay(num_of_frames, desired_duration, original_fps, new_fps):
    print(f"Calculating new frame delay\n")
    frame_reduction_factor = original_fps / new_fps
    print(f"Frame reduction factor: {frame_reduction_factor}\n")
    new_num_of_frames = num_of_frames / frame_reduction_factor
    print(f"New number of frames: {new_num_of_frames}\n")
    frame_delay = math.ceil((desired_duration * 1000) / new_num_of_frames)
    print(f"Frame delay: {frame_delay}\n")
    return frame_delay
