import io
from contextlib import contextmanager
import sys

@contextmanager
def patch(obj_to_patch, attr, val):
    try:
        oldval = getattr(obj_to_patch, attr)
        setattr(obj_to_patch, attr, val)
        yield oldval
    finally:
        setattr(obj_to_patch, attr, oldval)

@contextmanager
def patch_stdout():
    stream = textstream()
    with patch(sys, 'stdout', stream):
        yield stream

@contextmanager
def patch_stderr():
    stream = textstream()
    with patch(sys, 'stderr', stream):
        yield stream

def textstream() -> io.TextIOWrapper:
    return io.TextIOWrapper(io.BytesIO())
