from __future__ import annotations

from dataclasses import MISSING
from enum import Enum
from typing import Any, get_args, get_origin, get_type_hints


class ValidationError(ValueError):
    pass


class ConfigDict(dict):
    pass


class FieldInfo:
    def __init__(self, default: Any = MISSING, default_factory: Any = None):
        self.default = default
        self.default_factory = default_factory


def Field(default: Any = MISSING, default_factory: Any = None) -> Any:
    return FieldInfo(default=default, default_factory=default_factory)


class BaseModel:
    model_config: dict[str, Any] = {}

    def __init__(self, **kwargs: Any) -> None:
        annotations = get_type_hints(self.__class__)
        extras = set(kwargs.keys()) - set(annotations.keys())
        if extras and self.model_config.get("extra") == "forbid":
            raise ValidationError(f"extra fields not permitted: {sorted(extras)}")

        for name, expected in annotations.items():
            raw_default = getattr(self.__class__, name, MISSING)
            if isinstance(raw_default, FieldInfo):
                if name in kwargs:
                    value = kwargs[name]
                elif raw_default.default_factory is not None:
                    value = raw_default.default_factory()
                elif raw_default.default is not MISSING:
                    value = raw_default.default
                else:
                    raise ValidationError(f"missing required field: {name}")
            elif raw_default is not MISSING:
                value = kwargs.get(name, raw_default)
            else:
                if name not in kwargs:
                    raise ValidationError(f"missing required field: {name}")
                value = kwargs[name]

            try:
                coerced = self._validate_type(expected, value)
            except ValidationError:
                raise
            except Exception as exc:
                raise ValidationError(f"invalid field {name}: {exc}") from exc
            setattr(self, name, coerced)

    @classmethod
    def model_validate(cls, payload: dict[str, Any]) -> "BaseModel":
        return cls(**payload)

    def model_dump(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        for key in get_type_hints(self.__class__):
            value = getattr(self, key)
            data[key] = self._dump_value(value)
        return data

    @classmethod
    def _dump_value(cls, value: Any) -> Any:
        if isinstance(value, BaseModel):
            return value.model_dump()
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, list):
            return [cls._dump_value(v) for v in value]
        if isinstance(value, dict):
            return {k: cls._dump_value(v) for k, v in value.items()}
        return value

    @classmethod
    def _validate_type(cls, expected: Any, value: Any) -> Any:
        origin = get_origin(expected)
        args = get_args(expected)

        if origin is list:
            if not isinstance(value, list):
                raise ValidationError("expected list")
            return [cls._validate_type(args[0], v) for v in value]

        if origin is dict:
            if not isinstance(value, dict):
                raise ValidationError("expected dict")
            return {k: cls._validate_type(args[1], v) for k, v in value.items()}

        if origin is tuple:
            if not isinstance(value, tuple):
                raise ValidationError("expected tuple")
            return value

        if origin is Any:
            return value

        if origin is not None and str(origin).endswith("Literal"):
            if value not in args:
                raise ValidationError(f"expected one of {args}")
            return value

        if origin is None and hasattr(expected, "__args__") and type(None) in expected.__args__:
            if value is None:
                return None
            non_none = [a for a in expected.__args__ if a is not type(None)][0]
            return cls._validate_type(non_none, value)

        if isinstance(expected, type) and issubclass(expected, Enum):
            if isinstance(value, expected):
                return value
            try:
                return expected(value)
            except Exception as exc:
                raise ValidationError(str(exc)) from exc

        if isinstance(expected, type) and issubclass(expected, BaseModel):
            if isinstance(value, expected):
                return value
            if isinstance(value, dict):
                return expected(**value)
            raise ValidationError("expected object")

        if expected is Any:
            return value

        if expected is bool:
            if not isinstance(value, bool):
                raise ValidationError("expected bool")
            return value

        if expected in (str, int, float):
            if not isinstance(value, expected):
                raise ValidationError(f"expected {expected.__name__}")
            return value

        return value
