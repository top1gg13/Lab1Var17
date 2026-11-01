"""Исключение для ненайденных объектов."""
from exceptions.audio_editor_error import AudioEditorError


class NotFoundError(AudioEditorError):
    """Объект с указанным id не найден.

    Пример текста ошибки: «Не найдено: дорожка с id=7».
    """

    def __init__(self, entity: str, entity_id: int) -> None:
        self.entity: str = entity
        self.entity_id: int = entity_id
        super().__init__(f"Не найдено: {entity} с id={entity_id}")