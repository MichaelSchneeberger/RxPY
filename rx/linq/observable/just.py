import sys

from rx.core import Observable, AnonymousObservable

from rx.concurrency import current_thread_scheduler, immediate_scheduler
from rx.internal import extensionclassmethod


@extensionclassmethod(Observable)
def just(cls, value, scheduler=None):
    """Returns an observable sequence that contains a single element,
    using the specified scheduler to send out observer messages.
    There is an alias called 'just'.

    example
    res = rx.Observable.return(42)
    res = rx.Observable.return(42, rx.Scheduler.timeout)

    Keyword arguments:
    value -- Single element in the resulting observable sequence.
    scheduler -- [Optional] Scheduler to send the single element on. If
        not specified, defaults to Scheduler.immediate.

    Returns an observable sequence containing the single specified
    element.
    """

    def subscribe(observer, subscribe_scheduler):
        def action(_, __):
            def inner_action(_, __):
                observer.on_next(value)
                observer.on_completed()

            if scheduler:
                return scheduler.schedule(inner_action)
            else:
                inner_action(None, None)
        return subscribe_scheduler.schedule(action)
    return AnonymousObservable(subscribe)


@extensionclassmethod(Observable)
def from_callable(cls, supplier, scheduler=None):
    """Returns an observable sequence that contains a single element generate from a supplier,
       using the specified scheduler to send out observer messages.

       example
       res = rx.Observable.from_callable(lambda: calculate_value())
       res = rx.Observable.from_callable(lambda: 1 / 0) # emits an error

       Keyword arguments:
       value -- Single element in the resulting observable sequence.
       scheduler -- [Optional] Scheduler to send the single element on. If
           not specified, defaults to Scheduler.immediate.

       Returns an observable sequence containing the single specified
       element derived from the supplier
       """
    scheduler = scheduler or current_thread_scheduler

    def subscribe(observer):
        def action(scheduler, state=None):
            try:
                observer.on_next(supplier())
                observer.on_completed()
            except Exception as e:
                exc_tuple = sys.exc_info()
                observer.on_error(exc_tuple)
        return scheduler.schedule(action)

    return AnonymousObservable(subscribe)
