from __future__ import annotations

import importlib
from typing import Any, Callable

NUMBA_AVAILABLE = importlib.util.find_spec("numba") is not None

if NUMBA_AVAILABLE:
    from numba import njit  # type: ignore
    from numba import types  # type: ignore
    from numba.typed import Dict  # type: ignore

    def typed_dict_empty():
        return Dict.empty(key_type=types.int64, value_type=types.int64)

else:

    def njit(*args: Any, **kwargs: Any):
        if args:
            fn = args[0]
            return fn

        def decorator(fn: Callable[..., Any]):
            return fn

        return decorator

    def typed_dict_empty():
        return {}
