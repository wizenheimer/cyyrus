from typing import Dict, List

import pytest
from cyyrus.models.spec import level_order_traversal  # type: ignore


@pytest.mark.parametrize(
    "dependencies, expected_output",
    [
        (
            {
                "document_id": ["invoice"],
                "document_info": ["invoice"],
                "invoice_items": ["invoice"],
                "invoice_questions": ["invoice_items"],
            },
            [["invoice"], ["document_id", "document_info", "invoice_items"], ["invoice_questions"]],
        ),
        ({"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}, [["D"], ["B", "C"], ["A"]]),
        ({"A": [], "B": ["A"], "C": ["A"], "D": ["B", "C"]}, [["A"], ["B", "C"], ["D"]]),
        ({}, []),
        ({"A": []}, [["A"]]),
        ({"A": ["B"], "B": ["A"]}, []),  # Cyclic dependency should result in empty list
    ],
)
def test_level_order_traversal(
    dependencies: Dict[str, List[str]], expected_output: List[List[str]]
):
    assert list(level_order_traversal(dependencies)) == expected_output


def test_missing_dependency():
    dependencies = {"A": ["B"], "C": ["B"]}
    result = list(level_order_traversal(dependencies))
    assert "B" in result[0], "B should be in the first level as it's not in the dependencies dict"
    assert set(result[1]) == {"A", "C"}, "A and C should be in the second level"


def test_all_nodes_included():
    dependencies = {"A": ["B", "C"], "D": ["E"]}
    result = list(level_order_traversal(dependencies))
    all_nodes = set(sum(result, []))  # Flatten the result
    assert all_nodes == {"A", "B", "C", "D", "E"}, "All nodes should be included in the result"


def test_order_within_levels():
    dependencies = {"A": ["D"], "B": ["D"], "C": ["D"], "D": []}
    result = list(level_order_traversal(dependencies))
    assert result[0] == ["D"], "D should be in the first level"
    assert set(result[1]) == {"A", "B", "C"}, "A, B, C should be in the second level"
    assert len(result) == 2, "There should be only two levels"
