import os
import random
import string

# 定义函数以生成随机字符串
def random_string(length=100):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

# 定义文件位置的列表
file_locations = [
    {
        "InfoID": "1a2b3c4d5e6f",
        "Locations": ["./c/1a2b3c4d5e6f.json", "./d/1a2b3c4d5e6f.json", "./e/1a2b3c4d5e6f.json"]
    },
    {
        "InfoID": "2g3h4i5j6k7l",
        "Locations": ["./c/2g3h4i5j6k7l.json", "./d/2g3h4i5j6k7l.json"]
    },
    {
        "InfoID": "3m4n5o6p7q8r",
        "Locations": ["./d/3m4n5o6p7q8r.json", "./e/3m4n5o6p7q8r.json", "./f/3m4n5o6p7q8r.json"]
    },
    {
        "InfoID": "4s5t6u7v8w9x",
        "Locations": ["./e/4s5t6u7v8w9x.json", "./f/4s5t6u7v8w9x.json"]
    },
    {
        "InfoID": "5y6z7a8b9c0d",
        "Locations": ["./f/5y6z7a8b9c0d.json", "./c/5y6z7a8b9c0d.json", "./d/5y6z7a8b9c0d.json"]
    },
    {
        "InfoID": "6e7f8g9h0i1j",
        "Locations": ["./c/6e7f8g9h0i1j.json", "./e/6e7f8g9h0i1j.json"]
    },
    {
        "InfoID": "7k8l9m0n1o2p",
        "Locations": ["./d/7k8l9m0n1o2p.json", "./e/7k8l9m0n1o2p.json", "./f/7k8l9m0n1o2p.json"]
    },
    {
        "InfoID": "8q9r0s1t2u3v",
        "Locations": ["./e/8q9r0s1t2u3v.json", "./f/8q9r0s1t2u3v.json"]
    },
    {
        "InfoID": "9w0x1y2z3a4b",
        "Locations": ["./f/9w0x1y2z3a4b.json", "./c/9w0x1y2z3a4b.json", "./d/9w0x1y2z3a4b.json"]
    },
    {
        "InfoID": "0c1d2e3f4g5h",
        "Locations": ["./c/0c1d2e3f4g5h.json", "./d/0c1d2e3f4g5h.json"]
    }
]

key_file_locations = [
    {
        "InfoID": "9w0x1y2z3a4b",
        "Locations": ["./f/9w0x1y2z3a4b_key.txt"]
    },
    # ... 其他key文件位置 ...
    {
        "InfoID": "0c1d2e3f4g5h",
        "Locations": ["./c/0c1d2e3f4g5h_key.txt", "./d/0c1d2e3f4g5h_key.txt"]
    }
]

# 合并所有的文件位置
all_locations = file_locations + key_file_locations

# 为每个文件位置创建一个文件并填充随机内容
for file_location_group in all_locations:
    for location in file_location_group["Locations"]:
        # 确保目录存在
        directory = os.path.dirname(location)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # 为文件写入随机内容
        with open(location, 'w') as file:
            file.write(random_string())

print("Files have been created with random content!")
