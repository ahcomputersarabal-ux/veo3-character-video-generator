"""Unit tests for character manager"""

import pytest
import tempfile
import os
from pathlib import Path
from src.character.character_manager import CharacterManager


@pytest.fixture
def temp_cache_dir():
    """Create temporary cache directory"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def character_manager(temp_cache_dir):
    """Create character manager with temp directory"""
    return CharacterManager(cache_dir=temp_cache_dir)


class TestCharacterManager:
    """Test cases for CharacterManager"""

    def test_add_character(self, character_manager):
        """Test adding a character"""
        char = character_manager.add_character(
            id="test_char",
            name="Test Character",
            description="A test character",
            reference_images=[]
        )

        assert char.id == "test_char"
        assert char.name == "Test Character"
        assert char.description == "A test character"

    def test_get_character(self, character_manager):
        """Test retrieving a character"""
        character_manager.add_character(
            id="test_char",
            name="Test",
            description="Test",
            reference_images=[]
        )

        char = character_manager.get_character("test_char")
        assert char is not None
        assert char.id == "test_char"

    def test_list_characters(self, character_manager):
        """Test listing all characters"""
        character_manager.add_character("char1", "Char 1", "Test 1", [])
        character_manager.add_character("char2", "Char 2", "Test 2", [])

        chars = character_manager.list_characters()
        assert len(chars) == 2

    def test_delete_character(self, character_manager):
        """Test deleting a character"""
        character_manager.add_character("test_char", "Test", "Test", [])
        result = character_manager.delete_character("test_char")

        assert result is True
        assert character_manager.get_character("test_char") is None

    def test_get_nonexistent_character(self, character_manager):
        """Test getting a nonexistent character"""
        char = character_manager.get_character("nonexistent")
        assert char is None
