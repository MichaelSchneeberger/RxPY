import collections
import types

from rx.core import Observable, AnonymousObservable
from rx.disposables import CompositeDisposable, SingleAssignmentDisposable
from rx.internal import extensionmethod, extensionclassmethod


@extensionmethod(Observable, instancemethod=True)
def zip_last(self, sources, result_selector=None, scheduler=None):
    return Observable.zip_last([self] + sources, result_selector=result_selector, scheduler=scheduler)


@extensionclassmethod(Observable)
def zip_last(self, sources, result_selector=None, scheduler=None):
    """ zips two observables together.

    todo: test operator

    In case one observable emits less elements than the other observable, None elements are used as a filling.
    """

    if isinstance(sources, types.GeneratorType) or isinstance(sources, collections.Iterable):
        sources_ = list(sources)
    elif isinstance(sources, list) or isinstance(sources, tuple):
        sources_ = sources
    else:
        raise Exception('argument "sources" needs to be a list or generator')

    result_selector_ = result_selector or (lambda *v: v)

    if len(sources_) == 0:
        return Observable.empty(scheduler=scheduler)
    elif len(sources_) == 1:
        return sources_[0].map(lambda v, _: result_selector_(v))
    else:
        def subscribe(observer, scheduler):
            n = len(sources)
            queues = [[] for _ in range(n)]
            is_done = [False] * n
            last_values = [None for _ in range(n)]

            def next(i):
                if all([len(q) or is_done[j] for j, q in enumerate(queues)]):
                    try:
                        def gen1():
                            for j, q in enumerate(queues):
                                if is_done[j]:
                                    yield last_values[j]
                                else:
                                    val = q.pop(0)
                                    last_values[j] = val
                                    yield val

                        queued_values = list(gen1())
                        res = result_selector(*queued_values)
                    except Exception as ex:
                        observer.on_error(ex)
                        return True

                    observer.on_next(res)
                    return True
                return False

            def done(i):
                is_done[i] = True
                while (not all([len(q) == 0 for q in queues])):
                    next(0)
                if all(is_done):
                    observer.on_completed()

            subscriptions = [None] * n

            def func(i):
                source = sources[i]
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



