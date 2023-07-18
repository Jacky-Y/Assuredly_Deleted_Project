import mysql.connector

# 连接到数据库
cnx = mysql.connector.connect(
    host='localhost',      # 数据库主机地址
    user='deletion_root',  # 数据库用户名
    password='123456',  # 数据库密码
    database='deletion_db'   # 数据库名称
)

# 创建游标对象
cursor = cnx.cursor()

# 执行查询语句
query = "SELECT 1"
cursor.execute(query)

# 获取查询结果
result = cursor.fetchall()

# 处理查询结果
for row in result:
    print(row)

# 关闭游标和数据库连接
cursor.close()
cnx.close()
