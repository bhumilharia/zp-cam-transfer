import os
from typing import Dict

from Cryptodome.PublicKey import RSA
from PIL import Image
import click
from click import Choice
from pyzbar.pyzbar import Decoded, decode

from common import MessageBuilder, Packet
from conf import CONFIG_DIR, SENDER_DIR, RECEIVER_DIR


def extract_content_from_text_file(filepath: str) -> str:
    with open(filepath, 'r') as f:
        return f.read()


def extract_content_from_image(filepath: str) -> str:
    with open(filepath, 'rb') as f:
        image = Image.open(f)
        image.load()

    decoded_list = decode(image)
    decoded_list = [d for d in decoded_list if d.type == 'QRCODE']

    if not decoded_list:
        raise Exception('Could not parse/extract content from QR code')

    decoded = decoded_list[0]  # type: Decoded

    return decoded.data.decode()


@click.command()
@click.option('--ext', default='png', type=Choice(['png', 'txt']),
              help='Only read files with this extension')
def receive(ext):
    print('Waiting for message')
    print('Reading public key from {}'.format(CONFIG_DIR))
    print('Using configuration: file_ext = {}'.format(ext))

    with open(os.path.join(CONFIG_DIR, 'public_key'), 'r') as f:
        public_key = RSA.import_key(f.read())

    if not os.path.exists(RECEIVER_DIR):
        print('Creating directory: '.format(RECEIVER_DIR))
        os.makedirs(RECEIVER_DIR)

    messages_dict = dict()  # type: Dict[str, MessageBuilder]

    print('Looking for files in {}'.format(SENDER_DIR))
    for filename in os.listdir(SENDER_DIR):
        _, file_ext = os.path.splitext(filename)

        if file_ext[1:] != ext:
            print('  Skipping file with extension {}: {}'.format(file_ext, filename))
            continue

        print('  Reading packet from file: {}'.format(filename))

        filepath = os.path.join(SENDER_DIR, filename)

        try:
            if file_ext == '.txt':
                content = extract_content_from_text_file(filepath)

            elif file_ext == '.png':
                content = extract_content_from_image(filepath)

        except Exception as ex:
            print('    Error parsing contents, skipping file {}'.format(filename))
            continue

        # noinspection PyUnboundLocalVariable
        packet = Packet.deserialize(content)
        if packet.message_hash not in messages_dict:
            messages_dict[packet.message_hash] = MessageBuilder(packet.message_hash,
                                                                packet.message_signature,
                                                                packet.total_chunks,
                                                                public_key)

        messages_dict[packet.message_hash].add_packet(packet)

    print('Looking for complete messages from the packets received')
    for message_hash, builder in messages_dict.items():
        if not builder.is_complete():
            print("Skipping message '{}' because not all packets have been received".format(message_hash))
            continue

        message = builder.build()
        outfile = os.path.join(RECEIVER_DIR, message_hash)
        print("Writing message '{}' to {}".format(message_hash, outfile))
        with open(outfile, 'w') as f:
            f.write(message.message)


if __name__ == '__main__':
    receive()
