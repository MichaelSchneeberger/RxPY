import asyncio
from typing import TypeVar, Generic, Callable

from rx.core.typing import A


class Future(asyncio.Future, Generic[A]):
    def __init__(self, loop: asyncio.AbstractEventLoop, awaited_hook: Callable[['Future'], None] = None):
        super().__init__(loop=loop)

        self._awaited_hook = awaited_hook

    def __await__(self):
        if self._awaited_hook is not None:
            self._awaited_hook(self)

        return super().__await__()
