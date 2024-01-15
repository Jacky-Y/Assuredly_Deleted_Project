import mysql.connector
from mysql.connector import Error
import json
import csv
import subprocess
import os
import datetime

class DeleteInfoModel:
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
                CREATE TABLE IF NOT EXISTS DeleteInfo (
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
                    usedTime VARCHAR(255),
                    Success BOOLEAN,
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
        Adds a new record to the DeleteInfo table.
        """
        try:
            cursor = self.conn.cursor()
            add_query = """
            INSERT INTO DeleteInfo (
                systemID, systemIP, mainCMD, subCMD, evidenceID, msgVersion, 
                submittime, infoID, status, title, abstract, keyWords, 
                category, infoType, deletePerformer, deletePerformTime, 
                deleteDupinfoID, deleteInstruction, deleteControlSet, deleteAlg, 
                deleteAlgParam, deleteLevel, pathtree, affairsID, userID, 
                classification_info, deleteMethod, deleteGranularity, deleteKeyinfoID, 
                dataHash, datasign, isRoot,usedTime,Success
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                %s, %s, %s,%s
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
                record['isRoot'],
                record['usedTime'],
                record['Success'],
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
            query = "SELECT * FROM DeleteInfo WHERE infoID = %s"
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
            query = "SELECT * FROM DeleteInfo WHERE infoID = %s and affairsID = %s"
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
            query = "SELECT * FROM DeleteInfo WHERE submittime BETWEEN %s AND %s"
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
            update_query = f"UPDATE DeleteInfo SET {update_parts} WHERE evidenceID = %s AND infoID = %s"

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
            delete_query = "DELETE FROM DeleteInfo WHERE evidenceID = %s AND infoID = %s"
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
            delete_query = "DELETE FROM DeleteInfo WHERE submittime BETWEEN %s AND %s"
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
            delete_query = "DELETE FROM DeleteInfo"
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
            INSERT INTO DeleteInfo (
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
            base_query = "SELECT * FROM DeleteInfo WHERE"
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
            FROM DeleteInfo
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

    def success_ratio(self):
        """
        Calculate the ratio of records where success is 1.
        """
        query = "SELECT COUNT(*) AS total, SUM(Success) AS success_count FROM DeleteInfo"
        cursor = self.conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        total, success_count = result
        return success_count / total if total > 0 else 0

    def success_ratio_with_deleteKeyinfoID(self):
        """
        Calculate the ratio of records where deleteKeyinfoID is not 'null' and success is 1,
        compared to all records where deleteKeyinfoID is not 'null'.
        """
        # Query to count all records where deleteKeyinfoID is not 'null'
        total_query = "SELECT COUNT(*) FROM DeleteInfo WHERE deleteKeyinfoID != 'null'"
        # Query to count records where deleteKeyinfoID is not 'null' and Success is 1
        success_query = "SELECT COUNT(*) FROM DeleteInfo WHERE deleteKeyinfoID != 'null' AND Success = 1"

        cursor = self.conn.cursor()

        # Execute total_query
        cursor.execute(total_query)
        total_count = cursor.fetchone()[0]

        # Execute success_query
        cursor.execute(success_query)
        success_count = cursor.fetchone()[0]

        cursor.close()

        # Calculate the ratio
        return success_count / total_count if total_count > 0 else 1

    def average_used_time(self):
        """
        Calculate the average used time of all records in seconds.
        """
        query = "SELECT usedTime FROM DeleteInfo"
        cursor = self.conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        total_time = datetime.timedelta()
        count = 0

        for (used_time,) in results:
            if used_time:
                time_parts = used_time.split(':')
                hours, minutes = int(time_parts[0]), int(time_parts[1])
                seconds, microseconds = map(int, time_parts[2].split('.'))
                total_time += datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds, microseconds=microseconds)
                count += 1

        average_time_seconds = (total_time.total_seconds() / count) if count > 0 else 0
        # Round to 4 decimal places
        return round(average_time_seconds, 4)

# Example usage
# You need to replace 'host', 'user', 'password', and 'database' with your actual database credentials



       

    
if __name__=="__main__":
    deleteinfomodel=DeleteInfoModel("127.0.0.1","root","123456","combinedLog")
    print("Success Ratio:", deleteinfomodel.success_ratio())
    print("Success Ratio with deleteKeyinfoID:", deleteinfomodel.success_ratio_with_deleteKeyinfoID())
    print("Average Used Time:", deleteinfomodel.average_used_time())