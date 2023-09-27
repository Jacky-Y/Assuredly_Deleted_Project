import json
import random
import uuid

# 可能的 InfoType
possible_info_types = ["Name", "Gender", "Age", "Address", "Phone", "Email", "Occupation", "Nationality", "Education", "Hobbies"]

# 随机生成数据
def generate_data():
    info_id = str(uuid.uuid4()).replace('-', '')  # 生成一个没有"-"的UUID字符串
    info_types = random.sample(possible_info_types, random.randint(1, len(possible_info_types)))  # 随机选择 InfoType
    return {"InfoID": info_id, "InfoTypes": info_types}

data = [generate_data() for _ in range(10)]

# 将数据写入 JSON 文件
with open('random_info_data.json', 'w') as file:
    json.dump(data, file, indent=4)

# 从 JSON 文件中读取数据
with open('random_info_data.json', 'r') as file:
    loaded_data = json.load(file)

# 打印读取的数据
print(loaded_data)
