# 函数：generate_delete_level
# 功能：根据最高信息级别生成删除级别。这可能用于确定数据删除时需要应用的安全级别。
# 输入：
#    max_level: int - 表示最高信息安全级别的整数。
# 输出：
#    int - 根据最高信息级别计算出的删除级别。
def generate_delete_level(max_level):
    # 如果最高信息级别为5，则删除级别设置为7
    if max_level == 5:
        return 7
    # 如果最高信息级别为3或4，则删除级别设置为5
    elif max_level in [3, 4]:
        return 5
    # 如果最高信息级别为1或2，则删除级别设置为3
    elif max_level in [1, 2]:
        return 3
    # 如果最高信息级别不在上述范围内，则默认删除级别设置为1
    else:
        return 1

# 函数：generate_delete_commands
# 功能：根据提供的参数生成数据删除命令。
# 输入：
#    store_system_port: int - 存储系统的端口号。
#    max_level: int - 最高信息级别。
#    infoID: int/str - 信息的唯一标识符。
#    locations: list - 需要删除的数据的位置列表。
#    key_locations: list - 需要删除的关键数据的位置列表。
#    deleteGranularity: str - 删除的粒度。
#    deleteMethod: str - 使用的删除算法。
# 输出：
#    tuple - 包含两个字典，分别代表普通数据和密钥的删除命令。

def generate_delete_commands(store_system_ip,store_system_port, max_level, infoID, locations, key_locations, deleteGranularity, deleteMethod,infoType,affairsID):
    # # 检查 store_system_port 是否为整数
    # if not isinstance(store_system_port, int):
    #     raise TypeError("store_system_port must be an integer")

        # 检查 store_system_port 是否为整数
    if not isinstance(store_system_port, int):
        raise TypeError("store_system_port must be an integer")

    # 检查 max_level 是否为整数
    if not isinstance(max_level, int):
        raise TypeError("max_level must be an integer")

    # infoID 可以是整数或字符串，因此检查它是否为这两种类型之一
    if not isinstance(infoID, (int, str)):
        raise TypeError("infoID must be either an integer or a string")

    # 检查 locations 是否为列表
    if not isinstance(locations, list):
        raise TypeError("locations must be a list")

    # 检查 key_locations 是否为列表或者 None
    if not isinstance(key_locations, list) and key_locations is not None:
        raise TypeError("key_locations must be a list or None")


    # 检查 deleteGranularity 是否为字符串
    if not isinstance(deleteGranularity, str):
        raise TypeError("deleteGranularity must be a string")

    # 检查 deleteMethod 是否为字符串
    if not isinstance(deleteMethod, str):
        raise TypeError("deleteMethod must be a string")
    
    # 检查 infoType 是否为字符串
    if not isinstance(infoType, int):
        raise TypeError("infoType must be a int")


    # 根据最高信息级别生成删除级别
    deleteLevel = generate_delete_level(max_level)

    # 使用信息的唯一标识符作为删除算法的参数
    deleteAlgParam = infoID

    # 构造普通数据的删除命令
    duplicationDelCommand = {
        #指定infoID
        "infoID": infoID,
        #指定事务ID
        "affairsID":affairsID,
        # 指定删除目标的位置
        "target": locations,              
        # 指定删除操作的粒度
        "deleteGranularity": deleteGranularity,  
        # 指定使用的删除算法
        "deleteAlg": deleteMethod,               
        # 指定删除算法的参数
        "deleteAlgParam": deleteAlgParam,        
        # 指定删除操作的级别
        "deleteLevel": deleteLevel,
        # 指定信息类型
        "infoType": infoType,   
    }

    # 构造关键数据的删除命令
    keyDelCommand = {
        #指定infoID
        "infoID": infoID,
        #指定事务ID
        "affairsID":affairsID,
        # 指定关键数据删除目标的位置
        "target": key_locations,           
        # 指定使用的删除算法
        "deleteAlg": deleteMethod,                
        # 指定删除算法的参数
        "deleteAlgParam": deleteAlgParam,         
        # 指定删除操作的级别
        "deleteLevel": deleteLevel                
    }

    if key_locations==None:
        keyDelCommand = None

    # 返回构造的普通数据和关键数据的删除命令
    return duplicationDelCommand, keyDelCommand
