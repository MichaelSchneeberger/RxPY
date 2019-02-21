from rx.core import Observable, AnonymousObservable, Disposable
from rx.concurrency import current_thread_scheduler, immediate_scheduler
from rx.internal import extensionclassmethod
from rx.disposables import MultipleAssignmentDisposable


@extensionclassmethod(Observable)
def range(cls, start, count, scheduler=None):
    """Generates an observable sequence of integral numbers within a
    specified range, using the specified scheduler to send out observer
    messages.

    1 - res = Rx.Observable.range(0, 10)
    2 - res = Rx.Observable.range(0, 10, rx.Scheduler.timeout)

    Keyword arguments:
    start -- The value of the first integer in the sequence.
    count -- The number of sequential integers to generate.
    scheduler -- [Optional] Scheduler to run the generator loop on. If not
        specified, defaults to Scheduler.current_thread.

    Returns an observable sequence that contains a range of sequential
    integral numbers.
    """

    if scheduler is None:
        def subscribe(observer, subscribe_scheduler):
            sd = MultipleAssignmentDisposable()

            def action(_, __):
                break_loop = [False]

                def dispose_loop():
                    break_loop[0] = True

                sd.disposable = Disposable.create(dispose_loop)

                for n in range(start, count):
                    observer.on_next(n)

                observer.on_completed()

            sd.disposable = subscribe_scheduler.schedule(action)
            return sd

        return AnonymousObservable(subscribe)

    else:
        def subscribe(observer, subscribe_scheduler):
            sd = MultipleAssignmentDisposable()
            end = start + count

            def action(_, __):
                def inner_action(_, n):
                    if n < end:
                        observer.on_next(n)
                        sd.disposable = scheduler.schedule(inner_action, n + 1)
                    else:
                        observer.on_completed()

                return scheduler.schedule(inner_action, start)
            sd.disposable = subscribe_scheduler.schedule(action)

            return sd
        return AnonymousObservable(subscribe)
