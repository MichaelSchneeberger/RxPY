import sys

from rx.core import Observable, AnonymousObservable
from rx.internal import extensionclassmethod


@extensionclassmethod(Observable)
def defer(cls, observable_factory):
    """Returns an observable sequence that invokes the specified factory
    function whenever a new observer subscribes.

    Example:
    1 - res = rx.Observable.defer(lambda: rx.Observable.from_([1,2,3]))

    Keyword arguments:
    :param types.FunctionType observable_factory: Observable factory function
        to invoke for each observer that subscribes to the resulting sequence.

    :returns: An observable sequence whose observers trigger an invocation
    of the given observable factory function.
    :rtype: Observable
    """

    def subscribe(observer, scheduler):
        try:
            result = observable_factory()
        except Exception:
            exc_info = sys.exc_info()
            return Observable.throw_exception(exc_info).subscribe(observer)

        result = Observable.from_future(result)
        return result.unsafe_subscribe(observer, scheduler=scheduler)
    return AnonymousObservable(subscribe)
