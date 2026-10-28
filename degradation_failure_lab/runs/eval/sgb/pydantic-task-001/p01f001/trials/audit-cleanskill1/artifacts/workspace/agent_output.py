from __future__ import annotations

from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, WrapValidator, AfterValidator
from pydantic import ValidationInfo

VALIDATION_LOG: list[dict[str, Any]] = []


def _before_validator(value: Any) -> Any:
    VALIDATION_LOG.append({"event": "before", "value": value})
    # Convert raw input x into an intermediate value that, after inner int parsing
    # and the after-validator below, yields 2*x + 10.
    return value * 2 + 5


def _wrap_validator(value: Any, handler, info: ValidationInfo) -> Any:
    VALIDATION_LOG.append({"event": "wrap_start", "value": value})
    result = handler(value)
    VALIDATION_LOG.append({"event": "wrap_end", "value": result})
    return result


def _after_validator(value: int) -> int:
    VALIDATION_LOG.append({"event": "after", "value": value})
    return value * 2


class MyModel(BaseModel):
    value: Annotated[
        int,
        AfterValidator(_after_validator),
        WrapValidator(_wrap_validator),
        BeforeValidator(_before_validator),
    ]

    def model_post_init(self, __context: Any) -> None:
        # Expose the structured log on the instance as well.
        object.__setattr__(self, "validation_log", VALIDATION_LOG)
