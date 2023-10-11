from storeEvidence import *

import json

# 定义全局变量-数据包头
systemID = 1
systemIP = "210.73.60.100"
mainCMD = 0x0001
subCMD = 0x0020
evidenceID = "00032dab40af0c56d2fa332a4924d150"
msgVersion = 0x1000
submittime = "2020-08-01 08:00:00"

# 定义"data"字段中的子字段
title = "系统x删除x文件存证记录"
abstract = "系统x采用算法集合x删除x文件存证记录"
keyWords = "删除"
category = "12-345624"
others = "12-345624"
infoID = "BA4A7F24-ACA7-4844-98A5-464786DF5C09"
infoType = 1
deletePerformer = "王XX"
deletePerformTime = "2022-12-13 09:24:34"
deleteDupInfoID = "48942ECA-7CDA-4B02-8198-274C4D232E47"
deleteControlSet = "control-constraints cname……"
deleteAlg = 1
deleteAlgParam = "XX,YY"
deleteLevel = 2

# 定义"deleteInstruction"子字段
userID = "u100000003"
infoID_deleteInstruction = "283749abaa234cde"
deleteMethod = "软件删除"
deleteGranularity = "age"


# 定义其他字段
dataHash = "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa"
datasign = "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa"


# 定义初始请求中特有的变量并赋值
reqtime = "2020-08-01 08:00:00"
objectSize = 256
objectMode = "text"


# 然后构造 JSON 字符串
requestData = {
    "systemID": systemID,
    "systemIP": systemIP,
    "mainCMD": 0x0001,
    "subCMD": 0x0041,
    "evidenceID": evidenceID,
    "msgVersion": 0x4100,
    "reqtime": reqtime,
    "data": {
        "objectSize": objectSize,
        "objectMode": objectMode
    },
    "datasign": datasign
}
# print(requestData)




# 创建JSON对象
supervisionEvidence = {
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
        "others": others
    },
    "dataHash": dataHash,
    "datasign": datasign
}

# 序列化为JSON字符串
supervisionEvidence_str = json.dumps(supervisionEvidence, indent=4)

# # 打印或存储JSON字符串
# print(supervisionEvidence_str)


# 创建JSON对象
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
        "deleteDupInfoID": deleteDupInfoID,
        "deleteInstruction": {
            "userID": userID,
            "infoID": infoID_deleteInstruction,
            "deleteMethod": deleteMethod,
            "deleteGranularity": deleteGranularity
        },
        "deleteControlSet": deleteControlSet,
        "deleteAlg": deleteAlg,
        "deleteAlgParam": deleteAlgParam,
        "deleteLevel": deleteLevel
    },
    "dataHash": dataHash,
    "datasign": datasign
}

# 序列化为JSON字符串
fullEvidence_str = json.dumps(fullEvidence, indent=4)

# # 打印或存储JSON字符串
# print(fullEvidence_str)

client_interaction('124.127.245.34', 50010, '124.127.245.34', 50004, 
                   requestData, '0x0001', '0x4100', 
                   fullEvidence, '0x0003', '0x4100')

print("end")

packet=create_packet('0x0001', '0x0001', '0x0041', '0x4100', '0x00', '0x00',fullEvidence)
# print(packet)
# print(packet[18:-16])
# print(extract_from_packet(packet))


# json_data_str = json.dumps(fullEvidence, indent=4)
# # 将JSON字符串转换为字节流
# json_data_str_bytes = json_data_str.encode('utf-8')

# # 创建包头
# header = create_packet_header_with_json('0x0001', '0x0001', '0x0041', '0x4100', '0x00', '0x00', json_data_str)

# print(header)

# send_packet_tcp("124.127.245.34", 50010, packet)
# print("end")

