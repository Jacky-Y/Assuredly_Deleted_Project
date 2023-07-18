from flask import Flask#使用Flask框架编写的服务器端应用
from flask import request
import json
import requests
import mysql.connector

serve=Flask(__name__)#创建Flask应用实例：
@serve.route('/delete',methods=['GET','POST'])
def analyse():#包含了一个路由函数analyse()，用于接收HTTP请求并处理删除指令。
    if request.method=="POST":#定义路由函数analyse()，并设置请求方法为POST：检查请求方法是否为POST，如果是，则获取请求数据并解析为JSON格式：
        data=request.get_data()
        # print (data.decode("utf-8"))
        json_data=json.loads(data.decode("utf-8"))
        print(json_data)#打印接收到的JSON数据：
        user_id=json_data.get("user_id")
        delete_method=json_data.get("delete_method")
        delete_granularity=json_data.get("delete_granularity")
        print("user_id=%s,\ndelete_method=%s,\ndelete_granularity=%s"%(user_id,delete_method,delete_granularity))
        msg="received"#设置一个响应消息
        #以上为删除指令解析过程
              
        # 连接到数据库
        cnx = mysql.connector.connect(
            host='127.0.0.1',      # 数据库主机地址
            user='root',  # 数据库用户名
            password='123456',  # 数据库密码
            database='Assuredly_Deleted_System'   # 数据库名称
        )#连接到名为Assuredly_Deleted_System的MySQL数据库，并执行了一个SELECT查询，获取了查询结果并进行处理。
        # 创建游标对象
        cursor = cnx.cursor()
        # 创建查询语句
        sql_copies = f"SELECT * FROM user_information_index WHERE user_id = '{user_id}';"
        # 执行查询语句
        cursor.execute(sql_copies)
        # 获取查询结果
        result = cursor.fetchall()
        # 处理查询结果
        for row in result:
            print("user_id = ", row[0], "ip = ", row[1])
        #以上为多副本确定过程

        # delete_list是包含要更新的列名的列表
        delete_list = ['column1', 'column2', 'column3']

        # 构建 SET 子句的部分
        set_clause = ', '.join([f"{column} = ''" for column in delete_list])

        # 构建完整的 SQL 语句
        sql = f"UPDATE Person SET {set_clause} WHERE id = '{user_id}';"

        print(sql)

        data = {
        'command': sql
        }

        urls = ['127.0.0.2', '127.0.0.3', '127.0.0.4']

        print(data.get("command"))
        #以上为指令分解与下发过程
        
        # for url in urls:
        #     response = requests.post(url, data=data)
        #     print(f"Response from {url}: {response.text}")

        # 关闭游标和数据库连接
        curso


        