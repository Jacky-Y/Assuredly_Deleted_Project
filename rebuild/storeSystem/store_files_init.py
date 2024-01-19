import os
import json
import random
import shutil
from model.InfoTypesManager import InfoTypesManager
from model.PlaintextLocationManager import PlaintextLocationManager
from model.EncryptionStatusManager import EncryptionStatusManager
import datetime


import cipher_center


db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'plain_db'
}

infoTypesManager=InfoTypesManager(db_config)
plaintextLocationManager=PlaintextLocationManager(db_config)
encryptionStatusManager=EncryptionStatusManager(db_config)
ciphercenter = cipher_center.CipherCTR()


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


    return new_file_paths

def get_keys_from_json(file_path):
    """
    This function reads a JSON file from the given file path and returns a list of keys with non-empty values.

    :param file_path: The path to the JSON file.
    :return: A list of keys with non-empty values from the JSON file.
    """
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            non_empty_keys = [key for key, value in data.items() if value]
            return non_empty_keys
    except Exception as e:
        return f"Error: {e}"
    

def load_file(path,is_encrypted,store_paths,threshold=[],keywords=[]):
    if is_encrypted:
        file_extension = path.split('.')[-1].lower()
        if file_extension=="json":
            file_type=get_keys_from_json(path)
        elif file_extension =='txt':
            file_type=['Text']
        elif file_extension in [ 'mp3', 'wav', 'aac', 'flac']:
            file_type=['Audio']
        elif file_extension in [ 'mp4', 'avi', 'mov', 'wmv']:
            file_type=['Video']
        elif file_extension in [ 'jpg', 'bmp', 'jpeg', 'gif','png']:
            file_type=['Image']
        else:
            file_type=['Others']

        infoID = ''.join([random.choice("0123456789abcdef") for _ in range(16)])
        # print(infoID,"   generated!")
        infoTypesManager.add_record(infoID,file_type)
        num_locations_to_use = random.randint(1, len(store_paths))
        selected_locations = random.sample(store_paths, num_locations_to_use)
        if threshold == []:
            n = random.randint(1, len(store_paths))
            if n == 1:
                t = 1
            else:
                t = random.randint(2, n)
        else:
            n=threshold[0]
            t=threshold[1]

        if keywords == []:
            keywords.append(random.choice(["Name","Phone","Age","Email"]))
        ciphercenter.add_file(keywords, path, infoID, selected_locations, t, n)
        encryptionStatusManager.add_record(infoID, is_encrypted)

        return {infoID:file_type}
        
    else:
        file_extension = path.split('.')[-1].lower()
        if file_extension=="json":
            file_type=get_keys_from_json(path)
        elif file_extension =='txt':
            file_type=['Text']
        elif file_extension in [ 'mp3', 'wav', 'aac', 'flac']:
            file_type=['Audio']
        elif file_extension in [ 'mp4', 'avi', 'mov', 'wmv']:
            file_type=['Video']
        elif file_extension in [ 'jpg', 'bmp', 'jpeg', 'gif','png']:
            file_type=['Image']
        else:
            file_type=['Others']

        infoID = ''.join([random.choice("0123456789abcdef") for _ in range(16)])
        # print(infoID,"   generated!")
        infoTypesManager.add_record(infoID,file_type)
        new_file_paths=copy_and_delete_file(path,store_paths,infoID)
        # print(new_file_paths)
        encryptionStatusManager.add_record(infoID, is_encrypted)
        plaintextLocationManager.add_record(infoID,new_file_paths)

        return {infoID:file_type}

def generate_delete_commands(data_list):
    delete_commands = []

    for item in data_list:
        for info_id, types in item.items():
            command = {
                "systemID": "0x40000000",
                "systemIP": "127.0.0.1",
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data": {
                    "affairsID": ''.join(random.choices('0123456789', k=8)),
                    "userID": "u100000003",
                    "infoID": info_id,
                    "deleteMethod": "overwrittenDelete",
                    "deleteGranularity": "",
                    "deleteNotifyTree": "{\"b1000\": {\"children\": []}}"
                },
                "dataHash": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa"
            }

            # 设置 deleteGranularity
            if not set(types).issubset({'Image', 'Video', 'Audio', 'Text'}):
                command['data']['deleteGranularity'] = random.choice(types)

            delete_commands.append(command)

    return delete_commands

import os

def files_init(target_folder, store_paths, threshold=[], keywords=[]):


    # 获取 target_folder 中的所有文件
    files = [f for f in os.listdir(target_folder) if os.path.isfile(os.path.join(target_folder, f))]
    files.sort()  # 可以根据需要排序

    # 分类加密和非加密的文件
    encrypted_files = files[-10:] if len(files) >= 10 else []
    non_encrypted_files = files[:-10] if len(files) > 10 else files

    # 打印文件列表
    print(f"Encrypted files: {encrypted_files}")
    print(f"Non-Encrypted files: {non_encrypted_files}")

    infoIDs=[]

    # 处理每个文件
    for file in non_encrypted_files:
        path = os.path.join(target_folder, file)
        infoID=load_file(path, 0, store_paths, threshold, keywords)
        # print(infoID)
        infoIDs.append(infoID)
    for file in encrypted_files:
        path = os.path.join(target_folder, file)
        infoID=load_file(path, 1, store_paths, threshold, keywords)
        # print(infoID)
        infoIDs.append(infoID)

    return infoIDs

# 使用示例
infoids=files_init("./testdata", ['./c','./d','./e','./f'])
print(infoids)

# 生成删除指令
commands = generate_delete_commands(infoids)

# 将结果保存到 JSON 文件
with open('delete_commands.json', 'w', encoding='utf-8') as file:
    json.dump(commands, file, ensure_ascii=False, indent=4)



