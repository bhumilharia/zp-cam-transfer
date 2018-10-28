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


## Demo

### Installation
Ideally it would be best to simply set up a docker image for this, but not doing
that for now.

Installation steps are:
1. Create a new Python 3.5 (or higher) virtualenv: `virtualenv venv -p python3.5`
1. Activate the virtualenv
1. git clone the repo, and `cd ./zp-cam-transfer`
1. Install zbar
    - On Ubuntu, this is using `sudo apt-get install libzbar0`
    - On OS X, this is using `brew install zbar`
    - For other systems, look at steps [here](https://github.com/NaturalHistoryMuseum/pyzbar/)
1. Install python requirements: `pip install -r requirements.txt`
1. There is no requirement for setting up private/public key pairs, a sample
pair is already provided (and used) from inside `zp-cam-transfer/config/`. If for
any reason you wish to use your own pair, feel free to replace the ones inside the
config folder.

### Running the demo
All steps require an active virtualenv.

In order to simplify development/debugging, the demo was created with the following
approach:

**Step 1**

Make sender write QR images to filesystem, and make the receiver read those
images from the filesystem. While this does not achieve the overall objective, this
helps set the end-to-end pipe in place, so that the "filesystem" medium/transport
can simply be swapped later for the camera processing transport.

This step of the demo is working fully.

##### Sender
```bash
python sender.py --debug "Put here whatever message you wish to transmit"
```

The `debug` flag is optional of course, but it may help understand things.
This will cause files to be written inside `zp-cam-transfer/temp/sender` (these
files are cleared every time you run `sender.py`)

##### Receiver
```bash
python receiver.py
```

**Step 2**
After Step 1 which uses the filesystem, we work towards getting rid of the fs.
So basically make the sender output the QRs to a screen in a streaming fashion,
and make the receiver read from a camera.

Out of these, the sender part is implemented. Here's how to run it: 

##### Sender Server
```bash
python sender_server.py
```

This should start a simple server. Next. go to your browser and
browse to `http://localhost:5000`

##### Camera Receiver
This part has not yet been implemented, because of lack of time.


### Simplifications and Possible Improvements
As a demo project, this repo makes a number of simplifications. Listing them
down here:

- In order to simplify processing, we do not make any distinction between different
types of packets. A better, more efficient way of doing this would be to have a 
header containing the overall `message_signature` and `total_chunks`, with the rest
of the packets containing more content. Such design would of course bring in other
complexities.

- For this demo, the sender serializes the content as JSON. This is obviously
wasteful. Much more efficient serialization mechanisms can be implemented for higher
data transfer rates. A sample alternative is some sort of a TLV (Tag-Length-Value)
scheme that is often used in (debit/credit) card-processing systems. Even as JSON,
the keys for each fields are large - they could simply be cut down
to one or two characters, in order to be more efficient.

- As mentioned previously, another reasonable thing to implement would be to
also send `chunk_data` hashes in each packet - such a protocol can enable
identification of _which_ packet was corrupt and retransmit the same one.

- Since the keys are pre-shared between the machines, they are simply checked into
this repository for the demo. In a real-world scenario, you'd want to be able
to change/configure them.

- Depending on the actual production requirements, this can be written in different
ways.
    - A more user-friendly way to build the sender will obviously be to build it as
    a web page, with text input/file upload for users, using JavaScript to simply
    generate and display QR codes in a loop. This has already been implemented in
    `sender_server.py` as described above
    - Similarly, the receiver could be made more robust, perhaps accepting from
    multiple screens at once using multiple camera inputs.

