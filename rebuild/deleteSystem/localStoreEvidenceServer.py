import socket
import threading
import json
import struct
from storeEvidence import *

# 函数：extract_from_packet
# 功能：从网络数据包中提取JSON格式的有效载荷
# 输入：
#    data: bytes - 网络数据包的原始字节数据
# 输出：
#    dict - 解析后的JSON数据
# 定义一个函数用于从网络数据包中提取有效载荷
def extract_from_packet(data):
    # 假设数据包的前18个字节和最后16个字节是头部和尾部，移除它们
    packet_content = data[18:-16]
    # 解码并解析JSON格式的数据
    return json.loads(packet_content.decode())

# 函数：server1_thread
# 功能：作为服务器1运行，接收客户端请求，处理并响应
# 输入：
#    remote_ip_1: str - 服务器1监听的IP地址
#    remote_port_1: int - 服务器1监听的端口号
# 输出：
#    无直接输出，但会向连接的客户端发送数据
# 定义服务器1的线程函数
def server1_thread(remote_ip_1, remote_port_1):
    # 创建一个TCP socket并绑定到指定的IP地址和端口
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((remote_ip_1, remote_port_1))
        # 开始监听端口
        s.listen()
        print("Server 1 listening on", remote_ip_1, remote_port_1)
        # 接受连接
        conn, addr = s.accept()
        with conn:
            # 接收数据
            data = conn.recv(4096)
            # 提取请求内容
            request = extract_from_packet(data)
            print("Received from client in Server 1:", request)

            # 创建响应数据并发送给客户端
            response = {"randomidentification": "RANDOM_ID_1234"}
            response_data = create_packet('0x0001', '0x0001', '0x0041', '0x0001', '0x00', '0x00', response)
            conn.sendall(response_data)

# 函数：server2_thread
# 功能：作为服务器2运行，接收客户端请求，处理并响应
# 输入：
#    remote_ip_2: str - 服务器2监听的IP地址
#    remote_port_2: int - 服务器2监听的端口号
# 输出：
#    无直接输出，但会向连接的客户端发送数据
# 定义服务器2的线程函数
def server2_thread(remote_ip_2, remote_port_2):
    # 创建一个TCP socket并绑定到指定的IP地址和端口
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((remote_ip_2, remote_port_2))
        # 开始监听端口
        s.listen()
        print("Server 2 listening on", remote_ip_2, remote_port_2)
        # 接受连接
        conn, addr = s.accept()
        with conn:
            # 接收数据
            data = conn.recv(4096)
            # 提取请求内容
            request = extract_from_packet(data)
            print("Received from client in Server 2:", request)

            # 创建响应数据并发送给客户端
            response = {"status": "success"}
            response_data = create_packet('0x0001', '0x0002', '0x0041', '0x0001', '0x00', '0x00', response)
            conn.sendall(response_data)

if __name__ == "__main__":
    # 设置本地IP地址
    IP_ADDRESS = '127.0.0.1'
    # 设置服务器1的端口号
    PORT_1 = 65431
    # 设置服务器2的端口号
    PORT_2 = 65432

    # 启动两个线程，分别运行两个服务器
    threading.Thread(target=server1_thread, args=(IP_ADDRESS, PORT_1)).start()
    threading.Thread(target=server2_thread, args=(IP_ADDRESS, PORT_2)).start()
