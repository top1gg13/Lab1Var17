"""Консольное приложение «Аудиоредактор» — точка входа программы."""
from pathlib import Path

from audio import AudioClip, AudioFile
from effects import Equalizer, Fade, Reverb
from exceptions import (
    AudioEditorError,
    NotFoundError,
    StorageError,
    ValidationError,
)
from project import Project
from storage import JsonStorage, XmlStorage
from tracks import AudioTrack, MidiTrack, Track

DATA_DIR: Path = Path(__file__).parent / "data"


def ask_int(prompt: str) -> int:
    """Спрашивает целое число, пока не введут правильно."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Нужно ввести целое число.")


def ask_float(prompt: str) -> float:
    """Спрашивает дробное число, пока не введут правильно."""
    while True:
        try:
            return float(input(prompt).replace(",", "."))
        except ValueError:
            print("Нужно ввести число.")


class ConsoleApp:
    """Консольное меню аудиоредактора."""

    def __init__(self) -> None:
        # все проекты хранятся в памяти, пока их не сохранят в файл
        self._projects: list[Project] = []
        # хранилище (JSON или XML) выбирается один раз при запуске
        self._storage: JsonStorage | XmlStorage | None = None

    # ---------- поиск ----------
    def _find_project(self) -> Project:
        """Спрашивает id и возвращает проект; если нет — NotFoundError."""
        project_id = ask_int("id проекта: ")
        for project in self._projects:
            if project.id == project_id:
                return project
        raise NotFoundError("проект", project_id)

    def _find_track(self) -> tuple[Project, Track]:
        """Спрашивает id проекта и дорожки, возвращает обоих."""
        project = self._find_project()
        return project, project.get_track(ask_int("id дорожки: "))

    # ---------- проекты ----------
    def show_all(self) -> None:
        """Read: выводит все проекты деревом."""
        if not self._projects:
            print("Проектов пока нет.")
        for project in self._projects:
            print(f"\n{project}")
            for track in project.tracks:
                print(f"  {track}")
                if isinstance(track, AudioTrack):
                    for clip in track.clips:
                        print(f"    клип: {clip}")
                for effect in track.effects:
                    print(f"    эффект: {effect.describe()}")

    def add_project(self) -> None:
        """Create: создаёт новый проект."""
        new_id = max((p.id for p in self._projects), default=0) + 1
        title = input("Название проекта: ")
        rates = {"1": 44100, "2": 48000, "3": 96000}
        choice = input("Частота (1 - 44100, 2 - 48000, 3 - 96000 Гц): ")
        if choice not in rates:
            raise ValidationError("Частота", choice,
                                  "нужно выбрать 1, 2 или 3")
        project = Project(new_id, title, rates[choice])
        self._projects.append(project)
        print(f"Создан: {project}")

    def rename_project(self) -> None:
        """Update: переименовывает проект."""
        project = self._find_project()
        project.rename(input("Новое название проекта: "))
        print(f"Обновлено: {project}")

    def delete_project(self) -> None:
        """Delete: удаляет проект вместе с дорожками."""
        self._projects.remove(self._find_project())
        print("Проект удалён")

    # ---------- дорожки ----------
    def add_track(self) -> None:
        """Create: добавляет аудио- или MIDI-дорожку в проект."""
        project = self._find_project()
        kind = input("Тип (1 - аудио, 2 - MIDI): ")
        new_id = max((t.id for t in project.tracks), default=0) + 1
        title = input("Название дорожки: ")
        volume = ask_float("Громкость дорожки (0-100): ")
        if kind == "1":
            track: Track = AudioTrack(new_id, title, volume)
        elif kind == "2":
            instrument = input("Инструмент (например, Piano): ")
            track = MidiTrack(new_id, title, volume, instrument)
        else:
            raise ValidationError("Тип дорожки", kind, "нужно выбрать 1 или 2")
        project.add_track(track)
        print(f"Добавлена: {track}")

    def change_volume(self) -> None:
        """Update: меняет громкость дорожки."""
        _, track = self._find_track()
        track.volume = ask_float("Новая громкость дорожки (0-100): ")
        print(f"Обновлено: {track}")

    def delete_track(self) -> None:
        """Delete: удаляет дорожку из проекта."""
        project, track = self._find_track()
        project.remove_track(track.id)
        print("Дорожка удалена")

    # ---------- клипы и эффекты ----------
    def add_clip(self) -> None:
        """Create: добавляет клип на аудиодорожку."""
        _, track = self._find_track()
        if not isinstance(track, AudioTrack):
            raise ValidationError("Дорожка", track.title,
                                  "клипы есть только у аудиодорожек")
        path = input("Имя аудиофайла (например, voice.wav): ")
        formats = {"1": "wav", "2": "mp3", "3": "flac"}
        choice = input("Формат (1 - wav, 2 - mp3, 3 - flac): ")
        if choice not in formats:
            raise ValidationError("Формат файла", choice,
                                  "нужно выбрать 1, 2 или 3")
        file = AudioFile(path, formats[choice],
                         ask_float("Длительность файла (сек): "))
        new_id = max((c.id for c in track.clips), default=0) + 1
        clip = AudioClip(new_id, file, ask_float("Начало (сек): "),
                         ask_float("Длительность клипа (сек): "))
        track.add_clip(clip)
        print(f"Добавлен: {clip}")

    def add_effect(self) -> None:
        """Create: добавляет эффект на дорожку."""
        _, track = self._find_track()
        kind = input("Эффект (1 - эхо, 2 - эквалайзер, 3 - затухание): ")
        new_id = max((e.id for e in track.effects), default=0) + 1
        if kind == "1":
            effect = Reverb(new_id, ask_float("Размер комнаты (0-1): "))
        elif kind == "2":
            effect = Equalizer(new_id, ask_float("Низкие (дБ): "),
                               ask_float("Средние (дБ): "),
                               ask_float("Высокие (дБ): "))
        elif kind == "3":
            effect = Fade(new_id, ask_float("Появление (сек): "),
                          ask_float("Затухание (сек): "))
        else:
            raise ValidationError("Тип эффекта", kind,
                                  "нужно выбрать 1, 2 или 3")
        track.add_effect(effect)
        print(f"Добавлен: {effect.describe()}")

    # ---------- файлы ----------
    @staticmethod
    def _choose_storage() -> JsonStorage | XmlStorage:
        """Спрашивает формат и возвращает нужное хранилище."""
        choice = input("Формат (1 - JSON, 2 - XML): ")
        if choice == "1":
            return JsonStorage(DATA_DIR / "data.json")
        if choice == "2":
            return XmlStorage(DATA_DIR / "data.xml")
        raise ValidationError("Формат файла", choice, "нужно выбрать 1 или 2")

    def _start(self) -> None:
        """При запуске: выбор формата и загрузка проектов из файла."""
        while self._storage is None:
            try:
                self._storage = self._choose_storage()
            except AudioEditorError as error:
                print(f"Ошибка: {error}")
        try:
            self._projects = self._storage.load()
            print(f"Загружено проектов: {len(self._projects)}")
        except StorageError as error:
            print(f"Ошибка: {error}")
            print("Начинаем с пустого списка проектов.")

    def save(self) -> None:
        """Сохраняет все проекты в файл, выбранный при запуске."""
        if self._storage is not None:
            self._storage.save(self._projects)
            print("Сохранено")

    # ---------- главный цикл ----------
    def run(self) -> None:
        """Главный цикл: показывает меню и выполняет пункты."""
        menu = {
            "1": ("Показать всё", self.show_all),
            "2": ("Создать проект", self.add_project),
            "3": ("Переименовать проект", self.rename_project),
            "4": ("Удалить проект", self.delete_project),
            "5": ("Добавить дорожку", self.add_track),
            "6": ("Изменить громкость дорожки", self.change_volume),
            "7": ("Удалить дорожку", self.delete_track),
            "8": ("Добавить клип", self.add_clip),
            "9": ("Добавить эффект", self.add_effect),
            "10": ("Сохранить", self.save),
        }
        try:
            print("=== Аудиоредактор ===")
            self._start()
            while True:
                print("\n=== Аудиоредактор ===")
                for key, (title, _) in menu.items():
                    print(f"{key}. {title}")
                print("0. Выход")
                choice = input("Выберите пункт: ").strip()
                if choice == "0":
                    break
                if choice not in menu:
                    print("Нет такого пункта.")
                    continue
                try:
                    menu[choice][1]()
                except AudioEditorError as error:
                    print(f"Ошибка: {error}")
        except (EOFError, KeyboardInterrupt):
            print()
        print("До свидания!")


if __name__ == "__main__":
    ConsoleApp().run()