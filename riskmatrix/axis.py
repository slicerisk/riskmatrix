from __future__ import annotations
from functools import total_ordering
from typing import List, Optional, Tuple, Union


@total_ordering
class AxisPoint:
    """
    Has:
    * a code (e.g. 'A' or 1)
    * a name (e.g. 'Unlikely')
    * a description (e.g. For a definition.)
    * a numeric value
    """

    def __init__(
        self,
        code: str,
        name: str = "",
        description: str = "",
        value: Optional[int] = None,
    ) -> None:
        self.code = code
        self.name = name
        self.desc = description
        self.value = value
        self.axis = None

    def __repr__(self):
        return f"AxisPoint{self.code, self.name, self.desc}"

    def __str__(self):
        return f"Point: {self.code} - {self.name}"

    def __eq__(self, other: object) -> bool:
        """
        Allow equality based on code string or value.
        """
        if not isinstance(other, (AxisPoint, str)):
            return NotImplemented

        if isinstance(other, str):
            return self.code == other

        return self.value == other.value

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, AxisPoint):
            return NotImplemented

        return self.value < other.value

    def __hash__(self) -> int:
        return hash(f"{self.code} {self.name}")


class Axis:
    """An axis for a RiskMatrix. Contains AxisPoints.
    This class holds the points together and gives them an order.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self._points: List[AxisPoint] = []
        self.matrix = None

    def __repr__(self):
        return f"Axis({self.name})"

    def __str__(self):
        return self.name

    def __getitem__(self, key: int) -> AxisPoint:
        return self.points[key]

    def __len__(self) -> int:
        return len(self.points)

    @property
    def points(self) -> Tuple[AxisPoint, ...]:
        """Get the points of the Axis.

        :return: An ordered tuple of AxisPoint
        :rtype: Tuple[AxisPoint, ...]
        """
        return tuple(self._points)

    def add_point(self, point: AxisPoint) -> None:
        """Add an AxisPoint to the Axis.

        If no value is set, the AxisPoint value is set to the length+1 of the Axis.
        This means it's possible to have a point with a set value, and one without
        that gets set to the same value. In these cases, a ValueError is thrown.

        Args:
            point (AxisPoint): The point to add to the Axis.

        Raises:
            ValueError: Is raised when attempting to add an AxisPoint with a value that already exists.

        Returns:
            None
        """
        if point.value == None:
            point.value = len(self._points) + 1

        if point.value in [p.value for p in self._points]:
            raise ValueError(
                f"An AxisPoint with value {point.value} already exists on Axis {self.name}."
            )

        point.axis = self
        self._points.append(point)
        self._points = sorted(self.points)
