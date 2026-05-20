#!/usr/bin/env python

"""Tests for `Textify` package."""

import pytest
from src.textify.node import Textify

@pytest.fixture
def example_node():
    """Fixture to create an Example node instance."""
    return Textify()

def test_example_node_initialization(example_node):
    """Test that the node can be instantiated."""
    assert isinstance(example_node, Textify)

def test_return_types():
    """Test the node's metadata."""
    assert Textify.RETURN_TYPES == ("IMAGE",)
    assert Textify.FUNCTION == "convert"
    assert Textify.CATEGORY == "Textify"
