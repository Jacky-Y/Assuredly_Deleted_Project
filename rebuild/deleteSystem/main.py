from flask import Flask, request, jsonify
from StorageSystemClient import StorageSystemClient
import requests
import json
import os
from datetime import datetime


#定义全局变量
ifSendException = False
deletePerformer = "default Performer"
preset_duration_seconds=10

app = Flask(__name__)


class DeleteFailException(Exception):
    def __init__(self, message, error_data):
        super().__init__(message)
        self.error_data = error_data

class TimeoutException(Exception):
    def __init__(self, message, error_data):
        super().__init__(message)
        self.error_data = error_data

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
    try:
        # 从 POST 请求中解析 JSON 数据
        data = request.get_json()
        infoID = data['data']['infoID']
        
        # 构建文件路径
        file_path = os.path.join('log', f"{infoID}.json")
        
        # 检查文件是否存在
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                log_data = json.load(file)
                return jsonify(log_data)
        else:
            return jsonify({"error": "Log not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500




@app.route('/getInstruction', methods=['POST'])
def get_instruction():
    try:
        # 获取JSON数据
        outside_data = request.json
        data = outside_data.get("data")

#########################删除通知解析#########################
        print("\n------------------------------")
        print("Delete Notification Parsed")
        print("------------------------------")

        #解析外部的字段
        notifySystemID = outside_data.get("systemID")
        notifySystemIP = outside_data.get("systemIP")
        notifyTime = outside_data.get("time")

        # 解析内部data字段的值
        affairsID = data.get("affairsID")
        userID = data.get("userID")
        infoID = data.get("infoID")
        deleteMethod = data.get("deleteMethod")
        deleteGranularity = data.get("deleteGranularity")
        deleteNotifyTree=data.get("deleteNotifyTree")

        delete_instruction_str=f"在{notifyTime}时间下发以{deleteMethod}方式删除{infoID}信息的{deleteGranularity}的指令"
        
        print(f"Submit Time: {notifyTime}")
        print(f"Affairs ID: {affairsID}")
        print(f"User ID: {userID}")
        print(f"Info ID: {infoID}")
        print(f"Delete Method: {deleteMethod}")
        print(f"Delete Granularity: {deleteGranularity}")
        print(f"Delete NotifyTree: {deleteNotifyTree}")

#########################分类分级信息获取#########################
        print("\n------------------------------")
        print("Classification Information")
        print("------------------------------")

        sorted_data, max_level = fetch_and_process_data(infoID)

        print(f"Max Sensitive Level: {max_level}")
        print(f"Classified Information: {sorted_data}")



#########################副本及密钥信息#########################
        print("\n------------------------------")
        print("Duplication and Key Information")
        print("------------------------------")

        client = StorageSystemClient("http://127.0.0.1:7000")
        infoID_to_query = infoID  # 替换为需要查询的实际infoID值

        # Step 1: 查询infoID的存储状态
        status = client.get_status(infoID_to_query)
        print(f"Storage status for infoID {infoID_to_query}: {status}")

        # Step 2: 查询infoID的副本位置信息
        locations = client.get_duplication_locations(infoID_to_query)
        if locations:
            print(f"Locations for infoID {infoID_to_query}: {locations}")
        else:
            print(f"No duplication locations found for infoID {infoID_to_query}")

        # Step 3: 判断是否为加密状态
        key_locations=[]

        if status == "Encrypted":
            # Step 4: 查询密钥存储方式
            key_storage_method = client.get_key_storage_method(infoID_to_query)
            
            if key_storage_method:
                # Step 5: 根据密钥存储方式获取密钥位置
                if key_storage_method == "Centralized":
                    key_locations = client.get_centralized_key(infoID_to_query)
                elif key_storage_method == "Decentralized":
                    key_locations = client.get_decentralized_key(infoID_to_query)
                else:
                    print(f"Unknown key storage method: {key_storage_method}")
                    key_locations = None

                if key_locations:
                    print(f"Key locations for infoID {infoID_to_query}: {key_locations}")
                else:
                    print("Failed to retrieve key locations.")
            else:
                print("Failed to retrieve key storage method.")
        else:
            print(f"infoID {infoID_to_query} is not encrypted.")




#########################删除命令生成#########################
        print("\n------------------------------")
        print("Delete Commands")
        print("------------------------------")

        deleteLevel=generate_delete_level(max_level)

        deleteAlgParam=infoID

        duplicationDelCommand={
        "target": locations,
        "deleteGranularity": deleteGranularity,
        "deleteAlg": deleteMethod,
        "deleteAlgParam": deleteAlgParam,
        "deleteLevel": deleteLevel
        }
        keyDelCommand={
        "target": key_locations,
        "deleteAlg": deleteMethod,
        "deleteAlgParam": deleteAlgParam,
        "deleteLevel": deleteLevel
        }
        duplicationDelCommand_str=generate_delete_command_str(duplicationDelCommand)
        keyDelCommand_str=generate_delete_command_str(keyDelCommand)
        print(f"Duplication Delete Command: {duplicationDelCommand_str}")
        print(f"Key Delete Command: {keyDelCommand_str}")


#########################删除命令发送#########################
        print("\n------------------------------")
        print("Delete Command Deliveried")
        print("------------------------------")
        
        # 初始化最终状态为成功
        final_status = "success"

        # 发送duplicationDelCommand
        send_time = datetime.now()  # 记录发送前的时间
        duplication_response = client.send_dup_del_command(duplicationDelCommand)
        if duplication_response['status'] == 'error':
            print("Error during duplication delete:", duplication_response['message'])
            final_status = "fail"
        else:
            print("Response from duplication delete:", duplication_response)

        # 如果keyDelCommand不为空，则发送
        if keyDelCommand["target"]:
            key_del_response = client.send_key_del_command(keyDelCommand)

            if key_del_response['status'] == 'error':
                print("Error during key delete:", key_del_response['message'])
                final_status = "fail"
            else:
                print("Response from key delete:", key_del_response)
        else:
            print("Not encrypted, no need to delete key")

        deletePerformTime=datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 引起异常的逻辑
        # 检查是否删除成功
        if final_status == "fail":
            error_data = {
                "data": {
                    "DataType": 0x4102,
                    "content": {
                        "infoID": infoID,
                        "affairsID": affairsID,
                        "deleteInstruction": delete_instruction_str,
                        "deletePerformer": deletePerformer,
                        "deletePerformTime": deletePerformTime,
                        "deleteControlSet": duplicationDelCommand_str+" and "+keyDelCommand_str,
                        "deleteDupResult": f"未成功对{infoID}副本完成删除"
                    }
                }
            }
            print("Failure, delete failed")
            raise DeleteFailException("Delete operation failed.", error_data)

        # 检查是否超过预设时间
        if (datetime.now() - send_time).total_seconds() > preset_duration_seconds:
            error_data = {
                "data": {
                    "DataType": 0x4102,
                    "content": {
                        "infoID": infoID,
                        "affairsID": affairsID,
                        "deleteInstruction": delete_instruction_str,
                        "deletePerformer": deletePerformer,
                        "deletePerformTime": deletePerformTime,
                        "timeout": (datetime.now() - send_time).total_seconds()
                    }
                }
            }
            print("Time out, delete failed")
            raise TimeoutException("Operation took longer than the preset time.", error_data)


        # 打印最终的结果
        if final_status == "success":
            print("Final result: Success!")
        else:
            print("Final result: Failed!")
        
        



#########################存证信息#########################
        print("\n------------------------------")
        print("Evidence Record")
        print("------------------------------")
        # 创建完整版存证的JSON对象

        # 定义全局变量-数据包头
        systemID = 1
        systemIP = "210.73.60.100"
        mainCMD = 0x0001
        subCMD = 0x0020
        evidenceID = "00032dab40af0c56d2fa332a4924d150"
        msgVersion = 0x1000
        submittime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 定义"data"字段中的子字段
        title = f"系统{systemID}删除{infoID}文件存证记录"
        abstract = f"系统{systemID}采用算法集合{deleteMethod}删除{infoID}文件存证记录"
        keyWords = "删除"
        category = "12-345624"
        others = "none"
        # infoID = "BA4A7F24-ACA7-4844-98A5-464786DF5C09"
        infoType = 1
        # deletePerformTime = "2022-12-13 09:24:34"
        deleteDupinfoID = locations
        deleteControlSet=duplicationDelCommand_str+" and "+keyDelCommand_str
        deleteAlg_num=1





        # 定义其他字段
        dataHash = "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa"
        datasign = "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa"

        fullEvidence = {
            "systemID": systemID,
            "systemIP": systemIP,
            "mainCMD": mainCMD,
            "subCMD": subCMD,
            "evidenceID": evidenceID,
            "msgVersion": msgVersion,
            "submittime": submittime,
            "data": {
                "title": title,
                "abstract": abstract,
                "keyWords": keyWords,
                "category": category,
                "others": others,
                "infoID": infoID,
                "infoType": infoType,
                "deletePerformer": deletePerformer,
                "deletePerformTime": deletePerformTime,
                "deleteDupinfoID": deleteDupinfoID,
                "deleteInstruction": {
                    "affairsID": affairsID,
                    "userID": userID,
                    "infoID": infoID,
                    "notifyTime": notifyTime,
                    "deleteMethod": deleteMethod,
                    "deleteGranularity": deleteGranularity
                },
                "deleteControlSet": deleteControlSet,
                "deleteAlg": deleteAlg_num,
                "deleteAlgParam": deleteAlgParam,
                "deleteLevel": deleteLevel
            },
            "dataHash": dataHash,
            "datasign": datasign
        }

        # 使用 json.dumps 打印格式化的 JSON
        print(json.dumps(fullEvidence, indent=4, ensure_ascii=False))


#########################删除操作日志处理#########################
        print("\n------------------------------")
        print("Operation Log")
        print("------------------------------")

        #添加操作日志的特有的字段
        operation_log=fullEvidence

        del operation_log["data"]["others"]
        operation_log["data"]["affairsID"]=affairsID
        operation_log["data"]["userID"]=userID
        operation_log["data"]["classfication_info"]=sorted_data
        operation_log["data"]["deleteMethod"]=deleteMethod
        operation_log["data"]["deleteGranularity"]=deleteGranularity
        if key_locations:
            operation_log["data"]["deleteKeyinfoID"]=key_locations
        else:
            operation_log["data"]["deleteKeyinfoID"]=''
        # 确保log文件夹存在，不存在则创建
        log_dir = "log"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        if infoID:
            target_file_path = os.path.join(log_dir, f"{infoID}-{affairsID}.json")
            with open(target_file_path, 'w', encoding='utf-8') as target_file:
                json.dump(operation_log, target_file, ensure_ascii=False, indent=4)
            print(f"File saved as {target_file_path}")
        else:
            print("infoID not found in operation_log dictionary")


        

    

        return jsonify({"message": "Data received and parsed successfully!"}), 200

    except DeleteFailException as e:
        error_data = e.error_data
        infoID = error_data["data"]["content"]["infoID"]
        affairsID = error_data["data"]["content"]["affairsID"]
        with open(f'./err2/{infoID}-{affairsID}.json', 'w') as f:
            json.dump(error_data, f,indent=4)

        if ifSendException:
            # 发送数据包到远程主机的代码 ...
            pass

        return jsonify({"error": str(e)}), 400

    except TimeoutException as e:
        error_data = e.error_data
        infoID = error_data["data"]["content"]["infoID"]
        affairsID = error_data["data"]["content"]["affairsID"]
        with open(f'./err1/{infoID}-{affairsID}.json', 'w') as f:
            json.dump(error_data, f,indent=4)

        if ifSendException:
            # 发送数据包到远程主机的代码 ...
            pass

        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run()
    # app.run(host='10.12.170.110')
