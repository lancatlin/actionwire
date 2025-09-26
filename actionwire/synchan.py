from dataclasses import dataclass
import reactivex
from reactivex.abc.observer import ObserverBase
from reactivex.observable import Observable
import socketio


@dataclass
class SynchanState:
    playing: bool
    currentTime: float
    duration: float
    loop: bool
    latency: float


def create_socket(observer: ObserverBase[SynchanState], scheduler):
    sio = socketio.Client()

    @sio.event
    def connect():
        print("connection established")

    @sio.event
    def control(data):
        print("message received with ", data)
        nonce = data["nonce"]
        observer.on_next(
            SynchanState(
                playing=data["playing"],
                currentTime=data["currentTime"],
                duration=data["duration"],
                loop=data["loop"],
                latency=data["latency"],
            )
        )
        sio.emit("ping", nonce)

    @sio.event
    def disconnect():
        print("disconnected from server")
        observer.on_completed()

    sio.connect("http://localhost:3000")
    sio.wait()


def create_synchan() -> Observable[SynchanState]:
    return reactivex.create(create_socket)


if __name__ == "__main__":
    create_synchan().subscribe(print)
