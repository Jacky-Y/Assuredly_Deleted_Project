from flask import Flask, request
import json
import mysql.connector

app = Flask(__name__)

@app.route('/delete', methods=['POST'])
def analyse():
    if request.method == 'POST':
        #data = request.get_data()
        #json_data = json.loads(data.decode("utf-8"))
        
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

        # 解析JSON数据
        time = json_data.get("Time")
        log_type = json_data.get("Log Type")
        user_id = json_data.get("user_id")
        delete_target = json_data.get("Delete Target")
        delete_granularity = json_data.get("delete_granularity")
        sync_confirmation = json_data.get("Sync confirmation")
        delete_method = json_data.get("delete_method")
        replication_locations = json_data.get("Multiple replication locations")
        delete_configuration = json_data.get("Delete configuration")
        message = json_data.get("Message")

        # 连接到数据库
        cnx = mysql.connector.connect(
            host='127.0.0.1',
            user='admin',
            password='123456',
            database='mysqltest'
        )
        cursor = cnx.cursor()

        # 创建 delete logs table
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS `delete_logs_table` (
          `Time` VARCHAR(100) NOT NULL,
          `Log Type` VARCHAR(100) NOT NULL,
          `user_id` VARCHAR(100) NOT NULL,
          `Delete Target` VARCHAR(100) NOT NULL,
          `delete_granularity` VARCHAR(100) NOT NULL,
          `Sync confirmation` VARCHAR(100) NOT NULL,
          `delete_method` VARCHAR(100) NOT NULL,
          `Multiple replication locations` VARCHAR(100) NOT NULL,
          `Delete configuration` VARCHAR(100) NOT NULL,
          `Message` VARCHAR(100) NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        '''
        cursor.execute(create_table_query)

        # 构建插入SQL语句
        insert_query = '''
        INSERT INTO `delete_logs_table` (`Time`, `Log Type`, `user_id`, `Delete Target`, `delete_granularity`,
        `Sync confirmation`, `delete_method`, `Multiple replication locations`, `Delete configuration`, `Message`)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        values = (time, log_type, user_id, delete_target, delete_granularity, sync_confirmation, delete_method,
                  replication_locations, delete_configuration, message)

        # 执行插入操作
        cursor.execute(insert_query, values)

        # 提交事务并关闭连接
        cnx.commit()
        cursor.close()
        cnx.close()

        return 'Data inserted successfully.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
