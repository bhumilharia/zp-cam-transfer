import json
from typing import List

from Crypto.Hash import SHA256

from utils import split_every

_BASE_PKT_SIZE = len(json.dumps({
    "message_hash": "",
    "total_chunks": 999999,
    "chunk_index": 999999,
    "chunk_data": "",
}))


class Packet:
    """
    Represents each individual content packet to be transmitted
    """

    def __init__(self, message_hash: str, total_chunks: int, chunk_index: int, chunk_data: str):
        self.message_hash = message_hash
        self.total_chunks = total_chunks
        self.chunk_index = chunk_index
        self.chunk_data = chunk_data
        # self.chunk_hash = "currently unused"

    def serialize(self) -> str:
        return json.dumps({
            "message_hash": self.message_hash,
            "total_chunks": self.total_chunks,
            "chunk_index": self.chunk_index,
            "chunk_data": self.chunk_data,
        })

    @classmethod
    def deserialize(cls, serialized_packet: str) -> 'Packet':
        packet_dict = json.loads(serialized_packet)
        packet = Packet(message_hash=packet_dict['message_hash'],
                        total_chunks=packet_dict['total_chunks'],
                        chunk_index=packet_dict['chunk_index'],
                        chunk_data=packet_dict['chunk_data'])

        return packet


class Message:
    """
    Represents a (whole) message to be transmitted
    """

    def __init__(self, message_str: str):
        self.message = message_str
        self.hash = self._get_hash()

    def _get_hash(self):
        h = SHA256.new()
        h.update(self.message.encode())
        return h.hexdigest()

    def construct_packets(self, max_packet_size: int) -> List[Packet]:
        packets = []
        # break into chunks based on chunk size, which is based on max packet size

        chunk_size = max_packet_size - _BASE_PKT_SIZE - len(self.hash)
        chunk_size = 2
        if chunk_size < 0:
            raise Exception("max_packet_size is too low, could not chunk")

        chunks = list(split_every(chunk_size, self.message))
        total_chunks = len(chunks)

        for index, chunk_data in enumerate(chunks):
            packet = Packet(self.hash, total_chunks, index, chunk_data)
            packets.append(packet)

        return packets


class MessageBuilder:
    """
    Builder class used to reconstruct the full `Message`s using packets
    """

    def __init__(self, message_hash: str, total_chunks: int):
        self._message_hash = message_hash
        self._total_chunks = total_chunks

        # initialize a list of size total_chunks, setting all values to None
        # we could technically use a dict/map and set values as and when they
        # came in to enable a more "dynamic" sizing, but that complicates the
        # is_complete check, so optimizing for simplicity over performance.
        self._packets = [None] * self._total_chunks  # type: List[Packet]

    def add_packet(self, packet_index: int, packet: Packet):
        """
        Add a packet to build the message. If the packet has been seen before,
        it is simply discarded
        :param packet_index: The index (sequence number) of this packet
        :param packet: Actual value
        """
        self._packets[packet_index] = self._packets[packet_index] or packet

    def is_complete(self) -> bool:
        return all(v for v in self._packets)

    def build(self) -> Message:
        if not self.is_complete():
            raise Exception('Cannot build message, one or more packets missing')

        message_str = ''.join([packet.chunk_data for packet in self._packets])

        message = Message(message_str)
        if message.hash != self._message_hash:
            raise Exception(
                'Actual and expected hashes differ.\n'
                'Message: {}\n'
                'Expected Hash: {}\n'
                'Actual Hash: {}\n'.format(message_str,
                                           self._message_hash,
                                           message.hash)
            )

        return message
