"""Собственные исключения программы.

Иерархия:
    Exception
    └── AudioEditorError
        ├── ValidationError
        ├── NotFoundError
        ├── DuplicateNameError
        └── StorageError
"""
from exceptions.audio_editor_error import AudioEditorError
from exceptions.duplicate_name_error import DuplicateNameError
from exceptions.not_found_error import NotFoundError
from exceptions.storage_error import StorageError
from exceptions.validation_error import ValidationError

__all__ = [
    "AudioEditorError",
    "DuplicateNameError",
    "NotFoundError",
    "StorageError",
    "ValidationError",
]