from abc import ABCMeta, abstractmethod
from typing import Generic

from rx.core.typing import A


class Observer(Generic[A], metaclass=ABCMeta):
    @abstractmethod
    def on_next(self, value):
        return NotImplemented

    @abstractmethod
    def on_error(self, error):
        return NotImplemented

    @abstractmethod
    def on_completed(self):
        return NotImplemented
