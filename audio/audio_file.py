"""Класс AudioFile — сведения о звуковом файле."""
from exceptions import ValidationError


class AudioFile:
    """Звуковой файл на диске: путь, формат и длительность.

    Сам звук программа не читает, хранятся только сведения о файле.
    """

    FORMATS: tuple[str, ...] = ("wav", "mp3", "flac")

    def __init__(self, path: str, audio_format: str, duration: float) -> None:
        path = path.strip()
        audio_format = audio_format.strip().lower()
        if not path:
            raise ValidationError("Путь к файлу", path, "не может быть пустым")
        if audio_format not in self.FORMATS:
            raise ValidationError(
                "Формат файла", audio_format,
                f"допустимы только {', '.join(self.FORMATS)}"
            )
        if duration <= 0:
            raise ValidationError("Длительность файла", duration,
                                  "должна быть больше 0")
        self.__path: str = path
        self.__format: str = audio_format
        self.__duration: float = float(duration)

    @property
    def path(self) -> str:
        """Путь к файлу."""
        return self.__path

    @property
    def format(self) -> str:
        """Формат файла: wav, mp3 или flac."""
        return self.__format

    @property
    def duration(self) -> float:
        """Длительность файла в секундах."""
        return self.__duration

    def __str__(self) -> str:
        return f"{self.__path} ({self.__format}, {self.__duration:.1f} с)"