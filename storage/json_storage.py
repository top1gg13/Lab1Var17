"""Класс JsonStorage — хранение проектов в файле JSON."""
import json
from pathlib import Path

from exceptions import AudioEditorError, StorageError
from project import Project
from storage.converter import project_from_dict, project_to_dict


class JsonStorage:
    """Сохраняет список проектов в JSON-файл и загружает его обратно.

    Встроенные ошибки Python при работе с файлом перехватываются
    и превращаются в StorageError с понятным сообщением.
    """

    def __init__(self, path: Path) -> None:
        self.__path: Path = path

    def save(self, projects: list[Project]) -> None:
        """Сериализация: объекты -> словари -> текст JSON -> файл."""
        data = {"projects": [project_to_dict(p) for p in projects]}
        text = json.dumps(data, ensure_ascii=False, indent=2)
        try:
            self.__path.write_text(text, encoding="utf-8")
        except OSError as error:
            raise StorageError(self.__path,
                               f"не удалось записать ({error})") from error

    def load(self) -> list[Project]:
        """Десериализация: файл -> текст JSON -> словари -> объекты."""
        # 1. читаем файл
        try:
            text = self.__path.read_text(encoding="utf-8")
        except FileNotFoundError as error:
            raise StorageError(self.__path, "не найден") from error
        except OSError as error:
            raise StorageError(self.__path,
                               f"не удалось прочитать ({error})") from error

        # 2. разбираем текст JSON
        try:
            data = json.loads(text)
        except json.JSONDecodeError as error:
            raise StorageError(
                self.__path, f"повреждён (строка {error.lineno})"
            ) from error

        # 3. собираем объекты модели
        try:
            return [project_from_dict(item) for item in data["projects"]]
        except KeyError as error:
            raise StorageError(self.__path,
                               f"нет обязательного поля {error}") from error
        except (TypeError, ValueError) as error:
            raise StorageError(self.__path,
                               f"неверная структура ({error})") from error
        except AudioEditorError as error:
            raise StorageError(self.__path,
                               f"некорректные данные — {error}") from error