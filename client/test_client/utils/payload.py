# ====================================================================
# payload.py
# ====================================================================

from typing import (
    Any,
    TypeVar,
    Hashable,
)

from pydantic import BaseModel

Model = TypeVar("Model", bound=BaseModel)
DEFAULT_EXCLUDE = ("cls", "self", "__class__")


# --------------------------------------------------------------------
# filter_dictionary_none_values
#
# Извлечь все не NoneType значения и преобразовать всё в str
# --------------------------------------------------------------------
def filter_dictionary_none_values(
    dictionary: dict[Hashable, Any]
) -> dict[Hashable, str]:

    return {
        key: str(value)
        for key, value in dictionary.items()
        if value is not None
    }


# --------------------------------------------------------------------
# make_payload
#
# --------------------------------------------------------------------
def make_payload(**kwargs: Any) -> dict[Hashable, Any]:

    exclude_list = kwargs.pop("exclude", ())
    return {
        key: value
        for key, value in kwargs.items()
        if key not in DEFAULT_EXCLUDE + exclude_list and value is not None
    }
