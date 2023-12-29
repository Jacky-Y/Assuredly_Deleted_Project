import requests
from requests.exceptions import RequestException
import json

def fetch_and_process_data(infoID, store_system_port, classify_system_ip, classify_system_port):
    """
    从两个不同的系统（存储系统和分类系统）获取并处理数据。
    
    此函数首先从存储系统获取信息类型，然后使用这些信息类型查询分类系统。
    过程中包含了错误处理和网络请求的异常捕获。

    Args:
    - infoID (str): 需要查询的信息的唯一标识符。
    - store_system_port (int): 存储系统服务的端口号。
    - classify_system_ip (str): 分类系统的IP地址。
    - classify_system_port (int): 分类系统服务的端口号。

    Returns:
    - tuple: 返回一个包含排序后的数据和最高信息级别的元组。

    Raises:
    - ValueError: 参数验证错误或服务器返回的业务逻辑错误。
    - RequestException: 网络请求错误。
    - json.JSONDecodeError: JSON解析错误。
    - Exception: 捕获其他未预期的错误并重新抛出。
    """
    
    # 参数验证
    # 验证 infoID 是否为有效的字符串
    if not isinstance(infoID, str) or not infoID:
        raise ValueError("Invalid infoID provided")
    
    # 验证 store_system_port 是否为有效的端口号
    if not isinstance(store_system_port, int) or store_system_port <= 0:
        raise ValueError("Invalid store_system_port provided")
    
    # 验证 classify_system_ip 是否为有效的IP地址
    if not isinstance(classify_system_ip, str) or not classify_system_ip:
        raise ValueError("Invalid classify_system_ip provided")
    
    # 验证 classify_system_port 是否为有效的端口号
    if not isinstance(classify_system_port, int) or classify_system_port <= 0:
        raise ValueError("Invalid classify_system_port provided")

    try:
        # 从存储系统获取信息类型
        # 构建请求URL和头部信息
        url_get_info_type = f"http://127.0.0.1:{store_system_port}/getInfoType"
        headers_get_info_type = {"Content-Type": "application/json"}
        data_get_info_type = {"infoID": infoID}

        # 发送POST请求
        response_get_info_type = requests.post(url_get_info_type, headers=headers_get_info_type, json=data_get_info_type, timeout=10)
        # 检查响应状态码是否指示错误
        response_get_info_type.raise_for_status()
        # 解析JSON响应内容
        response_data_get_info_type = response_get_info_type.json()

        # 检查响应内容中是否有错误信息
        if 'error' in response_data_get_info_type:
            raise ValueError(f"Error from store system: {response_data_get_info_type['error']}")

        # 提取响应中的InfoTypes
        info_types = response_data_get_info_type.get('InfoTypes', [])

        # 使用获取的信息类型查询分类系统
        # 构建请求URL和头部信息
        url_query = f"http://{classify_system_ip}:{classify_system_port}/query"
        headers_query = {"Content-Type": "application/json"}
        data_query = {"InfoTypes": info_types}

        # 发送POST请求
        response_query = requests.post(url_query, headers=headers_query, json=data_query, timeout=10)
        # 检查响应状态码是否指示错误
        response_query.raise_for_status()
        # 解析JSON响应内容
        response_data = response_query.json()

        # 检查响应内容中是否有错误信息
        if 'error' in response_data:
            raise ValueError(f"Error from classify system: {response_data['error']}")

        # 对返回的数据基于'InfoLevel'字段进行排序，并获取最高信息级别
        sorted_data = sorted(response_data, key=lambda x: x['InfoLevel'], reverse=True)
        max_level = sorted_data[0]['InfoLevel']

        # 返回处理后的数据和最高信息级别
        return sorted_data, max_level

    except RequestException as e:
        # 处理与网络请求相关的异常
        print(f"网络请求错误: {e}")
        # 重新抛出异常，包含更多上下文信息
        raise RuntimeError("Failed to fetch data from external API") from e
    except json.JSONDecodeError as e:
        # 处理JSON解析错误
        print("JSON解析错误")
        # 重新抛出异常，包含更多上下文信息
        raise RuntimeError("JSON decoding error") from e
    except Exception as e:
        # 处理其他未预期的错误
        print(f"未预期的错误: {e}")
        # 重新抛出异常，包含更多上下文信息
        raise RuntimeError("An unexpected error occurred") from e
