=====
Usage
=====

To use Riskmatrix in a project::

    from riskmatrix import Riskmatrix

    rm = Riskmatrix("RAM")
    rm.add_axis("Severity", size=5)
    rm.add_axis("Probability", size=5, use_letters=True)

Define a riskmatrix
-------------------

Compare coordinates
-------------------
Determining if a coordinate is equal or not, can be done in two ways.

First, by seeing if the location of the coordinate is exactly the same. If that's
the case, they are of course the same.

Second is looking at the sum of all the points in the coordinate. This can lead to
coordinates which are not at the same place, but their points have an equivalent position.

The Python operators for comparing coordinates are using the second interpretation.
For a strict location comparison, use my_coordinate.location_equals(other_coordinate).

Example
-------

Imagine we have 3 axes called A, B and C.

We have two coordinates in this space.
Coordinate 1 has a value of A=1, B=2 and C=3
Coordinate 2 has the same values, but on different axes. E.g. A=1, B=3, C=2.

How do we determine which coordinate has a higher value if the coordinates point to equivalent positions?

We need a priority in the axes. So we say that A takes priority over B, which takes priority over C.
Using the priority, we can go through and compare each individual axis in turn, and compare the points
individually until we find an axis that has a higher value.

In our example, we start with the most important axis: A. The values are the same, so we continue with B.
Coordinate 2 is higher than Coordinate 1, so we can say that Coordinate 1 is higher.
