import types
from abc import abstractmethod

from rx import config
from rx.concurrency import CurrentThreadScheduler
from rx.disposables import SingleAssignmentDisposable

from . import Observer, Observable, Disposable
from .anonymousobserver import AnonymousObserver
from .autodetachobserver import AutoDetachObserver


class ObservableBase(Observable):
    """Represents a push-style collection."""

    def __init__(self):
        self.lock = config["concurrency"].RLock()

        # Deferred instance method assignment
        for name, method in self._methods:
            setattr(self, name, types.MethodType(method, self))

    def subscribe(self, on_next=None, on_error=None, on_completed=None, observer=None, scheduler=None):
        single_assignment_disposable = SingleAssignmentDisposable()

        def action(_, __):
            disposable = self.unsafe_subscribe(on_next=on_next, on_error=on_error, on_completed=on_completed,
                                         observer=observer, scheduler=scheduler)
            single_assignment_disposable.disposable = disposable

        scheduler = scheduler or CurrentThreadScheduler()
        scheduler.schedule(action)
        return single_assignment_disposable

    def unsafe_subscribe(self, on_next=None, on_error=None, on_completed=None, observer=None, scheduler=None):
        """Subscribe an observer to the observable sequence.

        Examples:
        1 - source.subscribe()
        2 - source.subscribe(observer)
        3 - source.subscribe(on_next)
        4 - source.subscribe(on_next, on_error)
        5 - source.subscribe(on_next, on_error, on_completed)

        Keyword arguments:
        on_next -- [Optional] Action to invoke for each element in the
            observable sequence.
        on_error -- [Optional] Action to invoke upon exceptional
            termination of the observable sequence.
        on_completed -- [Optional] Action to invoke upon graceful
            termination of the observable sequence.
        observer -- [Optional] The object that is to receive
            notifications. You may subscribe using an observer or
            callbacks, not both.

        Return disposable object representing an observer's subscription
            to the observable sequence.
        """
        # Accept observer as first parameter
        if isinstance(on_next, Observer):
            observer = on_next
        elif hasattr(on_next, "on_next") and callable(on_next.on_next):
            observer = on_next
        elif not observer:
            observer = AnonymousObserver(on_next, on_error, on_completed)

        auto_detach_observer = AutoDetachObserver(observer)

        try:
            subscriber = self._subscribe_core(auto_detach_observer, scheduler=scheduler)
        except Exception as ex:
            if not auto_detach_observer.fail(ex):
                raise
        else:
            if not hasattr(subscriber, "dispose"):
                subscriber = Disposable.create(subscriber)

            auto_detach_observer.disposable =  subscriber

        # Hide the identity of the auto detach observer
        return Disposable.create(auto_detach_observer.dispose)

    @abstractmethod
    def _subscribe_core(self, observer, scheduler):
        return NotImplemented
