import asyncio
from typing import Callable

from rx.concurrency import CurrentThreadScheduler
from rx.core import Observable
from rx.core.future import Future
from rx.internal import extensionmethod


@extensionmethod(Observable)
def to_future(self, loop: asyncio.AbstractEventLoop, awaited_hook: Callable[[Future], None] = None):
    """Converts an existing observable sequence to a asyncio Future
    """

    source = self

    future = Future(loop=loop, awaited_hook=awaited_hook)

    value = [None]
    has_value = [False]

    def on_next(v):
        value[0] = v
        has_value[0] = True

    def on_error(err):
        def func():
            # execute on proper thread
            if isinstance(err, tuple):
                future.set_exception(err[1])
            else:
                try:
                    future.set_exception(err)
                except:
                    raise Exception('illegal exception "{}"'.format(err))

        loop.call_soon_threadsafe(func)

    def on_completed():
        if has_value[0]:
            def func():
                # execute on proper thread
                future.set_result(value[0])

            loop.call_soon_threadsafe(func)

    subscribe_scheduler = CurrentThreadScheduler()
    source.unsafe_subscribe(on_next, on_error, on_completed, scheduler=subscribe_scheduler)

    # No cancellation can be done
    return future


# @extensionmethod(Observable)
# def __await__(self):
#     """Awaits the given observable
#     :returns: The last item of the observable sequence.
#     :rtype: Any
#     :raises TypeError: If key is not of type int or slice
#     """
#     return iter(self.to_future())

