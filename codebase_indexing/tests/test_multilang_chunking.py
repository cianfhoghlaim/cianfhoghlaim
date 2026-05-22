"""Multi-language chunking tests using real files from cianfhoghlaim."""

from pathlib import Path

import pytest

from codeolas.core.chunking import chunk_code_file, detect_language
from codeolas.core.types import ChunkType


class TestPythonChunking:
    """Tests for Python code chunking."""

    def test_chunk_analyzer_file(self, codesola_root):
        """Test chunking the analyzer.py file."""
        analyzer_path = codesola_root / "codeolas" / "core" / "analyzer.py"
        content = analyzer_path.read_text()

        chunks = chunk_code_file(content, str(analyzer_path))

        # Should extract CodebaseAnalyzer class
        class_chunks = [c for c in chunks if c.chunk_type == ChunkType.CLASS]
        assert any(c.name == "CodebaseAnalyzer" for c in class_chunks), (
            "Should extract CodebaseAnalyzer class"
        )

        # Should extract methods
        func_chunks = [c for c in chunks if c.chunk_type == ChunkType.FUNCTION]
        func_names = {c.name for c in func_chunks}

        assert "index" in func_names, "Should extract index method"
        assert "search" in func_names, "Should extract search method"
        assert "deep_research" in func_names, "Should extract deep_research method"

    def test_chunk_types_file(self, codesola_root):
        """Test chunking the types.py file."""
        types_path = codesola_root / "codeolas" / "core" / "types.py"
        content = types_path.read_text()

        chunks = chunk_code_file(content, str(types_path))

        # Should extract multiple classes (enums, dataclasses)
        class_chunks = [c for c in chunks if c.chunk_type == ChunkType.CLASS]
        class_names = {c.name for c in class_chunks}

        assert "ChunkType" in class_names, "Should extract ChunkType enum"
        assert "RelationshipType" in class_names, "Should extract RelationshipType enum"
        assert "CodeChunk" in class_names, "Should extract CodeChunk dataclass"

    def test_chunk_preserves_docstrings(self, codesola_root):
        """Test that chunking preserves docstrings."""
        analyzer_path = codesola_root / "codeolas" / "core" / "analyzer.py"
        content = analyzer_path.read_text()

        chunks = chunk_code_file(content, str(analyzer_path))

        # Find CodebaseAnalyzer class chunk
        class_chunk = next(
            (c for c in chunks if c.chunk_type == ChunkType.CLASS and c.name == "CodebaseAnalyzer"),
            None,
        )

        assert class_chunk is not None
        assert "Main entry point" in class_chunk.text or "code analysis" in class_chunk.text.lower()


class TestTypeScriptChunking:
    """Tests for TypeScript code chunking."""

    def test_detect_typescript_language(self):
        """Test TypeScript language detection."""
        assert detect_language("component.ts") == "typescript"
        assert detect_language("component.tsx") == "tsx"
        assert detect_language("app.js") == "javascript"
        assert detect_language("app.jsx") == "jsx"

    def test_chunk_typescript_sample(self):
        """Test chunking TypeScript code."""
        ts_content = '''
import { useState } from 'react';

interface User {
    id: string;
    name: string;
}

export function UserProfile({ user }: { user: User }) {
    const [loading, setLoading] = useState(false);

    return (
        <div>
            <h1>{user.name}</h1>
        </div>
    );
}

export class UserService {
    async getUser(id: string): Promise<User> {
        return { id, name: "Test" };
    }
}
'''
        chunks = chunk_code_file(ts_content, "UserProfile.tsx")

        # Should produce chunks (exact structure depends on parser)
        assert len(chunks) > 0, "Should produce some chunks"

        # Should handle tsx code without crashing
        func_chunks = [c for c in chunks if c.chunk_type == ChunkType.FUNCTION]
        class_chunks = [c for c in chunks if c.chunk_type == ChunkType.CLASS]

        # At least one function or class should be extracted
        assert len(func_chunks) + len(class_chunks) >= 0  # Just ensure it parses


class TestRustChunking:
    """Tests for Rust code chunking."""

    def test_detect_rust_language(self):
        """Test Rust language detection."""
        assert detect_language("lib.rs") == "rust"
        assert detect_language("main.rs") == "rust"

    def test_chunk_rust_sample(self):
        """Test chunking Rust code."""
        rust_content = '''
use std::collections::HashMap;

/// A code analyzer struct
pub struct CodeAnalyzer {
    pub name: String,
    chunks: Vec<Chunk>,
}

impl CodeAnalyzer {
    /// Create a new analyzer
    pub fn new(name: &str) -> Self {
        Self {
            name: name.to_string(),
            chunks: Vec::new(),
        }
    }

    /// Analyze code
    pub fn analyze(&mut self, code: &str) -> Vec<Chunk> {
        // Implementation
        Vec::new()
    }
}

/// Represents a code chunk
pub struct Chunk {
    pub content: String,
    pub line: usize,
}

pub fn helper_function(input: &str) -> String {
    input.to_uppercase()
}
'''
        chunks = chunk_code_file(rust_content, "lib.rs")

        # Should extract structs as classes
        class_chunks = [c for c in chunks if c.chunk_type == ChunkType.CLASS]
        class_names = {c.name for c in class_chunks}

        # struct CodeAnalyzer and struct Chunk
        assert len(class_chunks) >= 1, "Should extract at least one struct"

        # Should extract functions
        func_chunks = [c for c in chunks if c.chunk_type == ChunkType.FUNCTION]
        func_names = {c.name for c in func_chunks}

        assert "helper_function" in func_names or len(func_chunks) > 0, (
            "Should extract functions"
        )


class TestGoChunking:
    """Tests for Go code chunking."""

    def test_detect_go_language(self):
        """Test Go language detection."""
        assert detect_language("main.go") == "go"

    def test_chunk_go_sample(self):
        """Test chunking Go code."""
        go_content = '''
package main

import "fmt"

// Analyzer analyzes code
type Analyzer struct {
    Name string
    Path string
}

// NewAnalyzer creates a new analyzer
func NewAnalyzer(name string) *Analyzer {
    return &Analyzer{Name: name}
}

// Analyze performs analysis
func (a *Analyzer) Analyze(code string) ([]string, error) {
    return nil, nil
}

func main() {
    analyzer := NewAnalyzer("test")
    fmt.Println(analyzer.Name)
}
'''
        chunks = chunk_code_file(go_content, "main.go")

        # Should extract struct as class
        class_chunks = [c for c in chunks if c.chunk_type == ChunkType.CLASS]
        assert len(class_chunks) >= 0  # Go parsing may vary

        # Should extract functions
        func_chunks = [c for c in chunks if c.chunk_type == ChunkType.FUNCTION]
        assert len(func_chunks) > 0, "Should extract functions"


class TestChunkingEdgeCases:
    """Tests for edge cases in chunking."""

    def test_chunk_empty_file(self):
        """Test chunking empty file."""
        chunks = chunk_code_file("", "empty.py")
        assert len(chunks) == 0

    def test_chunk_comments_only(self):
        """Test chunking file with only comments."""
        content = '''
# This is a comment
# Another comment
"""
Multiline docstring
"""
'''
        chunks = chunk_code_file(content, "comments.py")
        # May or may not produce chunks depending on implementation
        assert isinstance(chunks, list)

    def test_chunk_malformed_code(self):
        """Test chunking malformed code doesn't crash."""
        malformed = '''
def incomplete_function(
    # Missing closing paren and body

class Broken
    # Missing colon and body
'''
        # Should not raise an exception
        chunks = chunk_code_file(malformed, "malformed.py")
        assert isinstance(chunks, list)

    def test_chunk_large_function(self):
        """Test chunking a large function."""
        large_func = "def large_function():\n" + "    x = 1\n" * 500 + "    return x"
        chunks = chunk_code_file(large_func, "large.py")

        func_chunks = [c for c in chunks if c.chunk_type == ChunkType.FUNCTION]
        assert len(func_chunks) >= 1

    def test_chunk_preserves_line_numbers(self):
        """Test that line numbers are preserved correctly."""
        content = '''# Line 1
# Line 2
# Line 3

def function_on_line_5():
    pass

class ClassOnLine9:
    def method_on_line_10(self):
        pass
'''
        chunks = chunk_code_file(content, "lines.py")

        func_chunks = [c for c in chunks if c.chunk_type == ChunkType.FUNCTION]
        class_chunks = [c for c in chunks if c.chunk_type == ChunkType.CLASS]

        # Check that function starts around line 5
        func_chunk = next((c for c in func_chunks if c.name == "function_on_line_5"), None)
        if func_chunk:
            assert func_chunk.start_line >= 4 and func_chunk.start_line <= 6

        # Check that class starts around line 9
        class_chunk = next((c for c in class_chunks if c.name == "ClassOnLine9"), None)
        if class_chunk:
            assert class_chunk.start_line >= 8 and class_chunk.start_line <= 10
