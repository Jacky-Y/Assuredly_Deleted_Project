import mysql.connector

# 创建数据库连接
cnx = mysql.connector.connect(
    host='localhost',
    user='dup_root',
    password='123456',
    database='dup_db'
)

cursor = cnx.cursor()

# 创建表
create_table_query = """
CREATE TABLE duplication_info (
    infoID VARCHAR(255),
    dbname VARCHAR(255),
    deleteDupInfoID VARCHAR(255)
)
"""

cursor.execute(create_table_query)

cnx.commit()
cnx.close()
