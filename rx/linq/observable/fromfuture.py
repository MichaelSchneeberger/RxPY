import sys

from rx.core import Observable, AnonymousObservable, Disposable
from rx.disposables import CompositeDisposable, SingleAssignmentDisposable
from rx.internal.utils import is_future
from rx.internal import extensionclassmethod


@extensionclassmethod(Observable)
def from_future(cls, future):
    """Converts a Future to an Observable sequence

    Keyword Arguments:
    future -- {Future} A Python 3 compatible future.
        https://docs.python.org/3/library/asyncio-task.html#future
        http://www.tornadoweb.org/en/stable/concurrent.html#tornado.concurrent.Future

    Returns {Observable} An Observable sequence which wraps the existing
    future success and failure.
    """
    single_assignment_disposable = SingleAssignmentDisposable()

    def subscribe(observer, scheduler):
        def done(future):
            def action(_, __):
                try:
                    value = future.result()
                except Exception as ex:
                    exc_tuple = sys.exc_info()
                    observer.on_error(exc_tuple)
                else:
                    observer.on_next(value)
                    observer.on_completed()

            single_assignment_disposable.disposable = scheduler.schedule(action)

        future.add_done_callback(done)

        def dispose():
            if future and future.cancel:
                future.cancel()

        return CompositeDisposable(Disposable.create(dispose), single_assignment_disposable)

    return AnonymousObservable(subscribe) if is_future(future) else future
