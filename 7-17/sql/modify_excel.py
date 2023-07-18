import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# 读取xlsx文件
df = pd.read_excel('infoauthset_datageneration.xlsx', engine='openpyxl')

# 删除指定列
df = df.drop(columns=['fromcompany', 'tocompany', 'rowcompany'])

# 只保留相同InfoID的第一行
df = df.drop_duplicates(subset='InfoID', keep='first')

# 新增六个列，生成随机值
df['deleteDupInfoID'] = "server1" + df['InfoID'].astype(str)
df['infoType'] = 1
df['infoOwner'] = np.random.choice(["mike","mary","amy"], df.shape[0])
df['infoCreator'] = np.random.choice(["mike","mary","amy"], df.shape[0])

# 生成随机日期
start_date = datetime(2020, 1, 1)
end_date = datetime(2022, 12, 31)
date_generated = [start_date + timedelta(days=x) for x in range(0, (end_date-start_date).days)]
df['infoCreateTime'] = [random.choice(date_generated).strftime("%Y-%m-%d %H:%M:%S") for _ in range(df.shape[0])]

df['infoCreateLoc'] = np.random.choice(["Beijing","Shanghai","Wuhan"], df.shape[0])

# 保存结果到新的Excel文件
df.to_excel('server1.xlsx', index=False)
