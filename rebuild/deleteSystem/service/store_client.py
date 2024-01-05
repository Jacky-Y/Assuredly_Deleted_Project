# services/data_service.py
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


class DataServiceError(Exception):
    """自定义异常类，用于处理数据服务中的错误。"""

def query_data_and_key_locations(infoID, store_system_port):
    """
    查询指定infoID的副本位置和密钥位置信息。

    此函数首先查询infoID的存储状态，然后查询副本位置信息。
    如果状态为加密，则进一步查询密钥存储方式和密钥位置。

    Args:
    - infoID (str): 需要查询的信息的唯一标识符。
    - store_system_port (int): 存储系统的端口号。

    Returns:
    - tuple: 包含副本位置(locations)和密钥位置(key_locations)的元组。

    Raises:
    - DataServiceError: 在查询过程中遇到的任何错误。
    """
    client = StorageSystemClient(f"http://127.0.0.1:{store_system_port}")

    try:
        # 查询infoID的存储状态
        status = client.get_status(infoID)
        if not status:
            raise DataServiceError(f"Failed to retrieve storage status for infoID {infoID}.")

        # 查询infoID的副本位置信息
        locations = client.get_duplication_locations(infoID)
        if not locations:
            # 如果未找到副本位置信息，则设置为None
            locations = None

        key_locations = None  # 初始化密钥位置为None
        if status == "Encrypted":
            # 查询密钥存储方式
            key_storage_method = client.get_key_storage_method(infoID)

            if not key_storage_method:
                raise DataServiceError(f"Failed to retrieve key storage method for infoID {infoID}.")

            # 根据密钥存储方式获取密钥位置
            if key_storage_method == "Centralized":
                key_locations = client.get_centralized_key(infoID)
            elif key_storage_method == "Decentralized":
                key_locations = client.get_decentralized_key(infoID)

            if not key_locations:
                # 如果未找到密钥位置信息，则设置为None
                key_locations = None

        return locations, key_locations

    except DataServiceError as e:
        # 捕获自定义的DataServiceError并向外部抛出
        raise e
    except Exception as e:
        # 捕获其他未预期的异常并转换为DataServiceError
        raise DataServiceError(f"An unexpected error occurred: {e}")
