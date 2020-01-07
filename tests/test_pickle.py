import pickle
from .test_riskmatrix import (
    rm_full,
    rm_with_categories,
    rm_coordinates,
    rm_with_axis,
    rm,
    rm_points,
    rm_categories,
)


def test_pickle_coordinates(tmpdir, rm_full):
    a1 = rm_full.get_coordinate("A1")
    b2 = rm_full.get_coordinate("B2")

    tmp_file = str(tmpdir.join("test_pickle_coordinates"))

    with open(tmp_file, "wb") as f:
        pickle.dump([a1, b2], f)

    with open(tmp_file, "rb") as f:
        p = pickle.load(f)

    assert p == [a1, b2]
