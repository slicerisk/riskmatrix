from __future__ import annotations
from itertools import combinations
from typing import Iterable, Union, Tuple
from .axis import AxisPoint

# This is a hack to make mypy happy
if False:
    from .matrix import RiskMatrix


class Coordinate:
    """A collection of AxisPoints to represent a location in a matrix."""

    def __init__(self, points: Iterable[AxisPoint]) -> None:
        self.__check_requirements(points)
        self.matrix: RiskMatrix = set(p.axis.matrix for p in points).pop()
        # Order the points in the coordinate with the same order as the axes in the matrix.
        _points = []
        for axis in self.matrix.axes:
            for point in points:
                if axis == point.axis:
                    _points.append(point)
        self.points: Tuple[AxisPoint, ...] = tuple(_points)

    def __repr__(self):
        return f"Coordinate({[p.code for p in self.points]})"

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
            other = self.matrix.get_coordinate(other)

        if self.matrix.strict_coordinate_comparison:
            return str(self) == str(other)

        return self.value == other.value

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Coordinate):
            return NotImplemented

        value_self = sum(p.value for p in self.points)
        value_other = sum(p.value for p in other.points)

        # Start with a comparison of Category. This should take precedence over the location value.
        if self.category != other.category:
            return self.category.value < other.category.value

        # If mode is set to strict, compare Coordinates with equal value
        # on the exact string representation instead of value.
        if self.matrix.strict_coordinate_comparison and value_self == value_other:
            return str(self) < str(other)

        return value_self < value_other

    @property
    def value(self) -> int:
        return sum(p.value for p in self.points)

    @property
    def category(self):
        return self.matrix.get_category(self)

    def __check_requirements(self, points: Iterable[AxisPoint]):
        if any(p.axis is None for p in points):
            raise ValueError(
                "There is at least one point which is not tied to an axis."
            )

        if any(p.axis.matrix is None for p in points):
            raise ValueError(
                "There is at least one point with an axis that is not tied to a matrix."
            )

        point_pairs = (pair for pair in combinations(points, 2))
        pair_sets = (set((pair[0].axis, pair[1].axis)) for pair in point_pairs)
        if any((len(s) == 1 for s in pair_sets)):
            raise ValueError(
                "There are two points on the same axis. Every point of a coordinate should be on a different axis."
            )

        if len(set(p.axis.matrix for p in points)) != 1:
            raise ValueError(
                "The points in this coordinate are not all from the same matrix."
            )
