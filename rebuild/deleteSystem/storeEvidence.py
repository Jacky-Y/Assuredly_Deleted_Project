import struct
import json
import socket
import requests
import os
from datetime import datetime


import struct

def create_packet_header_with_json(version, main_command, sub_command, message_version, encrypt_mode, auth_mode, json_str):
    reserved = "0x0000"  # 保留字段

    json_bytes = json_str.encode()  # 把JSON对象转换为字节序列
    json_length = len(json_bytes)  # 计算JSON对象的长度

    header_length = 18  # 计算消息头部的长度 
    auth_field_length = 16  # 认证与校验域的长度

    packet_length = header_length + json_length + auth_field_length  # 计算数据包的总长度

    # 将数据包长度转换为十六进制字符串
    packet_length_hex = '0x{:08x}'.format(packet_length)

    # 使用struct模块打包字节序列
    version_bytes = struct.pack('>H', int(version, 16)) 
    main_command_bytes = struct.pack('>H', int(main_command, 16))
    sub_command_bytes = struct.pack('>H', int(sub_command, 16))
    message_version_bytes = struct.pack('>H', int(message_version, 16)) # 添加了消息版本号的打包
    reserved_bytes = struct.pack('>I', int(reserved, 16))
    encrypt_mode_bytes = struct.pack('>B', int(encrypt_mode, 16))
    auth_mode_bytes = struct.pack('>B', int(auth_mode, 16))
    packet_length_bytes = struct.pack('>I', int(packet_length_hex, 16))

    # 连接所有的字节序列形成数据包头部
    packet_header = version_bytes + main_command_bytes + sub_command_bytes + message_version_bytes + encrypt_mode_bytes + auth_mode_bytes + reserved_bytes + packet_length_bytes

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


def client_interaction(remote_ip_1, remote_port_1, remote_ip_2, remote_port_2, initial_content, initial_main_cmd, initial_msg_version, second_content, second_main_cmd, second_msg_version):
    try:
        # 首先与第一个服务器进行交互
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s1:
            print("connect 1 start")
            s1.connect((remote_ip_1, remote_port_1))

            initial_content['mainCMD'] = int(initial_main_cmd, 16)
            initial_content['subCMD'] = 0x0041
            initial_content['msgVersion'] = int(initial_msg_version, 16)

            # 发送初始请求
            initial_data = create_packet('0x0001', initial_main_cmd, '0x0041', initial_msg_version, '0x00', '0x00', initial_content)
            s1.sendall(initial_data)

            # 从服务器1接收响应并获取随机标识
            data1 = s1.recv(4096)
            data1_json=extract_from_packet(data1)
            random_id = data1_json["randomidentification"]
            print("connect 1 done")

        # 使用从第一个服务器得到的随机标识与第二个服务器进行交互
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
            print("connect 2 start")
            s2.connect((remote_ip_2, remote_port_2))

            second_content['mainCMD'] = int(second_main_cmd, 16)
            second_content['subCMD'] = 0x0041
            second_content['msgVersion'] = int(second_msg_version, 16)

            # 添加接收到的随机标识到 second_content
            second_content["randomidentification"] = random_id
            second_data = create_packet('0x0001', second_main_cmd, '0x0041', second_msg_version, '0x00', '0x00', second_content)

            # 发送 second_content 到服务器2
            s2.sendall(second_data)

            # 从服务器2接收最终响应
            data2 = s2.recv(4096)
            data2_json=extract_from_packet(data2)
            print(data2_json)
            print("connect 2 done")

    except socket.error as e:
        print(f"Socket error: {e}")
    except json.JSONDecodeError:
        print("Failed to decode JSON response from server.")     
    except KeyError as e:
        print(f"Expected key not found in server response: {e}")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")


def extract_from_packet(data):
    """
    Args:
    - data (bytes): The data packet received from the socket.
    
    Returns:
    - dict: The extracted JSON content.
    """
    # 提取JSON部分，我们知道包头长度为18字节，认证与校验域长度为16字节
    json_data = data[18:-16]

    # 解码二进制数据并解析JSON数据
    parsed_json = json.loads(json_data.decode('utf-8'))

    return parsed_json


# # 示例调用这个函数
# initial_content = {
#     "datasign": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa"
# }
# second_content = {}  # 具体内容根据实际情况填写

# client_interaction('127.0.0.1', 65432, initial_content, second_content)



# print(create_packet_header("0x01","0x40","0x0001","0x00","0x00","0x00000000","0x00000011"))




