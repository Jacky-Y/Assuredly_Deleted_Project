import mysql.connector

# 连接到数据库
cnx = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='1234',
    database='mysql'
)

cursor = cnx.cursor()

# 执行查询操作
query = '''
SELECT *
FROM `delete_logs_table`
WHERE `Log Type` IN ('Delete Request', 'Delete Notification')
'''
cursor.execute(query)

# 获取查询结果
results = cursor.fetchall()

# 提取"Delete Request"和"Delete Notification"的行
delete_request = None
delete_notification = None

for row in results:
    log_type = row[1]

    if log_type == 'Delete Request':
        delete_request = row
    elif log_type == 'Delete Notification':
        delete_notification = row

# 比较并输出结果
if delete_request is not None and delete_notification is not None:
    column_names = [desc[0] for desc in cursor.description]
    for column_name in column_names:
        request_value = delete_request[column_names.index(column_name)]
	  notification_value = delete_notification[column_names.index(column_name)]
        #confirmation_value = delete_confirmation[column_names.index(column_name)]

        if notification_value == confirmation_value:
            print(f"{column_name}: True")
        else:
            print(f"{column_name}: False")
            print(f"Delete Request: {request_value}")
		print(f"Delete Notification: {notification_value}")
            #print(f"Delete Confirmation: {confirmation_value}")
            print("--------------------------------------")
else:
    print("Either Delete Request or Delete Notification is missing.")

# 关闭连接
cursor.close()
cnx.close()
