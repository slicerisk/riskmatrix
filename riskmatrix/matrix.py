from typing import List, Optional, Tuple, Union

from .axis import Axis, AxisPoint
from .category import Category
from .coordinate import Coordinate


class RiskMatrix:
    """
    Class to build a risk matrix. Contains 1 to n axes.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.axes = {}
        self.categories = {}
        self.coordinates = {}

    def __repr__(self):
        return f"RiskMatrix({self.name}) " + str(self.axes)

    def __str__(self):
        return self.name

    def add_axis(
        self, axis_name: str, *, points: List[AxisPoint] = None, size: int = None
    ) -> None:
        # Support list of axispoint codes and int for size
        if points and size:
            raise ValueError(
                "You should choose between giving a list of points or defining a size."
            )

        axis = Axis(axis_name)

        if points:
            for point in points:
                axis.add_point(point)
        elif size:
            for code in range(1, size + 1):
                axis_point = AxisPoint(str(code))
                axis.add_point(axis_point)

        self._add_axis(axis)

    def _add_axis(self, axis: Axis) -> None:
        axis.matrix = self
        self.axes[axis.name] = axis

    def add_category(self, category: Category) -> None:
        """ Check the category for None or existing value, and correct if true.
        Categories should be added from low to high if values are not explicitly set.
        """
        if category.value == None or category.value in [
            c.value for c in self.categories
        ]:
            category.value = len(self.categories) + 1
        self.categories[category.value] = category

    def map_coordinate(self, category: Category, coordinate: Coordinate) -> None:
        self.coordinates[coordinate] = self.categories[category.value]
        coordinate.matrix = self

    def map_coordinates(
        self, category: Category, coordinates: List[Coordinate]
    ) -> None:
        for coordinate in coordinates:
            self.map_coordinate(category, coordinate)

    def get_categories(self) -> List[Category]:
        return sorted(self.categories.values(), key=lambda x: x.value)

    def get_category(self, coordinate: Union[Coordinate, str]) -> Optional[Category]:
        for c in self.coordinates:
            if c == coordinate:
                return self.coordinates[c]

    def get_max_category(self, coordinates: List[str]) -> Category:
        max_category = None
        max_val = 0

        for coordinate in coordinates:
            cat = self.get_category(coordinate)
            if cat.value > max_val:
                max_val = cat.value
                max_category = cat

        return max_category

    def get_max_coordinate(self, coordinates: List[Coordinate]) -> Coordinate:
        max_coordinate = None
        max_val = 0

        for coordinate in coordinates:
            if coordinate.value > max_val:
                max_val = coordinate.value
                max_coordinate = coordinate

        return max_coordinate
