from rx import Observable, AnonymousObservable
from rx.internal import extensionmethod


@extensionmethod(Observable)
def first_or_empty(self):
    """
    todo: test operator

    :param self:
    :return:
    """

    def subscribe(observer, scheduler):
        def on_next(x):
            observer.on_next(x)
            observer.on_completed()

        return self.unsafe_subscribe(on_next, observer.on_error, observer.on_completed, scheduler=scheduler)
    return AnonymousObservable(subscribe)
