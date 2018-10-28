from flask import Flask, send_from_directory, request, jsonify

from message import Message
from conf import PRIVATE_KEY, MAX_PACKET_SIZE

app = Flask(__name__)


@app.route('/', methods=['GET'], strict_slashes=False)
def index():
    return send_from_directory('static/html', 'index.html')


@app.route('/api/qr-stream', methods=['POST'], strict_slashes=False)
def qr_stream():
    body = request.json
    message_str = body.get('message')
    max_packet_size = body.get('max_packet_size') or MAX_PACKET_SIZE

    message = Message(message_str)
    message.sign(PRIVATE_KEY)
    packets = message.construct_packets(max_packet_size)
    serialized_packets = [p.serialize() for p in packets]

    return jsonify(message_hash=message.hash,
                   message_signature=message.signature,
                   serialized_packets=serialized_packets)


if __name__ == '__main__':
    print(app.url_map)
    app.run(debug=True)
