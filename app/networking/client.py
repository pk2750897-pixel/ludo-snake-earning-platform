import json
import socket
import threading
from pathlib import Path

HOST = "127.0.0.1"
PORT = 5000
rooms = {}


def _server_loop():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(10)
    print(f"Socket server listening on {HOST}:{PORT}")

    while True:
        client_socket, address = server.accept()
        thread = threading.Thread(target=_handle_client, args=(client_socket, address), daemon=True)
        thread.start()


def _handle_client(client_socket, address):
    try:
        raw = client_socket.recv(4096).decode("utf-8")
        if not raw:
            return
        message = json.loads(raw)
        action = message.get("action")

        if action == "create_room":
            username = message.get("username", "guest")
            room_code = message.get("room_code") or _generate_room_code()
            rooms.setdefault(room_code, {"code": room_code, "players": []})
            rooms[room_code]["players"].append(username)
            client_socket.send(json.dumps({"status": "ok", "room_code": room_code, "players": rooms[room_code]["players"]}).encode())

        elif action == "join_room":
            username = message.get("username", "guest")
            room_code = message.get("room_code")
            room = rooms.get(room_code)
            if not room:
                client_socket.send(json.dumps({"status": "error", "message": "Room not found."}).encode())
            else:
                if username not in room["players"]:
                    room["players"].append(username)
                client_socket.send(json.dumps({"status": "ok", "room_code": room_code, "players": room["players"]}).encode())

        elif action == "status":
            room_code = message.get("room_code")
            room = rooms.get(room_code)
            if room:
                client_socket.send(json.dumps({"status": "ok", "players": room["players"]}).encode())
            else:
                client_socket.send(json.dumps({"status": "error", "message": "Room not found."}).encode())
        else:
            client_socket.send(json.dumps({"status": "error", "message": "Unsupported action."}).encode())
    except Exception as exc:
        client_socket.send(json.dumps({"status": "error", "message": str(exc)}).encode())
    finally:
        client_socket.close()


def _generate_room_code():
    import random
    return "ROOM" + str(random.randint(1000, 9999))


if __name__ == "__main__":
    _server_loop()
