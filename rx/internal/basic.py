from datetime import datetime


# Defaults
def noop(*args, **kw):
    """No operation. Returns nothing"""
    pass


def identity(x):
    """Returns argument x"""
    return x


def default_now():
    return datetime.utcnow()


def default_comparer(x, y):
    return x == y


def default_sub_comparer(x, y):
    return x - y


def default_key_serializer(x):
    return str(x)


def default_error(exc):
    if isinstance(exc, tuple):
        exc_type, exc_value, exc_traceback = exc
        if exc_value is None:
            print(exc)
        raise exc_value.with_traceback(exc_traceback)
    else:
        raise exc
