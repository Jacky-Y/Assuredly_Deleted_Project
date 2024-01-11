import os
import json

from models.operation_log_model import OperationLogModel

def save_operation_log(fullEvidence, affairsID, userID, sorted_data, deleteMethod, deleteGranularity, key_locations, infoID,isRoot):
    """
    保存操作日志。
    此函数用于根据提供的参数创建和保存操作日志文件。

    :param fullEvidence: dict - 完整的证据信息，包含操作日志需要的全部原始数据
    :param affairsID: str - 代表事务标识的字符串
    :param userID: str - 代表用户标识的字符串
    :param sorted_data: list/dict - 分类后的数据
    :param deleteMethod: str - 删除方法的描述
    :param deleteGranularity: str - 删除的粒度
    :param key_locations: list - 关键信息的位置列表
    :param infoID: str - 信息标识符
    """


    # 参数类型检查以确保输入参数符合预期的数据类型

    # 检查 fullEvidence 参数是否为字典类型
    # fullEvidence: 应为包含完整证据信息的字典，用于记录操作日志的原始数据
    if not isinstance(fullEvidence, dict):
        raise TypeError("fullEvidence must be a dictionary")

    # 检查 affairsID 参数是否为字符串类型
    # affairsID: 用于标识事务的字符串，通常用于关联日志和特定的业务流程或操作
    if not isinstance(affairsID, str):
        raise TypeError("affairsID must be a string")

    # 检查 userID 参数是否为字符串类型
    # userID: 代表执行操作用户的唯一标识符，通常用于追踪和审计操作日志
    if not isinstance(userID, str):
        raise TypeError("userID must be a string")

    # 检查 sorted_data 参数是否为列表或字典类型
    # sorted_data: 经过排序或分类处理的数据，可能为列表或字典类型，根据具体的业务逻辑进行处理
    if not isinstance(sorted_data, (list, dict)):
        raise TypeError("sorted_data must be a list or dictionary")

    # 检查 deleteMethod 参数是否为字符串类型
    # deleteMethod: 代表删除操作使用的方法，为字符串描述，例如 'immediate' 或 'delayed'
    if not isinstance(deleteMethod, str):
        raise TypeError("deleteMethod must be a string")

    # 检查 deleteGranularity 参数是否为字符串类型
    # deleteGranularity: 描述删除操作的粒度，为字符串描述，例如 'all', 'partial'
    if not isinstance(deleteGranularity, str):
        raise TypeError("deleteGranularity must be a string")

    # 检查 key_locations 参数是否为列表类型或为 None
    # key_locations: 包含关键信息位置的列表，如果没有关键信息位置则为 None
    if not isinstance(key_locations, list) and key_locations is not None:
        raise TypeError("key_locations must be a list or None")

    # 检查 infoID 参数是否为字符串类型
    # infoID: 代表信息的唯一标识符，用于在日志文件中标记特定的操作或事件
    if not isinstance(infoID, str):
        raise TypeError("infoID must be a string")
    
    # 检查 isRoot 参数是否为字符串类型 
    # isRoot: 代表当前是否为源域，用于在日志文件中标记是否为源域的信息
    if not isinstance(isRoot, bool):
        raise TypeError("isRoot must be a bool")


    # # 添加操作日志的特有的字段
    # operation_log = fullEvidence.copy() # 创建 fullEvidence 的副本以避免修改原始数据

    # # 修改 operation_log 字典中的部分字段
    # # 移除 'others' 字段
    # operation_log["data"].pop("others", None)

    # #添加isRoot字段
    # operation_log['isRoot']=isRoot

    # # 更新其他字段
    # operation_log["data"]["affairsID"] = affairsID
    # operation_log["data"]["userID"] = userID
    # operation_log["data"]["classification_info"] = sorted_data
    # operation_log["data"]["deleteMethod"] = deleteMethod
    # operation_log["data"]["deleteGranularity"] = deleteGranularity

    # # 根据 key_locations 的值更新或清除 deleteKeyinfoID 字段
    # operation_log["data"]["deleteKeyinfoID"] = key_locations if key_locations else ''

    # # 确保log文件夹存在，不存在则创建
    # log_dir = "log"
    # if not os.path.exists(log_dir):
    #     os.makedirs(log_dir)

    # # 检查 infoID 是否存在
    # if infoID:
    #     # 构建目标文件路径
    #     target_file_path = os.path.join(log_dir, f"{infoID}_{affairsID}.json")

    #     # 打开文件并写入操作日志
    #     with open(target_file_path, 'w', encoding='utf-8') as target_file:
    #         # 使用 json.dump 将操作日志转换为 JSON 格式并保存
    #         json.dump(operation_log, target_file, ensure_ascii=False, indent=4)

    #     # 输出保存成功的消息
    #     print(f"File saved as {target_file_path}")
    # else:
    #     # infoID 不存在时的错误提示
    #     print("infoID not found in operation_log dictionary")

    # 函数结束

    db_model = OperationLogModel("127.0.0.1", "root", "123456", "assured_deletion")
    db_model.add_record(fullEvidence)
    print("log added!")


