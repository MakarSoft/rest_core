# ====================================================================
# api_method.py
# ====================================================================

import abc
from typing import (
    Optional,
    Any,
    TypeVar,
    Generic,
    ClassVar,
    Callable,
    Set,
    cast,
    Union,
    no_type_check,
)

from sentinel import Sentinel
from pydantic import BaseModel, ConfigDict, model_validate, parse_obj_as

from pydantic.fields import ModelField
from pydantic.generics import GenericModel

from aiomonobank.core.session.holder import HTTPResponse
from aiomonobank.utils.compat import json


ReturningType = TypeVar("ReturningType")
_sentinel = Sentinel()

DEFAULT_EXCLUDE = {"request_schema", "endpoint", "http_method"}


# --------------------------------------------------------------------
# --------------------------------------------------------------------
def _filter_none_values(d: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in d.items() if v}


# --------------------------------------------------------------------
# --------------------------------------------------------------------
def _insert_value_into_dictionary(
    d: dict[str, Any], keychain: list[str], value: Any
) -> None:  # pragma: no cover
    """
    Вставка значения в словарь (d), используя цепочку ключей (keychain),
    которая представляет собой список строк (ключей).
    Если ключи в keychain указывают на вложенные словари - рекурсивно
    спускаемся по ним, чтобы вставить значение.
    Позволяет добавлять значения в словари с произвольной глубиной вложенности.
    """
    if not keychain:
        return

    current_key = keychain.pop(0)  # Получаем текущий ключ из keychain
    if not keychain:
        # Это последний ключ из keychain
        d[current_key] = value
        return  # Завершаем выполнение

    # Иначе продолжаем искать вложенные словари
    for k, v in d.items():
        if not isinstance(v, dict):
            continue

        if k == current_key:
            _insert_value_into_dictionary(v, keychain, value)


# ====================================================================
# ====================================================================
class RuntimeValueIsMissing(Exception):
    pass


# ====================================================================
# ====================================================================
class APIMethod(
    abc.ABC,
    GenericModel,
    Generic[ReturningType]
):
    """
    Абстрактный класс, который определяет структуру для работы с API-методами
    """

    model_config = ConfigDict(
        validate_default=True,
        extra="allow",
        allow_population_by_field_name=True,
        arbitrary_types_allowed=True,
        orm_mode=True,
        underscore_attrs_are_private=True,
        json_loads=json.loads,
        json_dumps=json.dumps,  # type: ignore
    )

    __returning_type__: ClassVar[Any] = _sentinel
    # __returning_type__ — это атрибут класса, который используется для
    # хранения информации о типе данных, который будет возвращен методом API.
    # Этот атрибут позволяет классу APIMethod быть обобщенным и адаптироваться
    # к различным типам данных, которые могут возвращаться в зависимости от
    # конкретного метода API.
    # __returning_type__ инициализируется значением _sentinel, что указывает
    # на то, что тип еще не был установлен.
    # для установки __returning_type__ используется метод __class_getitem__

    json_payload_schema: ClassVar[dict[str, Any]] = {}

    # url и http_method являются абстрактными свойствами, которые должны
    # быть реализованы в подклассах. Это позволяет каждому конкретному
    # API-методу определять свой URL и HTTP-метод.
    @property
    @abc.abstractmethod
    def url(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def http_method(self) -> str:
        pass

    # ----------------------------------------------------------------
    # __class_getitem__
    # Переопределяет поведение получения элемента класса, чтобы
    # поддерживать обобщенные типы. Проверяет, что параметры не пустые
    # и устанавливает __returning_type__.
    # ----------------------------------------------------------------
    @no_type_check
    def __class_getitem__(cls, params):
        """
        Позволяет получить универсальный класс во время выполнения
        вместо того, чтобы делать это явно в каждом классе, наследующем
        от APIMethod.
        """
        if  ++(params, tuple):
            return super().__class_getitem__(params)

        if not params and cls is not tuple:
            raise TypeError(
                f"Parameter list to {cls.__qualname__}[...] cannot be empty"
            )

        key = params  # just alias

        if cls.__returning_type__ is _sentinel or cls.__returning_type__ is ReturningType:  # type: ignore
            cls.__returning_type__ = key
        else:
            try:
                cls.__returning_type__ = cls.__returning_type__[key]
            except TypeError:
                cls.__returning_type__ = key

        return super().__class_getitem__(params)

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    def __init_subclass__(cls) -> None:
        if cls.__returning_type__ is not _sentinel:
            cls.__returning_type__ = cls.__returning_type__

    # ----------------------------------------------------------------
    # parse_http_response
    # Обрабатывает HTTP-ответ и возвращает объект нужного типа.
    # Проверяет наличие типа возвращаемого значения и валидирует ответ.
    # ----------------------------------------------------------------
    @classmethod
    def parse_http_response(cls, response: HTTPResponse) -> ReturningType:
        if cls.__returning_type__ is _sentinel or cls.__returning_type__ is ReturningType:  # type: ignore
            raise RuntimeError(
                f"{cls.__qualname__}: __returning_type__ is missing"
            )
        cls._validate_response(response)

        try:
            return cls.on_json_parse(response)
        except TypeError:
            pass

        json_response = response.json()

        try:
            if issubclass(cls.__returning_type__, BaseModel):
                return cast(
                    ReturningType,
                    cls.__returning_type__.parse_obj(json_response),
                )
        except TypeError:  # issubclass() arg 1 must be a class
            pass

        return cast(
            ReturningType, parse_obj_as(cls.__returning_type__, json_response)
        )

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    @classmethod
    @abc.abstractmethod
    def _validate_response(cls, response: HTTPResponse) -> None:
        pass

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    @classmethod
    def on_json_parse(
        cls, response: HTTPResponse
    ) -> Union[Any, ReturningType]:
        raise TypeError(
            f"{cls.__module__}.{cls.__qualname__}: doesn't implement json parse hook."
        )

    # ----------------------------------------------------------------
    # build_request
    # Формирует запрос на основе заданного URL и HTTP-метода.
    # Позволяя динамически формировать запросы на основе состояния модели
    # и переданных параметров.
    # Включает проверки, чтобы гарантировать, что запросы соответствуют
    # спецификациям HTTP.
    #
    # Обрабатывает параметры для GET и POST
    # Параметры:
    #   **url_format_kw: произвольное количество именованных аргументов,
    #     которые могут использоваться для форматирования URL.
    # ----------------------------------------------------------------
    def build_request(self, **url_format_kw: Any) -> "Request":

        # Создается словарь request_kw, который будет содержать параметры
        # для запроса.
        request_kw: dict[str, Any] = {
            "endpoint": self.url.format(
                **url_format_kw, **self._get_runtime_path_values()
            ),
            "http_method": self.http_method,
        }

        # Если HTTP-метод равен "GET" и определена схема JSON
        # (self.json_payload_schema), выбрасывается исключение TypeError.
        # Это связано с тем, что метод GET не должен содержать тело запроса,
        # и передача JSON-pyload в таком случае является некорректной.
        if self.http_method == "GET":
            if self.json_payload_schema:
                raise TypeError(
                    "Request schema is not compatible with GET http method "
                    "since GET method cannot transfer json payload"
                )

            # формируется параметр params, который заполняется значениями из
            # модели, исключая None значения и используя алиасы полей.
            # Метод self._get_exclude_set() используется для исключения полей,
            # которые не должны быть включены в запрос.
            request_kw["params"] = self.model_dump(
                exclude_none=True,
                by_alias=True,
                exclude=self._get_exclude_set(),
            )
        else:
            # POST
            if self.json_payload_schema:
                # Обработка JSON-payload для POST-запросов
                # Если определена схема JSON (self.json_payload_schema)
                # - формируется параметр json_payload, который заполняется
                # посредствам метода _get_filled_json_payload_schema()
                request_kw["json_payload"] = (
                    self._get_filled_json_payload_schema()
                )
            else:
                # Если схема JSON не определена, формируется параметр data,
                # который заполняется значениями из модели, аналогично
                # параметру params
                request_kw["data"] = self.model_dump(
                    exclude_none=True,
                    by_alias=True,
                    exclude=self._get_exclude_set(),
                )
        return Request.model_validate(_filter_none_values(request_kw))
        # return Request(**_filter_none_values(request_kw))

    # ----------------------------------------------------------------
    # _get_exclude_set
    # Метод возвращает множество строк (Set[str]), содержащее имена
    # полей, которые должны быть исключены из сериализации или обработки.
    # ----------------------------------------------------------------
    def _get_exclude_set(self) -> Set[str]:

        # DEFAULT_EXCLUDE - множество, содержащее имена полей,
        # которые должны быть исключены по умолчанию.
        to_exclude: Set[str] = DEFAULT_EXCLUDE.copy()

        # Итерация по полям модели
        for key, field in self.model_fields.items():
            # есть ли у поля дополнительная информация (в данном случае,
            # флаг path_runtime_value), указывающая на то, что это поле
            # является значением времени выполнения, которое не должно
            # быть включено в сериализацию.
            if field.field_info.extra.get("path_runtime_value", False):
                to_exclude.add(key)

        return to_exclude

    # ----------------------------------------------------------------
    # _get_filled_json_payload_schema
    #
    # ----------------------------------------------------------------
    def _get_filled_json_payload_schema(self) -> dict[str, Any]:
        """
        Алгоритм этого метода в первую очередь проверяет значения по умолчанию,
        если поле не имеет значения по умолчанию для схемы, он проверяет
        значения, которые были переданы методу.
        """

        request_schema = self._get_schema_with_filled_runtime_values()
        # получить словарь значений полей модели, исключая поля со
        # значением None, используя алиасы и исключая поля, которые
        # возвращает метод _get_exclude_set()
        schema_values = self.self.model_dump(
            exclude_none=True, by_alias=True, exclude=self._get_exclude_set()
        )

        # итерируемся по всем полям модели
        for key, field in self.model_fields.items():
            scheme_path: str = field.field_info.extra.get(
                "scheme_path", field.name
            )
            keychain = scheme_path.split(".")
            try:
                field_value = schema_values[key]
            except KeyError:
                continue

            _insert_value_into_dictionary(
                request_schema, keychain, field_value
            )

        return request_schema

    # ----------------------------------------------------------------
    # _get_schema_with_filled_runtime_values
    #
    # ----------------------------------------------------------------
    def _get_schema_with_filled_runtime_values(self) -> dict[str, Any]:

        scheme_paths: list[str] = [
            field.field_info.extra.get("scheme_path", field.name)
            for field in self.__fields__.values()
            if field.name in self.dict(exclude_none=True)
        ]
        schema = self.json_payload_schema.copy()

        # ------------------------------------------------------------
        def apply_runtime_values_to_schema(d: dict[str, Any]) -> None:

            for k, v in list(d.items()):
                if isinstance(v, dict):
                    apply_runtime_values_to_schema(v)
                elif isinstance(v, RuntimeValue):
                    if v.has_default() and k not in scheme_paths:
                        d[k] = v.get_default()
                        continue
                    elif v.is_mandatory is False:
                        d.pop(k)

        apply_runtime_values_to_schema(schema)

        return schema

    # ----------------------------------------------------------------
    # _get_runtime_path_values
    #
    # ----------------------------------------------------------------
    def _get_runtime_path_values(self) -> dict[str, Any]:

        result: dict[str, Any] = {}

        for field_name, value in self.dict().items():
            field: ModelField = self.__fields__[field_name]
            is_path_runtime_value = field.field_info.extra.get(
                "path_runtime_value", False
            )
            if not is_path_runtime_value:
                continue

            result[field.alias] = value

        return result


# ====================================================================
# ====================================================================
class Request(BaseModel):

    endpoint: str

    data: Optional[dict[str, Optional[Any]]] = None
    params: Optional[dict[str, Optional[Any]]] = None
    json_payload: Optional[dict[str, Any]] = None
    headers: dict[str, Any] = {}

    http_method: str = "GET"

    model_config = ConfigDict(arbitrary_types_allowed=True)


# ====================================================================
# ====================================================================
class RuntimeValue:

    __slots__ = ("_default", "_default_factory", "is_mandatory")

    def __init__(
        self,
        default: Optional[Any] = None,
        default_factory: Optional[Callable[..., Any]] = None,
        mandatory: bool = True,
    ):
        self._default = default
        self._default_factory = default_factory
        self.is_mandatory = mandatory

    def has_default(self) -> bool:
        return self._default is not None or self._default_factory is not None

    def get_default(self) -> Any:
        if self._default is not None:
            return self._default
        if self._default_factory is not None:
            return self._default_factory()
