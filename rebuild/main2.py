from flask import Flask, request, jsonify
from StorageSystemClient import StorageSystemClient
import requests
import json

app = Flask(__name__)


def fetch_and_process_data(infoID):
    # 第一步：从 http://127.0.0.1:7000/getInfoType 获取 InfoType 列表
    url_get_info_type = "http://127.0.0.1:7000/getInfoType"
    headers_get_info_type = {
        "Content-Type": "application/json"
    }
    data_get_info_type = {
        "infoID": infoID
    }

    response_get_info_type = requests.post(url_get_info_type, headers=headers_get_info_type, json=data_get_info_type)
    response_data_get_info_type = response_get_info_type.json()

    # 检查返回数据中是否包含 error，如果包含则抛出异常
    if 'error' in response_data_get_info_type:
        raise ValueError(response_data_get_info_type['error'])

    info_types = response_data_get_info_type.get('InfoTypes', [])

    # 第二步：使用 InfoType 列表请求 http://127.0.0.1:6000/query 获取结果
    url_query = "http://127.0.0.1:6000/query"
    headers_query = {
        "Content-Type": "application/json"
    }
    data_query = {
        "InfoTypes": info_types
    }

    response_query = requests.post(url_query, headers=headers_query, json=data_query)
    response_data = response_query.json()

    # 检查返回的数据是否包含错误。如果包含，则抛出异常
    if 'error' in response_data:
        raise ValueError(response_data['error'])

    # 对返回的数据基于 'InfoLevel' 进行排序
    sorted_data = sorted(response_data, key=lambda x: x['InfoLevel'], reverse=True)

    # 获取 InfoLevel 最高的数据
    max_level = sorted_data[0]['InfoLevel']

    return sorted_data, max_level


def generate_delete_level(max_level):
    if max_level == 5:
        return 7
    elif max_level in [3, 4]:
        return 5
    elif max_level in [1, 2]:
        return 3
    else:
        return 1

def generate_delete_command_str(command_json):
    target = command_json.get("target", "")
    deleteGranularity = command_json.get("deleteGranularity", None)
    deleteAlg = command_json.get("deleteAlg", "")
    deleteAlgParam = command_json.get("deleteAlgParam", "")
    deleteLevel = command_json.get("deleteLevel", "")
    
    if deleteGranularity:
        command_str = f"delete {deleteGranularity} of {target} using deleteAlg={deleteAlg} with deleteAlgParam={deleteAlgParam} at deleteLevel= {deleteLevel}"
    else:
        command_str = f"delete {target} using deleteAlg={deleteAlg} with deleteAlgParam={deleteAlgParam} at deleteLevel= {deleteLevel}"
    
    return command_str


@app.route('/getOperationLog', methods=['POST'])
def get_operation_log():
    # 验证请求的内容类型为application/json
    if not request.is_json:
        return jsonify(error="bad request"), 400
    
    # 此处可进行一些数据验证和处理，如保存日志等
    # ...

    # 返回指定的JSON数据
    response_data = {
        "systemID": 1,
        "systemIP": "210.73.60.100",
        "time": "2020-08-01 08:00:00",
        "data": {
            "userID": "u100000003",
            "infoID":"283749abaa234cde",
            "deletePerformer": "王XX",
            "deletePerformTime": "2022-12-13 09:24:34",
            "deleteDupinfoID": "48942ECA-7CDA-4B02-8198-274C4D232E47",
            "deleteInstruction": {
                "userID": "u100000003",
                "infoID":"283749abaa234cde",
                "deleteMethod": "Software deletion",
                "deleteGranularity":"age"
            },
            "deleteMethod": "Software deletion",
            "deleteGranularity":"age",
            "deleteControlSet": "control-constraints cname……",
            "deleteAlg": 1,
            "deleteAlgParam": "XX,YY",
            "deleteLevel": 2,
            "instructionConfirmationTime": "2022-12-13 09:24:34"
        },
        "dataHash": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa"
    }
    return jsonify(response_data)



@app.route('/getInstruction', methods=['POST'])
def get_instruction():
    try:
        # 获取JSON数据
        data = request.json

    
        # 解析内部data字段的值
        affairsID = data.get("affairs_id")
        userID = data.get("user_id")
        infoID = data.get("info_id")
        notifytime = data.get("notifytime")
        deleteMethod = data.get("deleteMethod")
        deleteGranularity = data.get("deleteGranularity")
        
        
        # 打印所有解析的值

        print("affairsID:", affairsID)
        print("Submit Time:", notifytime)
        print("User ID:", userID)
        print("Info ID:", infoID)
        print("Delete Method:", deleteMethod)
        print("Delete Granularity:", deleteGranularity)

        print("--------------------------------Delete Notification Parsed Done-----------------------------------")

        sorted_data, max_level = fetch_and_process_data(infoID)
        print(sorted_data)
        print("the max sensitive level is ---- >>",max_level)


        

        print("--------------------------------Classification Information Get-----------------------------------")

        client = StorageSystemClient("http://127.0.0.1:7000")
        info_id_to_query = infoID  # 替换为需要查询的实际infoID值

        # Step 1: 查询infoID的存储状态
        status = client.get_status(info_id_to_query)
        print(f"Storage status for infoID {info_id_to_query}: {status}")

        # Step 2: 查询infoID的副本位置信息
        locations = client.get_duplication_locations(info_id_to_query)
        if locations:
            print(f"Locations for infoID {info_id_to_query}: {locations}")
        else:
            print(f"No duplication locations found for infoID {info_id_to_query}")

        # Step 3: 判断是否为加密状态
        key_locations=[]

        if status == "Encrypted":
            # Step 4: 查询密钥存储方式
            key_storage_method = client.get_key_storage_method(info_id_to_query)
            
            if key_storage_method:
                # Step 5: 根据密钥存储方式获取密钥位置
                if key_storage_method == "Centralized":
                    key_locations = client.get_centralized_key(info_id_to_query)
                elif key_storage_method == "Decentralized":
                    key_locations = client.get_decentralized_key(info_id_to_query)
                else:
                    print(f"Unknown key storage method: {key_storage_method}")
                    key_locations = None

                if key_locations:
                    print(f"Key locations for infoID {info_id_to_query}: {key_locations}")
                else:
                    print("Failed to retrieve key locations.")
            else:
                print("Failed to retrieve key storage method.")
        else:
            print(f"infoID {info_id_to_query} is not encrypted.")

        print("--------------------------------Duplication and Key Information Get-----------------------------------")
##     生成删除命令

        deleteLevel=generate_delete_level(max_level)

        duplicationDelCommand={
        "target": locations,
        "deleteGranularity": "age",
        "deleteAlg": deleteMethod,
        "deleteAlgParam": "d3k7u8sh3iajalfjal82a",
        "deleteLevel": deleteLevel
        }
        keyDelCommand={
        "target": locations,
        "deleteAlg": deleteMethod,
        "deleteAlgParam": "d3k7u8sh3iajalfjal82a",
        "deleteLevel": deleteLevel
        }
        duplicationDelCommand_str=generate_delete_command_str(duplicationDelCommand)
        keyDelCommand_str=generate_delete_command_str(keyDelCommand)

        print("the duplication Delete Command is -->>",duplicationDelCommand_str)
        print("the key Delete Command is -->>",keyDelCommand_str)

        print("--------------------------------Delete Command Generated-----------------------------------")
##     删除命令下发
        # 发送duplicationDelCommand
        duplication_response = client.send_dup_del_command(duplicationDelCommand)
        if duplication_response['status'] == 'error':
            print("Error during duplication delete:", duplication_response['message'])
        else:
            print("Response from duplication delete:", duplication_response)


        # 如果keyDelCommand不为空，则发送
        if keyDelCommand:
            key_del_response = client.send_key_del_command(keyDelCommand)

            if key_del_response['status'] == 'error':
                print("Error during key delete:", key_del_response['message'])
            else:
                print("Response from key delete:", key_del_response)
        else:
            print("Not encrypted, no need to delete key")


#         print("--------------------------------Delete Command Deliveried-----------------------------------")
        


        


        



    

        return jsonify({"message": "Data received and parsed successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run()
    # app.run(host='10.12.170.110')
