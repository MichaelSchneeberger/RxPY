from rx import Observable
from rx.internal import extensionmethod

from .firstordefault import first_or_default_async


@extensionmethod(Observable)
def first(self, predicate=None, raise_exception_func=None):
    """Returns the first element of an observable sequence that satisfies
    the condition in the predicate if present else the first item in the
    sequence.

    Example:
    res = res = source.first()
    res = res = source.first(lambda x: x > 3)

    Keyword arguments:
    predicate -- {Function} [Optional] A predicate function to evaluate for
        elements in the source sequence.

    Returns {Observable} Sequence containing the first element in the
    observable sequence that satisfies the condition in the predicate if
    provided, else the first item in the sequence.
    """

    if predicate:
        return self.filter(predicate) \
            .first(raise_exception_func=raise_exception_func)
    else:
        return first_or_default_async(self, False,
                                      raise_exception_func=raise_exception_func)
