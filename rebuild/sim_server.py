from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/query', methods=['POST'])
def query_info():
    # 1. 从请求中获取 InfoID
    data = request.get_json()
    info_id = data.get('InfoID', None)

    # 如果 InfoID 不存在，返回错误
    if not info_id:
        return jsonify({"error": "InfoID not provided"}), 400

    # 2. 在 info_ids.json 中查找 InfoTypes
    with open('info_ids.json', 'r') as file:
        info_ids_data = json.load(file)

    info_item = next((item for item in info_ids_data if item["InfoID"] == info_id), None)
    if not info_item:
        return jsonify({"error": "InfoID not found"}), 404

    info_types = info_item['InfoTypes']

    # 3. 在 info_classify.json 中查找这些 InfoTypes 的 InfoLevel
    with open('info_classify.json', 'r') as file:
        info_classify_data = json.load(file)

    result = [{"InfoType": info_type, "InfoLevel": next(item["InfoLevel"] for item in info_classify_data if item["InfoType"] == info_type)} for info_type in info_types]

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
