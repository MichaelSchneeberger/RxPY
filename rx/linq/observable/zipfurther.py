from rx.core import Observable, AnonymousObservable
from rx.disposables import CompositeDisposable, SingleAssignmentDisposable
from rx.internal import extensionmethod




@extensionmethod(Observable, instancemethod=True)
def zip_further(self, sources, result_selector=lambda *v: v):
    """ zips two observables

    todo: test operator

    In case one observable emits less elements than the other observable, None elements are used as a filling.
    """

    def subscribe(observer, scheduler):
        n = len(sources)
        queues = [[] for _ in range(n)]
        is_done = [False] * n

        def next(i):
            if all([len(q) or is_done[j] for j, q in enumerate(queues)]):
                try:
                    def gen1():
                        for j, q in enumerate(queues):
                            if is_done[j]:
                                # yield None if completed
                                yield None
                            else:
                                yield q.pop(0)
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
            while(not all([len(q)==0 for q in queues])):
                next(0)
            if all(is_done):
                observer.on_completed()

        subscriptions = [None]*n

        def func(i):
            source = sources[i]
            sad = SingleAssignmentDisposable()
            source = Observable.from_future(source)

            def on_next(x):
                queues[i].append(x)
                next(i)

            sad.disposable = source.unsafe_subscribe(on_next, observer.on_error, lambda: done(i), scheduler=scheduler)
            subscriptions[i] = sad
        for idx in range(n):
            func(idx)
        return CompositeDisposable(subscriptions)
    return AnonymousObservable(subscribe)
