import requests

class StorageSystemClient:

    def __init__(self, base_url):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json"
        }

    def _post_request(self, endpoint, info_id):
        url = f"{self.base_url}/{endpoint}"
        data = {"InfoID": info_id}
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

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
