import mysql.connector
from mysql.connector import Error
import json
import ast
import time
import threading

class PlaintextLocationManager:
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
        """创建 PlaintextLocation 表"""
        try:
            cursor = self.connection.cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS PlaintextLocation (
                infoID VARCHAR(255) PRIMARY KEY,
                storageLocation JSON NOT NULL,
                FOREIGN KEY (infoID) REFERENCES EncryptionStatus(infoID) ON DELETE CASCADE
            );
            """
            cursor.execute(create_table_query)
            self.connection.commit()
        except Error as e:
            print(f"Error creating table: {e}")

    def add_record(self, infoID, storageLocation):
        """添加记录"""
        try:
            cursor = self.connection.cursor()
            insert_query = "INSERT INTO PlaintextLocation (infoID, storageLocation) VALUES (%s, %s)"
            storageLocation = json.dumps(storageLocation)  # 将列表转换为 JSON 字符串
            cursor.execute(insert_query, (infoID, storageLocation))
            self.connection.commit()
        except Error as e:
            print(f"Error adding record: {e}")

    def read_record(self, infoID):
        """读取记录"""
        try:
            cursor = self.connection.cursor()
            query = "SELECT * FROM PlaintextLocation WHERE infoID = %s"
            cursor.execute(query, (infoID,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error reading record: {e}")

    def update_record(self, infoID, storageLocation):
        """更新记录"""
        try:
            cursor = self.connection.cursor()
            update_query = "UPDATE PlaintextLocation SET storageLocation = %s WHERE infoID = %s"
            cursor.execute(update_query, (storageLocation, infoID))
            self.connection.commit()
        except Error as e:
            print(f"Error updating record: {e}")

    def delete_record(self, infoID):
        """删除记录"""
        try:
            cursor = self.connection.cursor()
            delete_query = "DELETE FROM PlaintextLocation WHERE infoID = %s"
            cursor.execute(delete_query, (infoID,))
            self.connection.commit()
        except Error as e:
            print(f"Error deleting record: {e}")

    def close_connection(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()

    def get_locations_list(self, infoID):
        """根据 infoID 获取存储位置列表"""
        try:
            cursor = self.connection.cursor()
            query = "SELECT storageLocation FROM PlaintextLocation WHERE infoID = %s"
            cursor.execute(query, (infoID,))
            result = cursor.fetchone()
            if result:
                # 解析存储位置字符串为列表
                result = json.loads(result[0])
                return  result
            else:
                return []  # 如果没有找到记录，返回空列表
        except Error as e:
            print(f"Error retrieving record: {e}")
            return []  # 在发生异常时返回空列表
        
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




# # 使用示例
# db_config = {
#     'host': 'localhost',
#     'user': 'username',
#     'password': 'password',
#     'database': 'your_database'
# }
# pl = PlaintextLocation(db_config)
# # 然后可以调用 pl.add_record(), pl.read_record() 等方法进行操作


if __name__=="__main__":


    # # JSON 数据
    # json_data = """
    # [
    #     {"infoID": "1a2b3c4d5e6f", "Locations": ["./c/1a2b3c4d5e6f.json", "./d/1a2b3c4d5e6f.json", "./e/1a2b3c4d5e6f.json"]},
    #     {"infoID": "2g3h4i5j6k7l", "Locations": ["./c/2g3h4i5j6k7l.json", "./d/2g3h4i5j6k7l.json"]},
    #     {"infoID": "3m4n5o6p7q8r", "Locations": ["./d/3m4n5o6p7q8r.json", "./e/3m4n5o6p7q8r.json", "./f/3m4n5o6p7q8r.json"]},
    #     {"infoID": "4s5t6u7v8w9x", "Locations": ["./e/4s5t6u7v8w9x.json", "./f/4s5t6u7v8w9x.json"]},
    #     {"infoID": "5y6z7a8b9c0d", "Locations": ["./f/5y6z7a8b9c0d.json", "./c/5y6z7a8b9c0d.json", "./d/5y6z7a8b9c0d.json"]},
    #     {"infoID": "6e7f8g9h0i1j", "Locations": ["./c/6e7f8g9h0i1j.json", "./e/6e7f8g9h0i1j.json"]},
    #     {"infoID": "7k8l9m0n1o2p", "Locations": ["./d/7k8l9m0n1o2p.json", "./e/7k8l9m0n1o2p.json", "./f/7k8l9m0n1o2p.json"]},
    #     {"infoID": "8q9r0s1t2u3v", "Locations": ["./e/8q9r0s1t2u3v.json", "./f/8q9r0s1t2u3v.json"]},
    #     {"infoID": "9w0x1y2z3a4b", "Locations": ["./f/9w0x1y2z3a4b.json", "./c/9w0x1y2z3a4b.json", "./d/9w0x1y2z3a4b.json"]},
    #     {"infoID": "0c1d2e3f4g5h", "Locations": ["./c/0c1d2e3f4g5h.json", "./d/0c1d2e3f4g5h.json"]}
    # ]
    # """

    # # 解析 JSON 数据
    # data = json.loads(json_data)


    #配置信息
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '123456',
        'database': 'plain_db'
    }

    # 创建 PlaintextLocation 实例
    pl = PlaintextLocationManager(db_config)

    # 添加记录
    pl.add_record("1a2b3c4d5e6f", ["Name", "Gender", "Phone"])

    # # 更新记录
    # itm.update_record("1a2b3c4d5e6f", ["Name", "Email"])

    # # 删除记录
    # itm.delete_record("1a2b3c4d5e6f")

    # 读取记录
    record = pl.get_locations_list("1a2b3c4d5e6f")
    print(record)
    print(type(record))



    # # 遍历数据并添加到数据库
    # for item in data:
    #     infoID = item['infoID']
    #     # 将 Locations 列表转换为字符串
    #     locations_str = ', '.join(item['Locations'])
    #     pl.add_record(infoID, locations_str)

    # pl 是已经创建的 PlaintextLocation 实例
    # locations = pl.get_locations_list("0364ae455c6f00cd")
    # print(locations)

    # print(type(locations))


    # 关闭数据库连接
    pl.close_connection()
