"""Unit tests for the Visualizer color scheme constants."""

import re

import pytest

import src.visualizer as viz


@pytest.mark.fast
def test_color_schemes_work_defined() -> None:
    """Test that COLOR_SCHEMES_WORK is properly defined."""
    assert hasattr(viz, "COLOR_SCHEMES_WORK")
    assert isinstance(viz.COLOR_SCHEMES_WORK, dict)
    assert len(viz.COLOR_SCHEMES_WORK) > 0


@pytest.mark.fast
def test_color_schemes_work_keys() -> None:
    """Test that COLOR_SCHEMES_WORK contains expected color scheme keys."""
    expected_schemes = ["ocean", "forest", "sunset", "lavender", "coral"]

    for scheme in expected_schemes:
        assert scheme in viz.COLOR_SCHEMES_WORK, f"Missing color scheme: {scheme}"


@pytest.mark.fast
def test_color_schemes_work_structure() -> None:
    """Test that COLOR_SCHEMES_WORK has correct structure for each scheme."""
    for scheme_name, colors in viz.COLOR_SCHEMES_WORK.items():
        assert isinstance(colors, list), f"Colors for {scheme_name} should be a list"
        assert len(colors) == 6, f"Color scheme {scheme_name} should have 6 colors"

        for color in colors:
            assert isinstance(color, str), f"Color in {scheme_name} should be a string"
            assert color.startswith("#"), f"Color {color} in {scheme_name} should be hex format"
            assert len(color) == 7, f"Color {color} in {scheme_name} should be 7 characters"


@pytest.mark.fast
def test_color_schemes_work_hex_format() -> None:
    """Test that all colors in COLOR_SCHEMES_WORK are valid hex colors."""
    hex_pattern = re.compile(r"^#[0-9A-Fa-f]{6}$")

    for scheme_name, colors in viz.COLOR_SCHEMES_WORK.items():
        for color in colors:
            assert hex_pattern.match(color), f"Invalid hex color {color} in {scheme_name}"


@pytest.mark.fast
def test_ocean_color_scheme_work() -> None:
    """Test specific ocean color scheme for work colors."""
    ocean_colors = viz.COLOR_SCHEMES_WORK["ocean"]

    assert len(ocean_colors) == 6
    assert all(color.startswith("#") for color in ocean_colors)

    # Check that colors are in expected blue range
    # Ocean colors should be blue tones
    expected_colors = ["#1E3A8A", "#1E40AF", "#2563EB", "#3B82F6", "#60A5FA", "#93C5FD"]
    assert ocean_colors == expected_colors


@pytest.mark.fast
def test_forest_color_scheme_work() -> None:
    """Test specific forest color scheme for work colors."""
    forest_colors = viz.COLOR_SCHEMES_WORK["forest"]

    assert len(forest_colors) == 6
    assert all(color.startswith("#") for color in forest_colors)

    # Check that colors are in expected green range
    expected_colors = ["#14532D", "#166534", "#15803D", "#16A34A", "#22C55E", "#4ADE80"]
    assert forest_colors == expected_colors


@pytest.mark.fast
def test_sunset_color_scheme_work() -> None:
    """Test specific sunset color scheme for work colors."""
    sunset_colors = viz.COLOR_SCHEMES_WORK["sunset"]

    assert len(sunset_colors) == 6
    assert all(color.startswith("#") for color in sunset_colors)

    # Check that colors are in expected orange range
    expected_colors = ["#9A3412", "#A03E0C", "#C2410C", "#EA580C", "#F97316", "#FB923C"]
    assert sunset_colors == expected_colors


@pytest.mark.fast
def test_lavender_color_scheme_work() -> None:
    """Test specific lavender color scheme for work colors."""
    lavender_colors = viz.COLOR_SCHEMES_WORK["lavender"]

    assert len(lavender_colors) == 6
    assert all(color.startswith("#") for color in lavender_colors)

    # Check that colors are in expected purple range
    expected_colors = ["#581C87", "#5B21B6", "#6B21A8", "#7C3AED", "#A855F7", "#C084FC"]
    assert lavender_colors == expected_colors


@pytest.mark.fast
def test_coral_color_scheme_work() -> None:
    """Test specific coral color scheme for work colors."""
    coral_colors = viz.COLOR_SCHEMES_WORK["coral"]

    assert len(coral_colors) == 6
    assert all(color.startswith("#") for color in coral_colors)

    # Check that colors are in expected pink/red range
    expected_colors = ["#BE185D", "#BE123C", "#DC2626", "#EC4899", "#F472B6", "#F9A8D4"]
    assert coral_colors == expected_colors
