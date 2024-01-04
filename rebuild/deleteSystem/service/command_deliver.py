from datetime import datetime
from  StorageSystemClient import StorageSystemClient

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

    # 检查 keyDelCommand 是否为字典类型
    # keyDelCommand: 用于描述关键删除命令的字典，应包含必要的删除指令信息
    if not isinstance(keyDelCommand, dict):
        raise TypeError("keyDelCommand must be a dictionary")

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
    if keyDelCommand["target"]:
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
    keyDelCommand_str = generate_delete_command_str(keyDelCommand)

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

