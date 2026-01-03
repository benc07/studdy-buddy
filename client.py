from datetime import datetime

import websocket
import requests
import json
import threading

BASE_URL = "http://127.0.0.1:5000"
WS_URL = "ws://127.0.0.1:5000/ws"

def format_str(msg):
    if isinstance(msg, str):
        msg = json.loads(msg)
    return f"({datetime.fromisoformat(msg['timestamp']):%d-%m-%Y %H:%M:%S}) [{msg['sent_by']}] {msg['message']}"

def listen(ws):
    while True:
        try:
            msg = ws.recv()
            if msg:
                print(format_str(msg))
        except:
            break

def main():
    user_id = input("Enter your user id: ")
    other_id = input("Enter the user id you want to chat with: ")

    print("Loading chat history...")
    r = requests.get(BASE_URL + "/messages/history", params={
        "user_1_id": user_id,
        "user_2_id": other_id
    })
    # print(json.dumps(r.json(), indent=2))
    for msg in r.json():
        print(format_str(msg))

    ws = websocket.create_connection(WS_URL)
    ws.send(json.dumps({"user_id": user_id}))

    threading.Thread(target=listen, args=(ws,), daemon=True).start()

    print("Type messages, or /delete <id>, or /quit")

    while True:
        text = input("> ")

        if text == "/quit":
            ws.close()
            break

        if text.startswith("/delete"):
            _, mid = text.split()
            ws.send(json.dumps({
                "user_id": user_id,
                "action": "delete_message",
                "message_id": mid
            }))
            continue

        ws.send(json.dumps({
            "user_id": user_id,
            "action": "send_message",
            "target_user_id": other_id,
            "message": text
        }))

if __name__ == "__main__":
    main()
