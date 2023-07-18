import pandas as pd
from sqlalchemy import create_engine
import openyxl

# 创建MySQL数据库连接
engine = create_engine('mysql+mysqlconnector://server3_root:123456@127.0.0.1:3306/server3_db')

# 读取Excel文件
df = pd.read_excel('server3.xlsx', engine='openpyxl')

# 处理keyvalueset列，将其转换为字典，并将缺失的键填充为空字符串
def process_keyvalueset(value):
    data = {"idNumber": "", "gender": "", "height": "", "age": "", "nation": "", "phone": "", "bloodType": "",
            "occupation": "", "education": "", "marriage": "", "nativePlace": "", "currentAddress": ""}
    data.update(eval(value))
    return data

df_keyvalueset = df['keyvalueset'].apply(process_keyvalueset).apply(pd.Series)




# 合并原始DataFrame和提取的keyvalueset列
df = pd.concat([df.drop(['keyvalueset'], axis=1), df_keyvalueset], axis=1)

# 将数据插入到数据库
df.to_sql('personal_information', engine, if_exists='append', index=False)
