import json

# 定义数据
data1 = [
    {"InfoType": "Name", "InfoLevel": 5},
    {"InfoType": "Gender", "InfoLevel": 3},
    {"InfoType": "Age", "InfoLevel": 4},
    {"InfoType": "Address", "InfoLevel": 5},
    {"InfoType": "Phone", "InfoLevel": 3},
    {"InfoType": "Email", "InfoLevel": 4},
    {"InfoType": "Occupation", "InfoLevel": 2},
    {"InfoType": "Nationality", "InfoLevel": 3},
    {"InfoType": "Education", "InfoLevel": 4},
    {"InfoType": "Hobbies", "InfoLevel": 1}
]

# 将数据写入 JSON 文件
with open('info_classify.json', 'w') as file:
    json.dump(data1, file, indent=4)

# 从 JSON 文件中读取数据
with open('info_classify.json', 'r') as file:
    loaded_data = json.load(file)

# 打印读取的数据
print(loaded_data)

data2 = [
    {"infoID": "1a2b3c4d5e6f", "InfoTypes": ["Name", "Gender", "Phone"]},
    {"infoID": "2g3h4i5j6k7l", "InfoTypes": ["Address", "Age"]},
    {"infoID": "3m4n5o6p7q8r", "InfoTypes": ["Email", "Phone", "Name", "Occupation"]},
    {"infoID": "4s5t6u7v8w9x", "InfoTypes": ["Nationality", "Hobbies"]},
    {"infoID": "5y6z7a8b9c0d", "InfoTypes": ["Name", "Age", "Address"]},
    {"infoID": "6e7f8g9h0i1j", "InfoTypes": ["Gender", "Education", "Occupation"]},
    {"infoID": "7k8l9m0n1o2p", "InfoTypes": ["Email", "Phone"]},
    {"infoID": "8q9r0s1t2u3v", "InfoTypes": ["Age", "Nationality", "Hobbies"]},
    {"infoID": "9w0x1y2z3a4b", "InfoTypes": ["Gender", "Address", "Phone", "Email"]},
    {"infoID": "0c1d2e3f4g5h", "InfoTypes": ["Name", "Education", "Hobbies"]}
]

# 将数据写入 JSON 文件
with open('infoIDs.json', 'w') as file:
    json.dump(data2, file, indent=4)

# 从 JSON 文件中读取数据
with open('infoIDs.json', 'r') as file:
    loaded_data = json.load(file)

# 打印读取的数据
print(loaded_data)