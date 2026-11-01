"""Класс AudioClip — фрагмент звукового файла на дорожке."""
from audio.audio_file import AudioFile
from exceptions import ValidationError


class AudioClip:
    """Кусочек звукового файла, размещённый на таймлайне дорожки."""

    def __init__(self, clip_id: int, file: AudioFile, start: float,
                 duration: float) -> None:
        if duration <= 0:
            raise ValidationError("Длительность клипа", duration,
                                  "должна быть больше 0")
        if duration > file.duration:
            raise ValidationError(
                "Длительность клипа", duration,
                f"не может быть больше длины файла ({file.duration:g} с)"
            )
        self.__id: int = clip_id
        self.__file: AudioFile = file  # агрегация: файл живёт отдельно
        self.__start: float = self.__check_start(start)
        self.__duration: float = float(duration)

    @staticmethod
    def __check_start(start: float) -> float:
        """Проверяет время начала и возвращает его."""
        if start < 0:
            raise ValidationError("Начало клипа", start,
                                  "не может быть отрицательным")
        return float(start)

    @property
    def id(self) -> int:
        """Номер клипа на дорожке."""
        return self.__id

    @property
    def file(self) -> AudioFile:
        """Файл, из которого взят клип."""
        return self.__file

    @property
    def start(self) -> float:
        """Время начала на таймлайне, сек."""
        return self.__start

    @property
    def duration(self) -> float:
        """Длительность клипа, сек."""
        return self.__duration

    @property
    def end(self) -> float:
        """Время окончания: вычисляется, а не хранится."""
        return self.__start + self.__duration

    def move(self, new_start: float) -> None:
        """Сдвигает клип по таймлайну."""
        self.__start = self.__check_start(new_start)

    def overlaps(self, other: "AudioClip") -> bool:
        """Проверяет, накладывается ли клип на другой клип."""
        return self.start < other.end and other.start < self.end

    def __str__(self) -> str:
        return (f"#{self.__id} {self.__file.path}: "
                f"{self.__start:.1f}–{self.end:.1f} с")