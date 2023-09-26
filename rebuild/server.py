import socket
import threading
import json
import struct
from  storeEvidence import *

def extract_from_packet(data):
    # 把头部从数据包中去掉，然后解析JSON
    packet_content = data[18:-16]
    return json.loads(packet_content.decode())

def server1_thread(remote_ip_1, remote_port_1):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((remote_ip_1, remote_port_1))
        s.listen()
        print("Server 1 listening on", remote_ip_1, remote_port_1)
        conn, addr = s.accept()
        with conn:
            data = conn.recv(4096)
            request = extract_from_packet(data)
            print("Received from client in Server 1:", request)

            # 创建一个随机标识并发送给客户端
            response = {"randomidentification": "RANDOM_ID_1234"}
            response_data = create_packet('0x0001', '0x0001', '0x0041', '0x0001', '0x00', '0x00', response)
            conn.sendall(response_data)

def server2_thread(remote_ip_2, remote_port_2):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((remote_ip_2, remote_port_2))
        s.listen()
        print("Server 2 listening on", remote_ip_2, remote_port_2)
        conn, addr = s.accept()
        with conn:
            data = conn.recv(4096)
            request = extract_from_packet(data)
            print("Received from client in Server 2:", request)

            # 回应客户端
            response = {"status": "success"}
            response_data = create_packet('0x0001', '0x0002', '0x0041', '0x0001', '0x00', '0x00', response)
            conn.sendall(response_data)

if __name__ == "__main__":
    # 同一地址，不同的端口
    IP_ADDRESS = '127.0.0.1'
    PORT_1 = 65431
    PORT_2 = 65432

    # 启动两个服务器线程
    threading.Thread(target=server1_thread, args=(IP_ADDRESS, PORT_1)).start()
    threading.Thread(target=server2_thread, args=(IP_ADDRESS, PORT_2)).start()
