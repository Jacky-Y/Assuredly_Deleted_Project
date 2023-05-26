# sql="UPDATE Person SET {any} = '' WHERE id = '{id}' "

# print(sql)
import requests

# delete_list是包含要更新的列名的列表
delete_list = ['column1', 'column2', 'column3']

# 假设 id 是要更新的记录的 ID
id = '123'

# 构建 SET 子句的部分
set_clause = ', '.join([f"{column} = ''" for column in delete_list])

# 构建完整的 SQL 语句
sql = f"UPDATE Person SET {set_clause} WHERE id = '{id}'"

print(sql)

data = {
    'command': sql
}

urls = ['127.0.0.2', '127.0.0.3', '127.0.0.4']

print(data.get("command"))

# for url in urls:
#     response = requests.post(url, data=data)
#     print(f"Response from {url}: {response.text}")

