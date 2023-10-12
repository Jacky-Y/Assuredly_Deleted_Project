from flask import Flask, request, jsonify
from StorageSystemClient import StorageSystemClient
import requests

app = Flask(__name__)

@app.route('/getInstruction', methods=['POST'])
def get_instruction():
    try:
        # 获取JSON数据
        data = request.json
        
        # 从JSON数据中解析所需的值
        systemID = data.get("systemID")
        systemIP = data.get("systemIP")
        mainCMD = data.get("mainCMD")
        subCMD = data.get("subCMD")
        evidencelD = data.get("evidencelD")
        msgVersion = data.get("msgVersion")
        submittime = data.get("submittime")
        
        # 解析内部data字段的值
        detailed_data = data.get("data")
        userID = detailed_data.get("userID")
        infoID = detailed_data.get("infoID")
        deleteMethod = detailed_data.get("deleteMethod")
        deleteGranularity = detailed_data.get("deleteGranularity")
        
        dataHash = data.get("dataHash")
        noncesign = data.get("noncesign")
        
        # 打印所有解析的值
        print("System ID:", systemID)
        print("System IP:", systemIP)
        print("Main CMD:", mainCMD)
        print("Sub CMD:", subCMD)
        print("Evidence ID:", evidencelD)
        print("Message Version:", msgVersion)
        print("Submit Time:", submittime)
        print("User ID:", userID)
        print("Info ID:", infoID)
        print("Delete Method:", deleteMethod)
        print("Delete Granularity:", deleteGranularity)
        print("Data Hash:", dataHash)
        print("Nonce Sign:", noncesign)

        print("--------------------------------删除指令解析完成-----------------------------------")

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
        print("最高敏感等级---- >>",max_level)

        print("--------------------------------分类分级信息获取完成-----------------------------------")

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


    

        return jsonify({"message": "Data received and parsed successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run()
