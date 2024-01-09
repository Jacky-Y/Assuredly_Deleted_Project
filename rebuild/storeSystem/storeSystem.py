from flask import Flask, request, jsonify
import json
from util import *
import base64
import os
import shutil
import random

from overwirter_class import JsonOverwriter
from overwirter_class import TextOverwriter
from overwirter_class import VideoOverwriter
from overwirter_class import AudioOverwriter
from overwirter_class import ImageOverwriter

# from model.CentralizedKeyManager import CentralizedKeyManager
# from model.DecentralizedKeyManager import DecentralizedKeyManager
from model.InfoTypesManager import InfoTypesManager
# from model.KeyStatusManager import KeyStatusManager
from model.PlaintextLocationManager import PlaintextLocationManager
from model.EncryptionStatusManager import EncryptionStatusManager
import cipher_center


db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'plain_db'
}

# centralizedKeyManager=CentralizedKeyManager(db_config)
# decentralizedKeyManager=DecentralizedKeyManager(db_config)
infoTypesManager=InfoTypesManager(db_config)
# keyStatusManager=KeyStatusManager(db_config)
plaintextLocationManager=PlaintextLocationManager(db_config)
encryptionStatusManager=EncryptionStatusManager(db_config)
ciphercenter = cipher_center.CipherCTR(True,True,False)

#  # 两处副本目录
# copy_paths = ["./c", "./e"]
# # 输入关键字集合
# keywords = ["Male"]

# # 确保预置测试文件存在
# # 拷贝一份，作为本系统输入明文文件
# file_in = "./1.png"

# if os.path.exists('./test_sample.json'):
#     shutil.copy('./test_sample.json', file_in)
# else:
#     print("请准备'./test_sample.json'文件！")
#     sys.exit(1)
# print("输入文件./9w0x1y2z3a4b.json生成成功！")

# # 添加文件，关键字Male，门限(2,3)
# ciphercenter.add_file(keywords, file_in, "0c1d2e3f4g5h", copy_paths, 2, 3)


app = Flask(__name__)


def copy_and_delete_file(original_file_path, locations, new_name=None):
    """
    Copy a file to randomly selected locations and delete the original file,
    using Linux-style paths with forward slashes.

    :param original_file_path: Path to the original file.
    :param locations: List of possible destination locations.
    :param new_name: New name for the file after being copied. If None, original file name is used.
    :return: List of new file paths where the file has been copied.
    """
    if not os.path.exists(original_file_path):
        return "Original file does not exist."

    if not locations:
        return "No destination locations provided."

    # 随机选择位置数量
    num_locations_to_use = random.randint(1, len(locations))
    selected_locations = random.sample(locations, num_locations_to_use)

    new_file_paths = []
    for location in selected_locations:
        if not os.path.exists(os.path.dirname(location)):
            os.makedirs(os.path.dirname(location))

        # Determine the new file name
        if new_name:
            base, ext = os.path.splitext(original_file_path)
            new_file_name = f"{new_name}{ext}"
        else:
            new_file_name = os.path.basename(original_file_path)

        # Construct the new file path
        new_file_path = os.path.join(location, new_file_name).replace('\\', '/')
        shutil.copy2(original_file_path, new_file_path)
        new_file_paths.append(new_file_path)

    os.remove(original_file_path)

    return new_file_paths

def get_keys_from_json(file_path):
    """
    This function reads a JSON file from the given file path and returns a list of keys with non-empty values.

    :param file_path: The path to the JSON file.
    :return: A list of keys with non-empty values from the JSON file.
    """
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            non_empty_keys = [key for key, value in data.items() if value]
            return non_empty_keys
    except Exception as e:
        return f"Error: {e}"
    

def load_file(path,is_encrypted,store_paths,threshold=[],keywords=[]):
    if is_encrypted:
        file_extension = path.split('.')[-1].lower()
        if file_extension=="json":
            file_type=get_keys_from_json(path)
        elif file_extension =='txt':
            file_type=['Text']
        elif file_extension in [ 'mp3', 'wav', 'aac', 'flac']:
            file_type=['Audio']
        elif file_extension in [ 'mp4', 'avi', 'mov', 'wmv']:
            file_type=['Video']
        elif file_extension in [ 'jpg', 'bmp', 'jpeg', 'gif','png']:
            file_type=['Image']
        else:
            file_type=['Others']

        infoID = ''.join([random.choice("0123456789abcdef") for _ in range(16)])
        print(infoID,"   generated!")
        infoTypesManager.add_record(infoID,str(file_type))
        num_locations_to_use = random.randint(1, len(store_paths))
        selected_locations = random.sample(store_paths, num_locations_to_use)
        if threshold == []:
            n = random.randint(1, len(store_paths))
            if n == 1:
                t = 1
            else:
                t = random.randint(2, n)
        else:
            n=threshold[0]
            t=threshold[1]

        if keywords == []:
            keywords.append(random.choice(["Name","Phone","Age","Email"]))
        ciphercenter.add_file(keywords, path, infoID, selected_locations, t, n)
        encryptionStatusManager.add_record(infoID, is_encrypted)
        
    else:
        file_extension = path.split('.')[-1].lower()
        if file_extension=="json":
            file_type=get_keys_from_json(path)
        elif file_extension =='txt':
            file_type=['Text']
        elif file_extension in [ 'mp3', 'wav', 'aac', 'flac']:
            file_type=['Audio']
        elif file_extension in [ 'mp4', 'avi', 'mov', 'wmv']:
            file_type=['Video']
        elif file_extension in [ 'jpg', 'bmp', 'jpeg', 'gif','png']:
            file_type=['Image']
        else:
            file_type=['Others']

        infoID = ''.join([random.choice("0123456789abcdef") for _ in range(16)])
        print(infoID,"   generated!")
        infoTypesManager.add_record(infoID,str(file_type))
        new_file_paths=copy_and_delete_file(path,store_paths,infoID)
        print(new_file_paths)
        encryptionStatusManager.add_record(infoID, is_encrypted)
        plaintextLocationManager.add_record(infoID,str(new_file_paths))



# 从文件中读取并反序列化密钥
def deserialize_keys(private_file='private_key.pem'):
    # 从文件读取并反序列化私钥
    with open(private_file, 'rb') as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
        )

    return private_key

private_key=deserialize_keys('private_key.pem')

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

# 使用 load_json 函数读取相应的 JSON 文件
infoTypesManager.load_json('storeStatus.json')
# centralizedKeyManager.load_json('centralizedKeyStore.json')
# decentralizedKeyManager.load_json('decentralizedKeyStore.json')
# keyStatusManager.load_json('keyStatus.json')
plaintextLocationManager.load_json('duplication_info.json')
encryptionStatusManager.load_json('storeStatus.json')


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
                # 检查文件是否存在
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"File {file_path} not found.")

                # 直接覆写整个文件内容为 alg_param
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(alg_param)
            
            except (IOError, FileNotFoundError) as e:
                print(f"Error processing file {file_path}: {e}")
                raise


def overwrite_file(target_files, granularity, alg_param, level):
    """
    模拟覆写文件函数
    :param target_files: 要覆写的目标文件列表
    :param granularity: 覆写的粒度（特定字段名）
    :param alg_param: 用于覆写的随机数
    :param level: 覆写的次数
    """
    for file_path in target_files:
        for _ in range(level):
            try:
                # 检查文件是否存在
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"File {file_path} not found.")

                if granularity:
                    # 读取 JSON 文件
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # 如果指定了 granularity，则只覆写特定字段
                    if granularity in data: 
                        data[granularity] = alg_param  # 覆写该字段
                    else:
                        print(f"Field '{granularity}' not found in {file_path}.")
                        continue

                    # 保存修改后的 JSON 数据
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)

                else:
                    # 如果没有指定 granularity，直接将文件内容覆写为 alg_param
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(alg_param)
            
            except (IOError, json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error processing file {file_path}: {e}")
                raise



@app.route('/getInfoType', methods=['POST'])
def get_info_type():
    # 获取 POST 请求中的 infoID
    infoID = request.json.get('infoID')

    # 如果没有提供 infoID，则返回错误
    if not infoID:
        return jsonify({'error': 'infoID not provided'}), 400

    infoTypes=infoTypesManager.get_infoTypes(infoID)
    if infoTypes:
        return jsonify({'InfoTypes': infoTypes}), 200

    # # 在 info_type_data 中查找 infoID
    # for item in info_type_data:
    #     if item["infoID"] == infoID:
    #         return jsonify({'InfoTypes': item['InfoTypes']}), 200

    # 如果没找到匹配的 infoID，则返回错误
    return jsonify({'error': 'infoID not found'}), 404

@app.route('/getCentralizedKey', methods=['POST'])
def get_centralized_key():
    data = request.json
    infoID = data.get("infoID", "")
    # for item in centralized_key_info:
    #     if item["infoID"] == infoID:
    #         return jsonify({"infoID": infoID, "Locations": item["Locations"]})
    try:
        ret = ciphercenter.search_by_infoid(infoID)
        
        return jsonify({"infoID": infoID, "Locations":ret})
    except Exception as e:
        print(str(e))

        # If infoID does not exist in the list
        return jsonify({"Error": str(e)}), 404

@app.route('/getDecentralizedKey', methods=['POST'])
def get_decentralized_key():
    data = request.json
    infoID = data.get("infoID", "")
    try:
        ret = ciphercenter.search_by_infoid(infoID)
        
        return jsonify({"infoID": infoID, "Locations":ret})
    except Exception as e:
        print(str(e))

        # If infoID does not exist in the list
        return jsonify({"Error": str(e)}), 404
    # for item in decentralized_key_info:
    #     if item["infoID"] == infoID:
    #         return jsonify({"infoID": infoID, "Locations": item["Locations"]})

    # # If infoID does not exist in the list 
    # return jsonify({"Error": "infoID not found"}), 404

@app.route('/getStatus', methods=['POST'])
def get_status():
    data = request.json
    infoID = data.get("infoID", "")
    isencrypted=encryptionStatusManager.get_encryption_status(infoID)
    if isencrypted==1:
        return jsonify({"infoID": infoID, "Status": "Encrypted"})
    elif isencrypted==0:
        return jsonify({"infoID": infoID, "Status": "Plaintext"})
    else:
        return jsonify({"Error": "infoID not found"}), 404

    # for item in info_status:
    #     if item["infoID"] == infoID:
    #         return jsonify({"infoID": infoID, "Status": item["Status"]})

    # If infoID does not exist in the list
    

@app.route('/getEncDuplicationLocations', methods=['POST'])
def get_enc_duplication_locations():
    data = request.json
    infoID = data.get("infoID", "")
    try:
        ret = ciphercenter.search_duplocation(infoID)
        return jsonify({"infoID": infoID, "Locations": ret})
    except Exception as e:
        print(str(e))

        # If infoID does not exist in the list
        return jsonify({"Error": str(e)}), 404

    # for item in duplication_info:
    #     if item["infoID"] == infoID:
    #         return jsonify({"infoID": infoID, "Locations": item["Locations"]})

    # # If infoID does not exist in the list
    # return jsonify({"Error": "infoID not found"}), 404

@app.route('/getDuplicationLocations', methods=['POST'])
def get_duplication_locations():
    data = request.json
    infoID = data.get("infoID", "")
    locations=plaintextLocationManager.get_locations_list(infoID)
    if locations:
        return jsonify({"infoID": infoID, "Locations": locations})
    
    return jsonify({"Error": "infoID not found"}), 404

    # for item in duplication_info:
    #     if item["infoID"] == infoID:
    #         return jsonify({"infoID": infoID, "Locations": item["Locations"]})

    # If infoID does not exist in the list
    

@app.route('/getKeyStorageMethod', methods=['POST'])
def get_key_storage_method():
    data = request.json
    infoID = data.get("infoID", "")
    try:
        _ret = ciphercenter.search_by_infoid(infoID)
        if len(_ret) == 1:
            ret = "Centralized"
        else:
            ret = "Decentralized"
        return jsonify({"infoID": infoID, "KeyStorageMethod":ret})
    except Exception as e:
        print(str(e))

        # If infoID does not exist in the list
        return jsonify({"Error": str(e)}), 404

    # for item in key_status:
    #     if item["infoID"] == infoID:
    #         return jsonify({"infoID": infoID, "KeyStorageMethod": item["KeyStorageMethod"]})

    # If infoID does not exist in the list
    # return jsonify({"Error": "infoID not found"}), 404

@app.route('/duplicationEncDel', methods=['POST'])
def duplication_enc_del():
    print("---------开始对密钥分片及密文副本进行删除-------------")
    # 获取POST请求中的JSON数据
    data = request.json
    # 提取duplicationDelCommand命令
    duplication_del_command = data.get('duplicationDelCommand')
    
    if not duplication_del_command:
        return jsonify({"status": "error", "message": "duplicationDelCommand not provided"}), 400

    # 分别解析各个字段
    infoID = duplication_del_command.get('infoID')
    target_files = duplication_del_command.get('target')
    delete_alg=duplication_del_command.get('deleteAlg')
    delete_granularity = duplication_del_command.get('deleteGranularity', None)  # 如果字段不存在则返回None
    delete_alg_param = duplication_del_command.get('deleteAlgParam')
    delete_level = duplication_del_command.get('deleteLevel')
    info_type=duplication_del_command.get('infoType')


    #计算vrf
    vrf_output, proof = compute_vrf(private_key, delete_alg_param.encode())

    # 将二进制数据转换为 Base64 字符串
    base64_vrf_output = base64.b64encode(vrf_output)
    base64_vrf_output_string = base64_vrf_output.decode('utf-8')  # 转换为字符串以便存储到 JSON



    if delete_granularity:
        try:
            if delete_alg=="overwrittenDelete":
                print("使用以下VRF随机输出进行覆写密钥分片及密文副本:",base64_vrf_output_string)
                ciphercenter.del_field(infoID, delete_granularity, delete_alg, base64_vrf_output_string, delete_level)
                return jsonify({"status": "success", "message": "Overwrite operation completed successfully."})
            elif delete_alg=="commandDelete":
                print("使用删除命令删除密钥分片及密文副本:")
                ciphercenter.del_field(infoID, delete_granularity, delete_alg, base64_vrf_output_string, delete_level)
                return jsonify({"status": "success", "message": "Command delete operation completed successfully."})
        except Exception as e:
            print(str(e))
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        try:
            if delete_alg=="overwrittenDelete":
                print("使用以下VRF随机输出进行覆写密钥分片及密文副本:",base64_vrf_output_string)
                ciphercenter.del_file(infoID, delete_alg, base64_vrf_output_string, delete_level)
                return jsonify({"status": "success", "message": "Overwrite operation completed successfully."})
            elif delete_alg=="commandDelete":
                print("使用删除命令删除密钥分片及密文副本:")
                ciphercenter.del_file(infoID, delete_alg, base64_vrf_output_string, delete_level)
                return jsonify({"status": "success", "message": "Command delete operation completed successfully."})
        except Exception as e:
            print(str(e))
            return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/duplicationDel', methods=['POST'])
def duplication_del():
    print("---------开始对副本进行删除-------------")
    # 获取POST请求中的JSON数据
    data = request.json
    # 提取duplicationDelCommand命令
    duplication_del_command = data.get('duplicationDelCommand')
    
    if not duplication_del_command:
        return jsonify({"status": "error", "message": "duplicationDelCommand not provided"}), 400

    # 分别解析各个字段
    target_files = duplication_del_command.get('target')
    delete_alg=duplication_del_command.get('deleteAlg')
    delete_granularity = duplication_del_command.get('deleteGranularity', None)  # 如果字段不存在则返回None
    delete_alg_param = duplication_del_command.get('deleteAlgParam')
    delete_level = duplication_del_command.get('deleteLevel')
    info_type=duplication_del_command.get('infoType')


    #计算vrf
    vrf_output, proof = compute_vrf(private_key, delete_alg_param.encode())

    # 将二进制数据转换为 Base64 字符串
    base64_vrf_output = base64.b64encode(vrf_output)
    base64_vrf_output_string = base64_vrf_output.decode('utf-8')  # 转换为字符串以便存储到 JSON


    if delete_alg=="overwrittenDelete":
        print("使用以下VRF随机输出进行覆写副本文件:",base64_vrf_output_string)

        if info_type==1:
            # 执行覆写操作
            try:
                # overwrite_file(target_files, delete_granularity, base64_vrf_output_string, delete_level)

                # 创建一个 JsonOverwriter 实例
                jsonoverwriter = JsonOverwriter(granularity=delete_granularity, alg_param=base64_vrf_output_string, level=delete_level)

                # 调用 overwrite_file 方法
                jsonoverwriter.overwrite_file(target_files)

                print(f"已经完成对{target_files}的覆写")

                return jsonify({"status": "success", "message": "Overwrite operation completed successfully."})
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 500
            
        elif info_type==2:
            # 执行覆写操作
            try:
                #对TXT进行覆写

                # 创建一个 TextOverwriter 实例
                textoverwriter = TextOverwriter(alg_param=base64_vrf_output_string, level=delete_level)

                # 调用 overwrite_file 方法
                textoverwriter.overwrite_file(target_files)

                print(f"已经完成对{target_files}的覆写")

                return jsonify({"status": "success", "message": "Overwrite operation completed successfully."})
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 500
            
        elif info_type==3:
            # 执行覆写操作
            try:
                #对Video进行覆写

                # 创建一个 VideoOverwriter 实例
                videooverwriter = VideoOverwriter(alg_param=base64_vrf_output_string, level=delete_level)


                # 调用 overwrite_file 方法
                videooverwriter.overwrite_file(target_files)

                print(f"已经完成对{target_files}的覆写")

                return jsonify({"status": "success", "message": "Overwrite operation completed successfully."})
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 500

        elif info_type==4:
            # 执行覆写操作
            try:
                #对Audio进行覆写

                # 创建一个 AudioOverwriter 实例
                audiooverwriter = AudioOverwriter(alg_param=base64_vrf_output_string, level=delete_level)

                # 调用 overwrite_file 方法
                audiooverwriter.overwrite_file(target_files)

                print(f"已经完成对{target_files}的覆写")

                return jsonify({"status": "success", "message": "Overwrite operation completed successfully."})
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 500
            

        elif info_type==5:
            # 执行覆写操作
            try:
                #对Image进行覆写

                # 创建一个 ImageOverwriter 实例
                imageoverwriter = ImageOverwriter(alg_param=base64_vrf_output_string, level=delete_level)

                # 调用 overwrite_file 方法
                imageoverwriter.overwrite_file(target_files)

                print(f"已经完成对{target_files}的覆写")

                return jsonify({"status": "success", "message": "Overwrite operation completed successfully."})
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 500
            
        else:
            return jsonify({"status": "error", "message": "the infotype doesn't exists"}), 500
    
    elif delete_alg=="commandDelete":
        print("使用系统命令执行副本删除")
        if info_type==1:
            # 执行命令删除操作
            try:

                # 创建一个 JsonOverwriter 实例
                jsonoverwriter = JsonOverwriter(granularity=delete_granularity, alg_param=base64_vrf_output_string, level=delete_level)

                # 调用 command_delete 方法
                jsonoverwriter.command_delete(target_files)

                return jsonify({"status": "success", "message": "Command deletion operation completed successfully."})
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 500
            
        elif info_type==2:
            # 执行命令删除操作
            try:
                #对TXT进行删除

                # 创建一个 TextOverwriter 实例
                textoverwriter = TextOverwriter(alg_param=base64_vrf_output_string, level=delete_level)

                # 调用 command_delete 方法
                textoverwriter.command_delete(target_files)

                return jsonify({"status": "success", "message": "Command deletion operation completed successfully."})
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 500
            
        elif info_type==3:
            # 执行命令删除操作
            try:
                #对Video进行覆写

                # 创建一个 VideoOverwriter 实例
                videooverwriter = VideoOverwriter(alg_param=base64_vrf_output_string, level=delete_level)

                # 调用 command_delete 方法
                videooverwriter.command_delete(target_files)

                return jsonify({"status": "success", "message": "Command deletion operation completed successfully."})
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 500

        elif info_type==4:
            # 执行命令删除操作
            try:
                #对Audio进行覆写

                # 创建一个 AudioOverwriter 实例
                audiooverwriter = AudioOverwriter(alg_param=base64_vrf_output_string, level=delete_level)

                # 调用 command_delete 方法
                audiooverwriter.command_delete(target_files)

                return jsonify({"status": "success", "message": "Command deletion operation completed successfully."})
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 500
            

        elif info_type==5:
            # 执行命令删除操作
            try:
                #对Image进行覆写

                # 创建一个 ImageOverwriter 实例
                imageoverwriter = ImageOverwriter(alg_param=base64_vrf_output_string, level=delete_level)

                # 调用 command_delete 方法
                imageoverwriter.command_delete(target_files)

                return jsonify({"status": "success", "message": "Command deletion operation completed successfully."})
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 500
            
        else:
            return jsonify({"status": "error", "message": "the infotype doesn't exists"}), 500
        

@app.route('/keyDel', methods=['POST'])
def key_del():
    print("---------开始对密钥进行删除-------------")
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
    delete_alg=key_del_command.get('deleteAlg')

    #计算vrf
    vrf_output, proof = compute_vrf(private_key, delete_alg_param.encode())

    # 将二进制数据转换为 Base64 字符串
    base64_vrf_output = base64.b64encode(vrf_output)
    base64_vrf_output_string = base64_vrf_output.decode('utf-8')  # 转换为字符串以便存储到 JSON
    

    if delete_alg=="overwrittenDelete":
        print("使用以下VRF随机输出进行覆写密钥文件:",base64_vrf_output_string)

        # 执行覆写操作
        try:
            # overwrite_key_file(target_files, base64_vrf_output_string, delete_level)

            # 创建一个 JsonOverwriter 实例
            textoverwriter = TextOverwriter(alg_param=base64_vrf_output_string, level=delete_level)

            # 调用 overwrite_file 方法
            textoverwriter.overwrite_file(target_files)

            return jsonify({"status": "success", "message": "Key overwrite operation completed successfully."})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
        
    elif delete_alg=="commandDelete":
        print("使用系统命令执行密钥删除")

        # 执行覆写操作
        try:
            # overwrite_key_file(target_files, base64_vrf_output_string, delete_level)

            # 创建一个 JsonOverwriter 实例
            textoverwriter = TextOverwriter(alg_param=base64_vrf_output_string, level=delete_level)

            # 调用 overwrite_file 方法
            textoverwriter.command_delete(target_files)

            return jsonify({"status": "success", "message": "Key overwrite operation completed successfully."})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500



if __name__ == '__main__':

    load_file(path="./1.png",is_encrypted=1,store_paths=['./e','./f','./c','./d'],threshold=[3,2],keywords=["abc"])
    ciphercenter.keyword_search("abc","./c")
    app.run(port=7000)
