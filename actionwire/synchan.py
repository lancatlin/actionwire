from dataclasses import dataclass
import reactivex
from reactivex.abc.observer import ObserverBase
from reactivex.observable import Observable
import reactivex.operators as ops
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

    def __init__(self, url: str) -> None:
        self.url: str = url

    def seek(self, to: int):
        r = requests.post(
            f"{self.url}/trpc/admin.seek", headers=self.headers, data=str(to)
        )

    def play(self):
        requests.post(f"{self.url}/trpc/admin.play", headers=self.headers)

    def pause(self):
        requests.post(f"{self.url}/trpc/admin.pause", headers=self.headers)


def create_synchan(url: str) -> Observable[SynchanState]:
    def subscribe(observer: ObserverBase[SynchanState], scheduler):
        sio = socketio.Client()

        @sio.event
        def connect():
            print("connection established")

        @sio.event
        def connect_error(data):
            print(f"connection failed: {data}")

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

        print(f"Connecting to synchan at {url}")
        sio.connect(url, wait_timeout=5, retry=True)
        sio.wait()

    return reactivex.create(subscribe).pipe(
        ops.catch(lambda err, src: reactivex.of()),  # ignore the error
        ops.share(),
        ops.subscribe_on(config.thread_pool_scheduler),
    )


if __name__ == "__main__":
    create_synchan("http://localhost:3000").subscribe(print)
