"""Класс MidiTrack — MIDI-дорожка с виртуальным инструментом."""
from exceptions import ValidationError
from tracks.track import Track


class MidiTrack(Track):
    """Дорожка с нотами для виртуального инструмента (без клипов)."""

    def __init__(self, track_id: int, title: str, volume: float,
                 instrument: str, muted: bool = False) -> None:
        super().__init__(track_id, title, volume, muted)
        self.__instrument: str = self.__check_instrument(instrument)

    @staticmethod
    def __check_instrument(instrument: str) -> str:
        instrument = instrument.strip()
        if not instrument:
            raise ValidationError("Инструмент", instrument,
                                  "не может быть пустым")
        return instrument

    @property
    def instrument(self) -> str:
        """Название инструмента, например Piano."""
        return self.__instrument

    def change_instrument(self, instrument: str) -> None:
        """Меняет инструмент дорожки."""
        self.__instrument = self.__check_instrument(instrument)

    def kind(self) -> str:
        return "midi"

    def __str__(self) -> str:
        return (f"MIDI-дорожка {super().__str__()}, "
                f"инструмент: {self.__instrument}")