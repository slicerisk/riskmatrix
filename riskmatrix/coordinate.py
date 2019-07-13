from __future__ import annotations
from typing import Tuple, Union
from .axis import AxisPoint


class Coordinate:
    """
    A collection of AxisPoints to represent a location in a matrix.
    """

    def __init__(self, points: Tuple[AxisPoint, AxisPoint]) -> None:
        if len(set(p.axis.matrix for p in points)) != 1:
            raise ValueError(
                "The points in this coordinate are not all from the same matrix."
            )
        self.points = points
        self.matrix = None

    def __repr__(self):
        return f"Coordinate({self.points})"

    def __str__(self) -> str:
        """ The str format is also used for determining equality with coordinates in string format """
        return f'{"".join(str(p.code) for p in self)}'

    def __getitem__(self, key: int) -> AxisPoint:
        return self.points[key]

    def __hash__(self) -> int:
        return hash(self.points)

    def __eq__(self, other: Union[Coordinate, str]) -> bool:
        """ Support equality for both string and Coordinate format """
        if type(other) is str:
            return str(self) == other
        return self.points == other.points

    @property
    def value(self) -> int:
        return sum(point.value for point in self.points)
