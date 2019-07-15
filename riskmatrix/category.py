from __future__ import annotations
from typing import Optional
from functools import total_ordering


@total_ordering
class Category:
    """
    A collection of points has a RiskMatrix Category.
    """

    def __init__(
        self,
        code: str,
        name: str,
        color: str,
        text_color: str,
        description: str = "",
        value: Optional[int] = None,
    ) -> None:
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

    def __eq__(self, other: Category) -> bool:
        return self.value == other.value

    def __lt__(self, other: Category) -> bool:
        return self.value < other.value
