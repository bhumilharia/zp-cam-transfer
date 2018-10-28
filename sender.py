import os

from Cryptodome.PublicKey import RSA
import click

from common import Message

CONFIG_DIR = os.path.abspath(os.path.join(__file__, os.path.pardir, 'config'))


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

    message = Message(message)
    message.sign(private_key)

    for packet in message.construct_packets(max_packet_size=1000):
        name = 'temp/{}_{}'.format(packet.message_hash, packet.chunk_index)
        with open(name, 'w') as f:
            f.write(packet.serialize())


if __name__ == '__main__':
    send()
