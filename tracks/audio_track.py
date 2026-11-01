"""Класс AudioTrack — звуковая дорожка с клипами."""
from audio.audio_clip import AudioClip
from exceptions import NotFoundError, ValidationError
from tracks.track import Track


class AudioTrack(Track):
    """Дорожка со звуковыми клипами, которые не накладываются друг на друга."""

    def __init__(self, track_id: int, title: str, volume: float,
                 muted: bool = False) -> None:
        super().__init__(track_id, title, volume, muted)
        self.__clips: list[AudioClip] = []  # композиция: клипы дорожки

    @property
    def clips(self) -> list[AudioClip]:
        """Копия списка клипов."""
        return list(self.__clips)

    def __check_overlap(self, clip: AudioClip) -> None:
        """Проверяет, что клип не накладывается на остальные клипы."""
        for other in self.__clips:
            if other is not clip and clip.overlaps(other):
                raise ValidationError(
                    "Время клипа", f"{clip.start:g}–{clip.end:g} с",
                    f"накладывается на клип #{other.id} "
                    f"({other.start:g}–{other.end:g} с)"
                )

    def add_clip(self, clip: AudioClip) -> None:
        """Добавляет клип на дорожку."""
        self.__check_overlap(clip)
        self.__clips.append(clip)

    def get_clip(self, clip_id: int) -> AudioClip:
        """Возвращает клип по id."""
        for clip in self.__clips:
            if clip.id == clip_id:
                return clip
        raise NotFoundError("клип", clip_id)

    def move_clip(self, clip_id: int, new_start: float) -> None:
        """Сдвигает клип; если он наложится на другой — возвращает назад."""
        clip = self.get_clip(clip_id)
        old_start = clip.start
        clip.move(new_start)
        try:
            self.__check_overlap(clip)
        except ValidationError:
            clip.move(old_start)
            raise

    def remove_clip(self, clip_id: int) -> None:
        """Удаляет клип по id."""
        self.__clips.remove(self.get_clip(clip_id))

    def kind(self) -> str:
        return "audio"

    def __str__(self) -> str:
        return (f"Аудиодорожка {super().__str__()}, "
                f"клипов: {len(self.__clips)}")