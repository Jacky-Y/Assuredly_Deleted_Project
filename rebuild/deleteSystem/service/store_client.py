# services/data_service.py
from  StorageSystemClient import StorageSystemClient

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
