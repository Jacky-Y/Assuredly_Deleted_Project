import struct
import json
import socket
import requests
import os
from datetime import datetime


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


def create_packet(version, main_command, sub_command, encrypt_mode, auth_mode, message_id, json_data):
    # 将JSON对象转换为JSON字符串
    json_data_str = json.dumps(json_data, indent=4)
    # 将JSON字符串转换为字节流
    json_data_str_bytes = json_data_str.encode('utf-8')

    # 创建包头
    header = create_packet_header_with_json(version, main_command, sub_command, encrypt_mode, auth_mode, message_id, json_data_str)

    # 创建包尾
    tail = struct.pack('>16s', b'\x00'*16)

    # 拼接头部，数据部分和尾部
    packet = header + json_data_str_bytes + tail

    return packet



def send_packet_tcp(host, port, packet):
    """
    发送TCP数据包,并接收并打印服务器的响应

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

    # 接收服务器响应
    response = s.recv(1024)  # 这里的1024是接收的最大字节，你可以根据需要进行修改

    # 打印服务器响应
    print("Received:", response.decode('utf-8'))

    # 关闭连接
    s.close()


# print(create_packet_header("0x01","0x40","0x0001","0x00","0x00","0x00000000","0x00000011"))




