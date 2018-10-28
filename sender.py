import os

from Cryptodome.PublicKey import RSA
import click
import pyqrcode

from common import Message
from conf import SENDER_DIR, CONFIG_DIR


@click.command()
@click.argument('message')
@click.option('--medium', default="fs", type=click.Choice(['fs', 'screen']),
              help='What transport medium to use')
@click.option('--encoding', default="text", type=click.Choice(['text', 'qr']),
              help='What to encode packets into')
def send(message, medium, encoding):
    print('Sending message: {}'.format(message))
    print('Using configuration: medium = {}'.format(medium))
    print('Using configuration: encoding = {}'.format(encoding))

    print('Reading private key from {}'.format(CONFIG_DIR))
    with open(os.path.join(CONFIG_DIR, 'private_key'), 'r') as f:
        private_key = RSA.import_key(f.read())

    if not os.path.exists(SENDER_DIR):
        print('Creating directory: '.format(SENDER_DIR))
        os.makedirs(SENDER_DIR)

    print('Using directory: '.format(SENDER_DIR))
    for filename in os.listdir(SENDER_DIR):
        print('  Removing old file in sender dir: {}'.format(filename))
        os.remove(os.path.join(SENDER_DIR, filename))

    message = Message(message)
    message.sign(private_key)

    for packet in message.construct_packets(max_packet_size=1000):
        packet_serialized = packet.serialize()
        name = '{}_{}'.format(packet.message_hash, packet.chunk_index)
        path_without_ext = os.path.join(SENDER_DIR, name)

        # write to txt file
        with open(path_without_ext + '.txt', 'w') as f:
            f.write(packet_serialized)

        # write to QR image file
        qr = pyqrcode.create(packet_serialized)
        qr.png(path_without_ext + '.png', scale=6)


if __name__ == '__main__':
    send()
