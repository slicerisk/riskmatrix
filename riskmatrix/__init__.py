"""
TODO
* Add matrix to coordinate so it can travel
* Write docstrings
* Type annotations
* Deterministic max value > what if 2 coordinates have the same value
* Import
* Charts
"""
from functools import total_ordering


class RiskMatrix:
    """
    Class to build a risk matrix. Contains 1 to n axes.
    """

    def __init__(self, name: str):
        self.name = name
        self.axes = {}
        self.categories = {}
        self.coordinates = {}

    def __repr__(self):
        return f"RiskMatrix({self.name}) " + str(self.axes)

    def __str__(self):
        return self.name

    def add_axis(self, axis_name: str, points):
        # Support list of axispoint codes and int for size
        axis = Axis(axis_name)

        if type(points) is list:
            for point in points:
                axis.add_point(point)
        elif type(points) is int:
            for code in range(1, points + 1):
                axis_point = AxisPoint(str(code))
                axis.add_point(axis_point)

        self._add_axis(axis)

    def _add_axis(self, axis):
        axis.matrix = self
        self.axes[axis.name] = axis

    def add_category(self, category):
        """ Check the category for None or existing value, and correct if true.
        Categories should be added from low to high if values are not explicitly set.
        """
        if category.value == None or category.value in [
            c.value for c in self.categories
        ]:
            category.value = len(self.categories) + 1
        self.categories[category.value] = category

    def map_coordinate(self, category, coordinate):
        self.coordinates[coordinate] = self.categories[category.value]
        coordinate.matrix = self

    def map_coordinates(self, category, coordinates):
        for coordinate in coordinates:
            self.map_coordinate(category, coordinate)

    def get_categories(self):
        return sorted(self.categories.values(), key=lambda x: x.value)

    def get_category(self, coordinate):
        for c in self.coordinates:
            if c == coordinate:
                return self.coordinates[c]

    def get_max_category(self, coordinates):
        max_category = None
        max_val = 0

        for coordinate in coordinates:
            cat = self.get_category(coordinate)
            if cat.value > max_val:
                max_val = cat.value
                max_category = cat

        return max_category

    def get_max_coordinate(self, coordinates):
        max_coordinate = None
        max_val = 0

        for coordinate in coordinates:
            if coordinate.value > max_val:
                max_val = coordinate.value
                max_coordinate = coordinate

        return max_coordinate


class Axis:
    """
    An axis of a risk matrix. Contains RiskMatrixAxisPoints
    This class holds the points together and can check and automatically
    correct the numeric value based on the order of the points.
    """

    def __init__(self, name):
        self.name = name
        self.points = []
        self.matrix = None

    def __repr__(self):
        return f"Axis({self.name})"

    def __str__(self):
        return self.name

    def __getitem__(self, key):
        return self.points[key]

    def __len__(self):
        return len(self.points)

    def add_point(self, point):
        # Check the point for None or existing value, and correct if true
        if point.value == None or point.value in [p.value for p in self]:
            point.value = len(self.points) + 1

        point.axis = self
        self.points.append(point)
        self.points = sorted(self.points)

    def get_points(self):
        return self.points


@total_ordering
class AxisPoint:
    """
    Has:
    * a code (e.g. 'A' or 1)
    * a name (e.g. 'Unlikely')
    * a description (e.g. For a definition.)
    * a numeric value
    """

    def __init__(self, code, name="", description="", value=None):
        self.code = code
        self.name = name
        self.desc = description
        self.value = value
        self.axis = None

    def __repr__(self):
        return f"AxisPoint{self.code, self.name, self.desc}"

    def __str__(self):
        return f"Point: {self.code} - {self.name}"

    def __eq__(self, other):
        """
        Allow equality based on code string or value.
        """
        if type(other) is str:
            return self.code == other
        return self.value == other.value

    def __lt__(self, other):
        return self.value < other.value

    def __hash__(self):
        return hash(f"{self.code} {self.name}")


class Coordinate:
    """
    A collection of AxisPoints to represent a location in a matrix.
    """

    def __init__(self, points):
        if len(set(p.axis.matrix for p in points)) != 1:
            raise ValueError(
                "The points in this coordinate are not all from the same matrix."
            )
        self.points = points
        self.matrix = None

    def __repr__(self):
        return f"Coordinate({self.points})"

    def __str__(self):
        """ The str format is also used for determining equality with coordinates in string format """
        return f'{"".join(str(p.code) for p in self)}'

    def __getitem__(self, key):
        return self.points[key]

    def __hash__(self):
        return hash(self.points)

    def __eq__(self, other):
        """ Support equality for both string and Coordinate format """
        if type(other) is str:
            return str(self) == other
        return self.points == other.points

    @property
    def value(self):
        return sum(point.value for point in self.points)


class Category:
    """
    A collection of points has a RiskMatrix Category.
    """

    def __init__(self, code, name, color, text_color, description="", value=None):
        self.code = code
        self.name = name
        self.desc = description
        self.color = color
        self.text_color = text_color
        self.value = value

    def __repr__(self):
        return f"Category{self.code, self.name, self.desc}"

    def __str__(self):
        return f"Category: {self.code} - {self.name}"
