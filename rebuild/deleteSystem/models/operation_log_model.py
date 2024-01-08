import mysql.connector
from mysql.connector import Error
import json
import csv
import subprocess
import os

class OperationLogModel:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.conn = None
        self._init_db()

    def _init_db(self):
        """
        Initialize the database connection and create the table if it does not exist.
        """
        try:
            # Connect to the MySQL database
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )

            # Check if connection was successful
            if self.conn.is_connected():
                print("Successfully connected to MySQL database")

                # Create table if it does not exist
                create_table_query = """
                CREATE TABLE IF NOT EXISTS OperationLog (
                    systemID VARCHAR(255),
                    systemIP VARCHAR(255),
                    mainCMD INT,
                    subCMD INT,
                    evidenceID VARCHAR(128) NOT NULL,
                    msgVersion INT,
                    submittime DATETIME,
                    infoID VARCHAR(128) NOT NULL,
                    status VARCHAR(255),
                    title VARCHAR(255),
                    abstract VARCHAR(1000),
                    keyWords VARCHAR(255),
                    category VARCHAR(255),
                    infoType INT,
                    deletePerformer VARCHAR(255),
                    deletePerformTime DATETIME,
                    deleteDupinfoID VARCHAR(1000),
                    deleteInstruction VARCHAR(1000),
                    deleteControlSet VARCHAR(1000),
                    deleteAlg INT,
                    deleteAlgParam VARCHAR(255),
                    deleteLevel INT,
                    pathtree VARCHAR(1000),
                    affairsID VARCHAR(255),
                    userID VARCHAR(255),
                    classification_info VARCHAR(1000),
                    deleteMethod VARCHAR(255),
                    deleteGranularity VARCHAR(255),
                    deleteKeyinfoID VARCHAR(1000),
                    dataHash VARCHAR(255),
                    datasign VARCHAR(255),
                    isRoot BOOLEAN,
                    PRIMARY KEY (evidenceID, infoID)
                )
                """
                cursor = self.conn.cursor()
                cursor.execute(create_table_query)
                cursor.close()
        except Error as e:
            print(f"An error occurred while connecting to MySQL: {e}")
            raise

    # Remember to add methods for adding, retrieving, updating, and deleting records.
    # Also, remember to handle database disconnection.
    def add_record(self, record):
        """
        Adds a new record to the OperationLog table.
        """
        try:
            cursor = self.conn.cursor()
            add_query = """
            INSERT INTO OperationLog (
                systemID, systemIP, mainCMD, subCMD, evidenceID, msgVersion, 
                submittime, infoID, status, title, abstract, keyWords, 
                category, infoType, deletePerformer, deletePerformTime, 
                deleteDupinfoID, deleteInstruction, deleteControlSet, deleteAlg, 
                deleteAlgParam, deleteLevel, pathtree, affairsID, userID, 
                classification_info, deleteMethod, deleteGranularity, deleteKeyinfoID, 
                dataHash, datasign, isRoot
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                %s, %s
            )
            """

            # Serialize nested JSON objects
            record['data']['deleteDupinfoID'] = json.dumps(record['data']['deleteDupinfoID'])
            record['data']['deleteInstruction'] = json.dumps(record['data']['deleteInstruction'])
            record['data']['pathtree'] = json.dumps(record['data']['pathtree'])
            record['data']['classification_info'] = json.dumps(record['data']['classification_info'])
            record['data']['deleteKeyinfoID'] = json.dumps(record['data']['deleteKeyinfoID'])

            # Prepare data tuple
            data_tuple = (
                record['systemID'], 
                record['systemIP'], 
                record['mainCMD'], 
                record['subCMD'], 
                record['evidenceID'], 
                record['msgVersion'], 
                record['submittime'], 
                record['data']['infoID'], 
                record['data']['status'], 
                record['data']['title'], 
                record['data']['abstract'], 
                record['data']['keyWords'], 
                record['data']['category'], 
                record['data']['infoType'], 
                record['data']['deletePerformer'], 
                record['data']['deletePerformTime'], 
                record['data']['deleteDupinfoID'], 
                record['data']['deleteInstruction'], 
                record['data']['deleteControlSet'], 
                record['data']['deleteAlg'], 
                record['data']['deleteAlgParam'], 
                record['data']['deleteLevel'], 
                record['data']['pathtree'], 
                record['data']['affairsID'], 
                record['data']['userID'], 
                record['data']['classification_info'], 
                record['data']['deleteMethod'], 
                record['data']['deleteGranularity'], 
                record['data']['deleteKeyinfoID'], 
                record['dataHash'], 
                record['datasign'],
                record['isRoot']
            )

            # Debug: Print the data tuple and its length
            # print("Data tuple:", data_tuple)
            # print("Number of elements in data tuple:", len(data_tuple))

            # Execute query
            cursor.execute(add_query, data_tuple)
            self.conn.commit()
            cursor.close()
        except mysql.connector.Error as e:
            if 'Duplicate entry' in str(e) and 'for key \'PRIMARY\'' in str(e):
                print("操作日志的主键重复，无法添加重复的记录。")
            else:
                print(f"An error occurred while inserting the record: {e}")
                raise  # 继续向上抛出非主键重复的异常

    def get_records_by_infoID(self, infoID):
        try:
            cursor = self.conn.cursor(dictionary=True)
            query = "SELECT * FROM OperationLog WHERE infoID = %s"
            cursor.execute(query, (infoID,))
            rows = cursor.fetchall()
            cursor.close()

            # 将查询结果转换为 JSON 列表
            return json.dumps(rows, default=str)  # 使用 default=str 以处理日期时间对象
        except Error as e:
            print(f"An error occurred while querying the record: {e}")
            raise
    
    def get_records_by_infoID_affairsID(self, infoID,affairsID):
        try:
            cursor = self.conn.cursor(dictionary=True)
            query = "SELECT * FROM OperationLog WHERE infoID = %s and affairsID = %s"
            cursor.execute(query, (infoID,affairsID,))
            rows = cursor.fetchall()
            cursor.close()

            # 将查询结果转换为 JSON 列表
            return json.dumps(rows, default=str)  # 使用 default=str 以处理日期时间对象
        except Error as e:
            print(f"An error occurred while querying the record: {e}")
            raise

    def get_records_by_time_period(self, start_time, end_time):
        try:
            cursor = self.conn.cursor(dictionary=True)
            query = "SELECT * FROM OperationLog WHERE submittime BETWEEN %s AND %s"
            cursor.execute(query, (start_time, end_time))
            rows = cursor.fetchall()
            cursor.close()

            # 将查询结果转换为 JSON 列表
            return json.dumps(rows, default=str)  # 使用 default=str 以处理日期时间对象
        except Error as e:
            print(f"An error occurred while querying the record: {e}")
            raise

    # evidenceID 和 infoID 是用来定位要更新的记录的。
    # update_data 是一个字典，包含要更新的字段及其新值。例如，{'status': '已处理', 'title': '更新后的标题'}。
    # 方法构建了一个动态的 SQL 更新语句，根据 update_data 中的键和值来设置字段。
    # 使用 cursor.execute 执行更新操作，然后提交更改。
    # 如果没有记录被更新，将打印 "No record updated"；否则，打印更新的记录数。

    def update_record(self, evidenceID, infoID, update_data):
        try:
            cursor = self.conn.cursor()

            # 准备更新的字段和值
            update_parts = ", ".join([f"{key} = %s" for key in update_data])
            update_values = list(update_data.values())

            # 构建更新 SQL 语句
            update_query = f"UPDATE OperationLog SET {update_parts} WHERE evidenceID = %s AND infoID = %s"

            # 添加 evidenceID 和 infoID 到参数列表
            update_values.extend([evidenceID, infoID])

            # 执行更新操作
            cursor.execute(update_query, tuple(update_values))
            self.conn.commit()
            cursor.close()

            if cursor.rowcount == 0:
                print("No record updated")
            else:
                print(f"{cursor.rowcount} record(s) updated successfully")
        except Error as e:
            print(f"An error occurred while updating the record: {e}")
            raise

    def delete_record_by_primary_key(self, evidenceID, infoID):
        try:
            cursor = self.conn.cursor()
            delete_query = "DELETE FROM OperationLog WHERE evidenceID = %s AND infoID = %s"
            cursor.execute(delete_query, (evidenceID, infoID))
            self.conn.commit()

            if cursor.rowcount == 0:
                print("No record deleted")
            else:
                print(f"{cursor.rowcount} record(s) deleted successfully")

            cursor.close()
        except Error as e:
            print(f"An error occurred while deleting the record: {e}")
            raise

    def delete_records_by_time_period(self, start_time, end_time):
        try:
            cursor = self.conn.cursor()
            delete_query = "DELETE FROM OperationLog WHERE submittime BETWEEN %s AND %s"
            cursor.execute(delete_query, (start_time, end_time))
            self.conn.commit()

            if cursor.rowcount == 0:
                print("No records deleted")
            else:
                print(f"{cursor.rowcount} record(s) deleted successfully")

            cursor.close()
        except Error as e:
            print(f"An error occurred while deleting records: {e}")
            raise

    def delete_all_records(self):
        try:
            cursor = self.conn.cursor()
            delete_query = "DELETE FROM OperationLog"
            cursor.execute(delete_query)
            self.conn.commit()

            if cursor.rowcount == 0:
                print("No records to delete")
            else:
                print(f"All {cursor.rowcount} record(s) deleted successfully")

            cursor.close()
        except Error as e:
            print(f"An error occurred while deleting all records: {e}")
            raise

    def add_records_batch(self, records):
        try:
            cursor = self.conn.cursor()
            insert_query = """
            INSERT INTO OperationLog (
                systemID, systemIP, mainCMD, subCMD, evidenceID, msgVersion, 
                submittime, infoID, status, title, abstract, keyWords, 
                category, infoType, deletePerformer, deletePerformTime, 
                deleteDupinfoID, deleteInstruction, deleteControlSet, deleteAlg, 
                deleteAlgParam, deleteLevel, pathtree, affairsID, userID, 
                classification_info, deleteMethod, deleteGranularity, deleteKeyinfoID, 
                dataHash, datasign, isRoot
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                %s, %s
            )
            """

            values = []
            for record in records:
                # 序列化嵌套 JSON 对象
                record['data']['deleteDupinfoID'] = json.dumps(record['data']['deleteDupinfoID'])
                record['data']['deleteInstruction'] = json.dumps(record['data']['deleteInstruction'])
                record['data']['pathtree'] = json.dumps(record['data']['pathtree'])
                record['data']['classification_info'] = json.dumps(record['data']['classification_info'])
                record['data']['deleteKeyinfoID'] = json.dumps(record['data']['deleteKeyinfoID'])

                # 准备要插入的数据元组
                row = (
                record['systemID'], 
                record['systemIP'], 
                record['mainCMD'], 
                record['subCMD'], 
                record['evidenceID'], 
                record['msgVersion'], 
                record['submittime'], 
                record['data']['infoID'], 
                record['data']['status'], 
                record['data']['title'], 
                record['data']['abstract'], 
                record['data']['keyWords'], 
                record['data']['category'], 
                record['data']['infoType'], 
                record['data']['deletePerformer'], 
                record['data']['deletePerformTime'], 
                record['data']['deleteDupinfoID'], 
                record['data']['deleteInstruction'], 
                record['data']['deleteControlSet'], 
                record['data']['deleteAlg'], 
                record['data']['deleteAlgParam'], 
                record['data']['deleteLevel'], 
                record['data']['pathtree'], 
                record['data']['affairsID'], 
                record['data']['userID'], 
                record['data']['classification_info'], 
                record['data']['deleteMethod'], 
                record['data']['deleteGranularity'], 
                record['data']['deleteKeyinfoID'], 
                record['dataHash'], 
                record['datasign'], 
                record['isRoot']
            )
                values.append(row)

            # 执行批量插入
            cursor.executemany(insert_query, values)
            self.conn.commit()
            cursor.close()
            print(f"{len(records)} records inserted successfully")
        except mysql.connector.Error as e:
            print(f"An error occurred while inserting records: {e}")
            raise

    def advanced_search(self, search_params):
        try:
            cursor = self.conn.cursor(dictionary=True)
            base_query = "SELECT * FROM OperationLog WHERE"
            conditions = []
            values = []

            # 构建搜索条件
            for key, value in search_params.items():
                if value:
                    conditions.append(f"{key} LIKE %s")
                    values.append(f"%{value}%")

            query = f"{base_query} {' AND '.join(conditions)}"
            cursor.execute(query, tuple(values))
            rows = cursor.fetchall()
            cursor.close()

            return json.dumps(rows, default=str)
        except Error as e:
            print(f"An error occurred while searching: {e}")
            raise

    def get_statistics(self, start_time, end_time, avg_field):
        try:
            cursor = self.conn.cursor()
            query = """
            SELECT COUNT(*) as record_count, AVG({}) as average_value
            FROM OperationLog
            WHERE submittime BETWEEN %s AND %s
            """.format(avg_field)
            cursor.execute(query, (start_time, end_time))
            result = cursor.fetchone()
            cursor.close()

            return {
                "record_count": result[0],
                "average_value_of_{}".format(avg_field): result[1]
            }
        except Error as e:
            print(f"An error occurred while getting statistics: {e}")
            raise

    def export_data_to_csv(self, query, csv_file_path):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()

            # 获取列名
            column_names = [i[0] for i in cursor.description]

            # 写入 CSV
            with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(column_names)
                writer.writerows(rows)

            print(f"Data exported successfully to {csv_file_path}")
        except Error as e:
            print(f"An error occurred while exporting data: {e}")
            raise



    def backup_database(self, backup_path, db_name):
        try:
            # 构建备份命令
            backup_command = f"mysqldump -u {self.user} -p{self.password} {db_name} > {backup_path}"

            # 执行备份命令
            process = subprocess.Popen(backup_command, shell=True)
            process.wait()

            if process.returncode == 0:
                print(f"Database backup successful. File saved as {backup_path}")
            else:
                print("Database backup failed.")
        except Exception as e:
            print(f"An error occurred while backing up the database: {e}")

    def restore_database(self, backup_path, db_name):
        try:
            # 构建恢复命令
            restore_command = f"mysql -u {self.user} -p{self.password} {db_name} < {backup_path}"

            # 执行恢复命令
            process = subprocess.Popen(restore_command, shell=True)
            process.wait()

            if process.returncode == 0:
                print("Database restore successful.")
            else:
                print("Database restore failed.")
        except Exception as e:
            print(f"An error occurred while restoring the database: {e}")

    def open_connection(self):
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            print("Database connection successfully opened.")
        except mysql.connector.Error as e:
            print(f"Error opening database connection: {e}")
            raise

    def close_connection(self):
        if self.conn.is_connected():
            self.conn.close()
            print("Database connection closed.")

    def format_log(self,x):
        y=json.loads(x)
        final_list=[]
        for original_dict in y:

            del original_dict['isRoot']
            del original_dict['pathtree']
            del original_dict['status']
            

            # 指定要保留在外层的键
            keys_to_keep = ["dataHash",
                            "datasign",
                            "evidenceID",
                            "mainCMD",
                            "msgVersion",
                            "subCMD",
                            "submittime",
                            "systemID",
                            "systemIP"]

            # 创建嵌套字典，其中包含除 keys_to_keep 之外的所有键
            nested_dict = {key: value for key, value in original_dict.items() if key not in keys_to_keep}

            # 创建最终的字典
            final_dict = {
                "data": nested_dict
            }

            # 将要保留在外层的键添加到最终的字典中
            for key in keys_to_keep:
                if key in original_dict:
                    final_dict[key] = original_dict[key]

            final_list.append(final_dict)
        return final_list
    






#数据库对象使用实例

if __name__=="__main__":

    #############初始化###############
    db_model = OperationLogModel("127.0.0.1", "root", "123456", "assured_deletion")



    #############增###############
    # # 文件路径
    # file_path = './log/0c1d2e3f4g5h_16881233.json'

    # # 从文件中读取 JSON 数据
    # with open(file_path, 'r', encoding='utf-8') as file:
    #     data = json.load(file)


    # # 此时，data 是一个包含 JSON 数据的 Python 字典
    # print(data)

    # db_model.add_record(data)


    #############查###############
    temp=db_model.get_records_by_infoID_affairsID('0c1d2e3f4g5h','16881233')
    data = db_model.format_log(temp)
    print(data)


    # x=db_model.get_records_by_infoID('0c1d2e3f4g5h')

    # print(db_model.format_log(x))
    # y=json.loads(x)
    # original_dict =y[0]

    # del original_dict['isRoot']
    # del original_dict['pathtree']
    # del original_dict['status']
    

    # # 指定要保留在外层的键
    # keys_to_keep = ["dataHash",
    #                 "datasign",
    #                 "evidenceID",
    #                 "mainCMD",
    #                 "msgVersion",
    #                 "subCMD",
    #                 "submittime",
    #                 "systemID",
    #                 "systemIP"]

    # # 创建嵌套字典，其中包含除 keys_to_keep 之外的所有键
    # nested_dict = {key: value for key, value in original_dict.items() if key not in keys_to_keep}

    # # 创建最终的字典
    # final_dict = {
    #     "data": nested_dict
    # }

    # # 将要保留在外层的键添加到最终的字典中
    # for key in keys_to_keep:
    #     if key in original_dict:
    #         final_dict[key] = original_dict[key]

    # print(final_dict)

    # with open('./log/mk.json', 'w', encoding='utf-8') as target_file:
    # # 使用 json.dump 将操作日志转换为 JSON 格式并保存
    #     json.dump(final_dict, target_file, ensure_ascii=False, indent=4)


    # # 定义要查询的时间段
    # start_time = "2024-01-01 00:00:00"  # 起始时间
    # end_time = "2024-01-07 23:59:59"    # 结束时间

    # # 使用 get_records_by_time_period 函数进行查询
    # result_json = db_model.get_records_by_time_period(start_time, end_time)

    # # 打印结果
    # print(result_json)


    #############改###############
    # # 假设 db_model 是 OperationLogModel 的实例

    # # 要更新的记录的标识符
    # evidenceID = "某个evidenceID"
    # infoID = "某个infoID"

    # # 要更新的数据
    # update_data = {
    #     'status': '已处理',
    #     'title': '更新后的标题'
    # }

    # # 调用更新方法
    # db_model.update_record(evidenceID, infoID, update_data)


    #############删###############
    # # 删除特定主键的记录
    # db_model.delete_record_by_primary_key("some_evidenceID", "some_infoID")

    # # 删除指定时间段的记录
    # db_model.delete_records_by_time_period("2024-01-01 00:00:00", "2024-01-07 23:59:59")

    # # 删除表中所有记录
    # db_model.delete_all_records()

    #############其他功能###############
    # # 高级搜索示例
    # search_params = {"title": "系统", "status": "已删除"}
    # search_result = db_model.advanced_search(search_params)
    # print(search_result)


    # # 统计和汇总示例
    # stats = db_model.get_statistics("2024-01-01 00:00:00", "2024-01-07 23:59:59", "mainCMD")
    # print(stats)

    # # 数据导出示例
    # export_query = "SELECT * FROM OperationLog"
    # db_model.export_data_to_csv(export_query, "operation_log_export.csv")


    # 使用示例

    # # 备份数据库
    # db_model.backup_database("/path/to/backup.sql", "your_database_name")

    # # 恢复数据库
    # db_model.restore_database("/path/to/backup.sql", "your_database_name")

    # # 开启和关闭数据库连接
    # db_model.open_connection()
    # # ... 执行数据库操作 ...
    # db_model.close_connection()



