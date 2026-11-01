"""Слой хранения: запись и чтение проектов в файлах JSON и XML."""
from storage.json_storage import JsonStorage
from storage.xml_storage import XmlStorage

__all__ = ["JsonStorage", "XmlStorage"]
