import mysql.connector

# 创建数据库连接
cnx = mysql.connector.connect(
    host='127.0.0.1',
    user='mass_root',
    password='123456',
    database='mass_db'
)

cursor = cnx.cursor()

# 创建表
create_table_query = """
CREATE TABLE your_table_name (
    id VARCHAR(255),
    userid VARCHAR(255),
    fromcompany VARCHAR(255),
    tocompany VARCHAR(255),
    rowcompany VARCHAR(255),
    idNumber VARCHAR(255),
    gender VARCHAR(255),
    height VARCHAR(255),
    age VARCHAR(255),
    nation VARCHAR(255),
    phone VARCHAR(255),
    bloodType VARCHAR(255),
    occupation VARCHAR(255),
    education VARCHAR(255),
    marriage VARCHAR(255),
    nativePlace VARCHAR(255),
    currentAddress VARCHAR(255),
    PRIMARY KEY (id)
)
"""

cursor.execute(create_table_query)

cnx.commit()
cnx.close()
