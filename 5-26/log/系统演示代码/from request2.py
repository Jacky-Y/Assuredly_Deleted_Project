from flask import Flask, request
import json
import mysql.connector

serve=Flask(__name__)#创建Flask应用实例：
@serve.route('/delete',methods=['GET','POST'])
def analyse():
    if request.method == 'POST':
        # 解析四个JSON文件的数据
        json_data1 = '''
        {
            "Time": "April 23, 2023 15:30:00",
            "Log Type": "Delete Request",
            "user_id": 12345,
            "Delete Target": "User Data",
            "delete_granularity": "single record",
            "Sync confirmation": "Yes",
            "delete_method": "Secure Erase",
            "Multiple replication locations": "Yes",
            "Delete configuration": "Soft deletion, with a retention period of 30 days, verified by third-party auditors for deletion"
        }
        '''

        json_data2 = '''
        {
            "Time": "April 23, 2023 15:30:00",
            "Log Type": "Delete Notification",
            "user_id": 12345,
            "Delete Target": "User Data",
            "delete_granularity": "individual records",
            "Sync confirmation": "Yes",
            "delete_method": "Secure Erase",
            "Multiple replication locations": "Yes",
            "Delete configuration": "Soft deletion, retention period of 30 days, deletion verified by third-party auditors",
            "Message": "Received delete request. Start the deletion operation."
        }
        '''

        json_data3 = '''
        {
            "Time": "April 23, 2023 15:30:05",
            "Log Type": "Delete Confirmation",
            "user_id": 12345,
            "Delete Target": "User Data",
            "delete_granularity": "individual records",
            "Sync confirmation": "Yes",
            "delete_method": "Secure Erase",
            "Multiple replication locations": "Yes",
            "Delete configuration": "Soft deletion, retention period of 30 days, deletion verified by third-party auditors",
            "Message": "The delete operation completed successfully. The data has been safely erased."
        }
        '''

        json_data4 = '''
        {
            "Time": "April 23, 2023 15:30:10",
            "Log Type": "Delete Operation",
            "user_id": 12345,
            "Delete Target": "Customer Data",
            "delete_granularity": "individual records",
            "Sync confirmation": "Yes",
            "delete_method": "Secure Erase",
            "Multiple replication locations": "Yes",
            "Delete configuration": "Soft deletion, retention period of 30 days, deletion verified by third-party auditors",
            "Message": "Individual records with user ID 12345 have been deleted from customer data. Adopting soft deletion method, the retention period is 30 days. The deletion operation has been verified by a third-party auditor."
        }
        '''

        # 连接到数据库
        cnx = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='123456',
            database='your_database_name'
        )
        cursor = cnx.cursor()

        # 将数据转换为SQL语句并插入到表中
        sql_template = "INSERT INTO your_table_name (log_type, user_id, delete_target, delete_granularity, sync_confirmation, delete_method, multiple_replication_locations, delete_configuration, message) VALUES ('{log_type}', '{user_id}', '{delete_target}', '{delete_granularity}', '{sync_confirmation}', '{delete_method}', '{multiple_replication_locations}', '{delete_configuration}', '{message}')"

        json_data_list = [json_data1, json_data2, json_data3, json_data4]

        for json_data in json_data_list:
            data = json.loads(json_data)
            log_type = data.get("Log Type")
            user_id = data.get("user_id")
            delete_target = data.get("Delete Target")
            delete_granularity = data.get("delete_granularity")
            sync_confirmation = data.get("Sync confirmation")
            delete_method = data.get("delete_method")
            multiple_replication_locations = data.get("Multiple replication locations")
            delete_configuration = data.get("Delete configuration")
            message = data.get("Message", "")

            # 构建SQL语句
            sql = sql_template.format(log_type=log_type, user_id=user_id, delete_target=delete_target,
                                      delete_granularity=delete_granularity, sync_confirmation=sync_confirmation,
                                      delete_method=delete_method,
                                      multiple_replication_locations=multiple_replication_locations,
                                      delete_configuration=delete_configuration, message=message)

            # 执行SQL语句
            cursor.execute(sql)

        # 提交事务并关闭连接
        cnx.commit()
        cursor.close()
        cnx.close()

        msg = "Data inserted into MySQL table"
        return msg

    return 'Method Not Allowed', 405

if __name__ == '__main__':
    app.run()
