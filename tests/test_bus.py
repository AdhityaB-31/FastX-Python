"""
Tests for Bus model.

Tests bus creation, properties, and constructor defaults.
"""

import pytest

from models.bus import Bus


class TestBusModel:
    """Test group for Bus model."""

    def test_bus_creation_defaults(self):
        """Test creating a Bus with default values."""
        bus = Bus(bus_name="Test Bus", bus_number="TN01XX0001")
        assert bus.bus_name == "Test Bus"
        assert bus.bus_number == "TN01XX0001"
        assert bus.bus_type == "SEAT"  # Default
        assert bus.total_seats == 40  # Default

    def test_bus_creation_full(self, sample_bus):
        """Test creating a Bus with all arguments."""
        assert sample_bus.bus_name == "FastX Express"
        assert sample_bus.bus_number == "PY01AB1234"
        assert sample_bus.bus_type == "Sleeper AC"
        assert sample_bus.total_seats == 40

    def test_bus_amenities_list(self, sample_bus):
        """Test amenities string to list conversion."""
        amenities = sample_bus.get_amenities_list()
        assert len(amenities) == 3
        assert "Water Bottle" in amenities
        assert "Charging Point" in amenities
        assert "TV" in amenities

    def test_bus_empty_amenities(self):
        """Test bus with no amenities."""
        bus = Bus("Test", "TN01XX0001", amenities="")
        assert bus.get_amenities_list() == []

    def test_bus_total_seats_validation(self, sample_bus):
        """Test total seats setter rejects non-positive values."""
        with pytest.raises(ValueError, match="positive number"):
            sample_bus.total_seats = 0

        with pytest.raises(ValueError, match="positive number"):
            sample_bus.total_seats = -5

    def test_bus_property_setters(self):
        """Test bus property setters."""
        bus = Bus("Original", "TN01XX0001")
        bus.bus_name = "Updated"
        bus.bus_type = "Sleeper"
        assert bus.bus_name == "Updated"
        assert bus.bus_type == "Sleeper"

    def test_bus_str(self, sample_bus):
        """Test Bus string representation."""
        result = str(sample_bus)
        assert "FastX Express" in result
        assert "PY01AB1234" in result

    @pytest.mark.parametrize(
        "bus_type,expected_in_str",
        [
            ("SEAT", "SEAT"),
            ("Sleeper AC", "Sleeper AC"),
            ("Semi-Sleeper", "Semi-Sleeper"),
        ]
    )
    def test_bus_types(self, bus_type, expected_in_str):
        """Test different bus type values."""
        bus = Bus("Test", "TN01XX0001", bus_type=bus_type)
        assert bus.bus_type == expected_in_str

    def test_bus_routine_flag(self):
        """Test is_routine property and setter."""
        bus = Bus("Daily Bus", "TN01RT1111", is_routine=True)
        assert bus.is_routine is True
        assert "Routine Daily" in str(bus)

        bus.is_routine = False
        assert bus.is_routine is False
        assert "Routine Daily" not in str(bus)
