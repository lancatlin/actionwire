from dataclasses import dataclass
from typing import override


@dataclass
class Color:
    name: str
    hue: int
    saturation: int
    brightness: int
    kelvin: int

    def __init__(self, name: str, color: list[int]) -> None:
        self._check(color)
        self.name = name
        [self.hue, self.saturation, self.brightness, self.kelvin] = color

    @override
    def __str__(self) -> str:
        return f"Color: {self.name}"

    def set_color(self, color: "Color") -> "Color":
        """Return a new color with the same brightness"""
        return color.set_brightness(self.brightness)

    def set_brightness(self, brightness: int) -> "Color":
        return Color(
            name=self.name,
            color=[
                self.hue,
                self.saturation,
                brightness,
                self.kelvin,
            ],
        )

    def code(self) -> list[int]:
        return [self.hue, self.saturation, self.brightness, self.kelvin]

    def _check(self, color: list[int]) -> None:
        if len(color) != 4:
            raise ValueError("the length of color input must be 4")
