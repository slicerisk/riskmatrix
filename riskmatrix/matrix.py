from typing import Dict, Iterable, Optional, Tuple, Union
from . import Axis, AxisPoint, Category, Coordinate, Point


class AxesDescriptor:
    """A descriptor for the axes attribute on the RiskMatrix.

    Raises:
        KeyError: When an axis name is not found in the axes.
        AttributeError: Overriding or deleting the axes attribute is not allowed.
    """

    def __init__(self):
        self._axes = []

    def __get__(self, instance, owner) -> Tuple[Axis, ...]:
        return tuple(self._axes)

    def __getitem__(self, val: Union[str, int]) -> Axis:
        if isinstance(val, str):
            for axis in self._axes:
                if axis.name == val:
                    return axis
            raise KeyError(f"No axis named {val}.")

        if isinstance(val, int):
            return self._axes[val]

        raise TypeError(f"Axes indices must be integers, or strings, not {val}")

    def __iter__(self):
        self.__i = 0
        return self

    def __next__(self):
        try:
            val = self[self.__i]
        except IndexError:
            raise StopIteration
        self.__i += 1
        return val

    def __set__(self, instance, val):
        raise AttributeError("Can't override axes attribute. Add axes individually.")

    def __delete__(self, instance):
        raise AttributeError("Can't delete axes attribute.")

    def add(self, axis: Axis):
        self._axes.append(axis)


class RiskMatrix:
    """The main class to build a risk matrix."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.axes: AxesDescriptor = AxesDescriptor()
        self._categories: Dict[int, Category] = {}
        self._coordinates: Dict[Coordinate, Category] = {}

        # This boolean determines whether it's ok to force Coordinate order if they have a similar value.
        # Setting it to False can make ordering Coordinates with equivalent values ambiguous.
        self.force_coordinate_order = True

    def __repr__(self):
        return f"RiskMatrix({self.name}) " + str(self.axes)

    def __str__(self):
        return self.name

    @property
    def categories(self) -> Tuple[Category, ...]:
        """Return a tuple of all Categories in the Riskmatrix.

        Sorted by value from low to high.

        Returns:
            Tuple[Category, ...]: A tuple of Categories.
        """
        return tuple(sorted(self._categories.values(), key=lambda x: x.value))

    @property
    def coordinates(self) -> Tuple[Coordinate, ...]:
        """Return a tuple of all Coordinates in the RiskMatrix.

        Returns:
            Tuple[Coordinate, ...]: Tuple of Coordinates sorted alphabetically.
        """
        return tuple(sorted(self._coordinates, key=lambda c: str(c)))

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
            points (Iterable[Tuple], optional): A list of points that make up the axis. Defaults to None.
            size (int, optional): A quick way to set up an axis by defining how many points you want. Defaults to None.
            use_letters (bool, optional): Option to use letters instead of numbers when specifying size. Defaults to False.

        Raises:
            ValueError: You have to provide either a list of points or a size. You can't do both.

        Returns:
            Axis
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

        self.axes.add(axis)

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

        Categories should be added from low to high.

        Args:
            code (str): A short code for the category. E.g. 'HIG'
            name (str): A full name for the category. E.g. 'High risk'
            color (str): A hexadecimal background color code.
            text_color (str): A hexadecimal text color code.
            description (str, optional): A longer description about what this category means. Defaults to "".

        Returns:
            Category
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
            points (Iterable[AxisPoint]): A collection of AxisPoint that make up a Coordinate.

        Returns:
            Coordinate
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
        """Given a Category and a list of AxisPoint collections (each making up a Coordinate), map the Category to
        each Coordinate.

        Args:
            category (Category): A single Category.
            coordinates (Iterable[Iterable[AxisPoint]]): A list of AxisPoint iterables that represent Coordinates.

        Returns:
            None
        """
        for coordinate_points in coordinates:
            self.map_coordinate(category, coordinate_points)

    def get_category(self, coordinate: Coordinate) -> Category:
        """Give a Coordinate to get a Category if there is a mapping between them.

        Args:
            coordinate (Coordinate): An instance of Coordinate.

        Returns:
            Category: An instance of Category.

        Exceptions:
            IndexError: If the Coordinate couldn't be found, an IndexError is raised.
        """
        try:
            return self._coordinates[coordinate]
        except KeyError as e:
            raise KeyError(
                f"{coordinate} couldn't be found. Are you sure you mapped it?"
            ) from e

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
