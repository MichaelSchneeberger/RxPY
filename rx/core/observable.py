import asyncio
from abc import ABCMeta, abstractmethod
from typing import Generic, Any, Iterable, Callable, List

from rx.core.future import Future
from rx.core.observer import Observer
from rx.core.scheduler import Scheduler
from rx.core.typing import A, B, C


class Observable(Generic[A], metaclass=ABCMeta):
    @abstractmethod
    def subscribe(self, observer: Observer[A]):
        return NotImplemented

    @abstractmethod
    def unsafe_subscribe(self, observer: Observer[A], scheduler: Scheduler):
        return NotImplemented

    def default_if_empty(self, default_value=None) -> 'Observable[A]':
        pass

    @classmethod
    def defer(cls, observable_factory: Callable[[], 'Observable[A]']) -> 'Observable[A]':
        pass

    def delay(self, duetime, scheduler=None) -> 'Observable[A]':
        pass

    @classmethod
    def empty(cls, scheduler: Scheduler = None) -> 'Observable':
        pass

    @classmethod
    def just(cls, value: A, scheduler: Scheduler = None) -> 'Observable[A]':
        pass

    @classmethod
    def from_(cls, iterable: Iterable[A], scheduler: Scheduler = None) -> 'Observable[A]':
        pass

    @classmethod
    def merge(cls, sources: List['Observable[A]']) -> 'Observable[A]':
        pass

    @classmethod
    def zip(cls, sources: List['Observable[A]'], result_selector: Callable[..., B] = None) -> 'Observable[B]':
        pass

    def filter(self, predicate: Callable[[A, int], bool]) -> 'Observable[A]':
        pass

    def first(self, predicate=None, raise_exception_func: Callable[[Callable[[], None]], None] = None) \
            -> 'Observable[A]':
        pass

    def flat_map(self, selector: Callable[[A, int], 'Observable[B]']) -> 'Observable[B]':
        pass

    def last(self, predicate=None, raise_exception_func: Callable[[Callable[[], None]], None] = None) \
            -> 'Observable[A]':
        pass

    def let(self, func: Callable[['Observable[A]'], 'Observable[B]'], **kwargs) -> 'Observable[B]':
        pass

    def map(self, selector: Callable[[A, int], B]) -> 'Observable[B]':
        pass

    def merge_all(self) -> 'Observable[B]':
        pass

    def multicast(self, subject=None, subject_selector=None, selector=None) -> 'Observable[A]':
        pass

    def observe_on(self, scheduler: Scheduler) -> 'Observable[A]':
        pass

    def synchronized_iterable(self, iterable: Iterable[B], selector: Callable[[A, B], C] =None) -> 'Observable[C]':
        pass

    def reduce(self, accumulator: Callable[[B, A], B], seed: B = None) -> 'Observable[B]':
        pass

    def share(self) -> 'Observable[A]':
        pass

    def start_with(self, *args, **kw) -> 'Observable[A]':
        pass

    def take_while(self, predicate: Callable[[A, int], bool]) -> 'Observable[A]':
        pass

    def to_future(self, loop: asyncio.AbstractEventLoop, awaited_hook: Callable[[Future], None] = None):
        pass

    def to_list(self) -> 'Observable[List[A]]':
        pass
