from typing import Callable

from rx.core import Observer
from rx.core import Disposable, Scheduler
from .observablebase import ObservableBase


class AnonymousObservable(ObservableBase):
    """Class to create an Observable instance from a delegate-based
    implementation of the Subscribe method."""

    def __init__(self, subscribe: Callable[[Observer, Scheduler], Disposable]):
        """Creates an observable sequence object from the specified
        subscription function.

        Keyword arguments:
        :param types.FunctionType subscribe: Subscribe method implementation.
        """

        self._subscribe = subscribe
        super(AnonymousObservable, self).__init__()

    def _subscribe_core(self, observer, scheduler):
        return self._subscribe(observer, scheduler)
