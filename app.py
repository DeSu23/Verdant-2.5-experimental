from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import json
import os

app = Flask(__name__)
socketio = SocketIO(app)

channels_messages = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('send_message')
def handle_send_message(data):
    if not data['message'].strip():
        return  # Do not process empty or whitespace-only messages
    channel = data['channel']
    message = "Stranger: " + data['message']
    
    if channel not in channels_messages:
        channels_messages[channel] = []

    channels_messages[channel].append(message)
    
    with open(f'{channel}.json', 'w') as f:
        json.dump(channels_messages[channel], f)
    
    socketio.emit('receive_message', {'message': message, 'channel': channel})

@socketio.on('join_channel')
def handle_join_channel(data):
    channel = data['channel']

    if os.path.exists(f'{channel}.json'):
        with open(f'{channel}.json', 'r') as f:
            channels_messages[channel] = json.load(f)
    
    socketio.emit('load_messages', {'channel': channel, 'messages': channels_messages.get(channel, [])}, room=request.sid)

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), allow_unsafe_werkzeug=True)
