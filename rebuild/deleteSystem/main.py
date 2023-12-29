# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
from StorageSystemClient import StorageSystemClient
import requests
import json
import os
import argparse
from datetime import datetime
from flask import current_app
from util import NotificationTreeUtils
import threading
import time


# 确定性删除系统
# 1.2.1系统整体概述
# 确定性删除系统从删除指令通知与确认系统获得删除指令，并对指令进行解析，从而获取删除粒度、删除方法、全局性标识等字段，然后确定性删除系统将根据全局性标识从存储系统获得该个人信息包含的字段类型，并向分类分级系统查询这些字段类型对应的分类等级，确定性删除系统接下来将向存储系统查询该个人信息的存储类型、存储位置、密钥位置，并综合分类等级、存储类型、存储位置、密钥位置生成具体删除命令，并将删除命令发送到存储系统，删除系统执行删除之后，将向确定性删除系统汇报删除结果。
# 1.2.2 系统功能介绍
# 1.删除指令解析功能
# 从删除指令通知与确认系统获得删除指令之后，对删除指令按照通信协议进行解析，若各字段数据类型正确，则将正常获得删除粒度、删除方法等信息。
# 2.多副本确定功能已完成
# 确定性删除系统通过信息标识符向存储系统查询个人信息副本的存储位置，存储系统将个人信息副本位置返回
# 3.指令分解与下发功能已完成
# 确定性删除系统根据得到的个人信息存储位置、个人信息存储状态、密钥存储位置、个人信息字段类型分级等信息，生成删除命令，并将删除命令下发给存储系统
# 4.指令理解与方法选择功能已完成
# 确定性删除系统通过信息标识符向存储系统查询个人信息的字段类型，然后根据个人信息的字段类型向分类分级系统查询分级信息，并根据分级信息确定删除覆写次数
# 5.操作行为自存证功能已完成
# 确定性删除系统完成删除操作之后，将完成删除的过程中产生的各个字段保存为删除操作日志
# 6.证据提取功能已完成
# 确定性删除系统开启监听，当收到删除效果评测系统的日志提取请求之后，将提取相应的删除操作日志并发送给删除效果评测系统
# 7.密钥定位功能已完成
# 确定性删除系统通过信息标识符向存储系统查询个人信息的储存类型，如果是密文存储，则继续向存储系统查询密钥的存储位置，存储系统将密钥存储位置返回
# 8.操作执行功能已完成
# 确定性删除系统向存储系统发送删除命令，存储系统解析并执行删除命令，并将执行后的删除结果返回给确定性删除系统
# 9.	密钥删除功能已完成
# 确定性删除系统向存储系统发送密钥删除命令，存储系统解析并执行密钥删除命令，并将执行后的密钥删除结果返回给确定性删除系统
# 10.密钥分量确定与删除功能已完成
# 确定性删除系统通过信息标识符向存储系统查询个人信息的储存类型，如果是密文存储并且密钥是通过分散存储的形式进行存储，则向存储系统查询所有密钥分量的位置，存储系统将所有密钥分片的存储位置返回
# 11.操作反馈功能已完成
# 进行删除指令解析之后，确定性删除系统将得到发起删除的源域信息，如果当前域为源域，则在删除操作执行之后完之后等待其他域的删除结果，如果当前域不为源域，则在删除操作执行之后向源域报告删除结果
# 12.操作结果可视化功能未完成
# 源域的确定性删除系统在完成收集所有来自其他域的确定性删除系统的删除结果之后，通过可视化的方式展示最终的删除结果，即是否所有域都按要求完成了删除


#定义全局变量
node_statuses={}
status_updated = False
ifSendException = False
deletePerformer = "default Performer"
preset_duration_seconds=10

app = Flask(__name__)

# 类：DeleteFailException
# 功能：表示删除操作失败的异常类
# 输入：
#    message: str - 异常的描述信息
#    error_data: dict - 异常相关的附加数据
class DeleteFailException(Exception):
    def __init__(self, message, error_data):
        super().__init__(message)
        self.error_data = error_data

# 类：TimeoutException
# 功能：表示操作超时的异常类
# 输入：
#    message: str - 异常的描述信息
#    error_data: dict - 异常相关的附加数据
class TimeoutException(Exception):
    def __init__(self, message, error_data):
        super().__init__(message)
        self.error_data = error_data

# 函数：fetch_and_process_data
# 功能：从特定URL获取并处理数据
# 输入：
#    infoID: str - 信息的唯一标识符
# 输出：
#    tuple - 包含排序后的数据和最高信息级别
def fetch_and_process_data(infoID):
    # 第一步：从 http://127.0.0.1:7000/getInfoType 获取 InfoType 列表
    url_get_info_type = f"http://127.0.0.1:{app.config['store_system_port']}/getInfoType"
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
    # url_query = "http://127.0.0.1:6000/query"
    url_query = f"http://{app.config['classify_system_ip']}:{app.config['classify_system_port']}/query"

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


# 函数：generate_delete_level
# 功能：根据最高信息级别生成删除级别
# 输入：
#    max_level: int - 最高信息级别
# 输出：
#    int - 计算出的删除级别
def generate_delete_level(max_level):
    if max_level == 5:
        return 7
    elif max_level in [3, 4]:
        return 5
    elif max_level in [1, 2]:
        return 3
    else:
        return 1

# 函数：generate_delete_command_str
# 功能：根据删除命令的JSON格式生成字符串形式的删除命令
# 输入：
#    command_json: dict - 包含删除命令信息的JSON对象
# 输出：
#    str - 格式化的删除命令字符串
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


# 函数：parse_arguments
# 功能：解析命令行参数
# 输入：
#    无
# 输出：
#    argparse.Namespace - 解析后的命令行参数
def parse_arguments():
    parser = argparse.ArgumentParser(description='Flask Node Startup Configuration')
    parser.add_argument('system_id', help='Name of the node to start')
    return parser.parse_args()

# 函数：load_config
# 功能：加载指定系统标识的配置信息
# 输入：
#    system_id: str - 系统标识符
# 输出：
#    dict 或 None - 成功时返回配置信息字典，失败时返回 None
def load_config(system_id):
    try:
        with open('config.json', 'r') as file:
            config = json.load(file)
            for node in config['nodes']:
                if node['system_id'] == system_id:
                    return node
    except FileNotFoundError:
        print("配置文件未找到。请确保 config.json 文件在正确的位置。")
    except json.JSONDecodeError:
        print("配置文件格式错误。请确保它是有效的 JSON 格式。")
    except Exception as e:
        print(f"读取配置文件时发生错误：{e}")

    return None

# 函数：load_system_configs
# 功能：加载系统的配置信息
# 输入：
#    无
# 输出：
#    tuple - 包含分类系统和存储系统配置的元组，失败时返回 (None, None)
def load_system_configs():
    try:
        with open('config.json', 'r') as file:
            config = json.load(file)

            # 提取 classifySystem 和 storeSystem 的配置
            classify_system_config = config.get("classifySystem")
            store_system_config = config.get("storeSystem")

            return classify_system_config, store_system_config

    except FileNotFoundError:
        print("配置文件未找到。请确保 config.json 文件在正确的位置。")
    except json.JSONDecodeError:
        print("配置文件格式错误。请确保它是有效的 JSON 格式。")
    except Exception as e:
        print(f"读取配置文件时发生错误：{e}")

    return None, None

# 函数：send_deletion_message
# 功能：向根节点发送删除消息
# 输入：
#    rootNode: str - 根节点的系统标识符
#    system_id: str - 当前系统的标识符
#    final_status: str - 最终状态信息
# 输出：
#    无直接输出，但会向根节点发送 POST 请求
def send_deletion_message(rootNode,system_id, final_status):
    # 从配置文件中加载根节点信息
    root_node_config = load_config(rootNode)
    if root_node_config is None:
        print("无法加载根节点配置。")
        return

    root_node_ip = root_node_config['ip']
    root_node_port=root_node_config['port']

    # 构造数据包
    data = {'node_id':system_id,'status': final_status}

    # 发送 POST 请求到根节点的 /gatherResult 路由
    url = f'http://{root_node_ip}:{root_node_port}/gatherResult'
    try:
        response = requests.post(url, json=data)
        print(f"Message sent to root node. Response: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error sending message to root node: {e}")

# 函数：wait_for_results
# 功能：等待并显示删除结果
# 输入：
#    timeout: int - 等待结果的超时时间（秒）
# 输出：
#    无直接输出，但会打印每个节点的状态和超时后的结果
def wait_for_results(timeout):
    print(f"开始等待来自{list(node_statuses.keys())}的删除结果")
    global status_updated
    start_time = time.time()
    while time.time() - start_time < timeout:
        if status_updated:
            # 显示每个节点的当前状态
            for node, status in node_statuses.items():
                print(f"节点 {node} 状态: {status}")
            status_updated = False  # 重置标志

        if all(status == 'success' for status in node_statuses.values()):
            print("所有节点都成功报告了删除结果。")
            return
        time.sleep(1)  # 等待一秒再次检查

    # 超时后检查未成功报告的节点
    for node, status in node_statuses.items():
        if status != 'success':
            print(f"节点 {node} 未成功报告删除结果。")


# 路由：/gatherResult
# 功能：接收节点的删除结果并更新状态
# 输入：
#    无（使用 Flask 的 request.json 获取输入数据）
# 输出：
#    JSON - 返回结果接收确认或错误信息
@app.route('/gatherResult', methods=['POST'])
def gather_result():
    global status_updated
    data = request.json
    node_id = data.get('node_id')
    status = data.get('status')

    if node_id and status:
        node_statuses[node_id] = status
        status_updated = True  # 标记状态已更新
        return jsonify({"message": "Result received"}), 200
    else:
        return jsonify({"error": "Invalid data received"}), 400

# 路由：/getOperationLog
# 功能：根据请求数据获取操作日志
# 输入：
#    无（使用 Flask 的 request.get_json() 获取输入数据）
# 输出：
#    JSON - 返回操作日志或错误信息
@app.route('/getOperationLog', methods=['POST'])
def get_operation_log():
    try:
        # 从 POST 请求中解析 JSON 数据
        data = request.get_json()
        infoID = data['data']['infoID']
        affairsID = data['data']['affairsID']

        filename=infoID+"_"+affairsID

        # 构建文件路径
        file_path = os.path.join('log', f"{filename}.json")
        
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
        systemID=current_app.config.get('SYSTEM_ID')
        affairsID = data.get("affairsID")
        userID = data.get("userID")
        infoID = data.get("infoID")
        deleteMethod = data.get("deleteMethod")
        deleteGranularity = data.get("deleteGranularity")
        deleteNotifyTree= json.loads(data.get("deleteNotifyTree"))
        parentNode = NotificationTreeUtils.find_parent(deleteNotifyTree, systemID)
        rootNode = NotificationTreeUtils.get_root_node(deleteNotifyTree)
        otherNode=NotificationTreeUtils.find_all_nodes_except(deleteNotifyTree, systemID)

        isRoot=False
        if systemID==rootNode:
            isRoot=True
        
        delete_instruction_str=f"在{notifyTime}时间下发以{deleteMethod}方式删除{infoID}信息的{deleteGranularity}的指令"
        
        print(f"Submit Time: {notifyTime}")
        print(f"Affairs ID: {affairsID}")
        print(f"User ID: {userID}")
        print(f"Info ID: {infoID}")
        print(f"Delete Method: {deleteMethod}")
        print(f"Delete Granularity: {deleteGranularity}")
        print(f"Delete NotifyTree: {deleteNotifyTree}")
        print(f"Parent Node: {parentNode}")
        print(f"Root Node: {rootNode}")
        print(f"Other Node: {otherNode}")
        print(f"Myself: {systemID}")

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

        # client = StorageSystemClient("http://127.0.0.1:7000")
        client = StorageSystemClient(f"http://127.0.0.1:{app.config['store_system_port']}")
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
            print("Error during duplication delete:", duplication_response)
            final_status = "fail"
        else:
            print("Response from duplication delete:", duplication_response)
        # 如果keyDelCommand不为空，则发送
        if keyDelCommand["target"]:
            key_del_response = client.send_key_del_command(keyDelCommand)

            if key_del_response['status'] == 'error':
                print("Error during key delete:", key_del_response)
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
        operation_log["data"]["classification_info"]=sorted_data
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
            target_file_path = os.path.join(log_dir, f"{infoID}_{affairsID}.json")
            with open(target_file_path, 'w', encoding='utf-8') as target_file:
                json.dump(operation_log, target_file, ensure_ascii=False, indent=4)
            print(f"File saved as {target_file_path}")
        else:
            print("infoID not found in operation_log dictionary")

#########################删除结果汇总#########################
        print("\n------------------------------")
        print("Delete Result Collected")
        print("------------------------------")
        if isRoot==True:
            if otherNode==[]:
                print("Root node is the only node, deletion completed")
            else:
                global node_statuses  # 指定接下来使用的是全局变量
                node_statuses = {node: 'pending' for node in otherNode}
                # 启动等待结果的线程
                timeout = 60  # 设置超时时间
                wait_thread = threading.Thread(target=wait_for_results, args=(timeout,))
                wait_thread.start()
        else:
            print("sending results to the root code")
            send_deletion_message(rootNode,systemID,final_status)
            #向源域节点发送消息

        
#########################成功返回#########################
        return jsonify({"message": "Data received and parsed successfully!"}), 200

#########################异常处理#########################
        print("\n------------------------------")
        print("Exception Occurs")
        print("------------------------------")
    except DeleteFailException as e:
        print("\n------------------------------")
        print("Delete Failure Exception Captured")
        print("------------------------------")
        error_data = e.error_data
        infoID = error_data["data"]["content"]["infoID"]
        affairsID = error_data["data"]["content"]["affairsID"]
        with open(f'./err2/{infoID}-{affairsID}.json', 'w') as f:
            json.dump(error_data, f,indent=4)

        print(f"error log is saved as ./err2/{infoID}-{affairsID}.json")

        if ifSendException:
            # 发送数据包到远程主机的代码 ...
            pass

        return jsonify({"error": str(e)}), 400

    except TimeoutException as e:
        print("\n------------------------------")
        print("Time Out Exception Captured")
        print("------------------------------")
        error_data = e.error_data
        infoID = error_data["data"]["content"]["infoID"]
        affairsID = error_data["data"]["content"]["affairsID"]
        with open(f'./err1/{infoID}-{affairsID}.json', 'w') as f:
            json.dump(error_data, f,indent=4)

        print(f"error log is saved as ./err1/{infoID}-{affairsID}.json")

        if ifSendException:
            # 发送数据包到远程主机的代码 ...
            pass

        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# if __name__ == "__main__":
#     app.run()
    # app.run(host='10.12.170.110')

if __name__ == "__main__":
    args = parse_arguments()
    node_config = load_config(args.system_id)
    classify_system_config, store_system_config = load_system_configs()

    if node_config:
        app.config['SYSTEM_ID'] = args.system_id  # Store system_id in app.config
        app.config['HOST'] = node_config['ip']
        app.config['PORT'] = node_config['port']

        # Store classifySystem configuration in app.config
        if classify_system_config:
            app.config['classify_system_ip'] = classify_system_config['ip']
            app.config['classify_system_port'] = classify_system_config['port']
        else:
            print("No configuration found for classifySystem")

        # Store storeSystem configuration in app.config
        if store_system_config:
            app.config['store_system_port'] = store_system_config['port']
        else:
            print("No configuration found for storeSystem")

        app.run(host=node_config['ip'], port=node_config['port'])
    else:
        print(f"No configuration found for node {args.system_id}")