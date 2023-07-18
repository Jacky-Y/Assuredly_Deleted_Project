import pandas as pd
import mysql.connector
from sqlalchemy import create_engine

# 读取excel文件
df = pd.read_excel('server1.xlsx', usecols=['InfoID'])

# 根据InfoID创建新的列
df_final = pd.DataFrame()
for server in range(1, 4):
    df_temp = df.copy()
    df_temp['dbname'] = f'server{server}'
    df_temp['deleteDupInfoID'] = df_temp['InfoID'].apply(lambda x: f'server{server}{x}')
    df_final = pd.concat([df_final, df_temp])

# 创建数据库连接
user = 'dup_root'
password = '123456'
host = 'localhost'
database = 'dup_db'
table_name = 'duplication_info'

engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}")
con = engine.connect()

# 将DataFrame中的数据写入MySQL数据库
df_final.to_sql(table_name, con, if_exists='append', index=False)

# 关闭数据库连接
con.close()
