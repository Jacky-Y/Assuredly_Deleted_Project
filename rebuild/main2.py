from flask import Flask, request, jsonify
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

        

        url = "http://127.0.0.1:6000/query"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "InfoID": "0c1d2e3f4g5h"
        }

        response = requests.post(url, headers=headers, json=data)

        print(response.status_code)
        print(response.json())



        return jsonify({"message": "Data received and parsed successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run()
