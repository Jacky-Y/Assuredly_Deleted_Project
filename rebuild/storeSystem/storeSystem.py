from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# Read from storeStatus.json
with open('storeStatus.json', 'r') as file:
    info_status = json.load(file)

# Read from duplication_info.json
with open('duplication_info.json', 'r') as file:
    duplication_info = json.load(file)

# Read from key_storage_info.json
with open('keyStatus.json', 'r') as file:
    key_status = json.load(file)

# Read from centralizedKeyStore.json
with open('centralizedKeyStore.json', 'r') as file:
    centralized_key_info = json.load(file)

# Read from decentralizedKeyStore.json
with open('decentralizedKeyStore.json', 'r') as file:
    decentralized_key_info = json.load(file)


# 从 info_type.json 读取数据
with open('info_type.json', 'r') as file:
    info_type_data = json.load(file)

@app.route('/getInfoType', methods=['POST'])
def get_info_type():
    # 获取 POST 请求中的 infoID
    info_id = request.json.get('infoID')

    # 如果没有提供 infoID，则返回错误
    if not info_id:
        return jsonify({'error': 'infoID not provided'}), 400

    # 在 info_type_data 中查找 infoID
    for item in info_type_data:
        if item["infoID"] == info_id:
            return jsonify({'InfoTypes': item['InfoTypes']}), 200

    # 如果没找到匹配的 infoID，则返回错误
    return jsonify({'error': 'infoID not found'}), 404

@app.route('/getCentralizedKey', methods=['POST'])
def get_centralized_key():
    data = request.json
    info_id = data.get("infoID", "")
    for item in centralized_key_info:
        if item["infoID"] == info_id:
            return jsonify({"infoID": info_id, "Locations": item["Locations"]})

    # If infoID does not exist in the list
    return jsonify({"Error": "infoID not found"}), 404

@app.route('/getDecentralizedKey', methods=['POST'])
def get_decentralized_key():
    data = request.json
    info_id = data.get("infoID", "")
    for item in decentralized_key_info:
        if item["infoID"] == info_id:
            return jsonify({"infoID": info_id, "Locations": item["Locations"]})

    # If infoID does not exist in the list 
    return jsonify({"Error": "infoID not found"}), 404

@app.route('/getStatus', methods=['POST'])
def get_status():
    data = request.json
    info_id = data.get("infoID", "")
    for item in info_status:
        if item["infoID"] == info_id:
            return jsonify({"infoID": info_id, "Status": item["Status"]})

    # If infoID does not exist in the list
    return jsonify({"Error": "infoID not found"}), 404


@app.route('/getDuplicationLocations', methods=['POST'])
def get_duplication_locations():
    data = request.json
    info_id = data.get("infoID", "")
    for item in duplication_info:
        if item["infoID"] == info_id:
            return jsonify({"infoID": info_id, "Locations": item["Locations"]})

    # If infoID does not exist in the list
    return jsonify({"Error": "infoID not found"}), 404

@app.route('/getKeyStorageMethod', methods=['POST'])
def get_key_storage_method():
    data = request.json
    info_id = data.get("infoID", "")
    for item in key_status:
        if item["infoID"] == info_id:
            return jsonify({"infoID": info_id, "KeyStorageMethod": item["KeyStorageMethod"]})

    # If infoID does not exist in the list
    return jsonify({"Error": "infoID not found"}), 404

@app.route('/duplicationDel', methods=['POST'])
def duplication_del():
    # 获取POST请求中的JSON数据
    data = request.json

    # 提取duplicationDelCommand命令
    duplication_del_command = data.get('duplicationDelCommand')
    
    if not duplication_del_command:
        return jsonify({"status": "error", "message": "duplicationDelCommand not provided"}), 400

    # 分别解析各个字段
    target = duplication_del_command.get('target')
    delete_granularity = duplication_del_command.get('deleteGranularity')
    delete_alg = duplication_del_command.get('deleteAlg')
    delete_alg_param = duplication_del_command.get('deleteAlgParam')
    delete_level = duplication_del_command.get('deleteLevel')

    # 基于解析的数据构建响应
    response_data = {
        "status": "success",
        "parsed_data": {
            "target": target,
            "deleteGranularity": delete_granularity,
            "deleteAlg": delete_alg,
            "deleteAlgParam": delete_alg_param,
            "deleteLevel": delete_level
        }
    }

    return jsonify(response_data)

@app.route('/keyDel', methods=['POST'])
def key_del():
    # 获取POST请求中的JSON数据
    data = request.json

    # 提取keyDelCommand命令
    key_del_command = data.get('keyDelCommand')
    
    if not key_del_command:
        return jsonify({"status": "error", "message": "keyDelCommand not provided"}), 400

    # 分别解析各个字段
    target = key_del_command.get('target')
    delete_alg = key_del_command.get('deleteAlg')
    delete_alg_param = key_del_command.get('deleteAlgParam')
    delete_level = key_del_command.get('deleteLevel')

    # 基于解析的数据构建响应
    response_data = {
        "status": "success",
        "parsed_data": {
            "target": target,
            "deleteAlg": delete_alg,
            "deleteAlgParam": delete_alg_param,
            "deleteLevel": delete_level
        }
    }

    return jsonify(response_data)


if __name__ == '__main__':
    app.run(port=7000)
