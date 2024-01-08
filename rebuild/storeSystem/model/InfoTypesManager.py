import mysql.connector
from mysql.connector import Error
import json

class InfoTypesManager:
    def __init__(self, db_config):
        """初始化时连接到数据库，并检查 InfoTypes 表是否存在，如果不存在则创建"""
        self._json_data = None  # 私有变量，用于存储从 JSON 文件读取的数据
        self.db_config = db_config
        self.connection = None
        try:
            self.connection = mysql.connector.connect(**db_config)
            self.create_table()
        except Error as e:
            print(f"Error connecting to MySQL: {e}")

    def create_table(self):
        """创建 InfoTypes 表"""
        try:
            cursor = self.connection.cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS InfoTypes (
                infoID VARCHAR(255) PRIMARY KEY,
                InfoTypes JSON NOT NULL
            );
            """
            cursor.execute(create_table_query)
            self.connection.commit()
        except Error as e:
            print(f"Error creating table: {e}")

    def add_record(self, infoID, infoTypes):
        """向 InfoTypes 表添加记录"""
        try:
            cursor = self.connection.cursor()
            insert_query = "INSERT INTO InfoTypes (infoID, InfoTypes) VALUES (%s, %s)"
            infoTypes_json = json.dumps(infoTypes)  # 将列表转换为 JSON 字符串
            cursor.execute(insert_query, (infoID, infoTypes_json))
            self.connection.commit()
        except Error as e:
            print(f"Error adding record: {e}")

    def update_record(self, infoID, new_infoTypes):
        """更新 InfoTypes 表中的记录"""
        try:
            cursor = self.connection.cursor()
            update_query = "UPDATE InfoTypes SET InfoTypes = %s WHERE infoID = %s"
            new_infoTypes_json = json.dumps(new_infoTypes)  # 将列表转换为 JSON 字符串
            cursor.execute(update_query, (new_infoTypes_json, infoID))
            self.connection.commit()
        except Error as e:
            print(f"Error updating record: {e}")

    def delete_record(self, infoID):
        """从 InfoTypes 表中删除记录"""
        try:
            cursor = self.connection.cursor()
            delete_query = "DELETE FROM InfoTypes WHERE infoID = %s"
            cursor.execute(delete_query, (infoID,))
            self.connection.commit()
        except Error as e:
            print(f"Error deleting record: {e}")

    def read_record(self, infoID):
        """从 InfoTypes 表中读取记录"""
        try:
            cursor = self.connection.cursor()
            query = "SELECT * FROM InfoTypes WHERE infoID = %s"
            cursor.execute(query, (infoID,))
            result = cursor.fetchone()
            if result:
                return {'infoID': result[0], 'InfoTypes': json.loads(result[1])}
            else:
                return None
        except Error as e:
            print(f"Error reading record: {e}")

    def get_infoTypes(self, infoID):
        """获取指定 infoID 对应的 infoTypes 列表"""
        try:
            cursor = self.connection.cursor()
            query = "SELECT InfoTypes FROM InfoTypes WHERE infoID = %s"
            cursor.execute(query, (infoID,))
            result = cursor.fetchone()
            if result:
                # 解析 JSON 字符串为列表并返回
                return json.loads(result[0])
            else:
                return None  # 如果没有找到记录，返回 None
        except Error as e:
            print(f"Error retrieving infoTypes: {e}")
            return None

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

    # 创建 InfoTypesManager 实例
    itm = InfoTypesManager(db_config)

    # 添加记录
    itm.add_record("1a2b3c4d5e6f", ["Name", "Gender", "Phone"])

    # # 更新记录
    # itm.update_record("1a2b3c4d5e6f", ["Name", "Email"])

    # # 删除记录
    # itm.delete_record("1a2b3c4d5e6f")

    # 读取记录
    record = itm.read_record("1a2b3c4d5e6f")
    print(record)
    print(type(record))


    #直接获取列表
    # 获取特定 infoID 的 infoTypes 列表
    infoTypes_list = itm.get_infoTypes("1a2b3c4d5e6f")
    print(infoTypes_list)
    print(type(infoTypes_list))

    # 关闭数据库连接
    itm.close_connection()
