"""Абстрактный класс Track — общий предок всех дорожек."""
from abc import ABC, abstractmethod

from effects.effect import Effect
from exceptions import NotFoundError, ValidationError


class Track(ABC):
    """Дорожка проекта: название, громкость, заглушка и эффекты.

    Создать объект Track напрямую нельзя (Python бросит TypeError):
    можно создавать только наследников — AudioTrack и MidiTrack.
    """

    MAX_TITLE_LENGTH: int = 50

    def __init__(self, track_id: int, title: str, volume: float,
                 muted: bool = False) -> None:
        self.__id: int = track_id
        self.__title: str = self.__check_title(title)
        self.__volume: float = self.__check_volume(volume)
        self.__muted: bool = muted
        self.__effects: list[Effect] = []  # композиция: эффекты дорожки

    # ---------- проверки ----------
    @classmethod
    def __check_title(cls, title: str) -> str:
        title = title.strip()
        if not title:
            raise ValidationError("Название дорожки", title,
                                  "не может быть пустым")
        if len(title) > cls.MAX_TITLE_LENGTH:
            raise ValidationError(
                "Название дорожки", title,
                f"должно быть не длиннее {cls.MAX_TITLE_LENGTH} символов"
            )
        return title

    @staticmethod
    def __check_volume(volume: float) -> float:
        if not 0 <= volume <= 100:
            raise ValidationError("Громкость", volume,
                                  "должна быть от 0 до 100")
        return float(volume)

    # ---------- свойства ----------
    @property
    def id(self) -> int:
        """Номер дорожки в проекте."""
        return self.__id

    @property
    def title(self) -> str:
        """Название дорожки."""
        return self.__title

    @property
    def volume(self) -> float:
        """Громкость в процентах: от 0 до 100."""
        return self.__volume

    @volume.setter
    def volume(self, value: float) -> None:
        # сеттер: при присваивании track.volume = x значение проверяется
        self.__volume = self.__check_volume(value)

    @property
    def is_muted(self) -> bool:
        """Заглушена ли дорожка."""
        return self.__muted

    @property
    def effects(self) -> list[Effect]:
        """Копия списка эффектов (сам список снаружи не изменить)."""
        return list(self.__effects)

    # ---------- методы ----------
    def rename(self, new_title: str) -> None:
        """Переименовывает дорожку."""
        self.__title = self.__check_title(new_title)

    def toggle_mute(self) -> None:
        """Выключает звук дорожки или включает обратно."""
        self.__muted = not self.__muted

    def add_effect(self, effect: Effect) -> None:
        """Добавляет эффект на дорожку."""
        self.__effects.append(effect)

    def get_effect(self, effect_id: int) -> Effect:
        """Возвращает эффект по id."""
        for effect in self.__effects:
            if effect.id == effect_id:
                return effect
        raise NotFoundError("эффект", effect_id)

    def remove_effect(self, effect_id: int) -> None:
        """Удаляет эффект по id."""
        self.__effects.remove(self.get_effect(effect_id))

    @abstractmethod
    def kind(self) -> str:
        """Тип дорожки для сохранения в файл: audio или midi."""

    def __str__(self) -> str:
        muted = " [без звука]" if self.__muted else ""
        return (f"#{self.__id} «{self.__title}», "
                f"громкость {self.__volume:g}%{muted}")