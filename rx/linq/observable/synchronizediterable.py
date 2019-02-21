from rx import Observable, config, AnonymousObservable
from rx.internal import extensionmethod


@extensionmethod(Observable, instancemethod=True)
def synchronized_iterable(self, iterable, selector=None):
    lock = config["concurrency"].RLock()

    def default_selector(rcv_item, iter_item):
        return rcv_item, iter_item

    selector_ = selector or default_selector

    def subscribe(observer, scheduler):
        iterator = iter(iterable)

        def on_next(v):
            complete_observable = False
            try:
                with lock:
                    item = next(iterator)

            except StopIteration:
                complete_observable = True
            else:
                observer.on_next(selector_(v, item))

            if complete_observable:
                observer.on_completed()

        return self.unsafe_subscribe(on_next=on_next, on_error=observer.on_error, on_completed=observer.on_completed,
                                     scheduler=scheduler)

    return AnonymousObservable(subscribe)
