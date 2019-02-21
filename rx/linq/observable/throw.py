import sys

from rx.core import Observable, AnonymousObservable

from rx.concurrency import immediate_scheduler
from rx.internal import extensionclassmethod


@extensionclassmethod(Observable, alias="throw_exception")
def throw(cls, exception, scheduler=None):
    """Returns an observable sequence that terminates with an exception,
    using the specified scheduler to send out the single OnError message.

    1 - res = rx.Observable.throw_exception(Exception('Error'))
    2 - res = rx.Observable.throw_exception(Exception('Error'),
                                            rx.Scheduler.timeout)

    Keyword arguments:
    exception -- An object used for the sequence's termination.
    scheduler -- Scheduler to send the exceptional termination call on. If
        not specified, defaults to ImmediateScheduler.

    Returns the observable sequence that terminates exceptionally with the
    specified exception object.
    """

    scheduler = scheduler or immediate_scheduler

    if isinstance(exception, str):
        try:
            raise Exception(exception)
        except:
            exc_info = sys.exc_info()

        exception = exc_info
    elif isinstance(exception, tuple):
        assert len(exception) == 3, 'tuple "{}" needs to be of length 3'.format(exception)
        assert isinstance(exception[1], Exception), '2nd argument "{}" needs to be of type Exception'.format(exception[1])
    elif isinstance(exception, Exception):
        exception = type(exception), exception, exception.__traceback__
    else:
        raise Exception('illegal format for exception "{}"'.format(exception))

    def subscribe(observer, subscribe_scheduler):
        def action(_, __):
            def inner_action(_, __):
                observer.on_error(exception)

            return scheduler.schedule(inner_action)
        return subscribe_scheduler.schedule(action)
    return AnonymousObservable(subscribe)
