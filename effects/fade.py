"""Класс Fade — эффект плавного появления и затухания."""
from effects.effect import Effect
from exceptions import ValidationError


class Fade(Effect):
    """Плавное нарастание громкости в начале и затухание в конце."""

    def __init__(self, effect_id: int, fade_in: float, fade_out: float,
                 enabled: bool = True) -> None:
        super().__init__(effect_id, enabled)
        if fade_in < 0:
            raise ValidationError("Время появления", fade_in,
                                  "не может быть отрицательным")
        if fade_out < 0:
            raise ValidationError("Время затухания", fade_out,
                                  "не может быть отрицательным")
        self.__fade_in: float = float(fade_in)
        self.__fade_out: float = float(fade_out)

    @property
    def fade_in(self) -> float:
        """Длительность появления, сек."""
        return self.__fade_in

    @property
    def fade_out(self) -> float:
        """Длительность затухания, сек."""
        return self.__fade_out

    def kind(self) -> str:
        return "fade"

    def describe(self) -> str:
        return (f"#{self.id} Появление {self.__fade_in:g} с, "
                f"затухание {self.__fade_out:g} с{self._status()}")