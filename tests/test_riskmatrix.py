import pytest
from riskmatrix import RiskMatrix, AxisPoint, Category, Coordinate


@pytest.fixture
def rm():
    return RiskMatrix("Risk Matrix name")


@pytest.fixture
def rm_points():
    return (
        AxisPoint("A", "Unlikely", value=1),
        AxisPoint("B", "Likely", value=2),
        AxisPoint("C", "Very Likely", value=3),
        AxisPoint(1, "No Impact"),
        AxisPoint(2, "Cheap"),
        AxisPoint(3, "Expensive"),
    )


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
def rm_categories():
    return (
        Category("LOW", "Low risk", "#ffff11", "#ffffff"),
        Category("MED", "Med risk", "#ffff00", "#ffffff"),
        Category("HIG", "Hig risk", "#ff0000", "#ffffff"),
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

    rm.add_category(low)
    rm.add_category(med)
    rm.add_category(hig)

    return rm


@pytest.fixture
def rm_full(rm_with_categories, rm_coordinates):
    rm = rm_with_categories
    a, b, c = rm.axes["x"].points
    one, two, three = rm.axes["y"].points
    low, med, hig = rm.get_categories()

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


class TestAxis:
    def test_add_axis_with_points(self, rm, rm_points):
        a, b, c, *_ = rm_points

        rm.add_axis("x", points=[a, b, c])

        assert rm.axes["x"][0] is a
        assert rm.axes["x"][1] is b
        assert rm.axes["x"][2] is c

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


class TestCategory:
    def test_add_category(self, rm, rm_categories):
        low, med, hig = rm_categories

        rm.add_category(low)
        rm.add_category(med)
        rm.add_category(hig)

        assert rm.categories[1] == low
        assert rm.categories[2] == med
        assert rm.categories[3] == hig

        assert rm.categories[1].value == 1
        assert rm.categories[2].value == 2
        assert rm.categories[3].value == 3

    def test_get_categories(self, rm_with_categories, rm_categories):
        low_origin, med_origin, hig_origin = rm_categories
        low, med, hig = rm_with_categories.get_categories()

        assert low is low_origin
        assert med is med_origin
        assert hig is hig_origin

    def test_category_value(self, rm_with_categories):
        low, med, hig = rm_with_categories.get_categories()

        assert low.value == 1
        assert med.value == 2
        assert hig.value == 3

    def test_max_category(self, rm_full):
        assert rm_full.get_max_category().value == 3


class TestCoordinate:
    def test_add_coordinate(self, rm_with_categories, rm_coordinates):
        rm = rm_with_categories

        low, med, hig = rm.get_categories()
        a1, a2, a3, b1, b2, b3, c1, c2, c3 = rm_coordinates

        rm.map_coordinates(low, [a1, a2, a3, b1])
        rm.map_coordinate(med, b2)
        rm.map_coordinate(hig, c3)

        assert rm.get_category(a3) == low
        # assert rm.get_category(b2) == med
        assert rm.get_category(c3) == hig

    def test_get_coordinate(self, rm_with_categories, rm_coordinates):
        rm = rm_with_categories

        low, med, hig = rm.get_categories()
        a, b, c = rm.axes["x"].points
        one, two, three = rm.axes["y"].points

        a1, a2, a3, b1, b2, b3, c1, c2, c3 = rm_coordinates

        rm.map_coordinates(low, [a1, a2, a3, b1])
        rm.map_coordinate(med, b2)
        rm.map_coordinate(hig, c3)

        get_a3 = rm.get_coordinate("A3")
        # wrong_a3 = rm.get_coordinate("3A")
        assert get_a3 == a3
        assert rm.get_category(get_a3) == low

    def test_max_coordinate(self, rm_full):
        rm = rm_full
        max_coordinate = rm.coordinates[-1]

        assert rm.get_max_coordinate(coordinates=rm.coordinates) == max_coordinate
        # This should work once there is an unambiguous way to determine what the maximum coordinate is
        # assert max(rm.coordinates) == max_coordinate
