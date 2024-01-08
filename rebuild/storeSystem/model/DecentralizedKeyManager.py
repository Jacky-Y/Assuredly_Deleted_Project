import json
import mysql.connector
from mysql.connector import Error

class DecentralizedKeyManager:
    def __init__(self, db_config):
        """初始化时连接到数据库，并检查 DecentralizedKey 表是否存在，如果不存在则创建"""
        self.db_config = db_config
        self.connection = None
        try:
            self.connection = mysql.connector.connect(**db_config)
            self.create_table()
        except Error as e:
            print(f"Error connecting to MySQL: {e}")

    def create_table(self):
        """创建 DecentralizedKey 表"""
        try:
            cursor = self.connection.cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS DecentralizedKey (
                infoID VARCHAR(255) PRIMARY KEY,
                Locations JSON NOT NULL
            );
            """
            cursor.execute(create_table_query)
            self.connection.commit()
        except Error as e:
            print(f"Error creating table: {e}")

    def add_record(self, infoID, locations):
        """向 DecentralizedKey 表添加记录"""
        try:
            cursor = self.connection.cursor()
            insert_query = "INSERT INTO DecentralizedKey (infoID, Locations) VALUES (%s, %s)"
            locations_json = json.dumps(locations)  # 将列表转换为 JSON 字符串
            cursor.execute(insert_query, (infoID, locations_json))
            self.connection.commit()
        except Error as e:
            print(f"Error adding record: {e}")

    def update_record(self, infoID, new_locations):
        """更新 DecentralizedKey 表中的记录"""
        try:
            cursor = self.connection.cursor()
            update_query = "UPDATE DecentralizedKey SET Locations = %s WHERE infoID = %s"
            new_locations_json = json.dumps(new_locations)  # 将列表转换为 JSON 字符串
            cursor.execute(update_query, (new_locations_json, infoID))
            self.connection.commit()
        except Error as e:
            print(f"Error updating record: {e}")

    def delete_record(self, infoID):
        """从 DecentralizedKey 表中删除记录"""
        try:
            cursor = self.connection.cursor()
            delete_query = "DELETE FROM DecentralizedKey WHERE infoID = %s"
            cursor.execute(delete_query, (infoID,))
            self.connection.commit()
        except Error as e:
            print(f"Error deleting record: {e}")

    def read_record(self, infoID):
        """从 DecentralizedKey 表中读取记录"""
        try:
            cursor = self.connection.cursor()
            query = "SELECT Locations FROM DecentralizedKey WHERE infoID = %s"
            cursor.execute(query, (infoID,))
            result = cursor.fetchone()
            if result:
                return json.loads(result[0])
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

if __name__=="__main__":

    # 使用示例
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '123456',
        'database': 'plain_db'
    }

    # 创建 DecentralizedKeyManager 实例
    dkm = DecentralizedKeyManager(db_config)

    # 添加记录
    dkm.add_record("0c1d2e3f4g5h", ["./c/0c1d2e3f4g5h_key.txt", "./d/0c1d2e3f4g5h_key.txt"])

    # 更新记录
    dkm.update_record("0c1d2e3f4g5h", ["./e/0c1d2e3f4g5h_key.txt", "./f/0c1d2e3f4g5h_key.txt"])

    # 读取记录
    locations = dkm.read_record("0c1d2e3f4g5h")
    print(locations)

    # 删除记录
    dkm.delete_record("0c1d2e3f4g5h")

    # 关闭数据库连接
    dkm.close_connection()
