import json
import random
import os
import string

# 预设列表
presets = {
    "Name": ["John Doe", "Jane Smith", "Alice Johnson", "Bob Brown"],
    "Gender": ["Male", "Female", "Non-Binary"],
    "Phone": ["123-456-7890", "987-654-3210", "555-444-3333"],
    "Address": ["123 Main St, City, Country", "456 Elm St, AnotherCity, AnotherCountry", "789 Maple St, YetAnotherCity, YetAnotherCountry"],
    "Age": ["25", "30", "35", "40"],
    "Email": ["john.doe@example.com", "jane.smith@example.com", "alice.johnson@example.com"],
    "Occupation": ["Engineer", "Doctor", "Artist", "Lawyer"],
    "Nationality": ["American", "British", "Chinese", "Indian"],
    "Hobbies": ["Reading", "Swimming", "Traveling", "Cooking"],
    "Education": ["PhD", "Masters", "Bachelors", "High School"]
}

# 生成伪加密字符串的函数
def generate_encrypted_content(length=32):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))



# 根据infoID和加密状态生成内容的函数
def generate_content(info_entry, status):
    content = {}
    content["infoID"] = info_entry["infoID"]
    for key in presets:
        if key in info_entry["InfoTypes"]:
            if status == "Encrypted":
                content[key] = generate_encrypted_content()
            else:
                content[key] = random.choice(presets[key])
        else:
            content[key] = ""
    return content


# 从文件读取数据
def read_json(filename):
    with open(filename, "r") as file:
        return json.load(file)

info_data = read_json("info_type.json")
duplication_data = read_json("duplication_info.json")
status_data = read_json("storeStatus.json")

# 生成并存储json文件的函数
def store_json_file(info_entry, duplication_entry, status_entry):
    content = generate_content(info_entry, status_entry["Status"])
    for location in duplication_entry["Locations"]:
        directory = os.path.dirname(location)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(location, 'w') as file:
            json.dump(content, file, indent=4)

def generate_random_key():
    # 生成长度为32的伪随机密钥
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

def write_keys_to_files(file_name):
    with open(file_name, 'r') as f:
        key_data = json.load(f)
    
    for entry in key_data:
        random_key = generate_random_key()
        for location in entry["Locations"]:
            directory = os.path.dirname(location)
            if not os.path.exists(directory):
                os.makedirs(directory)
            with open(location, 'w') as f:
                f.write(random_key)
    
    print(f"Keys written for {file_name}")



for info in info_data:
    for dup in duplication_data:
        for status in status_data:
            if info["infoID"] == dup["infoID"] == status["infoID"]:
                store_json_file(info, dup, status)


# 生成密钥
write_keys_to_files('centralizedKeyStore.json')
write_keys_to_files('decentralizedKeyStore.json')
