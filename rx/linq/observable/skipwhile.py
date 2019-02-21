import sys

from rx import Observable, AnonymousObservable
from rx.internal.utils import adapt_call
from rx.internal import extensionmethod


@extensionmethod(Observable)
def skip_while(self, predicate):
    """Bypasses elements in an observable sequence as long as a specified
    condition is true and then returns the remaining elements. The
    element's index is used in the logic of the predicate function.

    1 - source.skip_while(lambda value: value < 10)
    2 - source.skip_while(lambda value, index: value < 10 or index < 10)

    predicate -- A function to test each element for a condition; the
        second parameter of the function represents the index of the
        source element.

    Returns an observable sequence that contains the elements from the
    input sequence starting at the first element in the linear series that
    does not pass the test specified by predicate.
    """

    predicate = adapt_call(predicate)
    source = self

    def subscribe(observer, scheduler):
        i, running = [0], [False]

        def on_next(value):
            if not running[0]:
                try:
                    running[0] = not predicate(value, i[0])
                except Exception as exn:
                    exc_tuple = sys.exc_info()
                    observer.on_error(exc_tuple)
                    return
                else:
                    i[0] += 1

            if running[0]:
                observer.on_next(value)

        return source.unsafe_subscribe(on_next, observer.on_error, observer.on_completed, scheduler=scheduler)
    return AnonymousObservable(subscribe)
