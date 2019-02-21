import collections
import sys
import types

from rx.core import Observable, AnonymousObservable
from rx.disposables import CompositeDisposable, SingleAssignmentDisposable
from rx.internal import extensionmethod, extensionclassmethod


@extensionmethod(Observable, instancemethod=True)
def zip(self, sources, result_selector=None, scheduler=None):
    """Merges the specified observable sequences into one observable
    sequence by using the selector function whenever all of the observable
    sequences or an array have produced an element at a corresponding index.

    The last element in the arguments must be a function to invoke for each
    series of elements at corresponding indexes in the sources.

    1 - res = obs1.zip(obs2, fn)
    2 - res = x1.zip([1,2,3], fn)

    Returns an observable sequence containing the result of combining
    elements of the sources using the specified result selector function.
    """

    return Observable.zip([self] + sources, result_selector=result_selector, scheduler=scheduler)


@extensionclassmethod(Observable)
def zip(cls, sources, result_selector=None, scheduler=None):
    """Merges the specified observable sequences into one observable
    sequence by using the selector function whenever all of the observable
    sequences have produced an element at a corresponding index.

    The last element in the arguments must be a function to invoke for each
    series of elements at corresponding indexes in the sources.

    Arguments:
    args -- Observable sources.

    Returns an observable {Observable} sequence containing the result of
    combining elements of the sources using the specified result selector
    function.
    """

    if isinstance(sources, types.GeneratorType) or isinstance(sources, collections.Iterable):
        sources_ = list(sources)
    elif isinstance(sources, list) or isinstance(sources, tuple):
        sources_ = sources
    else:
        raise Exception('argument "sources" needs to be a list or generator')

    result_selector_ = result_selector or (lambda *v: list(v))

    if len(sources_) == 0:
        return Observable.empty(scheduler=scheduler)
    elif len(sources_) == 1:
        return sources_[0].map(lambda v, _: result_selector_(v))
    else:
        def subscribe(observer, scheduler):
            n = len(sources_)
            queues = [[] for _ in range(n)]
            is_done = [False] * n

            def next(i):
                if all([len(q) for q in queues]):
                    try:
                        queued_values = [x.pop(0) for x in queues]
                        res = result_selector_(*queued_values)
                    except Exception as ex:
                        exc_tuple = sys.exc_info()
                        observer.on_error(exc_tuple)
                        return

                    observer.on_next(res)
                elif all([x for j, x in enumerate(is_done) if j != i]):
                    observer.on_completed()

            def done(i):
                is_done[i] = True
                if all(is_done):
                    observer.on_completed()

            subscriptions = [None]*n

            def func(i):
                source = sources_[i]
                sad = SingleAssignmentDisposable()
                source = Observable.from_future(source)

                def on_next(x):
                    queues[i].append(x)
                    next(i)

                sad.disposable = source.unsafe_subscribe(on_next, observer.on_error, lambda: done(i),
                                                         scheduler=scheduler)
                subscriptions[i] = sad
            for idx in range(n):
                func(idx)
            return CompositeDisposable(subscriptions)
    return AnonymousObservable(subscribe)
