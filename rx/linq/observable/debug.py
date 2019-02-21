from rx import Observable, AnonymousObservable, Observer
from rx.core import Disposable
from rx.disposables import CompositeDisposable
from rx.internal import extensionmethod


@extensionmethod(Observable, instancemethod=True)
def debug(self, name):

    def subscribe(observer, scheduler):
        print('{} subscribe({}, {}), scheduler active = {}'.format(name, observer, scheduler,
                                                                   scheduler.queue is not None))

        class DebugObserver(Observer):
            def on_next(self, value):
                print('{} on_next({})'.format(name, value))
                observer.on_next(value)

            def on_error(self, error):
                print('{} on_error({})'.format(name, error))
                observer.on_error(error)

            def on_completed(self):
                print('{} on_completed()'.format(name))
                observer.on_completed()

        disposable = self.unsafe_subscribe(DebugObserver(), scheduler=scheduler)

        debug = Disposable.create(lambda: print('{} disposed'.format(name)))
        return CompositeDisposable(disposable, debug)

    return AnonymousObservable(subscribe)