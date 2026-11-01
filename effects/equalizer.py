"""Класс Equalizer — эффект эквалайзера."""
from effects.effect import Effect
from exceptions import ValidationError


class Equalizer(Effect):
    """Эквалайзер: меняет громкость низких, средних и высоких частот."""

    MIN_DB: float = -12.0
    MAX_DB: float = 12.0

    def __init__(self, effect_id: int, low: float, mid: float, high: float,
                 enabled: bool = True) -> None:
        super().__init__(effect_id, enabled)
        self.__low: float = self.__check_level("Низкие частоты", low)
        self.__mid: float = self.__check_level("Средние частоты", mid)
        self.__high: float = self.__check_level("Высокие частоты", high)

    @classmethod
    def __check_level(cls, band: str, value: float) -> float:
        """Проверяет, что уровень полосы в допустимых пределах."""
        if not cls.MIN_DB <= value <= cls.MAX_DB:
            raise ValidationError(
                band, value,
                f"должны быть от {cls.MIN_DB:g} до {cls.MAX_DB:g} дБ"
            )
        return float(value)

    @property
    def low(self) -> float:
        """Низкие частоты, дБ."""
        return self.__low

    @property
    def mid(self) -> float:
        """Средние частоты, дБ."""
        return self.__mid

    @property
    def high(self) -> float:
        """Высокие частоты, дБ."""
        return self.__high

    def kind(self) -> str:
        return "equalizer"

    def describe(self) -> str:
        return (f"#{self.id} Эквалайзер: низкие {self.__low:+g}, "
                f"средние {self.__mid:+g}, высокие {self.__high:+g} дБ"
                f"{self._status()}")