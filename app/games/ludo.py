import json
import socket

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000


def request(action, **payload):
    message = {"action": action, **payload}
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(5)
    client.connect((SERVER_HOST, SERVER_PORT))
    client.send(json.dumps(message).encode())
    response = client.recv(4096).decode("utf-8")
    client.close()
    return json.loads(response)


def create_room(username):
    return request("create_room", username=username)


def join_room(username, room_code):
    return request("join_room", username=username, room_code=room_code)


def get_room_status(room_code):
    return request("status", room_code=room_code)
