from flask import Flask, request, jsonify
import json

app = Flask(__name__)

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
    app.run(port=6000)
