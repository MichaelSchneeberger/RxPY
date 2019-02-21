from rx import AnonymousObservable
from rx.core import ObservableBase, Disposable
from rx.disposables import CompositeDisposable, MultipleAssignmentDisposable


class ConnectableObservable(ObservableBase):
    """Represents an observable that can be connected and disconnected."""

    def __init__(self, source, subject):
        self.subject = subject
        self.source = source.as_observable()
        self.has_subscription = False
        self.subscription = None

        import inspect
        curframe = inspect.currentframe()
        self.calframe = inspect.getouterframes(curframe, 2)

        super(ConnectableObservable, self).__init__()

    def _subscribe_core(self, observer, scheduler):
        return self.subject.unsafe_subscribe(observer, scheduler=scheduler)

    def connect(self, scheduler):
        """Connects the observable."""

        if not self.has_subscription:
            self.has_subscription = True

            def dispose():
                self.has_subscription = False

            disposable = self.source.unsafe_subscribe(self.subject, scheduler=scheduler)
            self.subscription = CompositeDisposable(disposable, Disposable.create(dispose))

        return self.subscription

    def ref_count(self, disposable: MultipleAssignmentDisposable = None):
        """Returns an observable sequence that stays connected to the
        source as long as there is at least one subscription to the
        observable sequence.
        """

        # connectable_subscription = [None]
        multi_assignment_disposable = disposable or MultipleAssignmentDisposable()
        count = [0]
        source = self
        first_scheduler = [None]

        def subscribe(observer, scheduler):
            count[0] += 1
            should_connect = count[0] == 1

            subscription = source.unsafe_subscribe(observer, scheduler=scheduler)

            if should_connect:
                first_scheduler[0] = scheduler
                disposable = source.connect(scheduler=scheduler)
                multi_assignment_disposable.disposable = disposable
            # else:
            #     assert first_scheduler[0] is scheduler, 'subscription scheduler need to be the same: {}'.format(self.calframe[4])

            def dispose():
                subscription.dispose()
                count[0] -= 1
                if not count[0]:
                    multi_assignment_disposable.dispose()

            disposable = Disposable.create(dispose)
            return disposable

        return AnonymousObservable(subscribe)

    def dispose_first(self, disposable: MultipleAssignmentDisposable = None):
        """Returns an observable sequence that stays connected to the
        source as long as there is at least one subscription to the
        observable sequence.
        """

        # connectable_subscription = [None]
        multi_assignment_disposable = disposable or MultipleAssignmentDisposable()
        count = [0]
        source = self
        first_scheduler = [None]
        is_disposed = [False]

        def subscribe(observer, scheduler):
            count[0] += 1
            should_connect = count[0] == 1

            subscription = source.unsafe_subscribe(observer, scheduler=scheduler)

            if should_connect:
                first_scheduler[0] = scheduler
                disposable = source.connect(scheduler=scheduler)
                multi_assignment_disposable.disposable = disposable
            # else:
            #     assert first_scheduler[0] is scheduler, 'subscription scheduler need to be the same: {}'.format(self.calframe[4])

            def dispose():
                subscription.dispose()
                if not is_disposed[0]:
                    is_disposed[0] = True
                    multi_assignment_disposable.dispose()

            disposable = Disposable.create(dispose)
            return disposable

        return AnonymousObservable(subscribe)

    def auto_connect(self, subscriber_count):
        """Returns an observable sequence that stays connected to the
        source indefinitely to the observable sequence.
        Providing a subscriber_count will cause it to connect() after that many subscriptions occur.
        A subscriber_count of 0 will result in emissions firing immediately without waiting for subscribers.
        """

        assert 0 < subscriber_count, 'subscriber count needs to be bigger than 0'

        connectable_subscription = [None]
        count = [0]
        source = self
        is_connected = [False]

        def subscribe(observer, scheduler):
            count[0] += 1
            should_connect = count[0] == subscriber_count and not is_connected[0]
            subscription = source.subscribe(observer)

            if should_connect:
                connectable_subscription[0] = source.connect(scheduler)
                is_connected[0] = True

            def dispose():
                subscription.dispose()
                count[0] -= 1
                is_connected[0] = False
                if not count[0]:
                    connectable_subscription[0].dispose()

            return Disposable.create(dispose)

        return AnonymousObservable(subscribe)
