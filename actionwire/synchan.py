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

    def seek(self, to: int):
        r = requests.post(
            f"{config.SYNCHAN_URL}/trpc/admin.seek", headers=self.headers, data=str(to)
        )

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

    print(f"Connecting to synchan at {config.SYNCHAN_URL}")
    sio.connect(config.SYNCHAN_URL, wait_timeout=5, retry=True)
    sio.wait()


def create_synchan() -> Observable[SynchanState]:
    return reactivex.create(create_socket).pipe(
        ops.catch(lambda err, src: reactivex.of()),  # ignore the error
        ops.share(),
        ops.subscribe_on(config.thread_pool_scheduler),
    )


if __name__ == "__main__":
    create_synchan().subscribe(print)
