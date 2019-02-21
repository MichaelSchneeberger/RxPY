from rx import AnonymousObservable
from rx.core import Observer, Disposable
from rx.core import Observable
from rx.disposables import CompositeDisposable
from rx.internal import extensionmethod


@extensionmethod(Observable, alias="to_iterable")
def to_list(self):
    """Creates a list from an observable sequence.

    Returns an observable sequence containing a single element with a list
    containing all the elements of the source sequence."""

    def subscribe(observer, scheduler):
        buffer = [[]]

        class FastListObserver(Observer):
            def on_next(self, value):
                buffer[0].append(value)

            def on_error(self, error):
                observer.on_error(error)

            def on_completed(self):
                observer.on_next(buffer[0])
                observer.on_completed()

        def dispose_buffer():
            del buffer[0]

        disposable = self.unsafe_subscribe(FastListObserver(), scheduler=scheduler)
        return CompositeDisposable(disposable, Disposable.create(dispose_buffer))
    return AnonymousObservable(subscribe)
