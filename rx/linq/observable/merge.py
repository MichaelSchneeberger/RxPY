import collections
import types

from rx.core import Scheduler, Observable, AnonymousObservable
from rx.disposables import CompositeDisposable, SingleAssignmentDisposable
from rx.concurrency import immediate_scheduler, CurrentThreadScheduler
from rx.internal import extensionmethod, extensionclassmethod


@extensionmethod(Observable, instancemethod=True)
def merge(self, sources):
    return Observable.merge([self] + sources)


@extensionclassmethod(Observable)  # noqa
def merge(cls, sources):
    """Merges all the observable sequences into a single observable
    sequence. The scheduler is optional and if not specified, the
    immediate scheduler is used.

    merged = rx.Observable.merge([xs, ys, zs])

    Returns the observable sequence that merges the elements of the
    observable sequences.
    """

    if isinstance(sources, types.GeneratorType) or isinstance(sources, collections.Iterable):
        sources_ = list(sources)
    elif isinstance(sources, list) or isinstance(sources, tuple):
        sources_ = sources
    else:
        raise Exception('argument "sources" needs to be a list or generator')

    def subscribe(observer, subscribe_scheduler):
        group = CompositeDisposable()

        for source in sources_:
            inner_subscription = SingleAssignmentDisposable()
            group.add(inner_subscription)

            def on_next(x):
                observer.on_next(x)

            def on_completed(inner_subscription=inner_subscription):
                group.remove(inner_subscription)
                if len(group) == 0:
                    observer.on_completed()

            disposable = source.unsafe_subscribe(on_next, observer.on_error, on_completed,
                                                 scheduler=subscribe_scheduler)
            inner_subscription.disposable = disposable
        return group

    return AnonymousObservable(subscribe)


@extensionmethod(Observable, alias="merge_observable")
def merge_all(self):
    """Merges an observable sequence of observable sequences into an
    observable sequence.

    Returns the observable sequence that merges the elements of the inner
    sequences.
    """

    sources = self

    def subscribe(observer, subscribe_scheduler):
        group = CompositeDisposable()
        is_stopped = [False]
        m = SingleAssignmentDisposable()
        group.add(m)

        def on_next(inner_source):
            inner_subscription = SingleAssignmentDisposable()
            group.add(inner_subscription)

            inner_source = Observable.from_future(inner_source)

            def on_next(x):
                observer.on_next(x)

            def on_completed():
                group.remove(inner_subscription)
                if is_stopped[0] and len(group) == 1:
                    observer.on_completed()

            # asynchronous situation
            # if subscribe_scheduler.queue is None:
            #     scheduler = CurrentThreadScheduler()
            # else:
            scheduler = subscribe_scheduler

            # subscribe not unsafe_subscribe!
            disposable = inner_source.subscribe(on_next, observer.on_error, on_completed, scheduler=scheduler)
            inner_subscription.disposable = disposable

        def on_completed():
            is_stopped[0] = True
            if len(group) == 1:
                observer.on_completed()

        m.disposable = sources.unsafe_subscribe(on_next, observer.on_error, on_completed, scheduler=subscribe_scheduler)
        return group

    return AnonymousObservable(subscribe)
