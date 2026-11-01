"""Класс XmlStorage — хранение проектов в файле XML."""
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from exceptions import AudioEditorError, StorageError
from project import Project
from storage.converter import project_from_dict, project_to_dict


class XmlStorage:
    """Сохраняет список проектов в XML-файл и загружает его обратно.

    Простые значения записываются атрибутами тега,
    списки — тегом-контейнером с дочерними тегами.
    Встроенные ошибки Python при работе с файлом перехватываются
    и превращаются в StorageError с понятным сообщением.
    """

    # тег-контейнер -> тег одного элемента внутри него
    CONTAINERS: dict[str, str] = {
        "tracks": "track",
        "clips": "clip",
        "effects": "effect",
    }

    def __init__(self, path: Path) -> None:
        self.__path: Path = path

    # ---------- словарь <-> XML ----------
    @classmethod
    def __to_element(cls, tag: str, data: dict[str, Any]) -> ET.Element:
        """Строит XML-тег из словаря."""
        element = ET.Element(tag)
        for key, value in data.items():
            if isinstance(value, list):
                container = ET.SubElement(element, key)
                for item in value:
                    container.append(cls.__to_element(cls.CONTAINERS[key],
                                                      item))
            elif isinstance(value, dict):
                element.append(cls.__to_element(key, value))
            elif isinstance(value, bool):
                element.set(key, "true" if value else "false")
            else:
                element.set(key, str(value))
        return element

    @classmethod
    def __from_element(cls, element: ET.Element) -> dict[str, Any]:
        """Строит словарь из XML-тега (все значения — строки)."""
        data: dict[str, Any] = dict(element.attrib)
        for child in element:
            if child.tag in cls.CONTAINERS:
                data[child.tag] = [cls.__from_element(item)
                                   for item in child]
            else:
                data[child.tag] = cls.__from_element(child)
        return data

    # ---------- файл ----------
    def save(self, projects: list[Project]) -> None:
        """Сериализация: объекты -> словари -> XML-теги -> файл."""
        root = ET.Element("projects")
        for project in projects:
            root.append(self.__to_element("project",
                                          project_to_dict(project)))
        tree = ET.ElementTree(root)
        ET.indent(tree, space="    ")
        try:
            tree.write(self.__path, encoding="utf-8", xml_declaration=True)
        except OSError as error:
            raise StorageError(self.__path,
                               f"не удалось записать ({error})") from error

    def load(self) -> list[Project]:
        """Десериализация: файл -> XML-теги -> словари -> объекты."""
        # 1. читаем и разбираем файл
        try:
            root = ET.parse(self.__path).getroot()
        except FileNotFoundError as error:
            raise StorageError(self.__path, "не найден") from error
        except ET.ParseError as error:
            raise StorageError(self.__path,
                               f"повреждён ({error})") from error
        except OSError as error:
            raise StorageError(self.__path,
                               f"не удалось прочитать ({error})") from error

        if root.tag != "projects":
            raise StorageError(self.__path,
                               "нет корневого тега <projects>")

        # 2. собираем объекты модели
        try:
            return [project_from_dict(self.__from_element(element))
                    for element in root.findall("project")]
        except KeyError as error:
            raise StorageError(self.__path,
                               f"нет обязательного атрибута {error}"
                               ) from error
        except (TypeError, ValueError) as error:
            raise StorageError(self.__path,
                               f"неверная структура ({error})") from error
        except AudioEditorError as error:
            raise StorageError(self.__path,
                               f"некорректные данные — {error}") from error