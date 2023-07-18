from flask import Flask
from flask import request
import json
import requests
import time
import datetime
import mysql.connector
import util
import struct

serve=Flask(__name__)
@serve.route('/delete',methods=['GET','POST'])
def analyse():
    if request.method=="POST":
        data=request.get_data()
        # print (data.decode("utf-8"))
        json_data=json.loads(data.decode("utf-8"))
        print(json_data)
        infoID=json_data.get("infoID")
        delete_method=json_data.get("delete_method")
        delete_granularity=json_data.get("delete_granularity")
        print("infoID=%s,\ndelete_method=%s,\ndelete_granularity=%s"%(infoID,delete_method,delete_granularity))
        msg="received"
        #以上为删除指令解析过程

              
        # 连接到数据库
        cnx = mysql.connector.connect(
            host='127.0.0.1',      # 数据库主机地址
            user='deletion_root',  # 数据库用户名
            password='123456',  # 数据库密码
            database='deletion_db'   # 数据库名称
        )
        # 创建游标对象
        cursor = cnx.cursor()
        # 创建查询语句
        sql_copies = f"SELECT * FROM personal_information_duplication_index WHERE infoID = '{infoID}';"
        # 执行查询语句
        cursor.execute(sql_copies)
        # 获取查询结果
        result = cursor.fetchall()
        # 处理查询结果
        ips = []
        deleteDupInfos=[]
        sqls=[]

        # delete_list是包含要更新的列名的列表
        delete_list = delete_granularity.split(",")
        # 构建 SET 子句的部分
        set_clause = ', '.join([f"{column} = \"\"" for column in delete_list])

        
        for row in result:
            print("infoID = ", row[0], "ip = ", row[1],"deleteDupInfo=",row[2])
            ips.append(row[1])
            deleteDupInfos.append(row[2])

            # 构建完整的 SQL 语句
            sql = f"UPDATE personal_information_table SET {set_clause} WHERE deleteDupInfo = \"{row[2]}\";"
            sqls.append(sql)
            #以上为多副本确定过程


        for i in range(0,3):
            print("deleting ",deleteDupInfos[i]," sending command ",sqls[i]," to ",ips[i])


    
    #     #以上为指令分解与下发过程

    #     for ip in ips:
    #         print(ip)
    #         print(sql)
    #     #     response = requests.post(ip, data=data)
    #     #     print(f"Response from {ip}: {response.text}")


        # 创建查询语句
        sql_copies = f"SELECT * FROM personal_information_table WHERE infoID = '{infoID}';"
        # 执行查询语句
        cursor.execute(sql_copies)
        # 获取查询结果
        result = cursor.fetchall()

        # print(result[0][-4])
        # print(result[0][-3])
        # print(result[0][-2])
        # print(result[0][-1])

        ############存证部分##########

        ##############body部分##############

        infoOwner=result[0][-4]
        infoCreator=result[0][-3]
        infoCreateTime=result[0][-2].strftime("%Y-%m-%d %H:%M:%S")
        infoCreateLoc=result[0][-1]

        deleteDupInfoID=deleteDupInfos
        deletePerformer="王XX"
        deletePerformTime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        deleteIntention="删除个人信息标识"
        deleteRequirements="can not be recovered"
        deleteControlSet=sqls
        deleteAlg=1
        deleteAlgParam="XX,YY"
        deleteLevel=5



        data = {
            "systemTypeID": 1,
            "systemIP": "210.73.60.100",
            "time": "2020-08-01 08:00:00",

        "data": {
            "DataType": 64,
            "content": {
                "infoID": infoID,
                "infoType": 1,
                "infoContent": delete_granularity,
                "infoOwner": infoOwner,
                "infoCreator": infoCreator,
                "infoCreateTime": infoCreateTime,
                "infoCreateLoc": infoCreateLoc,
                "deleteDupInfoID": deleteDupInfoID,
                "deletePerformer": deletePerformer,
                "deletePerformTime": deletePerformTime,
                "deleteIntention": deleteIntention,
                "deleteRequirements": deleteRequirements,
                "deleteControlSet": deleteControlSet,
                "deleteAlg": deleteAlg,
                "deleteAlgParam": deleteAlgParam,
                "deleteLevel": deleteLevel
            }
        }
    }
        json_data = json.dumps(data, indent=4)
        print(json_data)
        json_data_bytes = json_data.encode('utf-8')

        ##############header部分##############
        header=util.create_packet_header_with_json("0x01","0x40","0x0001","0x00","0x00","0x00000000",json_data)

        print(header)

        ##############tail部分##############

        tail = struct.pack('>16s', b'\x00'*16)

        packet=header+json_data_bytes+tail

        util.send_packet_tcp("192.168.43.243",50001,packet)







        # 关闭游标和数据库连接

        cursor.close()
        cnx.close()
    else: 
        msg="hello"
    return msg

if __name__ == '__main__':
    serve.run(host='0.0.0.0',port=5000)