from typing import Dict, Iterable, Optional, Tuple, Union
from . import Axis, AxisPoint, Category, Coordinate, Point


class RiskMatrix:
    """The main class to build a risk matrix."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.axes: Dict[str, Axis] = {}
        self._categories: Dict[int, Category] = {}
        self._coordinates: Dict[Coordinate, Category] = {}

    def __repr__(self):
        return f"RiskMatrix({self.name}) " + str(self.axes)

    def __str__(self):
        return self.name

    @property
    def categories(self) -> Tuple[Category, ...]:
        """Return a tuple of all Categories in the Riskmatrix.

        Returns:
            Tuple[Category, ...]: A tuple of Categories.
        """
        return tuple(sorted(self._categories.values(), key=lambda x: x.value))

    @property
    def coordinates(self):
        return tuple(self._coordinates.keys())

    def add_axis(
        self,
        axis_name: str,
        *,
        points: Iterable[Tuple] = None,
        size: int = None,
        use_letters: bool = False,
    ) -> Axis:
        """Add an axis to the risk matrix using a list of axis points.

        Alternatively, you can also give a size number to quickly set up an axis.
        This is nice if you don't care about the information in the axis points.

        Args:
            axis_name (str): The name for the axis. E.g. Severity or Probability.
            points (List[AxisPoint], optional): A list of points that make up the axis. Defaults to None.
            size (int, optional): A quick way to set up an axis by defining how many points you want. Defaults to None.
            use_letters (bool, optional): Option to use letters instead of numbers when specifying size. Defaults to False.

        Raises:
            ValueError: You have to provide either a list of points or a size. You can't do both.

        Returns:
            None
        """
        if points and size:
            raise ValueError(
                "You should choose between giving a list of points or defining a size."
            )

        axis = Axis(axis_name, self)

        if points:
            for point in points:
                p = Point(*point)
                axis.add_point(p)
        elif size:
            for code in range(1, size + 1):
                if use_letters:
                    code = self._convert_number_to_letter(code)
                axis_point = Point(str(code), "")
                axis.add_point(axis_point)

        self.axes[axis.name] = axis

        return axis

    def _convert_number_to_letter(self, number: int):
        """Provide a number between 1 and 26 to return the appropriate letter.

        Args:
            number (int): Number between 1 and 26

        Raises:
            ValueError: If the number is not between 1 and 26.

        Returns:
            str: A single letter equivalent to the number.
        """
        if not 0 <= number <= 26:
            raise ValueError(f"The number {number} has to be between 1 and 26.")

        return "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[number - 1]

    def add_category(
        self, code: str, name: str, color: str, text_color: str, description: str = ""
    ) -> Category:
        """Add a category to the Riskmatrix.

        Categories should be added from low to high if Category.value is not set,
        because it will be set with an increment. If Category.value is set, the
        order doesn't matter.

        Args:
            category (Category): An instance of Category.

        Returns:
            None
        """
        category = Category(code, name, color, text_color, description)
        category.value = len(self.categories)
        self._categories[category.value] = category

        return category

    def map_coordinate(
        self, category: Category, points: Iterable[AxisPoint]
    ) -> Coordinate:
        """Map a Category to a Coordinate

        Args:
            category (Category): An instance of Category.
            coordinate (Coordinate): An instance of Coordinate.

        Returns:
            None
        """
        c = Coordinate(points)

        if c.matrix is not self:
            raise ValueError(
                f"This Coordinate {c} does not belong to RiskMatrix {self.name}"
            )

        self._coordinates[c] = self.categories[category.value]
        return c

    def map_coordinates(
        self, category: Category, coordinates: Iterable[Iterable[AxisPoint]]
    ) -> None:
        """Given a Category and a list of Coordinate instances, map the Category to
        each Coordinate.

        Args:
            category (Category): A single Category instance.
            coordinates (List[Coordinate]): A list of Coordinate instances.

        Returns:
            None
        """
        for coordinate_points in coordinates:
            self.map_coordinate(category, coordinate_points)

    def get_category(self, coordinate: Coordinate) -> Optional[Category]:
        """Give a Coordinate to get a Category if there is a mapping between them.

        Args:
            coordinate (Coordinate): An instance of Coordinate.

        Returns:
            Optional[Category]: An instance of Category (or None if no Category could be found).
        """
        for c in self._coordinates:
            if c == coordinate:
                return self._coordinates[c]
        return None

    def get_coordinate(self, coordinate: str) -> Optional[Coordinate]:
        """Get the Coordinate for a string code like 'A2'.

        Args:
            coordinate (str): A string which is the code of the Coordinate. E.g. 'A2'

        Returns:
            Optional[Coordinate]: A Coordinate if it can be found, or None.
        """
        for c in self._coordinates:
            if str(c) == coordinate:
                return c
        return None

    def get_max_category(self) -> Optional[Category]:
        """Get the Category with the highest value in the RiskMatrix.

        Returns:
            Optional[Category]: The Category with the highest value.
            Will return None if there are no Categories defined in the RiskMatrix.
        """
        return max(self.categories, default=None)

    def get_max_coordinate(
        self,
        *,
        coordinates: Iterable[Coordinate] = None,
        coordinate_strings: Iterable[str] = None,
    ) -> Optional[Coordinate]:
        """Get the Coordinate with the highest value for a list of Coordinates.

        Todo:
            It's possible to get coordinates with the same value. It now returns the first coordinate with the
            highest value. This should be unambiguous by having a resolution order for the axes.

        Args:
            coordinates (List[Coordinate], optional): A list of Coordinates. Defaults to None.
            coordinate_strings (List[str], optional): A list of string Coordinate codes. Defaults to None.

        Returns:
            Optional[Coordinate]: The Coordinate with the highest value.
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
