import socketio

sio = socketio.Client()


@sio.event
def connect():
    print("connection established")


@sio.event
def control(data):
    print("message received with ", data)
    nonce = data["nonce"]
    sio.emit("ping", nonce)


@sio.event
def disconnect():
    print("disconnected from server")


sio.connect("http://localhost:3000")
sio.wait()
