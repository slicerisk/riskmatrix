from __future__ import annotations
from typing import Tuple, Union
from .axis import AxisPoint


class Coordinate:
    """A collection of AxisPoints to represent a location in a matrix."""

    def __init__(self, points: Tuple[AxisPoint]) -> None:
        if any(p.axis is None for p in points):
            raise ValueError(
                "There is at least one point which is not tied to an axis."
            )

        if any(p.axis.matrix is None for p in points):
            raise ValueError(
                "There is at least one point with an axis that is not tied to a matrix."
            )

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
        return f'{"".join(str(p.code) for p in self.points)}'

    def __getitem__(self, key: int) -> AxisPoint:
        return self.points[key]

    def __hash__(self) -> int:
        return hash(self.points)

    def __eq__(self, other: Coordinate) -> bool:
        return sum(p.value for p in self.points) == sum(p.value for p in other.points)

    def __lt__(self, other: Coordinate) -> bool:
        return sum(p.value for p in self.points) < sum(p.value for p in other.points)

    @property
    def value(self) -> int:
        return sum(p.value for p in self.points)

    def location_equals(self, other: Union[Coordinate, str]) -> bool:
        """Check if two Coordinates are pointing to the same location.

        Support equality for both string and Coordinate format.

        :param other: A Coordinate object or string representation.
        :type other: Union[Coordinate, str]
        :return: Return True if coordinate location is equal, otherwise return False.
        :rtype: bool
        """
        if type(other) is str:
            return str(self) == other
        return self.points == other.points
