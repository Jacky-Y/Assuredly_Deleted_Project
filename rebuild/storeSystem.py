from flask import Flask, request, jsonify

app = Flask(__name__)

# 上述提供的InfoID状态信息
info_status = [
    {"InfoID": "1a2b3c4d5e6f", "Status": "Plaintext"},
    {"InfoID": "2g3h4i5j6k7l", "Status": "Plaintext"},
    {"InfoID": "3m4n5o6p7q8r", "Status": "Plaintext"},
    {"InfoID": "4s5t6u7v8w9x", "Status": "Plaintext"},
    {"InfoID": "5y6z7a8b9c0d", "Status": "Plaintext"},
    {"InfoID": "6e7f8g9h0i1j", "Status": "Plaintext"},
    {"InfoID": "7k8l9m0n1o2p", "Status": "Plaintext"},
    {"InfoID": "8q9r0s1t2u3v", "Status": "Plaintext"},
    {"InfoID": "9w0x1y2z3a4b", "Status": "Encrypted"},
    {"InfoID": "0c1d2e3f4g5h", "Status": "Encrypted"}
]

@app.route('/getStatus', methods=['POST'])
def get_status():
    data = request.json
    info_id = data.get("InfoID", "")
    for item in info_status:
        if item["InfoID"] == info_id:
            return jsonify({"InfoID": info_id, "Status": item["Status"]})

    # 如果InfoID不存在于列表中
    return jsonify({"Error": "InfoID not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
