from dataclasses import dataclass
import reactivex
from reactivex.abc.observer import ObserverBase
from reactivex.observable import Observable
from reactivex.operators import share
import requests
import socketio

from actionwire import config


@dataclass
class SynchanState:
    playing: bool
    currentTime: float
    duration: float
    loop: bool
    latency: float


class SynchanController:
    headers: dict[str, str] = {"Content-Type": "application/json"}

    def seek(self, to: int):
        print(f"Seeking to {to}")
        r = requests.post(
            f"{config.SYNCHAN_URL}/trpc/admin.seek", headers=self.headers, data=str(to)
        )
        print(r.text)

    def play(self):
        requests.post(f"{config.SYNCHAN_URL}/trpc/admin.play", headers=self.headers)

    def pause(self):
        requests.post(f"{config.SYNCHAN_URL}/trpc/admin.pause", headers=self.headers)


def create_socket(observer: ObserverBase[SynchanState], scheduler):
    sio = socketio.Client()

    @sio.event
    def connect():
        print("connection established")

    @sio.event
    def control(data):
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

    sio.connect(config.SYNCHAN_URL)
    sio.wait()


def create_synchan() -> Observable[SynchanState]:
    return reactivex.create(create_socket).pipe(share())


if __name__ == "__main__":
    create_synchan().subscribe(print)
