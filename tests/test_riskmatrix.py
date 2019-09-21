import pytest
from riskmatrix import RiskMatrix, Axis, AxisPoint, Category, Coordinate, Point


@pytest.fixture
def rm():
    return RiskMatrix("Risk Matrix name")


@pytest.fixture
def rm_points():
    return (
        Point("A", "Unlikely"),
        Point("B", "Likely"),
        Point("C", "Very Likely"),
        Point(1, "No Impact"),
        Point(2, "Cheap"),
        Point(3, "Expensive"),
    )


@pytest.fixture
def rm_categories():
    return (
        ("LOW", "Low risk", "#ffff11", "#ffffff"),
        ("MED", "Med risk", "#ffff00", "#ffffff"),
        ("HIG", "Hig risk", "#ff0000", "#ffffff"),
    )


@pytest.fixture
def rm_with_axis(rm, rm_points):
    a, b, c, one, two, three = rm_points

    rm.add_axis("x", points=[a, b, c])
    rm.add_axis("y", points=[one, two, three])

    return rm


@pytest.fixture
def rm_with_categories(rm_with_axis, rm_categories):
    rm = rm_with_axis
    low, med, hig = rm_categories

    rm.add_category(*low)
    rm.add_category(*med)
    rm.add_category(*hig)

    return rm


@pytest.fixture
def rm_coordinates(rm_with_categories):
    rm = rm_with_categories
    a, b, c = rm.axes["x"].points
    one, two, three = rm.axes["y"].points

    return (
        Coordinate((a, one)),
        Coordinate((a, two)),
        Coordinate((a, three)),
        Coordinate((b, one)),
        Coordinate((b, two)),
        Coordinate((b, three)),
        Coordinate((c, one)),
        Coordinate((c, two)),
        Coordinate((c, three)),
    )


@pytest.fixture
def rm_full(rm_with_categories, rm_coordinates):
    rm = rm_with_categories
    low, med, hig = rm.categories

    a1, a2, a3, b1, b2, b3, c1, c2, c3 = rm_coordinates

    rm.map_coordinates(low, [a1, a2, a3, b1])
    rm.map_coordinates(med, [b2, c1])
    rm.map_coordinates(hig, [b3, c2, c3])

    return rm


class TestRiskMatrix:
    def test_riskmatrix_name(self):
        name = "Test name 1"
        rm = RiskMatrix(name)

        assert rm.name == name

        name2 = "Test name 2"

        assert rm.name != name2

        rm.name = name2

        assert rm.name == name2
        assert rm.name != name

    def test_sorted_coordinates(self, rm_full):
        rm = rm_full
        raw_data = ["A1", "B2", "C3", "A3", "B1", "B1", "A2"]

        # Get top 2 values
        coordinates = (rm.get_coordinate(c) for c in raw_data)
        r = sorted(coordinates, reverse=True)[:2]

        assert r == [rm.get_coordinate("C3"), rm.get_coordinate("B2")]

    def test_coordinates_have_right_category(self, rm_full):
        # Each category has all coordinates
        # These are the categories in rm_full:
        # low =  a1, a2, a3, b1
        # med =  b2, c1
        # hig =  b3, c2, c3
        rm = rm_full

        a1, a2, a3, b1, b2, b3, c1, c2, c3 = rm.coordinates
        low, med, hig = rm.categories

        assert a1.category == low
        assert a2.category == low
        assert a3.category == low
        assert b1.category == low
        assert b2.category == med
        assert c1.category == med
        assert b3.category == hig
        assert c2.category == hig
        assert c3.category == hig

    def test_coordinates_order_alphabetical(self, rm_full, rm_coordinates):
        rm = rm_full
        a1, a2, a3, b1, b2, b3, c1, c2, c3 = rm_coordinates
        a1a, a2a, a3a, b1a, b2a, b3a, c1a, c2a, c3a = rm.coordinates

        assert a1 == a1a
        assert a2 == a2a
        assert a3 == a3a
        assert b1 == b1a
        assert b2 == b2a
        assert b3 == b3a
        assert c1 == c1a
        assert c2 == c2a
        assert c3 == c3a

    def test_coordinate_median(self, rm_full):
        rm = rm_full
        raw_data = ["A1", "B2", "C3", "A3", "B1", "B1", "A2"]

        # Convert into coordinates
        coordinates = (rm.get_coordinate(c) for c in raw_data)

        # Calculate median
        import statistics

        median = statistics.median(coordinates)

        assert median == rm_full.get_coordinate("B1")


class TestAxis:
    def test_add_axis_with_points(self, rm, rm_points):
        a, b, c, *_ = rm_points

        rm.add_axis("x", points=[a, b, c])
        aa, bb, cc = rm.axes["x"].points

        assert a.code == aa.code
        assert a.name == aa.name
        assert a.description == aa.desc
        assert a.code != bb.code
        assert b.code == bb.code
        assert rm.axes["x"][0] is aa
        assert rm.axes["x"][1] is bb
        assert rm.axes["x"][2] is cc

    def test_add_axis_conflicting_named_arguments(self, rm, rm_points):
        a, b, c, *_ = rm_points

        try:
            rm.add_axis("x", points=[a, b, c], size=4)
        except ValueError as e:
            assert (
                str(e)
                == "You should choose between giving a list of points or defining a size."
            )

    def test_add_axis_requires_named_arguments(self, rm, rm_points):
        a, b, c, *_ = rm_points

        try:
            rm.add_axis("x", [a, b, c])
        except TypeError as e:
            assert str(e).startswith("add_axis() takes 2 positional arguments")

    def test_add_axis_with_size(self, rm):
        rm.add_axis("x", size=4)

        assert rm.axes["x"][0].code == "1"
        assert rm.axes["x"][1].code == "2"
        assert rm.axes["x"][2].code == "3"
        assert rm.axes["x"][3].code == "4"
        assert len(rm.axes["x"]) == 4

    def test_convert_number_to_letter(self, rm):
        assert rm._convert_number_to_letter(1) == "A"
        assert rm._convert_number_to_letter(26) == "Z"

        try:
            number = 27
            rm._convert_number_to_letter(number)
        except ValueError as e:
            assert str(e) == f"The number {number} has to be between 1 and 26."

        try:
            number = 0
            rm._convert_number_to_letter(number)
        except ValueError as e:
            assert str(e) == f"The number {number} has to be between 1 and 26."


class TestCategory:
    def test_add_category(self, rm, rm_categories):
        low, med, hig = rm_categories

        rm.add_category(*low)
        rm.add_category(*med)
        rm.add_category(*hig)

        assert len(rm.categories) == 3

        assert rm.categories[0].value == 0
        assert rm.categories[1].value == 1
        assert rm.categories[2].value == 2

    def test_get_categories(self, rm_with_categories, rm_categories):
        low_origin, med_origin, hig_origin = rm_categories
        low, med, hig = rm_with_categories.categories

        assert (low.code, low.name, low.color, low.text_color) == (low_origin)
        assert (med.code, med.name, med.color, med.text_color) == (med_origin)
        assert (hig.code, hig.name, hig.color, hig.text_color) == (hig_origin)

    def test_category_value(self, rm_with_categories):
        low, med, hig = rm_with_categories.categories

        assert low.value == 0
        assert med.value == 1
        assert hig.value == 2

    def test_max_category(self, rm_full):
        assert rm_full.get_max_category().value == 2


class TestCoordinate:
    def test_add_coordinate(self, rm_with_categories, rm_coordinates):
        rm = rm_with_categories

        low, med, hig = rm.categories
        a1, a2, a3, b1, b2, b3, c1, c2, c3 = rm_coordinates

        rm.map_coordinates(low, [a1, a2, a3, b1])
        rm.map_coordinates(med, (b2, b3, c1, c2))
        rm.map_coordinate(hig, c3)

        assert rm.get_category(a3) == low
        # assert rm.get_category(b2) == med
        assert rm.get_category(c3) == hig

    def test_add_multiple_points_on_one_axis(self, rm_with_axis):
        rm = rm_with_axis

        a, b, _ = rm.axes["x"].points

        try:
            Coordinate((a, b))
        except ValueError as e:
            assert (
                str(e)
                == "There are two points on the same axis. Every point of a coordinate should be on a different axis."
            )
        else:
            assert False

    def test_get_coordinate(self, rm_with_categories):
        rm = rm_with_categories
        low, med, hig = rm.categories
        a, b, c = rm.axes["x"].points
        one, two, three = rm.axes["y"].points

        rm.map_coordinates(low, [(a, one), (a, two), (a, three), (b, one)])

        rm.map_coordinates(med, [(b, two), (b, three), (c, one), (c, two)])

        c3 = rm.map_coordinate(hig, (c, three))

        get_c3 = rm.get_coordinate("C3")
        assert get_c3 == c3
        assert rm.get_category(get_c3) == hig

    def test_equivalent_coordinate_value(self, rm_full):
        """Test if we can force a coordinate order if two Coordinates have
        an equal value by using alphabetical order. Then also test if we can
        turn it off and let max() return the first of the equal values.
        """
        rm = rm_full

        c2 = rm.get_coordinate("C2")
        b3 = rm.get_coordinate("B3")

        rm.force_coordinate_order = True
        assert max(b3, c2) == c2

        rm.force_coordinate_order = False
        assert max(b3, c2) == b3

    def test_coordinate_code(self, rm_with_categories):

        rm = rm_with_categories
        a, *_ = rm.axes["x"].points
        one, *_ = rm.axes["y"].points

        a1 = Coordinate((a, one))
        a1_reverse = Coordinate((one, a))

        assert str(a1) == "A1"
        assert str(a1) != "1A"
        assert str(a1_reverse) == "A1"
        assert str(a1_reverse) != "1A"

    def test_max_coordinate(self, rm_full):
        rm = rm_full
        max_coordinate = rm.coordinates[-1]

        assert max(rm.coordinates) == max_coordinate
        # This should work once there is an unambiguous way to determine what the maximum coordinate is
        # assert max(rm.coordinates) == max_coordinate

    def test_add_wrong_coordinate(self, rm_with_categories):
        pass
