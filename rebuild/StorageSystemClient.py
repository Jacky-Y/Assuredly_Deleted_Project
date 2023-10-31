import requests

class StorageSystemClient:

    def __init__(self, base_url):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json"
        }

    def _post_request(self, endpoint, info_id):
        url = f"{self.base_url}/{endpoint}"
        data = {"infoID": info_id}
        response = requests.post(url, headers=self.headers, json=data, timeout=10)  # 添加超时
        response.raise_for_status()
        return response.json()

    def get_status(self, info_id):
        json_data = self._post_request("getStatus", info_id)
        return json_data.get("Status")

    def get_duplication_locations(self, info_id):
        json_data = self._post_request("getDuplicationLocations", info_id)
        return json_data.get("Locations")

    def get_centralized_key(self, info_id):
        json_data = self._post_request("getCentralizedKey", info_id)
        return json_data.get("Locations")

    def get_decentralized_key(self, info_id):
        json_data = self._post_request("getDecentralizedKey", info_id)
        return json_data.get("Locations")

    def get_key_storage_method(self, info_id):
        json_data = self._post_request("getKeyStorageMethod", info_id)
        return json_data.get("KeyStorageMethod")

    def send_dup_del_command(self, duplication_del_command):
        url = f"{self.base_url}/duplicationDel"
        data = {"duplicationDelCommand": duplication_del_command}
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=10)  # 添加超时
            response.raise_for_status()  # Check if the HTTP response was successful
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error sending duplication delete command to {url}: {e}")
            return {"status": "error", "message": str(e)}

    def send_key_del_command(self, key_del_command):
        url = f"{self.base_url}/keyDel"
        data = {"keyDelCommand": key_del_command}
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=10)  # 添加超时
            response.raise_for_status()  # Check if the HTTP response was successful
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error sending key delete command to {url}: {e}")
            return {"status": "error", "message": str(e)}

