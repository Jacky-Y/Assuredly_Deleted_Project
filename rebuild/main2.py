from flask import Flask, request, jsonify
from StorageSystemClient import StorageSystemClient
import requests
import json

app = Flask(__name__)


def generate_delete_command(deleteMethod, max_level=None):
    # 根据deleteMethod来判断
    if deleteMethod == "logicallyDelete":
        return "rm"
    elif deleteMethod == "overwrittenDelete":
        return "shred -n 3 -u"
    elif not deleteMethod:  # 如果deleteMethod为空
        if max_level is not None and max_level >= 5:
            return "shred -n 5 -u"
        else:
            return "shred -n 3 -u"
    else:
        raise ValueError("Invalid deleteMethod provided")

def generate_full_command(deleteCommand, locations, key_locations=None):
    # 基础命令
    commands = [f"{deleteCommand} {location}" for location in locations]

    # 如果key_locations不为空，则添加密钥路径到命令
    if key_locations:
        key_commands = [f"{deleteCommand} {key_location}" for key_location in key_locations]
        commands.extend(key_commands)
    
    # 使用&&连接命令,并返回最终命令
    full_command = " && ".join(commands)
    return full_command






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

        url = "http://127.0.0.1:6000/query"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "InfoID": infoID
        }

        response = requests.post(url, headers=headers, json=data)

        print(response.status_code)
        response_data = response.json()

        # Sort the list of dictionaries based on the 'InfoLevel' key
        sorted_data = sorted(response_data, key=lambda x: x['InfoLevel'], reverse=True)

        # Print the dictionary with the highest 'InfoLevel'
        print(sorted_data)
        max_level=sorted_data[0]['InfoLevel']
        print("the max sensitive level is ---- >>",max_level)

        print("--------------------------------Classification Information Get-----------------------------------")

        client = StorageSystemClient("http://127.0.0.1:7000")
        info_id_to_query = infoID  # 请替换为需要查询的实际InfoID值

        # Step 1: 查询InfoID的存储状态
        status = client.get_status(info_id_to_query)
        print(f"Storage status for InfoID {info_id_to_query}: {status}")

        # Step 2: 查询InfoID的副本位置信息
        locations = client.get_duplication_locations(info_id_to_query)
        if locations:
            print(f"Locations for InfoID {info_id_to_query}: {locations}")
        else:
            print(f"No duplication locations found for InfoID {info_id_to_query}")

        # Step 3: 判断是否为加密状态
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
                    print(f"Key locations for InfoID {info_id_to_query}: {key_locations}")
                else:
                    print("Failed to retrieve key locations.")
            else:
                print("Failed to retrieve key storage method.")
        else:
            print(f"InfoID {info_id_to_query} is not encrypted.")

        print("--------------------------------Duplication and Key Information Get-----------------------------------")
##     生成删除命令
        print(deleteMethod)
        deleteCommand=generate_delete_command(deleteMethod,max_level)
        result=generate_full_command(deleteCommand,locations,key_locations)
        print(result)



        print("--------------------------------Delete Command Generated-----------------------------------")
        


        


        



    

        return jsonify({"message": "Data received and parsed successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run()
    # app.run(host='192.168.43.65')
