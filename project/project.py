"""Класс Project — проект аудиоредактора."""
from datetime import date

from exceptions import DuplicateNameError, NotFoundError, ValidationError
from tracks.audio_track import AudioTrack
from tracks.track import Track


class Project:
    """Проект — главный объект: содержит все дорожки."""

    MAX_TITLE_LENGTH: int = 100
    SAMPLE_RATES: tuple[int, ...] = (44100, 48000, 96000)

    def __init__(self, project_id: int, title: str, sample_rate: int,
                 created_at: date | None = None) -> None:
        if sample_rate not in self.SAMPLE_RATES:
            rates = ", ".join(str(rate) for rate in self.SAMPLE_RATES)
            raise ValidationError("Частота дискретизации", sample_rate,
                                  f"допустимы только {rates} Гц")
        self.__id: int = project_id
        self.__title: str = self.__check_title(title)
        self.__sample_rate: int = sample_rate
        # если дата не передана — проект создан сегодня
        self.__created_at: date = created_at or date.today()
        self.__tracks: list[Track] = []  # композиция: дорожки проекта

    @classmethod
    def __check_title(cls, title: str) -> str:
        title = title.strip()
        if not title:
            raise ValidationError("Название проекта", title,
                                  "не может быть пустым")
        if len(title) > cls.MAX_TITLE_LENGTH:
            raise ValidationError(
                "Название проекта", title,
                f"должно быть не длиннее {cls.MAX_TITLE_LENGTH} символов"
            )
        return title

    # ---------- свойства ----------
    @property
    def id(self) -> int:
        """Номер проекта."""
        return self.__id

    @property
    def title(self) -> str:
        """Название проекта."""
        return self.__title

    @property
    def sample_rate(self) -> int:
        """Частота дискретизации, Гц."""
        return self.__sample_rate

    @property
    def created_at(self) -> date:
        """Дата создания проекта."""
        return self.__created_at

    @property
    def tracks(self) -> list[Track]:
        """Копия списка дорожек."""
        return list(self.__tracks)

    @property
    def duration(self) -> float:
        """Длина проекта: конец самого позднего клипа, сек."""
        ends = [clip.end
                for track in self.__tracks if isinstance(track, AudioTrack)
                for clip in track.clips]
        return max(ends, default=0.0)

    # ---------- методы ----------
    def rename(self, new_title: str) -> None:
        """Переименовывает проект."""
        self.__title = self.__check_title(new_title)

    def add_track(self, track: Track) -> None:
        """Добавляет дорожку; названия в проекте не повторяются."""
        for existing in self.__tracks:
            if existing.title.lower() == track.title.lower():
                raise DuplicateNameError("дорожка", track.title)
        self.__tracks.append(track)

    def get_track(self, track_id: int) -> Track:
        """Возвращает дорожку по id."""
        for track in self.__tracks:
            if track.id == track_id:
                return track
        raise NotFoundError("дорожка", track_id)

    def remove_track(self, track_id: int) -> None:
        """Удаляет дорожку по id."""
        self.__tracks.remove(self.get_track(track_id))

    def __str__(self) -> str:
        return (f"Проект #{self.__id} «{self.__title}», "
                f"{self.__sample_rate} Гц, "
                f"создан {self.__created_at:%d.%m.%Y}, "
                f"дорожек: {len(self.__tracks)}, "
                f"длина {self.duration:.1f} с")