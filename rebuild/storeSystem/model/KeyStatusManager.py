import mysql.connector
from mysql.connector import Error
import json
import time
import threading

class KeyStatusManager:
    def __init__(self, db_config):
        """初始化时连接到数据库，并检查 KeyStatus 表是否存在，如果不存在则创建"""
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
        """创建 KeyStatus 表"""
        try:
            cursor = self.connection.cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS KeyStatus (
                infoID VARCHAR(255) PRIMARY KEY,
                KeyStatusMethod VARCHAR(255) NOT NULL
            );
            """
            cursor.execute(create_table_query)
            self.connection.commit()
        except Error as e:
            print(f"Error creating table: {e}")

    def add_record(self, infoID, KeyStatusMethod):
        """向 KeyStatus 表添加记录"""
        try:
            cursor = self.connection.cursor()
            insert_query = "INSERT INTO KeyStatus (infoID, KeyStatusMethod) VALUES (%s, %s)"
            cursor.execute(insert_query, (infoID, KeyStatusMethod))
            self.connection.commit()
        except Error as e:
            print(f"Error adding record: {e}")

    def update_record(self, infoID, new_KeyStatusMethod):
        """更新 KeyStatus 表中的记录"""
        try:
            cursor = self.connection.cursor()
            update_query = "UPDATE KeyStatus SET KeyStatusMethod = %s WHERE infoID = %s"
            cursor.execute(update_query, (new_KeyStatusMethod, infoID))
            self.connection.commit()
        except Error as e:
            print(f"Error updating record: {e}")

    def delete_record(self, infoID):
        """从 KeyStatus 表中删除记录"""
        try:
            cursor = self.connection.cursor()
            delete_query = "DELETE FROM KeyStatus WHERE infoID = %s"
            cursor.execute(delete_query, (infoID,))
            self.connection.commit()
        except Error as e:
            print(f"Error deleting record: {e}")

    def read_record(self, infoID):
        """从 KeyStatus 表中读取记录"""
        try:
            cursor = self.connection.cursor()
            query = "SELECT KeyStatusMethod FROM KeyStatus WHERE infoID = %s"
            cursor.execute(query, (infoID,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
        except Error as e:
            print(f"Error reading record: {e}")

    def close_connection(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()

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

# 使用示例
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'plain_db'
}

# 创建 KeyStatusManager 实例
ksm = KeyStatusManager(db_config)

# 添加记录
ksm.add_record("9w0x1y2z3a4b", "Centralized")

# 更新记录
ksm.update_record("9w0x1y2z3a4b", "Distributed")

# 读取记录
key_storage_method = ksm.read_record("9w0x1y2z3a4b")
print(key_storage_method)

# 删除记录
ksm.delete_record("9w0x1y2z3a4b")

# 关闭数据库连接
ksm.close_connection()
