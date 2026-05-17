#!/usr/bin/env python

"""Tests for `asciify` package."""

import pytest
from src.asciify.nodes import ImageToAscii

@pytest.fixture
def example_node():
    """Fixture to create an Example node instance."""
    return ImageToAscii()

def test_example_node_initialization(example_node):
    """Test that the node can be instantiated."""
    assert isinstance(example_node, ImageToAscii)

def test_return_types():
    """Test the node's metadata."""
    assert ImageToAscii.RETURN_TYPES == ("IMAGE", "STRING")
    assert ImageToAscii.FUNCTION == "convert"
    assert ImageToAscii.CATEGORY == "Asciify"
