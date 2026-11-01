"""Исключение для ошибок работы с файлами."""
from pathlib import Path

from exceptions.audio_editor_error import AudioEditorError


class StorageError(AudioEditorError):
    """Файл JSON или XML не удалось прочитать или записать.

    Исходную ошибку Python (FileNotFoundError, JSONDecodeError и т. д.)
    сохраняем через «raise ... from error», она доступна в __cause__.
    Пример текста ошибки: «Файл data.json: повреждён (строка 2)».
    """

    def __init__(self, path: Path, reason: str) -> None:
        self.path: Path = path
        self.reason: str = reason
        super().__init__(f"Файл {path.name}: {reason}")