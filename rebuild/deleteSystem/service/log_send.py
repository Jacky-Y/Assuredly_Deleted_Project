import requests

def send_log(data, should_send, ip, port):
    """
    Send data to a remote server via POST request.

    :param data: Dictionary containing the data to be sent.
    :param should_send: Boolean flag to control whether to send data.
    :param ip: IP address of the remote server.
    :param port: Port number of the remote server.
    """
    if should_send:
        url = f"http://{ip}:{port}/log"  # Assuming the endpoint is the root. Modify if needed.
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            print("Data sent successfully. Server responded with:", response.text)
        except requests.RequestException as e:
            print("Error sending data:", e)
    else:
        print("Sending is disabled. No action taken.")


if __name__=="__main__":
    # Example usage
    data = {"key": "value"}  # Replace with your actual data
    should_send = True  # Set to False to disable sending
    ip = "192.168.1.1"  # Replace with the actual IP
    port = "8080"  # Replace with the actual port

    send_log(data, should_send, ip, port)
