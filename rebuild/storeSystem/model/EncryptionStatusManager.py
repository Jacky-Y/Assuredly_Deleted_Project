import mysql.connector
from mysql.connector import Error
import json
import time
import threading

class EncryptionStatusManager:
    def __init__(self, db_config):
        """初始化时连接到数据库，并检查表是否存在，如果不存在则创建"""
        self._json_data = None  # 私有变量，用于存储从 JSON 文件读取的数据
        self.db_config = db_config
        self.connection = None
        self.keep_alive_thread = None
        try:
            self.connection = mysql.connector.connect(**db_config)
            self.create_table()
            self._start_keep_alive_thread()
        except Error as e:
            print(f"Error connecting to MySQL: {e}")


    def _start_keep_alive_thread(self):
        """启动保持数据库连接活跃的线程"""
        if self.keep_alive_thread is None or not self.keep_alive_thread.is_alive():
            self.keep_alive_thread = threading.Thread(target=self._keep_connection_alive, daemon=True)
            self.keep_alive_thread.start()

    def _keep_connection_alive(self):
        """定期执行简单查询以保持数据库连接活跃"""
        while True:
            try:
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchall()  # 确保读取所有结果
                cursor.close()
            except Error as e:
                print(f"Connection lost. Attempting to reconnect: {e}")
                try:
                    self.connection = mysql.connector.connect(**self.db_config)
                    if self.connection.is_connected():
                        print("Reconnected to MySQL database")
                except Error as reconnect_error:
                    print(f"Failed to reconnect: {reconnect_error}")
            time.sleep(100)  # 每5分钟执行一次

    def create_table(self):
        """创建 EncryptionStatus 表"""
        try:
            cursor = self.connection.cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS EncryptionStatus (
                infoID VARCHAR(255) PRIMARY KEY,
                isEncrypted BOOLEAN NOT NULL
            );
            """
            cursor.execute(create_table_query)
            self.connection.commit()
        except Error as e:
            print(f"Error creating table: {e}")

    def add_record(self, infoID, isEncrypted):
        """添加记录"""
        try:
            cursor = self.connection.cursor()
            insert_query = "INSERT INTO EncryptionStatus (infoID, isEncrypted) VALUES (%s, %s)"
            cursor.execute(insert_query, (infoID, isEncrypted))
            self.connection.commit()
        except Error as e:
            print(f"Error adding record: {e}")

    def read_record(self, infoID):
        """读取记录"""
        try:
            cursor = self.connection.cursor()
            query = "SELECT * FROM EncryptionStatus WHERE infoID = %s"
            cursor.execute(query, (infoID,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error reading record: {e}")

    def update_record(self, infoID, isEncrypted):
        """更新记录"""
        try:
            cursor = self.connection.cursor()
            update_query = "UPDATE EncryptionStatus SET isEncrypted = %s WHERE infoID = %s"
            cursor.execute(update_query, (isEncrypted, infoID))
            self.connection.commit()
        except Error as e:
            print(f"Error updating record: {e}")

    def delete_record(self, infoID):
        """删除记录"""
        try:
            cursor = self.connection.cursor()
            delete_query = "DELETE FROM EncryptionStatus WHERE infoID = %s"
            cursor.execute(delete_query, (infoID,))
            self.connection.commit()
        except Error as e:
            print(f"Error deleting record: {e}")

    def close_connection(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
    
    def get_encryption_status(self, infoID):
        """根据 infoID 获取加密状态"""
        try:
            cursor = self.connection.cursor()
            query = "SELECT isEncrypted FROM EncryptionStatus WHERE infoID = %s"
            cursor.execute(query, (infoID,))
            result = cursor.fetchone()
            if result is not None:
                # 返回加密状态
                return result[0]
            else:
                return None  # 如果没有找到记录，返回 None
        except Error as e:
            print(f"Error retrieving encryption status: {e}")
            return None  # 在发生异常时返回 None
        
    def load_json(self, file_path):
        """从给定路径读取 JSON 文件并存储到私有变量"""
        try:
            with open(file_path, 'r') as file:
                self._json_data = json.load(file)
        except Exception as e:
            print(f"Error reading JSON file: {e}")

    def get_info_from_json(self, infoID):
        """根据 infoID 从加载的 JSON 数据中获取信息"""
        if self._json_data is None:
            print("JSON data is not loaded.")
            return None

        return self._json_data.get(infoID)



if __name__=="__main__":



    # 假设 JSON 数据存储在 json_data 变量中
    json_data = """
    [
        {"infoID": "1a2b3c4d5e6f", "Status": "Plaintext"},
        {"infoID": "2g3h4i5j6k7l", "Status": "Plaintext"},
        {"infoID": "3m4n5o6p7q8r", "Status": "Plaintext"},
        {"infoID": "4s5t6u7v8w9x", "Status": "Plaintext"},
        {"infoID": "5y6z7a8b9c0d", "Status": "Plaintext"},
        {"infoID": "6e7f8g9h0i1j", "Status": "Plaintext"},
        {"infoID": "7k8l9m0n1o2p", "Status": "Plaintext"},
        {"infoID": "8q9r0s1t2u3v", "Status": "Plaintext"},
        {"infoID": "9w0x1y2z3a4b", "Status": "Encrypted"},
        {"infoID": "0c1d2e3f4g5h", "Status": "Encrypted"}
    ]
    """

    # 解析 JSON 数据
    data = json.loads(json_data)

    # 使用示例
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '123456',
        'database': 'plain_db'
    }

    # 创建 EncryptionStatus 实例
    es = EncryptionStatusManager(db_config)

    # 遍历数据并添加到数据库
    for item in data:
        infoID = item['infoID']
        isEncrypted = item['Status'] == 'Encrypted'
        es.add_record(infoID, isEncrypted)

    # 使用示例
    # es 是已经创建的 EncryptionStatus 实例
    encryption_status = es.get_encryption_status("1a2b3c4d5e6f")
    print(encryption_status)
    print(type(encryption_status))

    # 关闭数据库连接
    es.close_connection()
