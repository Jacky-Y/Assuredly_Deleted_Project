from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# Read from storeStatus.json
with open('storeStatus.json', 'r') as file:
    info_status = json.load(file)

# Read from duplication_info.json
with open('duplication_info.json', 'r') as file:
    duplication_info = json.load(file)

# Read from key_storage_info.json
with open('keyStatus.json', 'r') as file:
    key_status = json.load(file)

# Read from centralizedKeyStore.json
with open('centralizedKeyStore.json', 'r') as file:
    centralized_key_info = json.load(file)

# Read from decentralizedKeyStore.json
with open('decentralizedKeyStore.json', 'r') as file:
    decentralized_key_info = json.load(file)

@app.route('/getCentralizedKey', methods=['POST'])
def get_centralized_key():
    data = request.json
    info_id = data.get("InfoID", "")
    for item in centralized_key_info:
        if item["InfoID"] == info_id:
            return jsonify({"InfoID": info_id, "Locations": item["Locations"]})

    # If InfoID does not exist in the list
    return jsonify({"Error": "InfoID not found"}), 404

@app.route('/getDecentralizedKey', methods=['POST'])
def get_decentralized_key():
    data = request.json
    info_id = data.get("InfoID", "")
    for item in decentralized_key_info:
        if item["InfoID"] == info_id:
            return jsonify({"InfoID": info_id, "Locations": item["Locations"]})

    # If InfoID does not exist in the list
    return jsonify({"Error": "InfoID not found"}), 404

@app.route('/getStatus', methods=['POST'])
def get_status():
    data = request.json
    info_id = data.get("InfoID", "")
    for item in info_status:
        if item["InfoID"] == info_id:
            return jsonify({"InfoID": info_id, "Status": item["Status"]})

    # If InfoID does not exist in the list
    return jsonify({"Error": "InfoID not found"}), 404


@app.route('/getDuplicationLocations', methods=['POST'])
def get_duplication_locations():
    data = request.json
    info_id = data.get("InfoID", "")
    for item in duplication_info:
        if item["InfoID"] == info_id:
            return jsonify({"InfoID": info_id, "Locations": item["Locations"]})

    # If InfoID does not exist in the list
    return jsonify({"Error": "InfoID not found"}), 404

@app.route('/getKeyStorageMethod', methods=['POST'])
def get_key_storage_method():
    data = request.json
    info_id = data.get("InfoID", "")
    for item in key_status:
        if item["InfoID"] == info_id:
            return jsonify({"InfoID": info_id, "KeyStorageMethod": item["KeyStorageMethod"]})

    # If InfoID does not exist in the list
    return jsonify({"Error": "InfoID not found"}), 404

if __name__ == '__main__':
    app.run(debug=True,port=7000)
