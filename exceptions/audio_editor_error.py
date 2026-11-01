"""Базовое исключение аудиоредактора."""


class AudioEditorError(Exception):
    """Общий предок всех исключений программы.

    Консоль ловит именно этот класс, поэтому любая наша ошибка
    выводится пользователю, а программа продолжает работать.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message: str = message

    def __str__(self) -> str:
        return self.message