from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

def load_config():
    # 构建 config.json 文件的路径
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, 'deleteSystem', 'config.json')

    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
            return config.get('classifySystem', {})
    except FileNotFoundError:
        print("配置文件未找到。请确保 config.json 文件在正确的位置。")
        return {}
    except json.JSONDecodeError:
        print("配置文件格式错误。请确保它是有效的 JSON 格式。")
        return {}
    except Exception as e:
        print(f"读取配置文件时发生错误：{e}")
        return {}

@app.route('/query', methods=['POST'])
def query_info():
    # 从请求中获取 InfoTypes 列表
    data = request.get_json()
    info_types = data.get('InfoTypes', None)

    # 如果 InfoTypes 不存在或为空列表，返回错误
    if not info_types or not isinstance(info_types, list):
        return jsonify({"error": "InfoTypes not provided or invalid"}), 400

    # 在 info_classify.json 中查找这些 InfoTypes 的 InfoLevel
    with open('info_classify.json', 'r') as file:
        info_classify_data = json.load(file)

    result = []
    for info_type in info_types:
        matched_item = next((item for item in info_classify_data if item["InfoType"] == info_type), None)
        if matched_item:
            result.append({"InfoType": info_type, "InfoLevel": matched_item["InfoLevel"]})
        else:
            result.append({"InfoType": info_type, "InfoLevel": "Not found"})

    return jsonify(result)

if __name__ == '__main__':
    config = load_config()
    classify_system_ip = config.get('ip', '127.0.0.1')  # 默认 IP
    classify_system_port = config.get('port', 6000)     # 默认端口

    app.run(host=classify_system_ip, port=classify_system_port)
