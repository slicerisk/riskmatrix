import pytest
from riskmatrix import RiskMatrix, AxisPoint, Category, Coordinate


@pytest.fixture
def rm():
    return RiskMatrix("Risk Matrix name")


@pytest.fixture
def rm_with_axis(rm):
    a = AxisPoint("A", "Unlikely", value=1)
    b = AxisPoint("B", "Likely", value=2)
    c = AxisPoint("C", "Very Likely", value=3)

    one = AxisPoint(1, "No Impact")
    two = AxisPoint(2, "Cheap")
    three = AxisPoint(3, "Expensive")

    rm.add_axis("x", [a, b, c])
    rm.add_axis("y", [one, two, three])

    return rm


@pytest.fixture
def rm_with_categories(rm_with_axis):
    low = Category("LOW", "Low risk", "#ffff11", "#ffffff")
    med = Category("MED", "Med risk", "#ffff00", "#ffffff")
    hig = Category("HIG", "Hig risk", "#ff0000", "#ffffff")

    rm_with_axis.add_category(low)
    rm_with_axis.add_category(med)
    rm_with_axis.add_category(hig)

    return rm_with_axis


@pytest.fixture
def rm_full(rm_with_categories):
    a1 = Coordinate((a, one))
    a2 = Coordinate((a, two))
    a3 = Coordinate((a, three))
    b1 = Coordinate((b, one))
    b2 = Coordinate((b, two))
    b3 = Coordinate((b, three))
    c1 = Coordinate((c, one))
    c2 = Coordinate((c, two))
    c3 = Coordinate((c, three))

    rm.map_coordinates(low, [a1, a2, a3, b1])
    rm.map_coordinates(med, [b2, c1])
    rm.map_coordinates(hig, [b3, c2, c3])


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
    def test_add_axis_with_points(self, rm):
        a = AxisPoint("A", "Unlikely", value=1)
        b = AxisPoint("B", "Likely", value=2)
        c = AxisPoint("C", "Very Likely", value=3)

        rm.add_axis("x", [a, b, c])

        assert rm.axes["x"][0] is a
        assert rm.axes["x"][1] is b
        assert rm.axes["x"][2] is c

    def test_add_axis_with_int(self, rm):
        rm.add_axis("x", 4)

        assert rm.axes["x"][0].code == "1"
        assert rm.axes["x"][1].code == "2"
        assert rm.axes["x"][2].code == "3"
        assert rm.axes["x"][3].code == "4"
        assert len(rm.axes["x"]) == 4


class TestCategory:
    def test_add_category(self, rm):
        low = Category("LOW", "Low risk", "#ffff11", "#ffffff")
        med = Category("MED", "Med risk", "#ffff00", "#ffffff")
        hig = Category("HIG", "Hig risk", "#ff0000", "#ffffff")

        rm.add_category(low)
        rm.add_category(med)
        rm.add_category(hig)

        assert rm.categories[1] == low
        assert rm.categories[2] == med
        assert rm.categories[3] == hig

        assert rm.categories[1].value == 1
        assert rm.categories[2].value == 2
        assert rm.categories[3].value == 3

    def test_get_categories(self, rm_with_categories):
        low, med, hig = rm_with_categories.get_categories()

        assert low.value == 1
        assert med.value == 2
        assert hig.value == 3


class TestCoordinate:
    def test_add_coordinate(self, rm_with_categories):
        rm = rm_with_categories

        low, med, hig = rm.get_categories()
        a, b, c = rm.axes["x"].get_points()
        one, two, three = rm.axes["y"].get_points()

        a1 = Coordinate((a, one))
        a2 = Coordinate((a, two))
        a3 = Coordinate((a, three))
        b1 = Coordinate((b, one))
        b2 = Coordinate((b, two))
        b3 = Coordinate((b, three))

        rm.map_coordinates(low, [a1, a2, a3, b1])
        rm.map_coordinate(med, b2)
        rm.map_coordinate(hig, b3)

        assert rm.get_category("A3") == low
        assert rm.get_category(a3) == low
        assert rm.get_category("3A") == None
        assert a1 == "A1"
        assert a1 != "1A"
        assert rm.get_max_category(["A1", "B1", "B2"]) == med
        assert rm.get_max_coordinate([b3, a1, b2]) == b3
