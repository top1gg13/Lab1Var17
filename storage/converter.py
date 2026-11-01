"""Перевод объектов модели в словари и обратно.

Эти функции общие для JSON и XML: оба хранилища работают
с одинаковой структурой данных (см. data/data.json и data/data.xml).
"""
from datetime import date
from typing import Any

from audio import AudioClip, AudioFile
from effects import Effect, Equalizer, Fade, Reverb
from project import Project
from tracks import AudioTrack, MidiTrack, Track


def to_bool(value: Any) -> bool:
    """Переводит true/false (bool из JSON или строку из XML) в bool."""
    if isinstance(value, bool):
        return value
    if value in ("true", "false"):
        return value == "true"
    raise ValueError(f"Ожидалось true или false, получено {value!r}")


# ---------- объект -> словарь (сериализация) ----------
def effect_to_dict(effect: Effect) -> dict[str, Any]:
    """Эффект -> словарь. Поля зависят от типа эффекта."""
    data: dict[str, Any] = {"id": effect.id, "type": effect.kind(),
                            "enabled": effect.enabled}
    if isinstance(effect, Reverb):
        data["room_size"] = effect.room_size
    elif isinstance(effect, Equalizer):
        data.update(low=effect.low, mid=effect.mid, high=effect.high)
    elif isinstance(effect, Fade):
        data.update(fade_in=effect.fade_in, fade_out=effect.fade_out)
    return data


def clip_to_dict(clip: AudioClip) -> dict[str, Any]:
    """Клип -> словарь; файл клипа вкладывается внутрь."""
    return {
        "id": clip.id,
        "start": clip.start,
        "duration": clip.duration,
        "file": {
            "path": clip.file.path,
            "format": clip.file.format,
            "duration": clip.file.duration,
        },
    }


def track_to_dict(track: Track) -> dict[str, Any]:
    """Дорожка -> словарь. У аудио есть clips, у MIDI — instrument."""
    data: dict[str, Any] = {
        "id": track.id,
        "kind": track.kind(),
        "title": track.title,
        "volume": track.volume,
        "muted": track.is_muted,
    }
    if isinstance(track, AudioTrack):
        data["clips"] = [clip_to_dict(clip) for clip in track.clips]
    elif isinstance(track, MidiTrack):
        data["instrument"] = track.instrument
    data["effects"] = [effect_to_dict(effect) for effect in track.effects]
    return data


def project_to_dict(project: Project) -> dict[str, Any]:
    """Проект -> словарь со всеми дорожками внутри."""
    return {
        "id": project.id,
        "title": project.title,
        "sample_rate": project.sample_rate,
        "created_at": project.created_at.isoformat(),
        "tracks": [track_to_dict(track) for track in project.tracks],
    }


# ---------- словарь -> объект (десериализация) ----------
def effect_from_dict(data: dict[str, Any]) -> Effect:
    """Словарь -> эффект. По полю type выбираем нужного наследника."""
    effect_id = int(data["id"])
    enabled = to_bool(data["enabled"])
    effect_type = data["type"]
    if effect_type == "reverb":
        return Reverb(effect_id, float(data["room_size"]), enabled)
    if effect_type == "equalizer":
        return Equalizer(effect_id, float(data["low"]), float(data["mid"]),
                         float(data["high"]), enabled)
    if effect_type == "fade":
        return Fade(effect_id, float(data["fade_in"]),
                    float(data["fade_out"]), enabled)
    raise ValueError(f"Неизвестный тип эффекта: {effect_type}")


def clip_from_dict(data: dict[str, Any]) -> AudioClip:
    """Словарь -> клип вместе с его файлом."""
    file_data = data["file"]
    file = AudioFile(file_data["path"], file_data["format"],
                     float(file_data["duration"]))
    return AudioClip(int(data["id"]), file, float(data["start"]),
                     float(data["duration"]))


def track_from_dict(data: dict[str, Any]) -> Track:
    """Словарь -> дорожка. По полю kind выбираем AudioTrack или MidiTrack."""
    track_id = int(data["id"])
    volume = float(data["volume"])
    muted = to_bool(data["muted"])
    track: Track
    if data["kind"] == "audio":
        track = AudioTrack(track_id, data["title"], volume, muted)
        for clip_data in data["clips"]:
            track.add_clip(clip_from_dict(clip_data))
    elif data["kind"] == "midi":
        track = MidiTrack(track_id, data["title"], volume,
                          data["instrument"], muted)
    else:
        raise ValueError(f"Неизвестный тип дорожки: {data['kind']}")
    for effect_data in data["effects"]:
        track.add_effect(effect_from_dict(effect_data))
    return track


def project_from_dict(data: dict[str, Any]) -> Project:
    """Словарь -> проект со всеми дорожками."""
    project = Project(int(data["id"]), data["title"],
                      int(data["sample_rate"]),
                      date.fromisoformat(data["created_at"]))
    for track_data in data["tracks"]:
        project.add_track(track_from_dict(track_data))
    return project