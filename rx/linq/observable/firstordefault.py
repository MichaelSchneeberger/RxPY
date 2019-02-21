import sys

from rx import Observable, AnonymousObservable
from rx.internal.exceptions import SequenceContainsNoElementsError
from rx.internal import extensionmethod


def first_or_default_async(source, has_default=False, default_value=None, raise_exception_func=None):
    def subscribe(observer, scheduler):
        def on_next(x):
            observer.on_next(x)
            observer.on_completed()

        def on_completed():
            if not has_default:
                def raise_exception(msg=None):
                    raise SequenceContainsNoElementsError(msg=msg)

                try:
                    if raise_exception_func is None:
                        raise_exception()
                    else:
                        raise_exception_func(raise_exception)
                except:
                    exc_tuple = sys.exc_info()
                    observer.on_error(exc_tuple)
            else:
                observer.on_next(default_value)
                observer.on_completed()

        return source.unsafe_subscribe(on_next, observer.on_error, on_completed, scheduler=scheduler)
    return AnonymousObservable(subscribe)


@extensionmethod(Observable)
def first_or_default(self, predicate=None, default_value=None):
    """Returns the first element of an observable sequence that satisfies
    the condition in the predicate, or a default value if no such element
    exists.

    Example:
    res = source.first_or_default()
    res = source.first_or_default(lambda x: x > 3)
    res = source.first_or_default(lambda x: x > 3, 0)
    res = source.first_or_default(null, 0)

    Keyword arguments:
    predicate -- {Function} [optional] A predicate function to evaluate for
        elements in the source sequence.
    default_value -- {Any} [Optional] The default value if no such element
        exists.  If not specified, defaults to None.

    Returns {Observable} Sequence containing the first element in the
    observable sequence that satisfies the condition in the predicate, or a
    default value if no such element exists.
    """

    return self.filter(predicate).first_or_default(None, default_value) if predicate else first_or_default_async(self, True, default_value)
