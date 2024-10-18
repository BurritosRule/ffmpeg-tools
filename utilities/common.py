import os


def translate_fps(fps):
    match fps:
        case "24000/1001":
            translated_fps = "23.976"
        case "30000/1001":
            translated_fps = "29.97"
        case "60000/1001":
            translated_fps = "59.94"
        case "24/1":
            translated_fps = "24"
        case "30/1":
            translated_fps = "30"
        case "25/1":
            translated_fps = "25"
        case _:
            print(f"Unsupported fps {fps} exiting script\n")
            exit()

    return translated_fps


def is_widescreen(width, height):
    if width > height:
        return True
    else:
        return False


def get_file_size(file):
    file_size = os.path.getsize(file)
    print(f"File size of {file} is {file_size}\n")
    return file_size
