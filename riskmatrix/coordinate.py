from __future__ import annotations
from typing import Iterable, Union, Tuple
from .axis import AxisPoint

# This is a hack to make mypy happy
if False:
    from .matrix import RiskMatrix


class Coordinate:
    """A collection of AxisPoints to represent a location in a matrix."""

    def __init__(self, points: Iterable[AxisPoint]) -> None:
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

        self.matrix: RiskMatrix = set(p.axis.matrix for p in points).pop()
        # Order the points in the coordinate with the same order as the axes in the matrix.
        _points = []
        for axis in self.matrix.axes:
            for point in points:
                if axis == point.axis:
                    _points.append(point)
        self.points: Tuple[AxisPoint, ...] = tuple(_points)

    def __repr__(self):
        return f"Coordinate({self.points})"

    def __str__(self) -> str:
        """ The str format is also used for determining equality with coordinates in string format """
        return f'{"".join(str(p.code) for p in self.points)}'

    def __getitem__(self, key: int) -> AxisPoint:
        return self.points[key]

    def __hash__(self) -> int:
        return hash(self.points)

    def __eq__(self, other: object) -> bool:
        """Check if two Coordinates are pointing to the same location.

        Args:
            other (Union[Coordinate, str]): A Coordinate object or string version.

        Returns:
            bool: Return True if coordinate location is equal, return False otherwise.
        """
        if not isinstance(other, (Coordinate, str)):
            return NotImplemented
        if isinstance(other, str):
            return str(self) == other
        return self.points == other.points

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Coordinate):
            return NotImplemented

        value_self = sum(p.value for p in self.points)
        value_other = sum(p.value for p in other.points)

        # If we need an order even if two coordinates have equivalent values,
        # compare the strings. This means the coordinates are ordered alphabetically
        # which is determined by the order of the axes.
        if value_self == value_other and self.matrix.force_coordinate_order:
            return str(self) < str(other)

        return value_self < value_other

    @property
    def value(self) -> int:
        return sum(p.value for p in self.points)
