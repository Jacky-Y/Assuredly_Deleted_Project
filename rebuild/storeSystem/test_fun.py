import os
import random
import shutil

def copy_and_delete_file(original_file_path, locations, new_name=None):
    """
    Copy a file to randomly selected locations and delete the original file,
    using Linux-style paths with forward slashes.

    :param original_file_path: Path to the original file.
    :param locations: List of possible destination locations.
    :param new_name: New name for the file after being copied. If None, original file name is used.
    :return: List of new file paths where the file has been copied.
    """
    if not os.path.exists(original_file_path):
        return "Original file does not exist."

    if not locations:
        return "No destination locations provided."

    # 随机选择位置数量
    num_locations_to_use = random.randint(1, len(locations))
    selected_locations = random.sample(locations, num_locations_to_use)

    new_file_paths = []
    for location in selected_locations:
        if not os.path.exists(os.path.dirname(location)):
            os.makedirs(os.path.dirname(location))

        # Determine the new file name
        if new_name:
            base, ext = os.path.splitext(original_file_path)
            new_file_name = f"{new_name}{ext}"
        else:
            new_file_name = os.path.basename(original_file_path)

        # Construct the new file path
        new_file_path = os.path.join(location, new_file_name).replace('\\', '/')
        shutil.copy2(original_file_path, new_file_path)
        new_file_paths.append(new_file_path)

    os.remove(original_file_path)

    return new_file_paths

# 使用示例
# new_paths = copy_and_delete_file("path/to/1.png", ["path/to/location1", "path/to/location2"], "new_name")
# print(new_paths)

# 使用示例
new_paths = copy_and_delete_file("1.png", ["./c", "./d"], "xxxxxxxxxxxxx")
print(new_paths)
