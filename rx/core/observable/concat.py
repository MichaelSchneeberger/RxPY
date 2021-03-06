from typing import Iterable

from rx.disposable import Disposable
from rx.core import Observable
from rx.disposable import SingleAssignmentDisposable, CompositeDisposable, SerialDisposable
from rx.concurrency import current_thread_scheduler


def _concat_with_iterable(sources: Iterable[Observable]) -> Observable:

    sources_ = iter(sources)

    def subscribe(observer, scheduler=None):
        scheduler = scheduler or current_thread_scheduler

        subscription = SerialDisposable()
        cancelable = SerialDisposable()
        is_disposed = False

        def action(action1, state=None):
            nonlocal is_disposed
            if is_disposed:
                return

            def on_completed():
                cancelable.disposable = scheduler.schedule(action)

            try:
                current = next(sources_)
            except StopIteration:
                observer.on_completed()
            except Exception as ex:  # pylint: disable=broad-except
                observer.on_error(ex)
            else:
                d = SingleAssignmentDisposable()
                subscription.disposable = d
                d.disposable = current.subscribe_(observer.on_next, observer.on_error, on_completed, scheduler)

        cancelable.disposable = scheduler.schedule(action)

        def dispose():
            nonlocal is_disposed
            is_disposed = True

        return CompositeDisposable(subscription, cancelable, Disposable(dispose))
    return Observable(subscribe)
