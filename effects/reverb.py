"""Класс Reverb — эффект эха."""
from effects.effect import Effect
from exceptions import ValidationError


class Reverb(Effect):
    """Эхо (реверберация): звук как будто в комнате заданного размера."""

    def __init__(self, effect_id: int, room_size: float,
                 enabled: bool = True) -> None:
        super().__init__(effect_id, enabled)
        if not 0 <= room_size <= 1:
            raise ValidationError("Размер комнаты", room_size,
                                  "должен быть от 0 до 1")
        self.__room_size: float = float(room_size)

    @property
    def room_size(self) -> float:
        """Размер комнаты от 0 (маленькая) до 1 (огромный зал)."""
        return self.__room_size

    def kind(self) -> str:
        return "reverb"

    def describe(self) -> str:
        return (f"#{self.id} Эхо, размер комнаты {self.__room_size}"
                f"{self._status()}")