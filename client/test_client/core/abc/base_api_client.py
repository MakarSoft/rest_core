# ====================================================================
# base_api_client.py
# ====================================================================

from __future__ import annotations

import abc
import inspect

from copy import deepcopy  # Функция для глубокого копирования объектов.
from types import TracebackType  #  Тип для обработки исключений.
from typing import (
    TYPE_CHECKING as MYPY,
    Any,
    Optional,
    Type,
    TypeVar,
    Dict,
    Callable,
    Awaitable,
    Union,
    Tuple,
)

if MYPY:
    from aiomonobank.core.request_service import (
        RequestServiceProto,
    )  # pragma: no cover


# Тип для фабрики, создающей RequestServiceProto,
# которая может быть как обычной, так и асинхронной функцией.
RequestServiceFactoryType = Callable[
    ..., Union[Awaitable["RequestServiceProto"], "RequestServiceProto"]
]

T = TypeVar("T", bound="BaseAPIClient")
MT = TypeVar("MT", bound="type")
# _C = TypeVar("_C", bound=Type["BaseAPIClient"])


# ====================================================================
# Этот метакласс может использоваться для создания классов API-клиентов,
# которые требуют инициализации некоторого сервиса перед выполнением
# асинхронных методов.
# Например, если у вас есть класс, который использует этот метакласс,
# все асинхронные методы, кроме тех, которые начинаются с двойного
# подчеркивания или являются исключениями, будут автоматически проверять,
# инициализирован ли _request_service, и инициализировать его при необходимости.
# ====================================================================
# Метаклассы в Python используются для создания классов и позволяют
# изменять поведение классов на этапе их создания.
# Класс APIClientMeta наследует от abc.ABCMeta, что позволяет ему быть
# метаклассом для абстрактных базовых классов.


class APIClientMeta(abc.ABCMeta):

    def __new__(
        mcs: Type[APIClientMeta],
        name: str,
        bases: tuple[type, ...],
        attrs: dict[str, Any],
        **kwargs: Any,
    ) -> APIClientMeta:

        # mcs: ссылка на метакласс (в данном случае APIClientMeta).
        # name: имя создаваемого класса.
        # bases: кортеж базовых классов.
        # attrs: словарь атрибутов и методов, определенных в классе.
        # **kwargs: дополнительные аргументы.

        # Из-за ограничений библиотеки aiohttp, которая требует создания
        # ClientSession только внутри сопрограммы, приходится писать
        # этот метакласс, чтобы избежать дополнительного громоздкого
        # шаблонного кода.

        # Метод проходит по всем атрибутам, определенным в классе, который
        # использует этот метакласс.
        for key, attribute in attrs.items():
            if key.startswith("__") or not inspect.iscoroutinefunction(
                attribute
            ):
                # Если имя атрибута начинается с двойного подчеркивания (что
                # обычно указывает на специальные методы)
                # или атрибут не является корутинной функцией (асинхронной
                # функцией), то он пропускается.
                continue

            if key in (
                "close",
                "_create_request_service",
                "create_request_service",
            ):
                # Если атрибут является одним из указанных (например
                # close, _create_request_service, create_request_service),
                # он также пропускается.
                continue

            def wrapper(m) -> Any:
                # Для каждого подходящего атрибута создается обертка wrapper,
                # которая определяет асинхронную функцию
                # check_request_service_before_execute.
                # Эта функция проверяет, инициализирован ли _request_service.
                # Если нет, она вызывает create_request_service для его
                # инициализации.
                # Затем она вызывает оригинальный метод m, передавая ему все
                # аргументы.

                async def check_request_service_before_execute(
                    self, *args: Any, **kw: Any
                ) -> Any:

                    if self._request_service is None:
                        self._request_service = (
                            await self.create_request_service()
                        )

                    return await m(self, *args, **kw)

                return check_request_service_before_execute

            # Оригинальный метод заменяется на обернутую версию.
            attrs[key] = wrapper(attrs[key])

        # вызываем super().__new__, чтобы создать новый класс
        # с измененными атрибутами.
        return super().__new__(mcs, name, bases, attrs, **kwargs)


# ====================================================================
# class BaseAPIClient(metaclass=APIClientMeta)
#
# Класс использует метакласс APIClientMeta и реализует основные
# функции для работы с API.
# ====================================================================
class BaseAPIClient(metaclass=APIClientMeta):

    # ----------------------------------------------------------------
    def __init__(
        self,
        request_service_factory: Optional[RequestServiceFactoryType] = None,
    ):

        self._request_service_factory = request_service_factory

        self._request_service: Optional[RequestServiceProto] = None  # type: ignore

    # ----------------------------------------------------------------
    async def __aenter__(self):  # type: ignore

        if self._request_service is None:
            self._request_service = await self.create_request_service()
        return self

    # ----------------------------------------------------------------
    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:

        await self.close()

    # ----------------------------------------------------------------
    async def close(self) -> None:

        if self._request_service is None:
            return None

        await self._request_service.shutdown()

    # ----------------------------------------------------------------
    async def create_request_service(self) -> RequestServiceProto:

        if self._request_service_factory is not None:
            if inspect.iscoroutinefunction(self._request_service_factory):
                return await self._request_service_factory(self)  # type: ignore
            return self._request_service_factory(self)  # type: ignore

        return await self._create_request_service()

    # ----------------------------------------------------------------
    @abc.abstractmethod
    async def _create_request_service(self) -> RequestServiceProto:
        pass

    # ----------------------------------------------------------------
    def __deepcopy__(self: T, memo: dict[Any, Any]) -> T:

        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            try:
                setattr(result, k, deepcopy(v, memo))
            except TypeError:
                pass

        return result
