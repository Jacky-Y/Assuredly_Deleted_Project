import json
import requests

def send_delete_commands(file_path, url):
    # 从文件中读取删除指令
    with open(file_path, 'r', encoding='utf-8') as file:
        commands = json.load(file)

    # 遍历指令并发送 POST 请求
    for command in commands:
        response = requests.post(url, json=command)
        print(f"Response for {command['data']['infoID']}: {response.status_code}, {response.text}")

# 指定 JSON 文件路径和目标 URL
file_path = 'delete_commands.json'
url = 'http://localhost:5000/getInstruction'  # 替换为实际的 URL

send_delete_commands(file_path, url)
