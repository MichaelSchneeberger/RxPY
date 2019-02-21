from rx.core import Observable, AnonymousObservable
from rx.concurrency import immediate_scheduler
from rx.internal import extensionclassmethod


@extensionclassmethod(Observable)
def empty(cls, scheduler=None):
    """Returns an empty observable sequence, using the specified scheduler
    to send out the single OnCompleted message.

    1 - res = rx.Observable.empty()
    2 - res = rx.Observable.empty(rx.Scheduler.timeout)

    scheduler -- Scheduler to send the termination call on.

    Returns an observable sequence with no elements.
    """

    scheduler = scheduler or immediate_scheduler

    def subscribe(observer, subscribe_scheduler):
        def action(_, __):
            def inner_action(_, __):
                observer.on_completed()

            return scheduler.schedule(inner_action)
        return subscribe_scheduler.schedule(action)

    return AnonymousObservable(subscribe)

