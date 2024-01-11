import requests
import json
import csv
import subprocess
import os
import requests
import time
from operation_log_model import OperationLogModel

# log_data = {
#     "message": "Example log message",
#     "level": "INFO",
#     "timestamp": "2021-01-01T12:00:00"
# }

# response = requests.post("http://localhost:5555/log", json=log_data)

db_model = OperationLogModel("127.0.0.1", "root", "123456", "assured_deletion")



#############查###############
temp=db_model.get_records_by_infoID_affairsID('0c1d2e3f4g5h','16881233')
temp_list=json.loads(temp)
temp_dict=temp_list[0]
# print(data)

temp_dict['Success']=True

formatted_dict = json.dumps(temp_dict, indent=4)
print(formatted_dict)



# 假设temp_dict是您要发送的数据
response = requests.post("http://localhost:5555/log", json=temp_dict)

while True:
    response = requests.post("http://localhost:5555/log", json=temp_dict)
    print(response)
    time.sleep(4)
