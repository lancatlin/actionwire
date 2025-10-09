import time
import reactivex as rx
from reactivex.observable.observable import Observable
import reactivex.operators as ops
import reactivex.scheduler as scheduler
from reactivex.scheduler.eventloop import AsyncIOScheduler
from reactivex.subject.subject import Subject
import multiprocessing

from actionwire.synchan import create_synchan

thread_count = multiprocessing.cpu_count()
thread_pool_scheduler = scheduler.ThreadPoolScheduler(thread_count)
print("Cpu count is : {0}".format(thread_count))


def push_five_strings(observer, scheduler):
    print("Create stream")
    time.sleep(0.1)
    observer.on_next("Alpha")
    time.sleep(0.1)
    observer.on_next("Beta")
    time.sleep(0.1)
    observer.on_next("Gamma")
    time.sleep(0.1)
    observer.on_next("Delta")
    time.sleep(0.1)
    observer.on_next("Epsilon")
    time.sleep(0.1)
    observer.on_completed()


words = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"]

sub: Subject[str] = rx.Subject()
stream = rx.create(push_five_strings).pipe(
    ops.share(), ops.subscribe_on(thread_pool_scheduler)
)  # .subscribe(sub)
# stream = rx.from_list(words).pipe(
#     ops.flat_map(lambda word: rx.timer(1).pipe(ops.map(lambda _: word)))
# )

s1 = stream.pipe(ops.map(lambda text: "1: " + text))
s2 = stream.pipe(ops.map(lambda text: "2: " + text))
# rx.merge(s1, s2).subscribe(print)

with_delay = rx.timer(0, 5, thread_pool_scheduler).pipe(
    ops.flat_map(
        lambda i: rx.merge(
            rx.of(f"immediate: {i}"),
            rx.timer(1.0).pipe(ops.map(lambda _: f"delayed: {i}")),
        )
    ),
    ops.share(),
)

# with_delay.subscribe(print)

timecodes = create_synchan()

b_timer = rx.timer(0, 1).pipe(ops.with_latest_from(timecodes))

b_timer.subscribe(print)

# input("Enter any key to exit")
