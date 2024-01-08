from datetime import datetime
import requests

# 类：StorageSystemClient
# 功能：通过HTTP请求与存储系统进行交互
class StorageSystemClient:

    # 构造函数
    # 输入：
    #   base_url: str - 存储系统的基本URL
    def __init__(self, base_url):
        self.base_url = base_url  # 存储系统的基本URL
        self.headers = {
            "Content-Type": "application/json"  # 设置请求头部为JSON格式
        }

    # 私有函数：发送POST请求
    # 功能：向指定的端点发送POST请求，并返回JSON响应
    # 输入：
    #   endpoint: str - 请求的端点
    #   infoID: str - 信息的唯一标识符
    # 输出：
    #   dict - 服务器的JSON响应
    def _post_request(self, endpoint, infoID):
        url = f"{self.base_url}/{endpoint}"  # 构建完整的URL
        data = {"infoID": infoID}  # 构建请求数据
        # 发送POST请求并设置超时为10秒
        response = requests.post(url, headers=self.headers, json=data, timeout=10)  
        response.raise_for_status()  # 检查HTTP响应是否成功
        return response.json()  # 返回JSON格式的响应 

    # 函数：get_status
    # 功能：获取信息的状态
    # 输入：
    #   infoID: str - 信息的唯一标识符
    # 输出：
    #   str - 状态信息
    def get_status(self, infoID):
        try:
            # 调用内部方法 _post_request 发送请求并获取响应
            json_data = self._post_request("getStatus", infoID)

            # 检查响应数据是否含有 'Status' 字段
            if "Status" in json_data:
                return json_data.get("Status")
            else:
                # 如果响应数据中没有 'Status' 字段，返回错误信息
                return "Error: 'Status' not found in response"
        except requests.exceptions.HTTPError as http_err:
            # 捕获HTTP错误异常，并返回错误信息
            return f"HTTP error occurred: {http_err}"
        except requests.exceptions.ConnectionError as conn_err:
            # 捕获连接错误异常，并返回错误信息
            return f"Connection error occurred: {conn_err}"
        except requests.exceptions.Timeout as timeout_err:
            # 捕获超时异常，并返回错误信息
            return f"Timeout occurred: {timeout_err}"
        except requests.exceptions.RequestException as req_err:
            # 捕获请求异常，并返回错误信息
            return f"Request exception occurred: {req_err}"
        except Exception as e:
            # 捕获其他所有异常，并返回错误信息
            return f"An error occurred: {e}"

    # 函数：get_duplication_locations
    # 功能：获取信息的副本位置
    # 输入：
    #   infoID: str - 信息的唯一标识符
    # 输出：
    #   list - 信息副本的位置列表
    def get_duplication_locations(self, infoID):
        try:
            # 调用内部方法 _post_request 发送请求并获取响应
            json_data = self._post_request("getDuplicationLocations", infoID)

            # 检查响应数据是否含有 'Locations' 字段
            if "Locations" in json_data:
                return json_data.get("Locations")
            else:
                # 如果响应数据中没有 'Locations' 字段，返回错误信息
                return "Error: 'Locations' not found in response"
        except requests.exceptions.HTTPError as http_err:
            # 捕获HTTP错误异常，并返回错误信息
            return f"HTTP error occurred: {http_err}"
        except requests.exceptions.ConnectionError as conn_err:
            # 捕获连接错误异常，并返回错误信息
            return f"Connection error occurred: {conn_err}"
        except requests.exceptions.Timeout as timeout_err:
            # 捕获超时异常，并返回错误信息
            return f"Timeout occurred: {timeout_err}"
        except requests.exceptions.RequestException as req_err:
            # 捕获请求异常，并返回错误信息
            return f"Request exception occurred: {req_err}"
        except Exception as e:
            # 捕获其他所有异常，并返回错误信息
            return f"An error occurred: {e}"
    
    # 函数：get_centralized_key
    # 功能：获取集中式密钥信息
    # 输入：
    #   infoID: str - 信息的唯一标识符
    # 输出：
    #   str - 集中式密钥
    def get_centralized_key(self, infoID):
        try:
            # 调用内部方法 _post_request 发送请求并获取响应
            json_data = self._post_request("getCentralizedKey", infoID)

            # 检查响应数据是否含有 'Locations' 字段
            if "Locations" in json_data:
                return json_data.get("Locations")
            else:
                # 如果响应数据中没有 'Locations' 字段，返回错误信息
                return "Error: 'Locations' not found in response"
        except requests.exceptions.HTTPError as http_err:
            # 捕获HTTP错误异常，并返回错误信息
            return f"HTTP error occurred: {http_err}"
        except requests.exceptions.ConnectionError as conn_err:
            # 捕获连接错误异常，并返回错误信息
            return f"Connection error occurred: {conn_err}"
        except requests.exceptions.Timeout as timeout_err:
            # 捕获超时异常，并返回错误信息
            return f"Timeout occurred: {timeout_err}"
        except requests.exceptions.RequestException as req_err:
            # 捕获请求异常，并返回错误信息
            return f"Request exception occurred: {req_err}"
        except Exception as e:
            # 捕获其他所有异常，并返回错误信息
            return f"An error occurred: {e}"

    # 函数：get_decentralized_key
    # 功能：获取分布式密钥信息
    # 输入：
    #   infoID: str - 信息的唯一标识符
    # 输出：
    #   str - 分布式密钥
    def get_decentralized_key(self, infoID):
        try:
            # 调用内部方法 _post_request 发送请求并获取响应
            json_data = self._post_request("getDecentralizedKey", infoID)

            # 检查响应数据是否含有 'Locations' 字段
            if "Locations" in json_data:
                return json_data.get("Locations")
            else:
                # 如果响应数据中没有 'Locations' 字段，返回错误信息
                return "Error: 'Locations' not found in response"
        except requests.exceptions.HTTPError as http_err:
            # 捕获HTTP错误异常，并返回错误信息
            return f"HTTP error occurred: {http_err}"
        except requests.exceptions.ConnectionError as conn_err:
            # 捕获连接错误异常，并返回错误信息
            return f"Connection error occurred: {conn_err}"
        except requests.exceptions.Timeout as timeout_err:
            # 捕获超时异常，并返回错误信息
            return f"Timeout occurred: {timeout_err}"
        except requests.exceptions.RequestException as req_err:
            # 捕获请求异常，并返回错误信息
            return f"Request exception occurred: {req_err}"
        except Exception as e:
            # 捕获其他所有异常，并返回错误信息
            return f"An error occurred: {e}"


    # 函数：get_key_storage_method
    # 功能：获取密钥的存储方式
    # 输入：
    #   infoID: str - 信息的唯一标识符
    # 输出：
    #   str - 密钥存储方法
    def get_key_storage_method(self, infoID):
        try:
            # 调用内部方法 _post_request 发送请求并获取响应
            json_data = self._post_request("getKeyStorageMethod", infoID)

            # 检查响应数据是否含有 'KeyStorageMethod' 字段
            if "KeyStorageMethod" in json_data:
                return json_data.get("KeyStorageMethod")
            else:
                # 如果响应数据中没有 'KeyStorageMethod' 字段，返回错误信息
                return "Error: 'KeyStorageMethod' not found in response"
        except requests.exceptions.HTTPError as http_err:
            # 捕获HTTP错误异常，并返回错误信息
            return f"HTTP error occurred: {http_err}"
        except requests.exceptions.ConnectionError as conn_err:
            # 捕获连接错误异常，并返回错误信息
            return f"Connection error occurred: {conn_err}"
        except requests.exceptions.Timeout as timeout_err:
            # 捕获超时异常，并返回错误信息
            return f"Timeout occurred: {timeout_err}"
        except requests.exceptions.RequestException as req_err:
            # 捕获请求异常，并返回错误信息
            return f"Request exception occurred: {req_err}"
        except Exception as e:
            # 捕获其他所有异常，并返回错误信息
            return f"An error occurred: {e}"

    # 函数：send_dup_del_command
    # 功能：发送副本删除命令
    # 输入：
    #   duplication_del_command: dict - 副本删除命令
    # 输出：
    #   dict - 服务器的响应


    def send_dup_del_command(self, duplication_del_command):
        """
        发送副本删除命令。

        此函数向存储系统发送副本删除命令，并处理服务器的响应。

        :param duplication_del_command: dict - 包含副本删除命令信息的字典
        :return: dict - 服务器的响应，包括状态和消息
        """
        # 构建请求的完整URL
        url = f"{self.base_url}/duplicationDel"

        # 验证 duplication_del_command 是否为字典
        if not isinstance(duplication_del_command, dict):
            print("Error: duplication_del_command must be a dictionary")
            return {"status": "error", "message": "Invalid command format"}

        # 构建请求数据
        data = {"duplicationDelCommand": duplication_del_command}

        try:
            # 发送POST请求，并设置超时
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            # 检查HTTP响应是否成功
            response.raise_for_status()
            # 返回JSON格式的响应
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            # 捕获并处理HTTP错误
            print(f"HTTP error occurred: {http_err}")
            return {"status": "error", "message": str(http_err)}
        except requests.exceptions.ConnectionError as conn_err:
            # 捕获并处理连接错误
            print(f"Connection error occurred: {conn_err}")
            return {"status": "error", "message": str(conn_err)}
        except requests.exceptions.Timeout as timeout_err:
            # 捕获并处理超时错误
            print(f"Timeout occurred: {timeout_err}")
            return {"status": "error", "message": str(timeout_err)}
        except requests.exceptions.RequestException as req_err:
            # 捕获并处理其他请求相关错误
            print(f"Request exception occurred: {req_err}")
            return {"status": "error", "message": str(req_err)}
        except Exception as e:
            # 捕获并处理所有其他异常
            print(f"An unexpected error occurred: {e}")
            return {"status": "error", "message": str(e)}


    # 函数：send_key_del_command
    # 功能：发送密钥删除命令
    # 输入：
    #   key_del_command: dict - 密钥删除命令
    # 输出：
    #   dict - 服务器的响应
    def send_key_del_command(self, key_del_command):
        """
        发送密钥删除命令。

        此函数向存储系统发送密钥删除命令，并处理服务器的响应。

        :param key_del_command: dict - 包含密钥删除命令信息的字典
        :return: dict - 服务器的响应，包括状态和消息
        """
        # 构建请求的完整URL
        url = f"{self.base_url}/keyDel"

        # 验证 key_del_command 是否为字典
        if not isinstance(key_del_command, dict):
            print("Error: key_del_command must be a dictionary")
            return {"status": "error", "message": "Invalid command format"}

        # 构建请求数据
        data = {"keyDelCommand": key_del_command}

        try:
            # 发送POST请求，并设置超时
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            # 检查HTTP响应是否成功
            response.raise_for_status()
            # 返回JSON格式的响应
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            # 捕获并处理HTTP错误
            print(f"HTTP error occurred: {http_err}")
            return {"status": "error", "message": str(http_err)}
        except requests.exceptions.ConnectionError as conn_err:
            # 捕获并处理连接错误
            print(f"Connection error occurred: {conn_err}")
            return {"status": "error", "message": str(conn_err)}
        except requests.exceptions.Timeout as timeout_err:
            # 捕获并处理超时错误
            print(f"Timeout occurred: {timeout_err}")
            return {"status": "error", "message": str(timeout_err)}
        except requests.exceptions.RequestException as req_err:
            # 捕获并处理其他请求相关错误
            print(f"Request exception occurred: {req_err}")
            return {"status": "error", "message": str(req_err)}
        except Exception as e:
            # 捕获并处理所有其他异常
            print(f"An unexpected error occurred: {e}")
            return {"status": "error", "message": str(e)}


# 函数：generate_delete_command_str
# 功能：根据删除命令的JSON格式生成字符串形式的删除命令
# 输入：
#    command_json: dict - 包含删除命令信息的JSON对象
# 输出：
#    str - 格式化的删除命令字符串
def generate_delete_command_str(command_json):
    # 确保传入的参数是一个字典
    if not isinstance(command_json, dict):
        raise ValueError("command_json must be a dictionary")

    # 从 JSON 对象中提取删除命令的各个部分
    target = command_json.get("target", "")
    deleteGranularity = command_json.get("deleteGranularity", None)
    deleteAlg = command_json.get("deleteAlg", "")
    deleteAlgParam = command_json.get("deleteAlgParam", "")
    deleteLevel = command_json.get("deleteLevel", "")
    
    # 根据是否提供了删除粒度来格式化删除命令字符串
    if deleteGranularity:
        command_str = f"delete {deleteGranularity} of {target} using deleteAlg={deleteAlg} with deleteAlgParam={deleteAlgParam} at deleteLevel= {deleteLevel}"
    else:
        command_str = f"delete {target} using deleteAlg={deleteAlg} with deleteAlgParam={deleteAlgParam} at deleteLevel= {deleteLevel}"
    
    return command_str

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

def deliver_delete_commands(store_system_port, duplicationDelCommand, keyDelCommand, infoID, affairsID, delete_instruction_str, deletePerformer, preset_duration_seconds):
    # 参数类型检查
    # 检查 store_system_port 是否为整数类型
    # store_system_port: 存储系统的端口号，应为整数类型
    if not isinstance(store_system_port, int):
        raise TypeError("store_system_port must be an integer")

    # 检查 duplicationDelCommand 是否为字典类型
    # duplicationDelCommand: 用于描述重复删除命令的字典，应包含必要的删除指令信息
    if not isinstance(duplicationDelCommand, dict):
        raise TypeError("duplicationDelCommand must be a dictionary")

    
    # 检查 key_locations 是否为列表或者 None
    # keyDelCommand: 用于描述密钥删除命令的字典，应包含必要的删除指令信息
    if not isinstance(keyDelCommand, list) and keyDelCommand is not None:
        raise TypeError("keyDelCommand must be a list or None")

    # 检查 infoID 是否为字符串类型
    # infoID: 代表信息标识的字符串，用于唯一确定需要删除的数据项
    if not isinstance(infoID, str):
        raise TypeError("infoID must be a string")

    # 检查 affairsID 是否为字符串类型
    # affairsID: 代表事务标识的字符串，用于记录和管理删除操作的上下文
    if not isinstance(affairsID, str):
        raise TypeError("affairsID must be a string")

    # 检查 delete_instruction_str 是否为字符串类型
    # delete_instruction_str: 包含删除指令详细信息的字符串
    if not isinstance(delete_instruction_str, str):
        raise TypeError("delete_instruction_str must be a string")

    # 检查 deletePerformer 是否为字符串类型
    # deletePerformer: 代表执行删除操作的实体（可能是用户或系统）的名称或标识
    if not isinstance(deletePerformer, str):
        raise TypeError("deletePerformer must be a string")

    # 检查 preset_duration_seconds 是否为整数或浮点数
    # preset_duration_seconds: 预设的操作超时时长，以秒为单位
    if not isinstance(preset_duration_seconds, (int, float)):
        raise TypeError("preset_duration_seconds must be a number")

    # 初始化最终状态为成功
    final_status = "success"

    # 记录操作开始时间
    send_time = datetime.now()

    # 创建 StorageSystemClient 实例
    client = StorageSystemClient(f"http://127.0.0.1:{store_system_port}")

    # 发送重复删除命令并处理响应
    duplication_response = client.send_dup_del_command(duplicationDelCommand)
    if duplication_response['status'] == 'error':
        print("Error during duplication delete:", duplication_response)
        final_status = "fail"
    else:
        print("Response from duplication delete:", duplication_response)

    # 如果 keyDelCommand 不为空，则发送关键删除命令
    if keyDelCommand:
        key_del_response = client.send_key_del_command(keyDelCommand)
        if key_del_response['status'] == 'error':
            print("Error during key delete:", key_del_response)
            final_status = "fail"
        else:
            print("Response from key delete:", key_del_response)
    else:
        print("Not encrypted, no need to delete key")

    # 格式化删除执行时间
    deletePerformTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 生成删除命令字符串
    duplicationDelCommand_str = generate_delete_command_str(duplicationDelCommand)
    if keyDelCommand:
        keyDelCommand_str = generate_delete_command_str(keyDelCommand)
    else:
        keyDelCommand_str ="no need for key deletion command"

    # 检查删除操作是否成功
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
                    "deleteControlSet": duplicationDelCommand_str + " and " + keyDelCommand_str,
                    "deleteDupResult": f"未成功对{infoID}副本完成删除"
                }
            }
        }
        print("Failure, delete failed")
        raise DeleteFailException("Delete operation failed.", error_data)

    # 检查操作是否超时
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

    # 返回删除操作的最终结果
    if final_status == "success":
        print("Final result: Success!")
        return "success", deletePerformTime
    else:
        print("Final result: Failed!")
        return "fail", deletePerformTime

