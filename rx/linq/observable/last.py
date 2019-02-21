from rx import Observable
from rx.internal import extensionmethod

from .lastordefault import last_or_default_async


@extensionmethod(Observable)
def last(self, predicate=None, raise_exception_func=None):
    """Returns the last element of an observable sequence that satisfies the
    condition in the predicate if specified, else the last element.

    Example:
    res = source.last()
    res = source.last(lambda x: x > 3)

    Keyword arguments:
    predicate -- {Function} [Optional] A predicate function to evaluate for
        elements in the source sequence.

    Returns {Observable} Sequence containing the last element in the
    observable sequence that satisfies the condition in the predicate.
    """

    if predicate is not None:
        return_obs = self.filter(predicate).last(raise_exception_func=raise_exception_func)
    else:
        return_obs = last_or_default_async(self, False, raise_exception_func=raise_exception_func)

    return return_obs
