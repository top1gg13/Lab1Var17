"""Абстрактный класс Effect — общий предок всех звуковых эффектов."""
from abc import ABC, abstractmethod


class Effect(ABC):
    """Звуковой эффект на дорожке.

    Создать объект Effect напрямую нельзя (Python бросит TypeError):
    можно создавать только наследников — Reverb, Equalizer, Fade.
    """

    def __init__(self, effect_id: int, enabled: bool = True) -> None:
        self.__id: int = effect_id
        self.__enabled: bool = enabled

    @property
    def id(self) -> int:
        """Номер эффекта на дорожке."""
        return self.__id

    @property
    def enabled(self) -> bool:
        """Включён ли эффект."""
        return self.__enabled

    def toggle(self) -> None:
        """Включает выключенный эффект и выключает включённый."""
        self.__enabled = not self.__enabled

    def _status(self) -> str:
        """Пометка для выключенного эффекта (для describe наследников)."""
        return "" if self.__enabled else " [выкл.]"

    @abstractmethod
    def kind(self) -> str:
        """Тип эффекта для сохранения в файл: reverb, equalizer, fade."""

    @abstractmethod
    def describe(self) -> str:
        """Описание эффекта: у каждого наследника своё (полиморфизм)."""