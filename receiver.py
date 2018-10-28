import os
from typing import Dict

from Cryptodome.PublicKey import RSA
import click

from common import MessageBuilder, Packet
from conf import CONFIG_DIR, SENDER_DIR, RECEIVER_DIR


@click.command()
def receive():
    print('Waiting for message')
    print('Reading public key from {}'.format(CONFIG_DIR))
    with open(os.path.join(CONFIG_DIR, 'public_key'), 'r') as f:
        public_key = RSA.import_key(f.read())

    messages_dict = dict()  # type: Dict[str, MessageBuilder]
    for filename in os.listdir(SENDER_DIR):
        _, ext = os.path.splitext(filename)
        if ext == '.txt':
            print('    Reading packet from {}'.format(filename))
            with open(os.path.join(SENDER_DIR, filename), 'r') as f:
                packet = Packet.deserialize(f.read())

            if packet.message_hash not in messages_dict:
                messages_dict[packet.message_hash] = MessageBuilder(packet.message_hash,
                                                                    packet.message_signature,
                                                                    packet.total_chunks,
                                                                    public_key)

            messages_dict[packet.message_hash].add_packet(packet)

        else:
            print('Skipping file with extension {}: {}'.format(ext, filename))
            continue

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
