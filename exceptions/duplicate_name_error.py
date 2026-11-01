"""Исключение для повторяющихся названий."""
from exceptions.audio_editor_error import AudioEditorError


class DuplicateNameError(AudioEditorError):
    """Объект с таким названием уже существует.

    Пример текста ошибки: «Уже существует: дорожка «Голос»».
    """

    def __init__(self, entity: str, name: str) -> None:
        self.entity: str = entity
        self.name: str = name
        super().__init__(f"Уже существует: {entity} «{name}»")