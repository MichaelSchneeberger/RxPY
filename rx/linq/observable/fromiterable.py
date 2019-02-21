from rx import config
from rx.core import Observable, AnonymousObservable, Disposable
from rx.concurrency import current_thread_scheduler
from rx.disposables import MultipleAssignmentDisposable
from rx.internal import extensionclassmethod


@extensionclassmethod(Observable, alias=["from_", "from_list"])
def from_iterable(cls, iterable, scheduler=None):
    """Converts an array to an observable sequence, using an optional
    scheduler to enumerate the array.

    1 - res = rx.Observable.from_iterable([1,2,3])
    2 - res = rx.Observable.from_iterable([1,2,3], rx.Scheduler.timeout)

    Keyword arguments:
    :param Observable cls: Observable class
    :param Scheduler scheduler: [Optional] Scheduler to run the
        enumeration of the input sequence on.

    :returns: The observable sequence whose elements are pulled from the
        given enumerable sequence.
    :rtype: Observable
    """

    lock = config["concurrency"].RLock()

    if scheduler is None:
        def subscribe(observer, subscribe_scheduler):
            sd = MultipleAssignmentDisposable()
            iterator = iter(iterable)

            def action(_, __):
                break_loop = [False]

                def dispose_loop():
                    break_loop[0] = True

                sd.disposable = Disposable.create(dispose_loop)

                while True:
                    if break_loop[0]:
                        break
                    try:
                        with lock:
                            item = next(iterator)
                    except StopIteration:
                        observer.on_completed()
                        break
                    else:
                        observer.on_next(item)

            sd.disposable = subscribe_scheduler.schedule(action)
            return sd

        return AnonymousObservable(subscribe)
    else:
        def subscribe(observer, subscribe_scheduler):
            sd = MultipleAssignmentDisposable()
            iterator = iter(iterable)

            def action(_, __):
                def inner_action(_, __):
                    try:
                        with lock:
                            item = next(iterator)

                    except StopIteration:
                        observer.on_completed()
                    else:
                        observer.on_next(item)
                        sd.disposable = scheduler.schedule(inner_action)
                return scheduler.schedule(inner_action)

            sd.disposable = subscribe_scheduler.schedule(action)
            return sd
        return AnonymousObservable(subscribe)
