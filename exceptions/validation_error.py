"""Исключение для неверных значений."""
from exceptions.audio_editor_error import AudioEditorError


class ValidationError(AudioEditorError):
    """Значение не прошло проверку.

    Хранит, какое поле проверялось, что было введено и почему
    значение не подходит. Пример текста ошибки:
    «Громкость: должна быть от 0 до 1 (введено: 1.5)».
    """

    def __init__(self, field: str, value: object, reason: str) -> None:
        self.field: str = field
        self.value: object = value
        self.reason: str = reason
        super().__init__(f"{field}: {reason} (введено: {value!r})")