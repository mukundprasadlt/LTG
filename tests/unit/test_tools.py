import os
os.environ['ENVIRONMENT'] = "test"
import pytest
import sys
from unittest.mock import Mock, MagicMock, AsyncMock, patch
path1 = "__file__".split("tests")[0]
from app.modules.policy.tools import (
    apply_markdown,
    apply_markdown_gap,
    merge_sets,
    create_policy_markdown
)
sys.path.append(path1)


sample_control = {
    "DomainId": "1",
    "Controls": [
        {"controlId": "101", "name": "Test Control", "description": "A test description"}
    ]
}

sample_gap_control = {
    "domain_number": "1",
    "controls": [
        {"control_number": "101", "control_name": "Gap Control", "control_description": "Gap description"}
    ]
}

# Test for apply_markdown
def test_apply_markdown():
    result = apply_markdown(sample_control, 1)
    assert result == ["**1:1:101 - Test Control**: A test description"]
    assert sample_control["Controls"][0]["markdown"] == result[0]
    assert sample_control["DomainId"] == "1:1"

# Test for apply_markdown_gap
def test_apply_markdown_gap():
    result = apply_markdown_gap(sample_gap_control, 1)
    assert result == ["**1:1:101 - Gap Control**: Gap description"]
    assert sample_gap_control["controls"][0]["markdown"] == result[0]
    assert sample_gap_control["domain_number"] == "1:1"

# Test for merge_sets
def test_merge_sets():
    setA = {1, 2, 3}
    setB = [{2, 4}, {5}]
    result = merge_sets(setA, setB)
    assert result[0] == {1, 2, 3, 4}
    assert result[1] == {5}
    
# Test for create_policy_markdown
def test_create_policy_markdown():
    test_obj = {
        "domain": "Test Domain",
        "Controls": [
            {"id": "1", "name": "Control Name", "description": "Description"}
        ]
    }
    result = create_policy_markdown(test_obj)
    assert "### Domain: Test Domain" in result
    assert "- **Control ID**: 1" in result
    assert "- **Name**: Control Name" in result
    assert "- **Description**: Description" in result
