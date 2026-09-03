"""Tests for code chunking."""

import pytest

from codeolas.core.chunking import chunk_code_file, detect_language
from codeolas.core.types import ChunkType


def test_detect_language_python():
    """Test Python language detection."""
    assert detect_language("test.py") == "python"
    assert detect_language("test.pyi") == "python"


def test_detect_language_typescript():
    """Test TypeScript language detection."""
    assert detect_language("test.ts") == "typescript"
    assert detect_language("test.tsx") == "tsx"


def test_detect_language_unknown():
    """Test unknown language returns None."""
    assert detect_language("test.xyz") is None


def test_chunk_python_function():
    """Test chunking a Python function."""
    content = '''
def hello(name: str) -> str:
    """Say hello."""
    return f"Hello, {name}!"
'''
    chunks = chunk_code_file(content, "test.py")

    assert len(chunks) >= 1
    func_chunks = [c for c in chunks if c.chunk_type == ChunkType.FUNCTION]
    assert len(func_chunks) >= 1
    assert func_chunks[0].name == "hello"


def test_chunk_python_class():
    """Test chunking a Python class."""
    content = '''
class Greeter:
    """A greeter class."""

    def greet(self, name: str) -> str:
        return f"Hello, {name}!"
'''
    chunks = chunk_code_file(content, "test.py")

    class_chunks = [c for c in chunks if c.chunk_type == ChunkType.CLASS]
    assert len(class_chunks) >= 1
    assert class_chunks[0].name == "Greeter"


def test_chunk_preserves_line_numbers():
    """Test that chunks preserve line numbers."""
    content = '''# Comment
def first():
    pass

def second():
    pass
'''
    chunks = chunk_code_file(content, "test.py")

    func_chunks = [c for c in chunks if c.chunk_type == ChunkType.FUNCTION]
    # May be merged or separate depending on size thresholds
    assert len(func_chunks) >= 1

    # First chunk should start after the comment (around line 2)
    first_chunk = func_chunks[0]
    assert first_chunk.start_line >= 1
    assert first_chunk.start_line <= 3


def test_chunk_empty_file():
    """Test chunking an empty file."""
    chunks = chunk_code_file("", "test.py")
    assert len(chunks) == 0


def test_chunk_fallback_for_unknown_language():
    """Test fallback chunking for unknown language."""
    content = "line1\nline2\nline3\n" * 20
    chunks = chunk_code_file(content, "test.xyz")

    assert len(chunks) >= 1
    assert all(c.chunk_type == ChunkType.OTHER for c in chunks)
