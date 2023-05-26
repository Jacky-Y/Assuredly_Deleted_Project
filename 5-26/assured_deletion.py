from flask import Flask
from flask import request
import json
import requests
import mysql.connector

serve=Flask(__name__)
@serve.route('/delete',methods=['GET','POST'])
def analyse():
    if request.method=="POST":
        data=request.get_data()
        # print (data.decode("utf-8"))
        json_data=json.loads(data.decode("utf-8"))
        print(json_data)
        user_id=json_data.get("user_id")
        delete_method=json_data.get("delete_method")
        delete_granularity=json_data.get("delete_granularity")
        print("user_id=%s,\ndelete_method=%s,\ndelete_granularity=%s"%(user_id,delete_method,delete_granularity))
        msg="received"
        #以上为删除指令解析过程
              
        # 连接到数据库
        cnx = mysql.connector.connect(
            host='127.0.0.1',      # 数据库主机地址
            user='root',  # 数据库用户名
            password='1234',  # 数据库密码
            database='Assuredly_Deleted_System'   # 数据库名称
        )
        # 创建游标对象
        cursor = cnx.cursor()
        # 创建查询语句
        sql_copies = f"SELECT * FROM user_information_index WHERE user_id = '{user_id}';"
        # 执行查询语句
        cursor.execute(sql_copies)
        # 获取查询结果
        result = cursor.fetchall()
        # 处理查询结果
        urls = []
        for row in result:
            print("user_id = ", row[0], "ip = ", row[1])
            urls.append(row[1])

        #以上为多副本确定过程

        # delete_list是包含要更新的列名的列表
        delete_list = delete_granularity.split(",")

        # 构建 SET 子句的部分
        set_clause = ', '.join([f"{column} = ''" for column in delete_list])

        # 构建完整的 SQL 语句
        sql = f"UPDATE Person SET {set_clause} WHERE id = '{user_id}';"


        data = {
        'command': sql
        }

    
        #以上为指令分解与下发过程

        for url in urls:
            print(url)
            print(sql)
        #     response = requests.post(url, data=data)
        #     print(f"Response from {url}: {response.text}")

        # 关闭游标和数据库连接

        cursor.close()
        cnx.close()
    else: 
        msg="hello"
    return msg

if __name__ == '__main__':
    serve.run(host='0.0.0.0',port=5000)