# Flask 后端示例 (app.py)
from flask_socketio import SocketIO, emit
import threading
import time
from flask import Flask, request, jsonify
from model.del_info_model import DeleteInfoModel

deleteinfomodel=DeleteInfoModel("127.0.0.1","root","123456","combinedLog")

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

# def log_handler():
#     count = 0
#     while True:
#         time.sleep(2)  # 每2秒发送一条模拟日志信息
#         log_data = f"New log entry {count} at {time.ctime()}"
#         socketio.emit('new_log', {'data': log_data})
#         count += 1

@app.route('/log', methods=['POST'])
def receive_log():
    log_data = request.json
    print(log_data)
    deleteinfomodel.add_record(log_data)

    socketio.emit('new_log', log_data, namespace='/')  # 发送给所有连接的客户端
    return jsonify({"status": "success"}), 200

@app.route('/getStatistic', methods=['POST'])
def getStatistic():
    pass

@app.route('/')
def index():
    return "Log Aggregator"

if __name__ == '__main__':
    # 如果您的应用需要在多线程环境下运行（比如同时处理WebSocket和HTTP请求）
    # 可以在socketio.run中设置threaded=True
    socketio.run(app, debug=True, port=5555)
