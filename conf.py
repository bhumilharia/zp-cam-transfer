import os

from Cryptodome.PublicKey import RSA

ROOT_DIR = os.path.abspath(os.path.join(__file__, os.path.pardir))

CONFIG_DIR = os.path.join(ROOT_DIR, 'config')
print('Reading private key from {}'.format(CONFIG_DIR))
with open(os.path.join(CONFIG_DIR, 'private_key'), 'r') as f:
    PRIVATE_KEY = RSA.import_key(f.read())

TEMP_DIR = os.path.join(ROOT_DIR, 'temp')
SENDER_DIR = os.path.join(TEMP_DIR, 'sender')
RECEIVER_DIR = os.path.join(TEMP_DIR, 'receiver')

MAX_PACKET_SIZE = 550
