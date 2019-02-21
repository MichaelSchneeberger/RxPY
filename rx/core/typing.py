from typing import TypeVar, Callable, Any

A = TypeVar('A', covariant=True)
B = TypeVar('B', covariant=True)
C = TypeVar('C', contravariant=True)

OnNext = Callable[[Any], None]
OnError = Callable[[Exception], None]
OnCompleted = Callable[[], None]

Mapper = Callable[[Any], Any]
MapperIndexed = Callable[[Any, int], Any]
Predicate = Callable[[Any], bool]
PredicateIndexed = Callable[[Any, int], bool]
Accumulator = Callable[[Any, Any], Any]
Dispose = Callable[[], None]