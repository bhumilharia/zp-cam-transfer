import os

from Cryptodome.PublicKey import RSA
import click
import pyqrcode

from common import Message
from conf import SENDER_DIR, CONFIG_DIR, PRIVATE_KEY


@click.command()
@click.argument('message')
@click.option('--debug/--no-debug', default=False, help='Enable debugging')
def send(message, debug):
    print('Sending message: {}'.format(message))
    print('Using configuration: debug = {}'.format(debug))

    if not os.path.exists(SENDER_DIR):
        print('Creating directory: '.format(SENDER_DIR))
        os.makedirs(SENDER_DIR)

    print('Using directory: '.format(SENDER_DIR))
    for filename in os.listdir(SENDER_DIR):
        print('  Removing old file in sender dir: {}'.format(filename))
        os.remove(os.path.join(SENDER_DIR, filename))

    message = Message(message)
    message.sign(PRIVATE_KEY)

    print('Constructing and transmitting packets')
    for packet in message.construct_packets(max_packet_size=550):
        packet_serialized = packet.serialize()
        name = '{}_{}'.format(packet.message_hash, packet.chunk_index)
        path_without_ext = os.path.join(SENDER_DIR, name)

        print('  Processing packet {}'.format(packet.chunk_index))

        if debug:
            # write to txt file
            with open(path_without_ext + '.txt', 'w') as f:
                f.write(packet_serialized)

        # write to QR image file
        qr = pyqrcode.create(packet_serialized)
        qr.png(path_without_ext + '.png', scale=6)


if __name__ == '__main__':
    send()
