import binascii
from datetime import datetime

#导入国密算法sm4包
from utils import sm3
from utils import sm4

def sm3_hash(message:bytes):
    """
    国密sm3加密
    :param message: 消息值，bytes类型
    :return: 哈希值
    """
    
    msg_list = [i for i in message]
    hash_hex = sm3.sm3_hash(msg_list)
    print(hash_hex)

    # bytes2hex(hash_hex);

    hash_bytes = bytes.fromhex(hash_hex)
    print(hash_bytes)

    # return bytes.hash
    # return hash

def bytes2hex(bytesData):
    hex = binascii.hexlify(bytesData) 
    print(hex)
    print(hex.decode())
    return hex

# main 
if __name__ == '__main__':
    # print("main begin");
    # message = b"123456" # bytes类型
    # sm3_hash(message);\
    time_str="2024-01-10 16:46:38 to 2024-01-12 16:46:38"
    if 'to' in time_str:
        start_time_str, end_time_str = time_str.split(' to ')
        start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')
    print(start_time)
    print(end_time)

    
