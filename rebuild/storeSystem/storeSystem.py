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

def overwrite_key_file(target_files, alg_param, level):
    """
    模拟覆写密钥文件函数
    :param target_files: 要覆写的目标文件列表
    :param alg_param: 用于覆写的随机数
    :param level: 覆写的次数
    """
    for _ in range(level):
        for file_path in target_files:
            try:
                # 直接覆写整个文件内容为 alg_param
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(alg_param)
            except IOError as e:
                print(f"Error processing file {file_path}: {e}")



def overwrite_file(target_files, granularity, alg_param, level):
    """
    模拟覆写文件函数
    :param target_files: 要覆写的目标文件列表
    :param granularity: 覆写的粒度（特定字段名）
    :param alg_param: 用于覆写的随机数
    :param level: 覆写的次数
    """
    for _ in range(level):
        for file_path in target_files:
            try:
                # 读取 JSON 文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 根据 granularity 覆写特定字段或整个文件
                if granularity:
                    if granularity in data:  # 检查字段是否存在
                        data[granularity] = alg_param  # 覆写该字段
                    else:
                        print(f"Field '{granularity}' not found in {file_path}.")
                        continue  # 如果字段不存在，跳过此次覆写并处理下一个文件

                else:
                    # 如果没有指定 granularity，直接将文件内容覆写为 alg_param
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(alg_param)
                        continue  # 跳过下面的 JSON 写入步骤，直接处理下一个文件

                # 保存修改后的 JSON 数据
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
            
            except (IOError, json.JSONDecodeError) as e:
                print(f"Error processing file {file_path}: {e}")

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
    target_files = duplication_del_command.get('target')
    delete_granularity = duplication_del_command.get('deleteGranularity', None)  # 如果字段不存在则返回None
    delete_alg_param = duplication_del_command.get('deleteAlgParam')
    delete_level = duplication_del_command.get('deleteLevel')

    # 执行覆写操作
    try:
        overwrite_file(target_files, delete_granularity, delete_alg_param, delete_level)
        return jsonify({"status": "success", "message": "Overwrite operation completed successfully."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/keyDel', methods=['POST'])
def key_del():
    # 获取POST请求中的JSON数据
    data = request.json

    # 提取keyDelCommand命令
    key_del_command = data.get('keyDelCommand')
    
    if not key_del_command:
        return jsonify({"status": "error", "message": "keyDelCommand not provided"}), 400

    # 分别解析各个字段
    target_files = key_del_command.get('target')
    delete_alg_param = key_del_command.get('deleteAlgParam')
    delete_level = key_del_command.get('deleteLevel')

    # 执行覆写操作
    try:
        overwrite_key_file(target_files, delete_alg_param, delete_level)
        return jsonify({"status": "success", "message": "Key overwrite operation completed successfully."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500



if __name__ == '__main__':
    app.run(port=7000)
