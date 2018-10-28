# zp-cam-transfer
Demo, proof-of-concept project for data transfer by reading QR streams.

## Problem
The problem is to have secure, one-way data transmission between two computers which
are not connected with each other by any network. The only available resources are
a screen at the sender's end and a camera at the receiver's end.

One way to do this is for the sender to display one or more QR codes (in succession),
and the receiver to use their camera to capture and decode this information (and if
necessary, string the pieces together to get the complete data).

Of course, the transmitted data must be signed by the sender using their private key,
public key for which is already assumed to be made available to the receiver prior to
this data streaming.

## General Architecture / Design
The general flow and architecture is as follows

### Sender

Steps at the sender:
- Receive user input `message` (text-based in this demo)
- Calculate a `signature` for `message`. This is done by computing a hash of the 
`message`, and then signing the hash by the sender's private key (and then base64 encoding it)
- Break `message` into several chunks based on a pre-defined/configurable `chunk_size`.
Let's say the total number of chunks is `N`
- These chunks need to be transmitted, along with some metadata to enable
reconstruction at the receiver's end. Let's call each transmitted value a `packet`
- These packets have to be sent, regardless of the `transport` (that is, the manner
in which they are sent). That is, the transfer protocol could be anything,
the data could be encoded into any value (QR code, barcode, etc) - those details
are orthogonal to the forming of these packets (or their subsequent
reconstruction at the receiver)

- Sample "packets" that need to be sent:
    ```json
    {
      "message_hash": "hex digest for identifying this message",
      "message_signature": signature,
      "total_chunks": N,
      "chunk_no": X,
      "chunk_data": "data for chunk number X",
      "chunk_hash": "can be used to make sure that THIS packet's data is correctly transmitted"
    }
    ```
    The addition of "message_signature" and "total_chunks" to each content packet
    is overhead, and could be avoided by simply adding a "header" packet. However,
    adding a "message_signature" to each content packet is anyway
    useful if you're multiplexing the sender -> receiver channel by
    sending multiple `message`s at the same time, so we can avoid adding complexity
    of creating and reading a header packet (since signatures are anyway present
    in the content packets).
    
    The chunk_hash is provided for understanding and design purposes,
    and is not implemented in this demo.

- These packets are then sent to the `transport`  for sending (in our case,
QR codes (per packet) sequentially displayed on a screen). The frequency using
which the QR codes change may be configurable/pre-determined.

### Receiver
Steps at the receiver:

- Watch screen using camera. On detection of any QR code, do the following:
- Decode the QR code to a binary/text `packet` value
- Parse the `packet` and extract its individual constituent values (message_signature,
total_chunks, chunk_no, chunk_data)
- When all chunks of a given message have been received (as defined by total_chunks),
string them together, and compute the `signature` of the received message.
- If signature matches, write message to a file on the filesystem (or elsewhere
in an actual production scenario)

