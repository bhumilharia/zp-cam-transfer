import os

ROOT_DIR = os.path.abspath(os.path.join(__file__, os.path.pardir))
CONFIG_DIR = os.path.join(ROOT_DIR, 'config')

TEMP_DIR = os.path.join(ROOT_DIR, 'temp')

SENDER_DIR = os.path.join(TEMP_DIR, 'sender')
RECEIVER_DIR = os.path.join(TEMP_DIR, 'receiver')
if not os.path.exists(RECEIVER_DIR):
    os.makedirs(RECEIVER_DIR)
