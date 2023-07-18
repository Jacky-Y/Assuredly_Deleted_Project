import json
import mysql.connector

# 连接到数据库
cnx = mysql.connector.connect(
    host='your_host',
    user='your_user',
    password='your_password',
    database='your_database'
)
cursor = cnx.cursor()

# 解析JSON文件并插入到数据库
json_files = [
    'Delete Request.json',
    'Delete Notification.json',
    'Delete Confirmation.json',
    'Delete Operation.json'
]

for json_file in json_files:
    with open(json_file, 'r') as file:
        json_data = json.load(file)

        user_id = json_data.get("user_id")
        delete_method = json_data.get("delete_method")
        delete_granularity = json_data.get("delete_granularity")

        # 将数据转换为SQL语句并插入到表中
        sql = "INSERT INTO your_table_name (user_id, delete_method, delete_granularity) VALUES (%s, %s, %s)"
        values = (user_id, delete_method, delete_granularity)

        cursor.execute(sql, values)

# 提交事务并关闭连接
cnx.commit()
cursor.close()
cnx.close()


