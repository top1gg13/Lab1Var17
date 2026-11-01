"""Консольное приложение «Аудиоредактор» — точка входа программы."""
from pathlib import Path

from domain import (
    AudioClip,
    AudioFile,
    AudioTrack,
    Equalizer,
    Fade,
    MidiTrack,
    Project,
    Reverb,
    Track,
)
from exceptions.audio_editor_error import AudioEditorError
from exceptions.not_found_error import NotFoundError
from exceptions.validation_error import ValidationError
from storage import JsonStorage, XmlStorage

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
        self._projects: list[Project] = []

    # ---------- поиск ----------
    def _find_project(self) -> Project:
        project_id = ask_int("id проекта: ")
        for project in self._projects:
            if project.id == project_id:
                return project
        raise NotFoundError(f"Проект с id={project_id} не найден")

    def _find_track(self) -> tuple[Project, Track]:
        project = self._find_project()
        return project, project.get_track(ask_int("id дорожки: "))

    # ---------- проекты ----------
    def show_all(self) -> None:
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
        new_id = max((p.id for p in self._projects), default=0) + 1
        project = Project(new_id, input("Название: "),
                          ask_int("Частота (44100/48000/96000): "))
        self._projects.append(project)
        print(f"Создан: {project}")

    def rename_project(self) -> None:
        project = self._find_project()
        project.rename(input("Новое название: "))
        print(f"Обновлено: {project}")

    def delete_project(self) -> None:
        self._projects.remove(self._find_project())
        print("Проект удалён")

    # ---------- дорожки ----------
    def add_track(self) -> None:
        project = self._find_project()
        kind = input("Тип (1 - аудио, 2 - MIDI): ")
        new_id = max((t.id for t in project.tracks), default=0) + 1
        title = input("Название: ")
        volume = ask_float("Громкость (0-1): ")
        if kind == "1":
            track: Track = AudioTrack(new_id, title, volume)
        elif kind == "2":
            track = MidiTrack(new_id, title, volume, input("Инструмент: "))
        else:
            raise ValidationError("Нужно выбрать 1 или 2")
        project.add_track(track)
        print(f"Добавлена: {track}")

    def change_volume(self) -> None:
        _, track = self._find_track()
        track.volume = ask_float("Новая громкость (0-1): ")
        print(f"Обновлено: {track}")

    def delete_track(self) -> None:
        project, track = self._find_track()
        project.remove_track(track.id)
        print("Дорожка удалена")

    # ---------- клипы и эффекты ----------
    def add_clip(self) -> None:
        _, track = self._find_track()
        if not isinstance(track, AudioTrack):
            raise ValidationError("Клипы есть только у аудиодорожек")
        file = AudioFile(input("Файл: "), input("Формат (wav/mp3/flac): "),
                         ask_float("Длительность файла (сек): "))
        new_id = max((c.id for c in track.clips), default=0) + 1
        clip = AudioClip(new_id, file, ask_float("Начало (сек): "),
                         ask_float("Длительность клипа (сек): "))
        track.add_clip(clip)
        print(f"Добавлен: {clip}")

    def add_effect(self) -> None:
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
            raise ValidationError("Нужно выбрать 1, 2 или 3")
        track.add_effect(effect)
        print(f"Добавлен: {effect.describe()}")

    # ---------- файлы ----------
    @staticmethod
    def _choose_storage() -> JsonStorage | XmlStorage:
        choice = input("Формат (1 - JSON, 2 - XML): ")
        if choice == "1":
            return JsonStorage(DATA_DIR / "data.json")
        if choice == "2":
            return XmlStorage(DATA_DIR / "data.xml")
        raise ValidationError("Нужно выбрать 1 или 2")

    def save(self) -> None:
        self._choose_storage().save(self._projects)
        print("Сохранено")

    def load(self) -> None:
        self._projects = self._choose_storage().load()
        print("Загружено")

    # ---------- главный цикл ----------
    def run(self) -> None:
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
            "10": ("Сохранить в файл", self.save),
            "11": ("Загрузить из файла", self.load),
        }
        try:
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