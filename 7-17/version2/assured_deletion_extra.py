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
        print(data)
        infoID=json_data.get("infoID")
        delete_method=json_data.get("delete_method")
        delete_granularity=json_data.get("delete_granularity")
        print("infoID=%s,\ndelete_method=%s,\ndelete_granularity=%s"%(infoID,delete_method,delete_granularity))
        msg="received"

        receive_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #以上为删除指令解析过程



        ########################设置固定信息########################
        deletePerformer="王XX"
        deleteIntention="删除个人信息标识"
        deleteRequirements="can not be recovered"
        deleteAlg="Secure Erase"
        deleteAlgParam="random bits"
        deleteLevel=3



        ########################解析完成  生成删除确认日志################################
        delete_confirmation_log= { 
                                "deletePerformer": deletePerformer,
                                "Log_Type": "Delete_Confirmation",
                                "infoID": infoID,
                                "delete_granularity":delete_granularity,
                                "deleteIntention": "删除个人信息标识",
                                "deleteRequirements": "can not be recovered"
                                        }
        print(delete_confirmation_log)
        result=util.save_dict_as_json_and_post(delete_confirmation_log,"Delete_Comfirmation","http://172.18.0.207:5000/receive_files")
        print("确认日志状态：",result)



              
        # 连接到数据库
        cnx = mysql.connector.connect(
            host='127.0.0.1',      # 数据库主机地址
            user='dup_root',  # 数据库用户名
            password='123456',  # 数据库密码
            database='dup_db'   # 数据库名称
        )
        # 创建游标对象
        cursor = cnx.cursor()
        # 创建查询语句
        sql_copies = f"SELECT * FROM duplication_info WHERE infoID = '{infoID}';"
        # 执行查询语句
        cursor.execute(sql_copies)
        # 获取查询结果
        result = cursor.fetchall()
        # 处理查询结果
        servers = []
        deleteDupInfos=[]
        sqls=[]

        # delete_list是包含要更新的列名的列表
        delete_list = delete_granularity.split(",")
        # 构建 SET 子句的部分
        set_clause = ', '.join([f"{column} = \"\"" for column in delete_list])

        
        for row in result:
            # print("infoID = ", row[0], "server = ", row[1],"deleteDupInfo=",row[2])
            servers.append(row[1])
            deleteDupInfos.append(row[2])

            # 构建完整的 SQL 语句
            sql = f"UPDATE personal_information SET {set_clause} WHERE deleteDupInfoID = \"{row[2]}\";"
            sqls.append(sql)
            #以上为多副本确定过程


        for i in range(0,3):
            # print("deleting ",deleteDupInfos[i]," sending command ",sqls[i]," to ",servers[i])
            print(sqls[i])


    
    #     #以下为指令分解与下发过程

        # 数据库连接信息
        db_info = [
            {"host": "localhost", "user": "server1_root", "password": "123456", "database": "server1_db"},
            {"host": "localhost", "user": "server2_root", "password": "123456", "database": "server2_db"},
            {"host": "localhost", "user": "server3_root", "password": "123456", "database": "server3_db"},
        ]

        # InfoID，你需要将这里改为你实际需要删除的InfoID
        deleteDupInfos_to_delete = deleteDupInfos

        # 遍历数据库连接信息
        for i in range(0,3):
            db=db_info[i]
            sql=sqls[i]
            try:
                # 创建数据库连接
                cnx = mysql.connector.connect(**db)

                # 创建游标
                cursor = cnx.cursor()

                # 执行删除操作
                # delete_query = "DELETE FROM personal_information WHERE InfoID = %s"
                # cursor.execute(delete_query, (info_id_to_delete,))
                cursor.execute(sql)

                # 提交更改
                cnx.commit()
                print("deletion for %s is done"%(db_info[i]["database"]))

            except mysql.connector.Error as err:
                print("Something went wrong: {}".format(err))

            finally:
                if (cnx.is_connected()):
                    cursor.close()
                    cnx.close()
                    print("MySQL for %s connection is closed"%(db_info[i]["database"]))



#####################以下是存证部分#######################

        # 创建数据库连接
        cnx = mysql.connector.connect(**db_info[0])
        # 创建游标
        cursor = cnx.cursor()
        # 创建查询语句
        sql_copies = f"SELECT * FROM personal_information WHERE infoID = '{infoID}';"
        # 执行查询语句
        cursor.execute(sql_copies)
        # 获取查询结果
        result = cursor.fetchall()



    #     ############存证部分##########

    #     ##############body部分##############

        infoOwner=result[0][-4]
        infoCreator=result[0][-3]
        infoCreateTime=result[0][-2].strftime("%Y-%m-%d %H:%M:%S")
        infoCreateLoc=result[0][-1]

        deleteDupInfoID=deleteDupInfos
        # deletePerformer="王XX"
        deletePerformTime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # deleteIntention="删除个人信息标识"
        # deleteRequirements="can not be recovered"
        deleteControlSet=sqls
        # deleteAlg="Secure Erase"
        # deleteAlgParam="random bits"
        # deleteLevel=3



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

        ##############tail部分##############

        tail = struct.pack('>16s', b'\x00'*16)

        packet=header+json_data_bytes+tail

        ##############存证发送#############    
        # print(packet)
        # util.send_packet_tcp("192.168.43.243",50004,packet)

        #########################删除操作日志#############################
        delete_operation_log=data["data"]["content"]
        delete_operation_log["Log_Type"]="Delete_Operation"
        print(delete_operation_log)
        result=util.save_dict_as_json_and_post(delete_operation_log,"Delete_Operation","http://172.18.0.207:5000/receive_files")
        print("操作日志状态：",result)
        


        # 关闭游标和数据库连接

        cursor.close()
        cnx.close()
    else: 
        msg="hello"
    return msg

if __name__ == '__main__':
    serve.run(host='0.0.0.0',port=5000)