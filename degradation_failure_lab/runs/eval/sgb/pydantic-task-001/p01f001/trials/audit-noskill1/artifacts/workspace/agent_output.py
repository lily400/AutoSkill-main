from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, AfterValidator, WrapValidator

VALIDATION_LOG = []


def before_validator(value: Any):
    VALIDATION_LOG.append({"event": "before", "value": value})
    return value


def wrap_validator(value: Any, handler):
    VALIDATION_LOG.append({"event": "wrap_start", "value": value})
    result = handler(value)
    VALIDATION_LOG.append({"event": "wrap_end", "value": result})
    return result


def after_validator(value: int):
    VALIDATION_LOG.append({"event": "after", "value": value})
    return 2 * value + 10


class MyModel(BaseModel):
    value: Annotated[int, BeforeValidator(before_validator), WrapValidator(wrap_validator), AfterValidator(after_validator)]

    def model_post_init(self, __context):
        self.validation_log = VALIDATION_LOG
