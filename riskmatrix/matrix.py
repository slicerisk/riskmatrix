from typing import List, Optional, Tuple, Union
from . import Axis, AxisPoint, Category, Coordinate


class RiskMatrix:
    """The main class to build a risk matrix.
    It contains 1 to n axes.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.axes = {}
        self.categories = {}
        self._coordinates = {}

    def __repr__(self):
        return f"RiskMatrix({self.name}) " + str(self.axes)

    def __str__(self):
        return self.name

    @property
    def coordinates(self):
        return tuple(self._coordinates.keys())

    def add_axis(
        self, axis_name: str, *, points: List[AxisPoint] = None, size: int = None
    ) -> None:
        """Add an axis to the risk matrix using a list of axis points.

        Alternatively, you can also give a size number to quickly set up an axis.
        This is nice if you don't care about the information in the axis points.

        :param axis_name: The name for the axis. E.g. Severity or Probability.
        :type axis_name: str
        :param points: A list of AxisPoint that make up the axis, defaults to None
        :type points: List[AxisPoint], optional
        :param size: A quick way to set up an axis by defining how many points you want, defaults to None
        :type size: int, optional
        :raises ValueError: You have to provide either a list of points or a size. You can't do both.
        """
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
        """Helper function to add an Axis to the Riskmatrix.

        :param axis: Should be a single Axis.
        :type axis: Axis
        """
        axis.matrix = self
        self.axes[axis.name] = axis

    def add_category(self, category: Category) -> None:
        """Add a Category to the Riskmatrix.

        Categories should be added from low to high if Category.value is not set,
        because it will be set with an increment. If Category.value is set, the
        order doesn't matter.

        :param category: An instance of Category.
        :type category: Category
        """
        if category.value == None or category.value in [
            c.value for c in self.categories
        ]:
            category.value = len(self.categories) + 1
        self.categories[category.value] = category

    def map_coordinate(self, category: Category, coordinate: Coordinate) -> None:
        """Map a Category to a Coordinate.

        :param category: An instance of Category
        :type category: Category
        :param coordinate: An instance of Coordinate
        :type coordinate: Coordinate
        """
        self._coordinates[coordinate] = self.categories[category.value]
        coordinate.matrix = self

    def map_coordinates(
        self, category: Category, coordinates: List[Coordinate]
    ) -> None:
        """Given a Category and a list of Coordinate instances, map the Category to
        each Coordinate.

        :param category: A single Category instance.
        :type category: Category
        :param coordinates: A list of Coordinate instances.
        :type coordinates: List[Coordinate]
        """
        for coordinate in coordinates:
            self.map_coordinate(category, coordinate)

    def get_categories(self) -> Tuple[Category]:
        """Return a tuple of all Categories in the Riskmatrix.

        :return: A tuple of Categories
        :rtype: Tuple[Category]
        """
        return tuple(sorted(self.categories.values(), key=lambda x: x.value))

    def get_category(self, coordinate: Coordinate) -> Optional[Category]:
        """Give a Coordinate to get a Category if there is a mapping between them.

        :param coordinate: An instance of Coordinate.
        :type coordinate: Coordinate
        :return: An instance of Category or None if no Category could be found.
        :rtype: Optional[Category]
        """
        for c in self._coordinates:
            if c == coordinate:
                return self._coordinates[c]

    def get_coordinate(self, coordinate: str) -> Coordinate:
        """Get the Coordinate for a string code like 'A2'.

        :param coordinate: A string which is the code of the Coordinate. E.g. 'A2'
        :type coordinate: str
        :return: A Coordinate object if it can be found, or None.
        :rtype: Optional[Coordinate]
        """
        for c in self._coordinates:
            if str(c) == coordinate:
                return c

    def get_max_category(self) -> Category:
        """Get the Category with the highest value in the risk matrix.

        :return: The category with the highest value.
        :rtype: Category
        """
        return max(self.get_categories())

    def get_max_coordinate(
        self,
        *,
        coordinates: List[Coordinate] = None,
        coordinate_strings: List[str] = None,
    ) -> Coordinate:
        """Get the Coordinate with the highest value for a list of Coordinates.

        TODO: It's possible to get coordinates with the same value. It now returns the first coordinate with the
        highest value. This should be unambiguous by having a resolution order for the axes.

        :param coordinates: A list of Coordinate objects.
        :type coordinates: List[Coordinate]
        :param coordinate_strings: A list of string Coordinate codes.
        :type coordinate_strings: List[str]
        :return: The coordinate with the highest value.
        :rtype: Coordinate
        """

        all_coordinates = []

        if coordinate_strings:
            for c_str in coordinate_strings:
                c = self.get_coordinate(c_str)
                if c:
                    all_coordinates.append(c)

        if coordinates:
            all_coordinates += coordinates

        max_coordinate = None
        max_val = 0

        for coordinate in all_coordinates:
            if coordinate.value > max_val:
                max_val = coordinate.value
                max_coordinate = coordinate

        return max_coordinate
