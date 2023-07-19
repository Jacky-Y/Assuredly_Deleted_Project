import struct
import json
import socket
import requests
import os
from datetime import datetime


def create_packet_header(version, main_command, sub_command, encrypt_mode, auth_mode, message_id, packet_length):
    reserved = "0x0000"  #保留字段

    # 使用struct模块打包字节序列，'>B'表示一个大端字节序的无符号字符（1字节）
    version_bytes = struct.pack('>B', int(version, 16))
    main_command_bytes = struct.pack('>B', int(main_command, 16))

    # '>H'表示一个大端字节序的无符号短整数（2字节）
    sub_command_bytes = struct.pack('>H', int(sub_command, 16))
    reserved_bytes = struct.pack('>H', int(reserved, 16))

    encrypt_mode_bytes = struct.pack('>B', int(encrypt_mode, 16))
    auth_mode_bytes = struct.pack('>B', int(auth_mode, 16))

    # '>I'表示一个大端字节序的无符号整数（4字节）
    message_id_bytes = struct.pack('>I', int(message_id, 16))
    packet_length_bytes = struct.pack('>I', int(packet_length, 16))

    # 连接所有的字节序列形成数据包头部
    packet_header = version_bytes + main_command_bytes + sub_command_bytes + encrypt_mode_bytes + auth_mode_bytes + reserved_bytes + message_id_bytes + packet_length_bytes

    return packet_header



def create_packet_header_with_json(version, main_command, sub_command, encrypt_mode, auth_mode, message_id, json_str):
    reserved = "0x0000"  #保留字段

    json_bytes = json_str.encode()  # 把JSON对象转换为字节序列
    json_length = len(json_bytes)  # 计算JSON对象的长度

    header_length = 16  # 计算消息头部的长度
    auth_field_length = 16  # 认证与校验域的长度

    packet_length = header_length + json_length + auth_field_length  # 计算数据包的总长度

    # 将数据包长度转换为十六进制字符串
    packet_length_hex = '0x{:08x}'.format(packet_length)

    # 使用struct模块打包字节序列
    version_bytes = struct.pack('>B', int(version, 16))
    main_command_bytes = struct.pack('>B', int(main_command, 16))
    sub_command_bytes = struct.pack('>H', int(sub_command, 16))
    reserved_bytes = struct.pack('>H', int(reserved, 16))
    encrypt_mode_bytes = struct.pack('>B', int(encrypt_mode, 16))
    auth_mode_bytes = struct.pack('>B', int(auth_mode, 16))
    message_id_bytes = struct.pack('>I', int(message_id, 16))
    packet_length_bytes = struct.pack('>I', int(packet_length_hex, 16))

    # 连接所有的字节序列形成数据包头部
    packet_header = version_bytes + main_command_bytes + sub_command_bytes + encrypt_mode_bytes + auth_mode_bytes + reserved_bytes + message_id_bytes + packet_length_bytes

    return packet_header



def send_packet_tcp(host, port, packet):
    """
    发送TCP数据包

    :param host: 目标主机名
    :param port: 目标端口
    :param packet: 要发送的数据包
    """
    # 创建一个socket对象
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 连接到服务器
    s.connect((host, port))

    # 发送数据包
    s.sendall(packet)

    # 关闭连接
    s.close()


# print(create_packet_header("0x01","0x40","0x0001","0x00","0x00","0x00000000","0x00000011"))






def save_dict_as_json_and_post(my_dict, filename, url):
    # 获取当前的日期和时间并添加到文件名
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    filename_with_time = f"{filename}_{current_time}.json"
    
    # 将字典转换为json并保存为文件
    try:
        with open(filename_with_time, 'w') as f:
            json.dump(my_dict, f)
    except Exception as e:
        print(f"Error saving JSON file: {e}")
        return False

    # 获取文件的完整路径
    full_path = os.path.realpath(filename_with_time)

    # 发送POST请求
    try:
        with open(full_path, 'rb') as f:
            response = requests.post(url, files={"file": f})

        # 如果请求返回的状态码不是200，我们认为请求失败
        if response.status_code != 200:
            print(f"POST request failed with status code: {response.status_code}")
            return False

    except Exception as e:
        print(f"Error sending POST request: {e}")
        return False

    # 如果以上都没有问题，返回True
    return True
