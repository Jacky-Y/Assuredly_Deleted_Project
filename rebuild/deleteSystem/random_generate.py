import json
import random
import uuid
import os

# 定义可能的 InfoType
possible_info_types = ["Name", "Gender", "Age", "Address", "Phone", "Email", "Occupation", "Nationality", "Education", "Hobbies"]

# 函数：generate_data
# 功能：随机生成包含唯一标识符和随机信息类型的数据
# 输入：
#    无输入参数
# 输出：
#    dict - 包含唯一标识符(infoID)和一组随机信息类型(InfoTypes)的字典
def generate_data():
    try:
        # 生成一个没有"-"的UUID字符串作为唯一标识符
        infoID = str(uuid.uuid4()).replace('-', '')
        # 随机选择 InfoType，数量在1到possible_info_types长度之间
        info_types = random.sample(possible_info_types, random.randint(1, len(possible_info_types)))
        return {"infoID": infoID, "InfoTypes": info_types}
    except Exception as e:
        # 捕捉并打印异常信息，返回空字典
        print(f"Error in generate_data: {e}")
        return {}

# 生成10个随机数据项
data = [generate_data() for _ in range(10)]

# 将数据写入 JSON 文件
file_path = 'random_info_data.json'
try:
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)
except IOError as e:
    # 捕捉并打印文件写入错误
    print(f"Error writing to {file_path}: {e}")

# 检查文件是否存在并从 JSON 文件中读取数据
if os.path.exists(file_path):
    try:
        with open(file_path, 'r') as file:
            loaded_data = json.load(file)
    except IOError as e:
        # 捕捉并打印文件读取错误
        print(f"Error reading from {file_path}: {e}")
        loaded_data = []
    except json.JSONDecodeError as e:
        # 捕捉并打印JSON解析错误
        print(f"Error parsing JSON from {file_path}: {e}")
        loaded_data = []
else:
    print(f"File {file_path} does not exist.")
    loaded_data = []

# 打印读取的数据
print(loaded_data)
