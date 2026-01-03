import uuid
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_sock import Sock

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
sock = Sock(app)

class Message(db.Model):
    __tablename__ = 'messages'
    message_id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    participants = db.Column(db.JSON, nullable=False)
    sent_by = db.Column(db.String, nullable=False)
    message = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def serialize(self):
        return {
            'message_id': self.message_id,
            'participants': self.participants,
            'sent_by': self.sent_by,
            'message': self.message,
            'timestamp': self.timestamp.isoformat()
        }

with app.app_context():
    db.create_all()

@app.route("/messages/", methods=["POST"])
def create_message():
    data = request.get_json()
    required = ["participants", "sent_by", "message"]

    if not all(k in data for k in required):
        return jsonify({"error": "Missing fields"}), 400

    if len(data['participants']) != 2:
        return jsonify({"error": "participants must be list of 2 user ids"}), 400

    # ensure canonical participant order
    parts = list(data['participants'])
    parts = sorted(parts)

    msg = Message(
        participants=parts,
        sent_by=data['sent_by'],
        message=data['message']
    )

    db.session.add(msg)
    db.session.commit()
    return jsonify(msg.serialize()), 200

@app.route("/messages/<message_id>", methods=["DELETE"])
def delete_message(message_id):
    user_id = request.args.get("user_id")
    msg = Message.query.filter_by(message_id=message_id).first()

    if not msg:
        return jsonify({"error": "Message not found"}), 404

    if user_id != msg.sent_by:
        return jsonify({"error": "Not authorized"}), 403

    db.session.delete(msg)
    db.session.commit()

    return jsonify({"status": "deleted", "message_id": message_id}), 200

@app.route("/messages/history", methods=["GET"])
def get_history():
    u1 = request.args.get("user_1_id")
    u2 = request.args.get("user_2_id")

    if not u1 or not u2:
        return jsonify({"error": "Missing user ids"}), 400

    before = request.args.get("before_timestamp")
    after = request.args.get("after_timestamp")
    during = request.args.get("during_timestamp")

    # Normalize participant order so [a, b] and [b, a] are treated the same.
    canonical = sorted([u1, u2])

    q = Message.query.filter(
        (Message.participants == canonical) | (Message.participants == [u2, u1])
    )

    if before:
        q = q.filter(Message.timestamp < datetime.fromisoformat(before))
    if after:
        q = q.filter(Message.timestamp > datetime.fromisoformat(after))
    if during:
        dt = datetime.fromisoformat(during)
        q = q.filter(Message.timestamp == dt)

    msgs = q.order_by(Message.timestamp.asc()).all()
    return jsonify([m.serialize() for m in msgs]), 200

active_connections = {}

@sock.route('/ws')
def websocket_handler(ws):
    user_id = None
    try:
        while True:
            raw = ws.receive()
            if raw is None:
                break

            data = json.loads(raw)
            if "user_id" not in data:
                continue

            if user_id is None:
                user_id = data["user_id"]
                active_connections[user_id] = ws

            action = data.get("action")

            if action == "send_message":
                target = data.get("target_user_id")
                text = data.get("message")

                participants = sorted([user_id, target])

                msg = Message(
                    participants=participants,
                    sent_by=user_id,
                    message=text
                )
                db.session.add(msg)
                db.session.commit()

                payload = {"type": "new_message", **msg.serialize()}

                if target in active_connections:
                    active_connections[target].send(json.dumps(payload))

                ws.send(json.dumps(payload))

            if action == "delete_message":
                message_id = data.get("message_id")
                msg = Message.query.filter_by(message_id=message_id).first()

                if msg and msg.sent_by == user_id:
                    db.session.delete(msg)
                    db.session.commit()

                    notice = {
                        "type": "message_deleted",
                        "message_id": message_id
                    }

                    for uid in msg.participants:
                        if uid in active_connections:
                            active_connections[uid].send(json.dumps(notice))

    finally:
        if user_id in active_connections:
            del active_connections[user_id]

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
